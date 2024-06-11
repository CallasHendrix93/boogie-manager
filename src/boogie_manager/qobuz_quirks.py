import pathlib

from boogie_manager.set_defaults import *

def clean_album_art(folder):
    
    """
    clean_album_art : removes Qobuz's png files and sets jpg filenames
                      to the respective album titles. Assumes there are no 2
                      jpg files directly in the same folder!
                      
    :param folder : (str) path of the folder
    """
    
    # Get all the png files in the folder (came with Qobuz download)
    p = pathlib.Path(folder)    
    qobuz_pngs = list(p.rglob('*_cover.png')) + list(p.rglob('image_*.png'))
    # Get all the jpg files (the proper high-res album art, must have been
    # manually placed in the correct folders first)
    jpglist = list(p.rglob('*.jpg'))
    
    # Delete the png files
    for pngfile in qobuz_pngs:
        pngfile.unlink()
        
    # For all the jpgs, get the name of the folder where they reside
    # (assumed to be an album title)
    # and set the filename to this folder name
    for jpgfile in jpglist:
        albumtitle = jpgfile.parent.stem
        newfilename = albumtitle + jpgfile.suffix
        newpath = jpgfile.parent / newfilename
        jpgfile.rename(newpath)
        
    
def clean_folders(folder, max_nesting=6, titlecase=True, titlecase_list=TITLECASE_EN):

    """
    clean_folders : replaces all hyphens by spaces in all folder names
                    within the given parent folder
                      
    :param folder         : (str) path of the parent folder
    :param max_nesting    : (int) deepest nesting level to consider
    :oaram titlecase      : (bool) whether or not to correct the folder names to "title case"
    :param titlecase_list : (tuple) tuple of all the words to make lowercase for title case
    """
    
    p = pathlib.Path(folder)
    
    nesting_levels = range(max_nesting, 0, -1)
    
    for nesting in nesting_levels:
            # Get all the relevant folders at this nesting level    
            globstring = '/'.join(['*' for i in range(nesting)])    
            folders = [path for path in list(p.glob(globstring)) if path.is_dir()]
            
            for f in folders:
                # Replace hyphens by spaces (by default, Qobuz downloads represent all spaces
                # in artist/album names as hyphens in the respective folder names;
                # this code fixes that)
                newname = f.stem.replace('-', ' ')
                # Replace specific words from 'titlecase_list' (e.g. 'And', 'Or')
                # with their lower-case counterparts
                if titlecase:
                    for word in titlecase_list:
                        word_padded = ' ' + word + ' '
                        newname = newname.replace(word_padded, word_padded.lower())
                # Generate the full new path and rename the folder
                newpath = f.parent / newname
                f.rename(newpath)