# Boogie Manager

> *I'm a boogie man, and I boogie all the time!*

– John Lee Hooker

> *I find romance when I start to dance in Boogie Wonderland...*

– Earth, Wind & Fire

Boogie Manager is a package for music nerds who still have a large music library stored on their hard drive.

* **Generalise** Mutagen's tagging operations across three file types (MP3, MP4 and FLAC) so you don't have to look up the specific syntax every time
* Perform **batch tagging operations** on all files in a certain folder
* Easily **collect and analyse data** about your music library

Dependencies (outside of Python standard library): ``matplotlib``, ``mutagen``, ``pandas``, ``numpy``

Project status: code itself done; some functions still need more commenting; readme under construction

# ``base.py``: wrappers around MP3/MP4/FLAC tagging functions

At the heart of Boogie Manager is the ``AudioWrapper`` class, which is a wrapper around Mutagen's functions for reading and writing metadata to different types of audio files. The supported file types are:

* MP3 (ID3v2 tags) (*.mp3)
* MP4/ALAC (*.m4a)
* FLAC (*.flac)

Due to the different structures of each of these file types, Mutagen has subtly different syntax and logic for reading and writing metadata to each type. ``AudioWrapper`` saves you a lot of trips to https://mutagen.readthedocs.io by packaging them all into a single, hopefully intuitive interface. Once you have created an ``AudioWrapper`` object of an audio file, by calling ``AudioWrapper(p)`` where ``p`` is the file path, you can simply:

* ``get_value(tagname)`` – get the value of a single metadata field, e.g. ``'artist'`` or ``'title'``
* ``set_value(tagname, val)`` – set the metadata tag ``tagname`` to the value ``val``
* ``save()`` – save any changes made to the file's metadata

Other methods of ``AudioWrapper`` are:

* ``get_length()`` – get the length of the file in seconds
* ``remove_unused_tags()`` – remove all metadata tags not explicitly whitelisted (use with care!)
* ``add_album_art(art_obj)`` – add album art

The last one requires as an input another wrapper object: ``AlbumArt``. Mutagen's processing of image files into metadata that can be written to an audio file, again, differs depending on the audio file type. ``AlbumArt`` objects are initiated with two arguments: ``AlbumArt(image_path, audio_filetype)`` where ``audio_filetype`` must be either ``'MP3'``, ``'MP4'`` or ``'FLAC'``.

**N.B.:** Both the ``p`` argument for creating an ``AudioWrapper`` object, and the ``image_path`` argument for creating an ``AlbumArt`` object, must be a ``pathlib.Path`` object pointing to the file in question, not just a string of the file path.

## Example code

    filepath = r'C:\Users\henk\Music\Jackson, Joe\Is She Really Going Out with Him.mp3'
    p = pathlib.Path(filepath)
    wrapper = AudioWrapper(p)
    wrapper.set_value('album', 'Look Sharp')
    wrapper.set_value('track', '3')
    wrapper.save()

## Mapping of field names for MP3, MP4 and FLAC files

The file ``inputs/fieldnames.csv`` contains the default mappings from tag names (as you provide them to the ``set_value()`` and ``get_value()`` methods of ``AudioWrapper``) to the actual tags in the file. You can edit this file to change the mappings or add more fields, as long as you don't touch the column names (header row). 

| | MP3 | MP4 | FLAC |
|---|---|-----|------|
title | TIT2 | ©nam | title
artist | TPE1 | ©ART | artist
album | TALB | ©alb | album
year | TDRC | ©day | date
genre | TCON | ©gen | genre
track | TRCK | trkn | tracknumber
disc | TPOS | disk | discnumber
comment | COMM::eng | ©cmt | comment
album art | APIC: | covr | 
sort artist | TSOP | soar | artistsortorder
sort album | TSOA | soal | albumsortorder
album artist | TPE2 | aART | albumartist
compilation | TCMP | cpil | itunescompilation

**N.B.:** Beyond these standard tags, the file ``inputs/fieldnames.csv`` also contains mappings for a number of custom tags I have created that are specific to how I manage my library. You can give the file a quick check to make sure they don't interfere with anything you want to do, but for the rest you can safely ignore them.

# ``batch_ops.py``: batch tagging operations on folders

This file contains a number of functions for batch operations.

``titles2filenames(folder)`` does what it says on the tin: it renames all music files in the targeted folder (including subfolders) based on their "title" metadata tag. E.g. a file called ``10 - Michael Jackson - Smooth Criminal.flac`` with title ``Smooth Criminal`` will be called ``Smooth Criminal.flac`` after this operation. The default setting is to automatically apply "title case", which means a standard list of words will be forced to lowercase. This list can be found in ``inputs\titlecase_words.csv``, and ends up in the argument ``titlecase_list`` via ``set_defaults.py``.

``strip_phrase(folder, rstrip_phrase)`` removes a specific phrase from the end of all filenames of music files in the target folder (including subfolders). Useful if all files have e.g. `` (Remastered 2009)`` at the end of their name and you want to get rid of that. Optionally you can specify an ``lstrip_phrase`` too, for a string you want to remove from the *start* of all filenames, but this argument is set to ``None`` by default.

Other functions TBA

# ``library_data.py`` and ``graphs.py``: data collection and analysis

TBA

