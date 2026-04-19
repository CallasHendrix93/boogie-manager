# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import pathlib

from .base import AudioWrapper
from .set_defaults import *


def grab_all_music_files(basepath=ROOTFOLDER, require_numeric=True, tagdf=FIELDNAMES):
    
    """
    grab_all_music_files : creates a dataframe of all music files in the library with their metadata
    
    :param basepath        : (str) root folder of the music library
    :param require_numeric : (bool) if True, of the folders directly below the root, only those 
                             folder names whose first two characters are digits will be included.
                             E.g. a folder '01 metal' or '05 jazz' will be included but 'new downloads'
                             or 'to be added' will not.
                             If False, all contents of 'basepath' will be included 
    :param tagdf           : (DataFrame) dataframe with the supported file types as columns
                             and human-readable tag names (e.g. 'artist', 'album') as rows.
                             Each element is the field name to be used for that tag on that
                             type of file
                      
    return df : (DataFrame) dataframe with the file paths as rows and the tags (as 
                they appear in the index of 'tagdf') as columns. Each element is the
                value of that tag for that file
    """

    # Grab all the music files (MP3/MP4/FLAC) in the selected folder
    # (see note on 'require_numeric' in docstring)
    masterlist = []
    p = pathlib.Path(basepath)
    toplevel_dirs = list(p.glob('*'))
    for dn in toplevel_dirs:
        if dn.is_dir() and (dn.stem[:2].isnumeric() or require_numeric == False):
            masterlist.extend(list(dn.rglob('*.m4a')))
            masterlist.extend(list(dn.rglob('*.mp3')))
            masterlist.extend(list(dn.rglob('*.flac')))

    # Create an empty dataframe with the tags ('artist', 'album' etc.) as columns
    # and the paths of the music files (relative to the root folder) as rows.
    # From the list of tags, remove 'album art' (should not be written to the dataframe)
    # and add a column for the length (not a tag but a property of the audio file itself)   
    alltags = list(tagdf.index)
    alltags.remove('album art')     
    df = pd.DataFrame(columns=alltags + ['length'], index=[p.relative_to(basepath) for p in masterlist])

    # Grab the metadata and length for each file, using the AudioWrapper class to
    # read data from MP3, MP4 and FLAC files in the same way
    for mf in masterlist:
        tag_obj = AudioWrapper(mf)
        # Grab the metadata for each file
        for tag in alltags:
            val = tag_obj.get_value(tag)
            df.loc[mf.relative_to(basepath), tag] = val
        # Grab the length for each file
        df.loc[mf.relative_to(basepath), 'length'] = tag_obj.get_length()

    return df


def add_derived_cols(df, sourcedict=SOURCEDICT, sep='.'):

    """
    add_derived_cols : adds some columns to the dataframe produced by 'grab_all_music_files'
                       for easier grouping and processing

    :param df         : (DataFrame) the original dataframe
    :param sourcedict : (dict) dictionary mapping various values for the file source tag (stored in
                        the comment field) to a smaller set of shorter names
    :param sep        : (str) separator for nesting levels used in genre tags, e.g. '.', '-' or '|'.
                        If None, genre tags are assumed not to use nesting and the interpretation of
                        nesting levels is skipped. See longer comment below

    :return df_extended : (DataFrame) the original dataframe with some columns added, which
                          are derived from the information in the original columns
    """

    # Make a copy so the function doesn't modify its own input
    df_extended = df.copy()

    # Add a column for the file type (the row labels are file paths)
    df_extended['File type'] = [idx.suffix for idx in df_extended.index]

    # Quirk of my library: genres are tagged with a sort of nested Dewey Decimal System
    # e.g. '03.01.04 Philadelphia soul' (a part of '03.01 soul' which is a part of '03 soul/funk/disco').
    # These added columns split out the genre tag to its different nesting levels,
    # e.g. for '03.01.04 Philadelphia soul' you would end up with
    # 'genre level 1' = '03'
    # 'genre level 2' = '01'
    # 'genre level 3' = '04'
    # This for easier processing and filtering later on
    if sep is not None:
        max_genre_nesting = max([len(genrestring.split(sep)) for genrestring in df_extended['genre']])
        for nest_lvl in range(max_genre_nesting):
            df_extended['genre level {0}'.format(nest_lvl + 1)] = [np.nan for i in range(len(df_extended))]
        for i in range(len(df_extended)):
            genre = df_extended['genre'].iloc[i]
            genre_levels = genre.split(sep)
            # Strip out the actual NAME of the genre - we just want the numbers
            genre_levels[-1] = genre_levels[-1].split(' ')[0]
            for j in range(len(genre_levels)):
                df_extended['genre level {0}'.format(j + 1)].iloc[i] = genre_levels[j]    

    genrefolders = []
    for filepath in df_extended.index:
        lvl1parent = filepath.parent
        if lvl1parent.stem.startswith('Disc '):
            genrefolders.append(str(lvl1parent.parent.parent.parent))
        else:
            genrefolders.append(str(lvl1parent.parent.parent))
    df_extended['genre folder'] = genrefolders

    # Get the file sources (stored in the comments)
    # and map them to shorter category names
    # (and sometimes multiple different values to the same category)
    sources = []
    for filepath in df_extended.index:
        source = df_extended.loc[filepath, 'comment']
        if source in sourcedict.keys():
            sources.append(sourcedict[source])
        else:
            sources.append('99. Other')
    df_extended['source'] = sources    

    return df_extended


def check_genre_placement(df_extended, rootfolder=ROOTFOLDER, splitfolder=SPLITFOLDER):

    """
    check_genre_placement : check if each file's placement in the directory structure matches its genre tag
                            (only useful if you have a genre-based directory structure)

    :param df_extended : (DataFrame) dataframe with information about the music library, as returned by 
                         'add_derived_cols'
    :param rootfolder  : (str) root folder where the entire music library is stored
    :param splitfolder : (str) folder where the music of 'split' artists is stored (i.e. artists whose music
                         is split across multiple genres at the highest nesting level)
    :param folder_df   : (DataFrame) dataframe with all the different genre tags in the library as index,
                         and a single column which stores the (absolute) path of the folder where that genre
                         should be stored

    """

    rp = pathlib.Path(rootfolder)

    # Get the unique combinations of artist + genre tag + genre folder
    # (excluding all compilation tracks)

    df_artists_genres = df_extended[df_extended['compilation'].isna()][[
                        'artist', 'genre level 1', 'genre level 2', 
                        'genre level 3', 'genre folder']].drop_duplicates(
                        ).reset_index(drop=True)
    gb_artists_genres = df_artists_genres.groupby('artist')
    artists = list(gb_artists_genres.groups.keys())

    # Get the folder where each genre is SUPPOSED to be stored

    lvl1folders = {lvl1tag: str(list(rp.glob(lvl1tag + '*'))[0].relative_to(rp)) for lvl1tag in df_extended['genre level 1'].unique()}
    lvl2folders = {}
    for lvl2tag in df_extended.groupby(['genre level 1', 'genre level 2']).groups.keys():
        lvl1folder = list(rp.glob(lvl2tag[0] + '*'))[0]
        try:
            lvl2folders[lvl2tag] = str(list(lvl1folder.glob(lvl2tag[1] + '*'))[0].relative_to(rp))
        except IndexError:
            lvl2folders[lvl2tag] = str(lvl1folder.relative_to(rp))
    lvl3folders = {}
    for lvl3tag in df_extended[~df_extended['genre level 3'].isna()].groupby(['genre level 1', 'genre level 2', 'genre level 3']).groups.keys():
        lvl1folder = list(rp.glob(lvl3tag[0] + '*'))[0]
        try:
            lvl2folder = list(lvl1folder.glob(lvl3tag[1] + '*'))[0]
        except IndexError:
            lvl3folders[lvl3tag] = str(lvl1folder.relative_to(rp))
            continue
        try:
            lvl3folders[lvl3tag] = str(list(lvl2folder.glob(lvl3tag[2] + '*'))[0].relative_to(rp))
        except IndexError:
            lvl3folders[lvl3tag] = str(lvl2folder.relative_to(rp))

    # Get the artist's supposed folder based on their genre tag(s)

    for artist in artists:
        subdf_artist = gb_artists_genres.get_group(artist)
        if len(subdf_artist['genre level 1'].unique()) > 1:
            supposed_folder = splitfolder
        elif len(subdf_artist['genre level 1'].unique()) == 1 and len(subdf_artist['genre level 2'].unique()) > 1:
            supposed_folder = lvl1folders[subdf_artist['genre level 1'].iloc[0]]
        elif len(subdf_artist['genre level 1'].unique()) == 1 and len(subdf_artist['genre level 2'].unique()) == 1 and \
            (len(subdf_artist['genre level 3'].unique()) > 1 or any(subdf_artist['genre level 3'].isna())):
            artist_genre_tag = (subdf_artist['genre level 1'].iloc[0], subdf_artist['genre level 2'].iloc[0])
            supposed_folder = lvl2folders[artist_genre_tag]
        else:
            artist_genre_tag = (subdf_artist['genre level 1'].iloc[0], subdf_artist['genre level 2'].iloc[0], subdf_artist['genre level 3'].iloc[0])
            supposed_folder = lvl3folders[artist_genre_tag]
        genre_folder = subdf_artist['genre folder'].iloc[0]

        # Compare the supposed against the actual folder
        if genre_folder != supposed_folder:
            print('Artist misplaced:', artist)
            print('Supposed location:', supposed_folder)
            print('Actual location:', genre_folder)
        # If an artist's non-compilation tracks are split across multiple genre folders, something is wrong as well
        elif len(subdf_artist['genre folder'].unique()) > 1:
            print('Artist split over multiple genre folders:', artist)
            print(subdf_artist['genre folder'].unique())

