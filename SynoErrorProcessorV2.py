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


from collections import defaultdict
from SynoProcessResults import ProcessingResult
from string_format_wrap import swrap 
import json 
import os
# Global Vars

LIST_FILE_TYPE = [".jpg", ".png", ".jpeg", ".mp4", ".gif", ".dng", ".webp", ".mov", ".heic"]

LIST_SOURCE_PATH_FOLDERS = [
    r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\White Coat Ceremony _26",
    r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Vicky_s Surprise Sweet Sixteen!",
    r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Untitled",
    r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\SUGA _ AGUST D 4-27",
    r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\SUGA _ AGUST D @ UBS 4-27",
    # str(r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\ASHP Midyear 23 - Anaheim, CA"), 
    
    # str(r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\test_folder")
    # "E:\Apps"
]


results = None
curr_source_path = None
curr_source_path_album_folder = ""
curr_file_type = ""

processed_path = curr_source_path_album_folder + "\\Processed"
skipped_path = curr_source_path_album_folder + "\\Skipped"



def processing_media(): 
    # For each folder
    #for source_path in LIST_SOURCE_PATH_FOLDERS: 
        
        #For each file
        #for root, _, files in os.walk(source_path): 
            
            #Create Processed_Filetype if does not exist
            
            # Retrieve current date values
            # retrieve json value
            # ask to override 
            # if overwrite --> process action
                #when processing complete --> move into //Processed_originals
            # else
                # let file be and move on
    return

def scan_all_sources(): 
    # print(str(results.get_progress_tracker()))
    
    print("-------- SCANNING SOURCE PATHS -------------")
    for source_path in LIST_SOURCE_PATH_FOLDERS: 
        #Loop through all source folders
        
        # For each folder, count total files + count per filetype 
        total_media_count = 0
        media_type_aggr = defaultdict(int)
        
        if not os.path.isdir(source_path):
            print(swrap("r", f"Skipping non-existent folder: {source_path}"))
            continue
            
        # Traverse all files in the folder to count everything
        print(f"\nScanning folder: {source_path}")
        for root, _, files in os.walk(source_path):
            for file in files:
                file_ext = os.path.splitext(file)[-1].lower()  # Extract file extension
                if file_ext in LIST_FILE_TYPE:
                    media_type_aggr[file_ext] += 1
                    total_media_count += 1
        # Print results
        # print(f"Finished scanning!")
        print(f"Total count: {total_media_count} -- Type breakdown:", dict(media_type_aggr))
        
        # Add findings to tracker
        results.add_folder_to_tracking(source_path, total_media_count, media_type_aggr)
    print("-------- SCANNING FINISHED FOR SOURCE PATHS -------------")
    
    
def main(): 
    # Pre execution setup
    print(swrap("bold", swrap("blubg", "Synology Photos Metadata Corrector")))
    print("--------------SETUP---------------")
    global results
    global curr_source_path
    global curr_source_path_album_folder
    global curr_file_type
    global processed_path
    global skipped_path
    
    
    
    # Print global variables
    print("Supported Types: ", str(LIST_FILE_TYPE))
    print("Folders to Process: ")
    for folderPath in LIST_SOURCE_PATH_FOLDERS: 
        print(swrap("g", folderPath))
    
    
    results = ProcessingResult()
    print(results)
    results.set_total_paths(LIST_SOURCE_PATH_FOLDERS)
    results.set_total_file_types(LIST_FILE_TYPE)
    print("--------------SETUP END ---------------\n")
    
    
    scan_all_sources()
    processing_media() #main function
    # action = input (swrap("b", "Continue to processing menu? [y]"))
    
    # if action == "": 
    #     print("hello" )
    
    
    # if action != "y" or action != "" : 
    #     exit(0)
    # else: 
    #     print("Continuing!")
    # # Wait for user to continue program 
    
    # # Folder(s) Traversal
    # swrap()
    

if __name__ == "__main__": 
    main()