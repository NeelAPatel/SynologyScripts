# from datetime import datetime, timezone
# from hachoir.metadata import extractMetadata
# from hachoir.parser import createParser
# from os.path import join, isfile
# from PIL import Image
# from PIL.ExifTags import TAGS
# import json
# import os
# import piexif
# import re
# import shutil
# import win32com.client
# import dateRecallFunctions as drf
# import ffmpeg
# import piexif
# import struct
# from PIL import Image
# import subprocess
# from PIL import ImageFile


from SynoProcessResults import ProcessingResult
from string_format_wrap import swrap

# Global Vars

LIST_FILE_TYPE = [".jpg", ".png", ".jpeg", ".mp4", ".gif", ".dng", ".webp", ".mov", ".heic"]
CURR_FILE_TYPE = ""

LIST_SOURCE_PATH_FOLDERS = [
    str(r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\ASHP Midyear 23 - Anaheim, CA"), 
    str(r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\test_folder")
]
CURR_SOURCE_PATH_FOLDER = ""
CURR_SOURCE_PATH = None

PROCESSED_PATH = CURR_SOURCE_PATH_FOLDER + "\\Processed"
SKIPPED_PATH = CURR_SOURCE_PATH_FOLDER + "\\Skipped"



RESULTS = None



#<folder> <type> <count/max> <latest complete> <current_working> <completed_list>


# Counter = 
# TotalMediaCounter
# PerFiletypeCounter
#


def per_folder_traversal(): 
    for source_path in LIST_SOURCE_PATH_FOLDERS: 
        
        CURR_SOURCE_PATH_FOLDER = source_path
        
        # traverse that folder for files
        
        # traversal is complete
        result_dict
    
    
def main(): 
    # Pre execution setup
    print("Synology Photos Metadata Corrector")
    print("--------------SETUP---------------")
    
    # Print global variables
    '''
    - Supported File Types
    - Processed path
    - Skipped Path
    - List of Source Paths
    '''
    print("Supported Types: ", str(LIST_FILE_TYPE))
    print("Folders to Process: ")
    for folderPath in LIST_SOURCE_PATH_FOLDERS: 
        print(swrap("g", folderPath))
    
    
    RESULTS = ProcessingResult()
    RESULTS.set_total_file_types(LIST_FILE_TYPE)
    RESULTS.set_total_paths(LIST_SOURCE_PATH_FOLDERS)
    
    
    # # Wait for user to continue program 
    
    # # Folder(s) Traversal
    # swrap()
    

if __name__ == "__main__": 
    main()