# -*- coding: utf-8 -*-

import pathlib

from boogie_manager.set_defaults import *
from boogie_manager.base import AudioWrapper, AlbumArt


def titles2filenames(folder, titlecase=True, titlecase_list=TITLECASE_EN, tagdf=FIELDNAMES):

    """
    titles2filenames : sets the filename to the title for all files in a given folder
                    
    :param folder         : (str) path of the folder
    :oaram titlecase      : (bool) whether or not to correct the title to "title case"
    :param titlecase_list : (tuple) tuple of all the words to make lowercase for title case
    :param tagdf          : (DataFrame) dataframe with the supported file types as columns
                            and human-readable tag names (e.g. 'artist', 'album') as rows.
                            Each element is the field name to be used for that tag on that
                            type of file.
    """
    
    # Grab all the music files in the specified folder (including subfolders)
    p = pathlib.Path(folder)
    mfs = list(p.rglob('*.mp3')) + list(p.rglob('*.m4a')) + list(p.rglob('*.flac'))
    
    for mf in mfs:
        # Get each file's title
        tag_obj = AudioWrapper(mf, tagdf)
        title = tag_obj.get_value('title')
        # Replace some characters which are forbidden in (Windows) filenames
        title = title.replace('?', '')
        title = title.replace('/', '-')
        title = title.replace(':', ' -')
        title = title.replace('"', '\'')
        # Replace specific words from 'titlecase_list' (e.g. 'And', 'Or')
        # with their lower-case counterparts
        if titlecase:
            for word in titlecase_list:
                word_padded = ' ' + word + ' '
                title = title.replace(word_padded, word_padded.lower())
        # Generate the full new path
        newfilename = title + mf.suffix
        newpath = mf.parent / newfilename
        # Check if the filename already matches the title.
        # If not, try to set the filename to the generated title string
        if str(newpath) != str(mf):
            try:
                mf.rename(newpath)
                print('renamed file {0} to {1}'.format(mf, newpath))
            except (OSError, FileExistsError):
                print('could not rename file {0} to {1}'.format(mf, newpath))
    

def batch_cleanup(folder, strip_tags=False, tagdf=FIELDNAMES):
    
    """
    batch_cleanup : strips non-whitelisted tags from the files in a given folder and sets
                    the title field to the filename
                    
    :param folder     : (str) path of the folder
    :param strip_tags : (bool) whether or not to strip non-whitelisted tags from the files
    :param tagdf      : (DataFrame) dataframe with the supported file types as columns
                        and human-readable tag names (e.g. 'artist', 'album') as rows.
                        Each element is the field name to be used for that tag on that
                        type of file. Relevant here mostly because (if 'strip_tags' == True)
                        tag fields not appearing in 'tagdf' will be stripped from all 
                        music files in the folder!
    """

    # Grab all the music files in the specified folder (including subfolders)    
    p = pathlib.Path(folder)
    mfs = list(p.rglob('*.mp3')) + list(p.rglob('*.m4a')) + list(p.rglob('*.flac'))
    
    for mf in mfs:
        # Make an AudioWrapper object to access file metadata
        tag_obj = AudioWrapper(mf, tagdf)
        # If track numbers are in 'x/y' format ('track X out of Y tracks total')
        # simplify this to 'x'.
        # E.g. if the track number is '4/9', it simply becomes '4'
        trkno = tag_obj.get_value('track')
        if type(trkno) is str:
            if '/' in trkno:
                tag_obj.set_value('track', trkno.split('/')[0])
        # Get the title
        oldtitle = tag_obj.get_value('title')
        # If the title does not match the filename, use the filename
        # as the new title
        if oldtitle != mf.stem:
            tag_obj.set_value('title', mf.stem)
            print('set title of file {0} to {1}'.format(mf, mf.stem))
        # If specified, strip from the file all tags that don't
        # explicitly appear in the 'tagdf' column for that file's file type
        if strip_tags:
            tag_obj.remove_unused_tags()
        # Save the changes to the file metadata
        tag_obj.save()
  
        
def strip_phrase(folder, rstrip_phrase, lstrip_phrase=None):

    """
    strip_phrase : strips a given string from the filenames of all music files in a folder
                    
    :param folder        : (str) path of the folder
    :param rstrip_phrase : (str) phrase to strip from the end of each filename
    :param lstrip_phrase : (str) phrase to strip from the start of each filename
    """

    # Grab all the music files in the specified folder (including subfolders)
    p = pathlib.Path(folder)
    mfs = list(p.rglob('*.mp3')) + list(p.rglob('*.m4a')) + list(p.rglob('*.flac'))
    
    for mf in mfs:
        # Get each file's filename and remove 'rstrip_phrase' from the end of
        # each filename
        oldfilestem = mf.stem
        newfilestem = oldfilestem.removesuffix(rstrip_phrase)
        # If specified, also remove 'lstrip_phrase' from the start of
        # each filename
        if lstrip_phrase is not None:
            newfilestem = oldfilestem.removeprefix(lstrip_phrase)
        # Generate the full new path
        newfilename = newfilestem + mf.suffix
        newpath = mf.parent / newfilename
        # Check if the new path is actually different from the old one.
        # If yes, try to rename the file
        if str(newpath) != str(mf):
            try:
                mf.rename(newpath)
                print('renamed file {0} to {1}'.format(mf, newpath))
            except (OSError, FileExistsError):
                print('could not rename file {0} to {1}'.format(mf, newpath))
        
        
def clean_discography(folder, artist_nesting=0, skip_name='Import', tagdf=FIELDNAMES):
    
    """
    clean_discography : easily adds years, album tags and album sort tags to 
                        multiple albums in a folder. Assumes the folder names
                        correspond to the album titles; clean this up first if
                        necessary
                        
    :param folder         : (str) path of the top-level folder of interest
    :param artist_nesting : (int) level of nesting within the folder where the artist folder(s) should be sought. 
                            If artist_nesting == 0, 'folder' itself will be considered the artist folder, and its subdirectories
                            album folders.
                            If artist_nesting == 1, the direct subdirectories of 'folder' will be considered artist folders, and
                            *their* subdirectories album folders.
                            If artist_nesting == 2, the subdirectories of subdirectories of 'folder' will be considered artist
                            folders, etc..
    :param skip_name      : (str) folder name to always skip
    :param tagdf          : (DataFrame) dataframe with the supported file types as columns
                            and human-readable tag names (e.g. 'artist', 'album') as rows.
                            Each element is the field name to be used for that tag on that
                            type of file.
    """
    
    # Get Path objects for all the artist folders, given the nesting level specified
    if artist_nesting == 0:
        artist_folders = [pathlib.Path(folder)]
    else:
        p_top = pathlib.Path(folder)
        globstring = '/'.join(['*' for i in range(artist_nesting)])
        artist_folders = [p for p in list(p_top.glob(globstring)) if p.is_dir() and p.stem != skip_name]

    for artist_folder in artist_folders:
        # Get the album folders within each album folder
        dirlist = [p for p in list(artist_folder.glob('*')) if p.is_dir()]
        
        # Print the list of folders found (so the user can verify the script found the album folders as intended)
        print('\nFolder:', artist_folder)
        print('Albums found:')
        for p in dirlist:
            print(p.stem)
            
        # Ask the user to input year data (and possibly an extra A/B/C tag for sorting) for each album
        years = {}
        for p in dirlist:
            inputstr = '\nPlease provide the release year of the album {0}.'.format(p.stem) \
                     + ' Use A, B, C etc. to sort albums released in the same year;' \
                     + ' the first 4 characters of the string will be interpreted as the year.\n'
            years[p] = input(inputstr)
            
        for p in dirlist:
            # For each album, define the album, year, and sort album tags
            # based on the album folder name and the year provided
            albumtitle = p.stem
            sortstr = years[p]
            year = sortstr[:4]
            sortalbum = sortstr + ' - ' + albumtitle
            # Grab all music files in the folder
            # (use rglob, just in case there are 'Disc 1', 'Disc 2', etc. folders within the album folder)
            mfs = list(p.rglob('*.mp3')) + list(p.rglob('*.m4a')) + list(p.rglob('*.flac'))
            # Set the new tag values to each file
            for mf in mfs:
                tag_obj = AudioWrapper(mf, tagdf)
                tag_obj.set_value('album', albumtitle)
                tag_obj.set_value('year', year)
                tag_obj.set_value('sort album', sortalbum)
                tag_obj.save()
                print('updated year, album, sort album tags for file {0}: {1}'.format(mf, sortalbum))


def batch_add_album_art(folder, album_nesting=0, image_filetypes=tuple(MIME_TYPES.keys())):

    """
    batch_add_album_art : function to automatically add album art to large numbers of files.
                          Within each album folder, it looks for an image with the same filename
                          as the folder name, then writes that as the album cover to each music
                          file in that album folder and subfolders

    :param folder          : (str) path of the folder
    :param album_nesting   : (int) level of nesting within the folder where the album folder(s) should be sought. 
                             If album_nesting == 0, 'folder' itself will be considered the album folder.
                             If album_nesting == 1, the direct subdirectories of 'folder' will be considered album folders.
                             If album_nesting == 2, the subdirectories of subdirectories of 'folder' will be considered album
                             folders, etc..
    :param image_filetypes : (tuple) tuple of image file extensions to look for, e.g. ('.jpg', '.jpeg', '.png', '.bmp').
                             In each album folder, the function tries the file types in order, looking first for 
                             <foldername>.jpg, then for <foldername>.jpeg, etc. 
    """


    # Get Path objects for all the album folders, given the nesting level specified
    if album_nesting == 0:
        album_folders = [pathlib.Path(folder)]
    else:
        p_top = pathlib.Path(folder)
        globstring = '/'.join(['*' for i in range(album_nesting)])
        album_folders = [p for p in list(p_top.glob(globstring)) if p.is_dir()]

    # Find the album cover (assuming the file is named the same as the folder),
    # trying all the specified file extensions until one is found
    for folder in album_folders:
        albumname = folder.stem
        for extension in image_filetypes:
            albumcover_path = folder / (albumname + extension)
            if albumcover_path.exists():
                break
        else:
            print('No album cover found for album {0}'.format(albumname))
            continue


        # Grab all music files in the folder
        # (use rglob, just in case there are 'Disc 1', 'Disc 2', etc. folders within the album folder);
        # separate them by file type as different file types require different means of applying album art
        mp3files = list(folder.rglob('*.mp3'))
        mp4files = list(folder.rglob('*.m4a'))
        flacfiles = list(folder.rglob('*.flac'))

        art_obj_dict = {}

        # For each type of music file, create an AlbumArt object of the appropriate type
        # and assign it to the relevant files
        if len(mp3files) > 0:
            art4mp3 = AlbumArt(albumcover_path, 'MP3')
            for mp3file in mp3files:
                art_obj_dict[mp3file] = art4mp3
        if len(mp4files) > 0:
            art4mp4 = AlbumArt(albumcover_path, 'MP4')
            for mp4file in mp4files:
                art_obj_dict[mp4file] = art4mp4
        if len(flacfiles) > 0:
            art4flac = AlbumArt(albumcover_path, 'FLAC')
            for flacfile in flacfiles:
                art_obj_dict[flacfile] = art4flac

        # Write the album art to the audio files
        try: 
            for audiofile in art_obj_dict.keys():
                wrapper = AudioWrapper(audiofile)
                wrapper.add_album_art(art_obj_dict[audiofile])
                wrapper.save()
            print('Wrote album art for album {0}'.format(albumname))
        # Very high-resolution album covers may be rejected, hence the exception
        except Exception:
            print('Cover for album {0} too large to write'.format(albumname))

    
def adopt_filenames(srcfolder, dstfolder, offset=0):

    """
    adopt_filenames : function to set the filename of each audio file in a folder
                      to that of an audio file in a different folder with the same
                      track number

    :param srcfolder : (str) path of the source folder to copy filenames from
    :param dstfolder : (str) path of the target folder whose files should be renamed
    :param offset    : (int) track number offset. E.g. if offset = 3, then the name of
                       track 1 from the source folder will be applied to track 4 in the
                       target folder, track 2 to track 5, etc.. 
                       Can also be negative for an offset in the other direction: e.g.
                       if offset = -4, then the name of track 5 from the source folder
                       will be applied to track 1 in the target folder, track 6 to
                       track 2, etc..
    """

    # Get Path objects for both folders
    src_p = pathlib.Path(srcfolder)
    dst_p = pathlib.Path(dstfolder)

    # Grab all music files in the folder
    # (use rglob, just in case there are 'Disc 1', 'Disc 2', etc. folders within the album folder)
    src_files = list(src_p.rglob('*.mp3')) + list(src_p.rglob('*.m4a')) + list(src_p.rglob('*.flac'))
    dst_files = list(dst_p.rglob('*.mp3')) + list(dst_p.rglob('*.m4a')) + list(dst_p.rglob('*.flac'))

    # Make a dictionary mapping track numbers (in the destination folder) to desired filenames
    filename_dict = {}

    # Fill the dictionary based on the filenames in the source folder, taking the
    # specified offset into account
    for src_file in src_files:
        filename = src_file.stem
        src_wrapper = AudioWrapper(src_file)
        src_trkno = int(src_wrapper.get_value('track'))
        filename_dict[src_trkno + offset] = filename

    # Given the filled dictionary, check the destination files' track numbers
    # and attempt to rename them based on the dictionary
    for dst_file in dst_files:
        dst_wrapper = AudioWrapper(dst_file)
        dst_suffix = dst_file.suffix
        dst_trkstr = dst_wrapper.get_value('track')
        # Convert the track numbers to integer values,
        # taking into account the situation where the track number
        # tag might include the total number of tracks on the disc
        # (e.g. '5/9')
        if '/' in dst_trkstr:
            dst_trkno = int(dst_trkstr.split('/')[0])
        else:
            dst_trkno = int(dst_trkstr)
        # Attempt the renaming operation 
        # (if the new filename and the existing one aren't identical)
        if dst_trkno in filename_dict.keys():
            newfilename = filename_dict[dst_trkno] + dst_suffix
            newpath = dst_file.parent / newfilename
            if str(newpath) != str(dst_file):
                try:
                    dst_file.rename(newpath)
                    print('renamed file {0} to {1}'.format(dst_file, newpath))
                except (OSError, FileExistsError):
                    print('could not rename file {0} to {1}'.format(dst_file, newpath))