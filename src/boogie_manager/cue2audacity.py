# -*- coding: utf-8 -*-

import pathlib


def cue2audacity(cuefile):
    
    """
    cue2audacity : translates the timestamps from a .cue file into a format
                   Audacity can use for label import
                   
    :param cuefile : (str) path of the source .cue file
    """
    
    cuefilepath = pathlib.Path(cuefile)
    dst_path = cuefilepath.parent / 'audacity_labels.txt'
    
    try:
        with open(cuefile) as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        with open(cuefile, encoding='ansi') as f:
            lines = f.readlines()            
        
    namelines = [line for line in lines if line.startswith('    TITLE')]
    timestamplines = [line for line in lines if line.startswith('    INDEX 01')]
    
    names = [line.removeprefix('    TITLE "').removesuffix('"\n') for line in namelines]
    timestamps = [line.removeprefix('    INDEX 01 ').removesuffix('\n') for line in timestamplines]
    
    timestamps_sec = []
    for timestamp in timestamps:
        mins, sec, cs = tuple(timestamp.split(':'))
        seconds = (int(mins) * 60) + int(sec) + (float(cs) / 100)
        timestamps_sec.append(seconds)

    try:   
        newlines = ['\t'.join([str(timestamps_sec[i]), str(timestamps_sec[i]), names[i]]) + '\n' for i in range(len(timestamps_sec))]
    except IndexError:
        newlines = ['\t'.join([str(timestamps_sec[i]), str(timestamps_sec[i]), 'no title {0}'.format(i+1)]) + '\n' for i in range(len(timestamps_sec))]
    
    with open(dst_path, 'w') as nf:
        nf.writelines(newlines)