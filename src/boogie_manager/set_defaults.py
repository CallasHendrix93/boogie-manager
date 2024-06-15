# -*- coding: utf-8 -*-

import getpass
import pandas as pd
import pathlib

inputs_folder = pathlib.Path(__file__).resolve().parent.parent.parent / 'inputs'

username = getpass.getuser()
ROOTFOLDER = pathlib.Path(r'C:/Users/{0}/Music'.format(username))

FIELDNAMES = pd.read_csv(inputs_folder / 'fieldnames.csv', index_col=0, header=0, sep=';')
TITLECASE_EN = tuple(pd.read_csv(inputs_folder / 'titlecase_words.csv', index_col=None, header=0)['word'])

MIME_TYPES = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.bmp': 'image/bmp'}
MP4_COVERTYPES = {'.jpg': 'FORMAT_JPEG', '.jpeg': 'FORMAT_JPEG', '.png': 'FORMAT_PNG'}
FILETYPES = {'.m4a': 'ALAC', '.mp3': 'MP3', '.flac': 'FLAC'}

# ================= Everything below this line is specific to author's library, probably not relevant for other users =================  

FOLDER_DF = pd.read_csv(inputs_folder / 'genres.csv', index_col=0, header=0, sep=';')

SPLITFOLDER = '98 splits'

SOURCEDICT = {'CD rip': '1. CD rip',
               'Download from Qobuz': '2. Qobuz',
              'Download from Presto': '3. Presto',
              'Download from 7digital': '4. 7digital',
              '[No lossless source] Download from 7digital': '4. 7digital',
              'Vinyl rip': '5. Vinyl rip'}

SOURCEDICT_REV = {'1. CD rip': 'CD rip',
                  '2. Qobuz': 'Qobuz',
                  '3. Presto': 'Presto',
                  '4. 7digital': '7digital',
                  '5. Vinyl rip': 'vinyl rip',
                  '99. Other': 'other'}

MAINGENRES = {'00': 'classical',
              '01': 'metal',
              '02': 'pop/rock',
              '03': 'soul/funk/disco',
              '04': 'blues/country/rock & roll',
              '05': 'jazz',
              '06': 'trad pop',
              '07': 'hip-hop',
              '08': 'electronic',
              '99': 'various'}

MAINGENRES4YEARS = {'00': 'classical (recording date)',
                    '01': 'metal',
                    '02': 'pop/rock',
                    '03': 'soul/funk/disco',
                    '04': 'blues/country/rock & roll',
                    '05': 'jazz',
                    '06': 'trad pop',
                    '07': 'hip-hop',
                    '08': 'electronic',
                    '99': 'various'}

SUBGENRES_METAL = {'01': 'trad',
                   '02': 'doom',
                   '03': 'power',
                   '04': 'thrash',
                   '05': 'black',
                   '06': 'death',
                   '07': 'melodeath/folk',
                   '08': 'stoner + newer trad'}