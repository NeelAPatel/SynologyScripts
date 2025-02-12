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
from SynoProcessLogger import ProcessLogger
import dateRecallFunctions as drf
from string_format_wrap import swrap, pwrap, swrap_test
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


_results = None
_curr_source_path = None
_curr_file_type = None
_curr_processed_path = None
# processed_path = curr_source_path + "\\Processed"
# skipped_path = curr_source_path + "\\Skipped"

def parse_json_dategeo_response(data):

    if data is None: 
        return None
    else:

        # json_name = os.path.basename(data['file_path'])
        # json_path = data['file_path']
        # print()
        # print(f"  JSON name: {json_name}")
        # print(f"  Dates/Times:")
        
        creationTime = data['dates_times'][0][1]
        photoTakenTime = data['dates_times'][1][1]
        
        locationData = []
        if data['locations']: 
            for loc in data['locations']: 
                locDict = {
                    "latitude": loc['latitude'],
                    "longitude": loc['longitude'],
                    "altitude": loc['altitude']
                }
                locationData.append(locDict)
        else:
            locationData = None
        # count = 8
        # for dt in data['dates_times']:
        #     print(f"    - [{count}] {dt[0]}, {dt[1]}, {type(dt[1])}")
        #     count += 1
        
        # if data['locations']:
        #     print("Locations:")
        #     for location in data['locations']:
        #         print(f"    - Latitude: {location['latitude']}, Longitude: {location['longitude']}, Altitude: {location['altitude']} meters")
        # else:
        #     print("  Locations: None")

        return creationTime, photoTakenTime, locationData

def show_menuselection_for_current_file(date_extractors: dict): 
    myIndex = 1
    for key in date_extractors: 
        if (key == "JSON"):
            
            if (date_extractors[key] is None): 
                print(swrap("b", f"[{myIndex}] {key:<15} : "), swrap("r", "None"))    
                break
            
            creationTime, photoTakenTime, locationData = parse_json_dategeo_response(date_extractors[key])
            print(swrap("b", f"    {key:<22} : "), swrap("g", f"Valid!"))
            print(swrap("b", f"[7] {"JSON - CREATION TIME":<22} : "), swrap("g", f"{creationTime}"))
            print(swrap("b", f"[8] {"JSON - PHOTOTAKEN TIME":<22} : "), swrap("g", f"{photoTakenTime}"))
            print(swrap("b", "  ---------- JSON LOCATION : "), swrap("g",f"{locationData}") if locationData is not None else swrap("r", "None"))
            
        else: 
            strResponse = date_extractors[key]
            print(swrap("b", f"[{myIndex}] {key:<22} : "), swrap("g", f"{strResponse}") if strResponse is not None else swrap("r", "None"))
            myIndex += 1


def extract_dates_from_file(file_path:str):
    return {
        'DateFileName': drf.get_date_from_filename(file_path),
        'TimeFileName': drf.get_time_from_filename(file_path),
        'CREATION': drf.get_date_from_creation_date(file_path),
        'MODIFIED': drf.get_date_from_modified_date(file_path),
        'METADATA': drf.get_date_from_metadata(file_path),
        'EXIF': drf.get_date_from_EXIF(file_path),
        'DATEACQUIRED': drf.get_date_from_dateAcquired(file_path),
        'JSON': drf.parse_json_for_dategeo_data(file_path)
    }


def pad_counter_header_integer(total_count: int, index: int):
    strCount = ""
    for _ in range(len(str(total_count)) - len(str(index))): 
        strCount+= "0"
    strCount += str(index)
    return strCount

def show_header_for_current_file(file_name: str, index: int, total_index): 
    # Counter Header: shows count of current file type and count of total files to process in the album
    total_mediacount_of_type = _results.get_total_mediacount_of_currType()
    total_mediacount_of_album = _results.get_total_mediacount_of_currAlbum()
    strtotaltypecount = pad_counter_header_integer(total_count=total_mediacount_of_type, index=index)
    strtotalalbumcount = pad_counter_header_integer(total_count=total_mediacount_of_album, index=total_index)
    
    # Header for each file
    # [ 001/100 JPG 001/900 album ] | < file name> 
    file_ext = os.path.splitext(file_name)[-1].lower()
    pwrap("bold", swrap("gbg", f"[{strtotaltypecount}/{total_mediacount_of_type} {file_ext}s || {strtotalalbumcount}/{total_mediacount_of_album} in album] | {file_name}" ))
    
    
def create_processed_folder_ifnotexists(file_name: str):
    # Global values to edit in this function scope
    #global _results
    #global _curr_source_path
    global _curr_processed_path
    global _curr_file_type
    
    # Set up processed folder path
    _curr_file_type = os.path.splitext(file_name)[-1].lower()  # Extract file extension
    _curr_processed_path = _curr_source_path + "\\Processed" + "_" + _curr_file_type.replace(".", "")
    
    #If doesn't exist, create one. 
    if not os.path.exists(_curr_processed_path):
        os.makedirs(_curr_processed_path)
        pwrap("m",f"Folder created: {_curr_processed_path}")


def process_all_albums(): 
    # Global values to edit in this function scope
    global _results
    global _curr_source_path
    #global _curr_processed_path
    #global _curr_file_type
    
    # For each folder
    pwrap("reset", "------- PROCESSING ALBUMS STARTED --------------")
    for source_path in LIST_SOURCE_PATH_FOLDERS: 
        #Global set
        _curr_source_path = source_path
        total_album_index = 1
        
        for root, _, files in os.walk(source_path): 
            #For each traversal, 
            
            #Sort all the files
            files = sorted(os.listdir(_curr_source_path))
            index = 1            
            for file_name in files:
                
                # Create a file_path alongside file_name
                file_path = os.path.join(_curr_source_path, file_name)
                # If the file is a valid file we're ready to process, go ahead and show the menu
                if os.path.isfile(file_path) and any(file_name.lower().endswith(ext) for ext in LIST_FILE_TYPE):
                    
                    
                    #Set current file as its being explored 
                    _results.set_current_processing_file(file_path)
                    
                    #Create processed folder
                    create_processed_folder_ifnotexists(file_name)
                    #print(file_name)
                    
                    show_header_for_current_file(file_path, index, total_album_index)
                    
                    date_extractions = extract_dates_from_file(file_path)
                    action = show_menuselection_for_current_file(date_extractions)
                    
                    #Show File Name and counter
                    dummyaction = input("everything looks good? ")
                    index += 1
                    #if os.path.isfile()
                    
                    # Create Processed_Filetype folde rif does not exist

                    
                    # Retrieve current date values
                # retrieve json value
                # ask to override 
                # if overwrite --> process action
                    #when processing complete --> move into //Processed_originals
                # else
                    # let file be and move on
    
    #print(_curr_processed_path)
    #print(_curr_file_type)
    #print(_curr_source_path)
    pwrap("reset", "------- PROCESSING ALBUMS ENDED --------------")
    return

def scan_all_album_sources():
    print("-------- SCANNING SOURCE PATHS -------------")
    
    full_total = 0
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
        print(f"Total count: {total_media_count} -- Type breakdown:", dict(media_type_aggr))
        
        # Add findings to tracker
        _results.add_album_to_tracking(source_path, total_media_count, media_type_aggr)
        full_total += total_media_count
    
    
    _results.set_total_mediacount_process(full_total)
    print("-------- SCANNING FINISHED FOR SOURCE PATHS -------------")
    
def main(): 
    # Global values to edit in this function scope
    global _results
    
    # Pre execution setup
    swrap_test()
    
    # Title
    print(swrap("bold", swrap("blubg", "Synology Photos Metadata Corrector")))
    print("--------------SETUP---------------")
    
    # Print global variables
    print("Supported Types: ", str(LIST_FILE_TYPE))
    print("Folders to Process: ")
    for folderPath in LIST_SOURCE_PATH_FOLDERS: 
        print(swrap("g", folderPath))
    
    # Set up output for results file
    _results = ProcessLogger()    
    _results.set_total_paths(LIST_SOURCE_PATH_FOLDERS)
    _results.set_total_file_types(LIST_FILE_TYPE)
    print("--------------SETUP END ---------------\n")
    
    #Procedure
    scan_all_album_sources()
    process_all_albums()
    

if __name__ == "__main__": 
    main()