# -*- coding: utf-8 -*-

from mutagen.flac import FLAC, Picture
from mutagen.id3 import __getattribute__, APIC, PictureType
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4Cover
import numpy as np
  
from boogie_manager.set_defaults import *


class AudioWrapper:
    
    """
    AudioWrapper : wrapper class to generalise mutagen's tagging operations across 3 file types (MP3, MP4, FLAC)
    """
        
    def __init__(self, p, tagdf=FIELDNAMES):
        
        """
        :param p     : (Path) pathlib.Path object of an audio file
        :param tagdf : (DataFrame) dataframe with the supported file types as columns
                       and human-readable tag names (e.g. 'artist', 'album') as rows.
                       Each element is the field name to be used for that tag on that
                       type of file
        """
        
        self.tagdf = tagdf
        self.p = p
        if p.suffix == '.mp3':
            self.mp3obj = MP3(p)
            self.id3obj = self.mp3obj.tags
            self.filetype = 'MP3'
        elif p.suffix == '.m4a':
            self.mp4obj = MP4(p)
            self.filetype = 'MP4'
        elif p.suffix == '.flac':
            self.flacobj = FLAC(p)
            self.filetype = 'FLAC'
        else:
            print('File type not supported:', str(p))
            

    def get_value(self, tagname):
        
        """
        get_value : gets the value of a tag from the opened file
        
        :param tagname : (str) name of the tag (as it appears in the index of self.tagdf)
        
        :return val : the tag value
        """
        
        field = self.tagdf.loc[tagname, self.filetype]
        
        if self.filetype == 'MP3':
            try:
                val = self.id3obj[field].text[0]
            except TypeError:
                val = self.id3obj[field].text
            except KeyError:
                val = np.nan
        elif self.filetype == 'MP4':
            try:
                if field in ['trkn', 'disk']:
                    val = self.mp4obj.tags[field][0][0]
                else:
                    try:
                        val = self.mp4obj.tags[field][0]
                    except TypeError:
                        val = self.mp4obj.tags[field]
            except KeyError:
                val = np.nan
        elif self.filetype == 'FLAC':
            try:
                val = self.flacobj[field]
            except KeyError:
                val = np.nan
        
        if type(val) is list:
            val = val[0]
        
        return val
    
    def set_value(self, tagname, val):
        
        """
        set_value : sets the value of a tag in the opened file
        
        :param tagname : (str) name of the tag (as it appears in the index of self.tagdf)
        :param val     : the desired value of the tag
        """
        
        field = self.tagdf.loc[tagname, self.filetype]
        
        if self.filetype == 'MP3':
            try:
                self.id3obj[field].text = val
            except KeyError:
                obj2add = __getattribute__(field)
                self.id3obj.add(obj2add(text=val))
            except TypeError:
                print('File {0}: Cannot set value {1} to field {2}'.format(self.p, val, field))
        elif self.filetype == 'MP4':
            self.mp4obj.tags[field] = val
        elif self.filetype == 'FLAC':
            self.flacobj[field] = val
    

    def add_album_art(self, art_obj):
        
        """
        add_album_art : write an album cover image to the file

        :param art_obj : (AlbumArt) AlbumArt wrapper object 
        """

        if self.filetype == 'MP3':
            self.id3obj.delall('APIC')
            self.save()
            self.id3obj.add(art_obj.image)
        elif self.filetype == 'MP4':
            self.mp4obj['covr'] = art_obj.image
        elif self.filetype == 'FLAC':
            self.flacobj.clear_pictures()
            self.flacobj.add_picture(art_obj.image)
    

    def remove_unused_tags(self):
        
        """
        remove_unused_tags : removes all tags not seen in self.tagdf from the file.
                             Use with care
        """
        
        used_tags = list(self.tagdf[self.filetype])
        
        if self.filetype == 'MP3':
            for tag in list(self.id3obj.keys()):
                if tag not in used_tags:
                    self.id3obj.pop(tag, None)
                    print('removed tag {0} from file {1}'.format(tag, self.p))
        elif self.filetype == 'MP4':
            for tag in list(self.mp4obj.tags.keys()):
                if tag not in used_tags:
                    self.mp4obj.tags.pop(tag, None)
                    print('removed tag {0} from file {1}'.format(tag, self.p))
        elif self.filetype == 'FLAC':
            for tag in list(self.flacobj.keys()):
                if tag not in used_tags and tag.lower() not in used_tags:
                    self.flacobj.pop(tag, None)
                    print('removed tag {0} from file {1}'.format(tag, self.p))


    def get_length(self):

        if self.filetype == 'MP3':
            length = self.mp3obj.info.length
        elif self.filetype == 'MP4':
            length = self.mp4obj.info.length
        elif self.filetype == 'FLAC':
            length = self.flacobj.info.length

        return length


    def save(self):
        
        """
        save : saves the changes made to the file's tags
        """
        
        if self.filetype == 'MP3':
            self.id3obj.save(self.p)
        elif self.filetype == 'MP4':
            self.mp4obj.save()
        elif self.filetype == 'FLAC':
            keys = list(self.flacobj.keys())
            for key in keys:
                if not key.islower():
                    self.flacobj[key.lower()] = self.flacobj[key]
                    print('changed field name {0} to {1} in file {2}'.format(key, key.lower(), self.p))
                    self.flacobj.pop(key, None)
            self.flacobj.save()


class AlbumArt:

    """
    AlbumArt : wrapper class to read an album cover image into an object that can be 
               written to either an MP3, MP4, or FLAC audio file
    """

    def __init__(self, image_path, audio_filetype):

        """
        param image_path     : (Path) pathlib.Path object pointing to the image file
        param audio_filetype : (str) string indicating the type of audio files to prepare
                               the image file for. Must be either 'MP3', 'MP4', or 'FLAC'
        """

        if audio_filetype == 'MP3':
            with open(image_path, 'rb') as acfile:
                self.image = APIC(encoding=3,
                                  mime=MIME_TYPES[image_path.suffix],
                                  type=3,
                                  desc=u'Cover',
                                  data = acfile.read())
        elif audio_filetype == 'MP4':
            with open(image_path, 'rb') as acfile:
                # The conversion to bytes and then to a list is some black magic fuckery
                # but mutagen requires this for some reason
                self.image = [bytes(MP4Cover(data=acfile.read(),
                                             imageformat=MP4_COVERTYPES[image_path.suffix]))]                               
        elif audio_filetype == 'FLAC':
            self.image = Picture()
            self.image.type = PictureType.COVER_FRONT
            self.image.mime = MIME_TYPES[image_path.suffix]
            with open(image_path, 'rb') as acfile:
                self.image.data = acfile.read()
