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


# ========= ACTION PROCESSING =================
def create_destination_paths(action, selected_date,selected_time, selected_location, selected_json_path, file_path): 
    print ("---------- Creating Destination Path Names -------------")
    print("Selected Date", selected_date)
    print("Location Detection: ", selected_location)
    print("JSON Path if used: ", selected_json_path)
    
    # file_name = os.path.basename(file_path)
    # base_filename = os.path.basename(file_path)
    # path_to_directory = os.path.dirname(file_path)
    # base_dirname = os.path.basename(path_to_directory)
    
    
    # print(file_name, '\n', base_filename, '\n', path_to_directory, '\n',  base_dirname)
    # print(_curr_processed_path)
    # print(_curr_file_type)
    # print(_curr_source_path)
    
    # Handle Date
    dest_datetime_str = ""
    clean_date = str(selected_date).replace(" ", "_").replace(":", "-").replace(".", "-")
    
    # Handle Time
    clean_time = ""
    if selected_time is not None: 
        #TODO: Incorporate selected_time
        clean_date = str(clean_date).replace("_00-00-00", "")
        clean_time = str(selected_time).replace(" ", "_").replace(":", "-").replace(".", "-")
        clean_time += "_"
    
    # Handle Location
    dest_loc_str = ""
    if selected_location is not None: 
        print("LA: ", str(selected_location[0]["latitude"]) )
        print("LO: ", str(selected_location[0]["longitude"]) )
        print("AL: ", str(selected_location[0]["altitude"]))
        dest_loc_str += "_LA-" +str(selected_location[0]["latitude"]) 
        dest_loc_str += "_LO-" +str(selected_location[0]["longitude"]) 
        dest_loc_str += "_AL-" +str(selected_location[0]["altitude"]) + "_"
        print(dest_loc_str, "\033[0m")
        
    # Sanity check and Append
    dest_datetime_str += f"{str(clean_date)}_"
    dest_datetime_str += f"{str(clean_time)}"
    print("Date handling: ", selected_date , " >> " , clean_date)
    print("Time handling: ", selected_time , " >> " , clean_time)
    
    # Get Original File Name
    base_filename = os.path.basename(file_path)   
    
    dest_final_media_name = dest_datetime_str + dest_loc_str + base_filename
    print("Destination Name: ", dest_final_media_name)
    
    if selected_json_path is not None: 
        base_jsonname = os.path.basename(selected_json_path)
        dest_final_json_name = dest_datetime_str + dest_loc_str + base_jsonname
        print("Destination JSON: ", dest_final_json_name)
    else: 
        print("No JSON option was selected")
    
    
    exit(0)
    
    
def process_user_action(action:int, file_path:str, date_extractions):
    
    print("Action selected: ", action)
    # print(date_extractions)
    selected_location = date_extractions['JSON - Location Data']
    selected_json_path = date_extractions['JSON - Path'] if (action == 7 or action == 8) else None
    
    
    selected_date = 0
    selected_time = None
    
    match action: 

        case 1:
            selected_date = date_extractions['DateTime in FileName'] [0]
            selected_time = date_extractions['DateTime in FileName'] [1]
        case 2:
            selected_date = date_extractions['FILE_CREATION']
        case 3:
            selected_date = date_extractions['FILE_MODIFIED']
        case 4:
            selected_date = date_extractions['METADATA']
        case 5:
            selected_date = date_extractions['EXIF']
        case 6:
            selected_date = date_extractions['FILE_DATEACQUIRED']
        case 7:
            selected_date = date_extractions['JSON - CreationTime']
        case 8:
            selected_date = date_extractions['JSON - PhotoTakenTime']

    # At this point we have everything we need to start. 
    # Steps: 
    # Create names for destination file name and save path ( based on date, time, location.)
    #   if JSON --> create destination stuff for media AND json
    #   else: --> create destination stuff for media only
    # Override date in media using ffmpeg if video or
    

    
    dest_media_path, dest_json_path = create_destination_paths(action, selected_date,selected_time, selected_location, selected_json_path, file_path)
    

# ========== MENU BUILDING ===============
def parse_json_dategeo_response(data):

    if data is None: 
        return None
    else:

        json_name = os.path.basename(data['file_path'])
        json_path = data['file_path']
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

        return creationTime, photoTakenTime, locationData, json_path

def show_menuselection_for_current_file(date_extractors: dict): 
    myIndex = 1
    for key in date_extractors: 
        if (key == "JSON - Location Data"  or key == 'JSON - Path'):
            print(swrap("b", f"    {key:<22} : "), swrap("g",f"{date_extractors[key]}") if date_extractors[key] is not None else swrap("r", "None"))
        else: 
            strResponse = date_extractors[key]
            print(swrap("b", f"[{myIndex}] {key:<22} : "), swrap("g", f"{strResponse}") if strResponse is not None else swrap("r", "None"))
            myIndex += 1


def extract_dates_from_file(file_path:str):
    json_response = drf.get_dategeo_from_JSON(file_path)
    print(json_response)
    
    creationTime, photoTakenTime, locationData, json_path = parse_json_dategeo_response(json_response)
    
    return {
        'DateTime in FileName': [drf.get_date_from_filename(file_path), drf.get_time_from_filename(file_path)],
        'FILE_CREATION': drf.get_date_from_creation_date(file_path),
        'FILE_MODIFIED': drf.get_date_from_modified_date(file_path),
        'METADATA': drf.get_date_from_metadata(file_path),
        'EXIF': drf.get_date_from_EXIF(file_path),
        'FILE_DATEACQUIRED': drf.get_date_from_dateAcquired(file_path),
        'JSON - CreationTime': creationTime, 
        'JSON - PhotoTakenTime': photoTakenTime, 
        'JSON - Location Data': locationData ,
        'JSON - Path': json_path
    }   


def pad_counter_header_integer(total_count: int, index: int):
    strCount = ""
    for _ in range(len(str(total_count)) - len(str(index))): 
        strCount+= "0"
    strCount += str(index)
    return strCount

def show_header_for_current_file(file_path: str, index: int, total_index): 
    # Counter Header: shows count of current file type and count of total files to process in the album
    total_mediacount_of_type = _results.get_total_mediacount_of_currType()
    total_mediacount_of_album = _results.get_total_mediacount_of_currAlbum()
    strtotaltypecount = pad_counter_header_integer(total_count=total_mediacount_of_type, index=index)
    strtotalalbumcount = pad_counter_header_integer(total_count=total_mediacount_of_album, index=total_index)
    
    # Header for each file
    # [ 001/100 JPG 001/900 album ] | < file name> 
    file_ext = os.path.splitext(file_path)[-1].lower()
    pwrap("bold", swrap("gbg", f"[{strtotaltypecount}/{total_mediacount_of_type} {file_ext}s || {strtotalalbumcount}/{total_mediacount_of_album} in album] | {file_path}" ))
    
    
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
                    
                    
                    while True: 
                        # Header and Menu
                        
                        date_extractions = extract_dates_from_file(file_path)
                        show_menuselection_for_current_file(date_extractions)
                        
                        action = input(swrap("y", "Enter 1-8 to select override date, 'r' to refresh, 'x' to exit: \n >>> "))
                        
                        indexed_keys = dict(enumerate(date_extractions.keys()))
                        # action = '1' # AUTO LOOPER
                        
                        if action in ['1', '2', '3', '4', '5', '6', '7', '8', 'x', 'r']:
                            if action == 'x':
                                pwrap("rbg", "Exiting...")
                                exit(0)
                            elif (date_extractions[indexed_keys[int(action)-1]] is None): 
                                
                                pwrap("rbg", f"Selected Date override [{indexed_keys[int(action)-1]}] is marked as [None].  Refreshing...")
                                continue  # Restart the loop to refresh the information
                            elif action == 'r':
                                pwrap("cbg", "Refreshing...")
                                continue  # Restart the loop to refresh the information
                            else:
                                # Process action based on the user's valid selection
                                process_user_action(int(action), file_path, date_extractions)
                                
                                
                                # Stopper 
                                input("STOPPER LINE")
                                break
                        else:
                            # Print an error message for invalid input and re-ask the question
                            pwrap("r","Invalid input! Please enter a number between 1-8, 'r' to refresh, 'x'to exit.")
                    index += 1
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
    # swrap_test()
    
    # Title
    print(swrap("bold", swrap("blubg", "Synology Photos Metadata Corrector")))
    print("--------------SETUP---------------")
    
    # Print global variables
    # print("Supported Types: ", str(LIST_FILE_TYPE))
    # print("Folders to Process: ")
    # for folderPath in LIST_SOURCE_PATH_FOLDERS: 
    #     print(swrap("g", folderPath))
    
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