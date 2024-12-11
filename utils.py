import os
import glob

def clear_directory(directory):
    files = glob.glob(f'{directory}/*')
    for f in files:
        os.remove(f)
