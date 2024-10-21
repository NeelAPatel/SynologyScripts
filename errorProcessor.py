from datetime import datetime, timezone
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from os.path import join, isfile
from PIL import Image
from PIL.ExifTags import TAGS
import json
import os
import piexif
import re
import shutil
import win32com.client
import dateRecallFunctions as drf
import ffmpeg
import piexif
import struct
from PIL import Image
# CONSTANTS

FILE_TYPE = ".JPG".lower()
SOURCE_PATH = str(r"E:\GPhotos-Metadatafixer\2024-10-01-173418557\AAATotal\Error" + FILE_TYPE.replace('.', "")) # + "\\bleh"
# "E:\GPhotos-Metadatafixer\2024-10-01-173418557\AAATotal\ErrorJPG\Problem Files Still Need to Process\IMG-20161107-WA0008.jpg"

PROCESSED_PATH = SOURCE_PATH + "\\Processed2"
SKIPPED_PATH = SOURCE_PATH + "\\Skipped"


def walk_directory(dir_to_walk, printflag, countflag): 
    print("Walking directory...")
    files = []
    for file_name in os.listdir(dir_to_walk):
        # print(file_name)
        file_path = os.path.join(dir_to_walk, file_name) 
        if os.path.isfile(file_path): 
            files.append((file_path, file_name))

            if printflag: 
                print(file_name)

    if countflag: 
        print(len(files))


def print_readable_format(data):

    if data is None: 
        return None
    else:

        json_name = os.path.basename(data['file_path'])
        json_path = data['file_path']
        print()
        print(f"  JSON name: {json_name}")
        print(f"  Dates/Times:")
        count = 8
        for dt in data['dates_times']:
            print(f"    - [{count}] {dt[0]}, {dt[1]}, {type(dt[1])}")
            count += 1
        
        if data['locations']:
            print("Locations:")
            for location in data['locations']:
                print(f"    - Latitude: {location['latitude']}, Longitude: {location['longitude']}, Altitude: {location['altitude']} meters")
        else:
            print("  Locations: None")

        return "Valid!"


def action_menu():
    action = input("\033[94m>>> s=skip, 1-8=select override date\n>>> \033[0m")
    return action

def copy_and_check(source, destination):
    # Check if the destination file exists before copying
    file_exists = os.path.exists(destination)

    if file_exists:
        # Get the timestamp and size of the existing file
        existing_stat = os.stat(destination)
        existing_timestamp = existing_stat.st_mtime
        existing_size = existing_stat.st_size

    # Perform the copy operation with metadata preservation
    # print("Copying from: ", source)
    # print("Copying to: ", destination)
    shutil.copy2(source, destination)

    # Check if the file exists after the copy operation
    if os.path.exists(destination):
        # Get the timestamp and size of the copied file
        copied_stat = os.stat(destination)
        copied_timestamp = copied_stat.st_mtime
        copied_size = copied_stat.st_size

        if file_exists:
            # Compare timestamps and sizes to determine if it was overwritten
            if (copied_timestamp != existing_timestamp or
                copied_size != existing_size):
                print(f"File copied successfully to {destination} (Overwritten).")
            else:
                print(f"File already exists at {destination}, and no changes were made.")
        else:
            print(f"File copied successfully to {destination} (New file created).")
    else:
        print("Error: File was not copied.")

def override_video_data(destinationfilepath, selected_date, selected_location):
    # Convert the selected date to the appropriate format for video metadata
    exif_date_str = selected_date.strftime("%Y-%m-%dT%H:%M:%S")  # ffmpeg uses this format for metadata
    # Update EXIF date values (This would be ffmpeg metadata for video)
    # Here, we pass the `exif_date_str` as metadata
    # For video, we use the 'creation_time' metadata tag to update the date
    # Note: Video doesn't have multiple EXIF date fields, just one creation date field
    try:
        # Prepare ffmpeg command to update the video metadata
        ffmpeg.input(destinationfilepath).output(destinationfilepath,
            **{
                'metadata': f'creation_time={exif_date_str}',  # Set video creation time
            }
        ).run()

        print(f"\033[92mVideo metadata updated for {destinationfilepath}\033[0m")
    except Exception as e:
        print(f"\033[91mFailed to update video metadata: {e}\033[0m")


    # Update file system times
    if isinstance(selected_date, str):
        new_datetime = datetime.datetime.strptime(selected_date, "%Y:%m:%d %H:%M:%S")
    else:
        new_datetime = selected_date
    
    timestamp = new_datetime.timestamp()

    # Update file system access and modification times
    os.utime(destinationfilepath, (timestamp, timestamp))




def convert_degrees_to_rational(deg):
    """Helper function to convert degrees into rational format required for EXIF."""
    d = int(deg[0])
    m = int(deg[1])
    s = deg[2] * 100
    return ((d, 1), (m, 1), (int(s), 100))

def convert_rational_to_degrees(rational):
    """Helper function to convert rational format back to degrees."""
    d = rational[0][0] / rational[0][1]
    m = rational[1][0] / rational[1][1]
    s = rational[2][0] / rational[2][1] / 100
    return d + (m / 60.0) + (s / 3600.0)

def override_image_data(destinationfilepath, selected_date, selected_location): 
    # Open the image and load existing EXIF data
    img = Image.open(destinationfilepath)


    # ==== RESOLVE EXIF existence ====
    if 'exif' not in img.info: 
        print("\033[91mEXIF data not present\033[0m")
        print("Exif data needs to be created with date time data")
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}, "thumbnail": None}
    else: 
        exif_dict = piexif.load(img.info['exif'])
        print("EXIF data loaded: ")
        exifdata = img.getexif()
        for tag_id in exifdata:
            # get the tag name, instead of human unreadable tag id
            tag = TAGS.get(tag_id, tag_id)
            data = exifdata.get(tag_id)
            # decode bytes
            if isinstance(data, bytes):
                data = data.decode()
            print(f"{tag:25}: {data}")
        print()
    



        # === DEBUGGING: Log GPS Data ====
        print("=== DEBUG: Checking GPS Data ===")
        if 'GPS' in exif_dict:
            for key, value in exif_dict['GPS'].items():
                print(f"GPS Tag: {key}, Value: {value}")
                # Check if the value exceeds 32-bit integer limit
                if isinstance(value, int) and value > 4294967295:
                    print(f"\033[91mWARNING: GPS Value too large! Key: {key}, Value: {value}\033[0m")
                    # Optionally: Modify or remove the invalid entry
                    # exif_dict['GPS'][key] = 0  # Set to 0 or handle it differently
        else:
            print("No GPS data found in EXIF.")

    
    # === OVERRIDE DATE ====
    exif_date_str = selected_date.strftime("%Y:%m:%d %H:%M:%S")

    # Update EXIF date values
    exif_dict['0th'][piexif.ImageIFD.DateTime] = exif_date_str
    exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = exif_date_str
    exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = exif_date_str



    # === OVERRIDE GPS IF NEEDED === 

    # if GPS in exif
        # do nothing
    # if GPS not in exif and GPS in selected
        # add
    # if gps not in exif and GPS not in selected
        # do nothing

    

    if exif_dict['GPS'] and selected_location: 
        print("GPS in: Photo and JSON  = No Overwrite, checking exactness")
        print("Coords from JSON: ", selected_location[0])


        gps_data = exif_dict['GPS']
        lat = convert_rational_to_degrees(gps_data[piexif.GPSIFD.GPSLatitude])
        lat_ref = gps_data[piexif.GPSIFD.GPSLatitudeRef].decode('utf-8')
        lon = convert_rational_to_degrees(gps_data[piexif.GPSIFD.GPSLongitude])
        lon_ref = gps_data[piexif.GPSIFD.GPSLongitudeRef].decode('utf-8')
        print(f"Coords from PHOTO: : Latitude: {lat} {lat_ref}, Longitude: {lon} {lon_ref}")

        if lat_ref == "" or lon_ref == "": 
            if lat_ref == "": 
                print("Error: Fixing EMPTY lat_ref")
                gps_data[piexif.GPSIFD.GPSLatitudeRef] = b'N' if selected_location[0]['latitude'] >= 0 else b'S'
        
            if lon_ref == "": 
                print("Error: Fixing EMPTY lon_ref")
                gps_data[piexif.GPSIFD.GPSLongitudeRef] = b'E' if selected_location[0]['longitude'] >= 0 else b'W'
        
            lat = convert_rational_to_degrees(gps_data[piexif.GPSIFD.GPSLatitude])
            lat_ref = gps_data[piexif.GPSIFD.GPSLatitudeRef].decode('utf-8')
            lon = convert_rational_to_degrees(gps_data[piexif.GPSIFD.GPSLongitude])
            lon_ref = gps_data[piexif.GPSIFD.GPSLongitudeRef].decode('utf-8')
            print(f"Coords from FIXED PHOTO : Latitude: {lat} {lat_ref}, Longitude: {lon} {lon_ref}")
    elif 'GPS' not in exif_dict and selected_location: 
        print("GPS in: JSON Only = Overwring with Matching GPS Data")

        gps_data = exif_dict[exif_dict]
        new_lat = selected_location[0]["latitude"]
        new_lon = selected_location[0]["longitude"]
        
        print("NEW LAT: ", str(new_lat))
        print("NEW LON: ", str(new_lon))
        if (new_lat != 0.0) and (new_lon != 0.0):
                gps_ifd = {
                    piexif.GPSIFD.GPSLatitudeRef: b'N' if new_lat >= 0 else b'S',
                    piexif.GPSIFD.GPSLatitude: convert_degrees_to_rational([abs(new_lat), 0, 0]),  # Assuming basic format
                    piexif.GPSIFD.GPSLongitudeRef: b'E' if new_lon >= 0 else b'W',
                    piexif.GPSIFD.GPSLongitude: convert_degrees_to_rational([abs(new_lon), 0, 0]),
                }
                exif_dict['GPS'] = gps_ifd
        else:
            print("Geolocation values are all zero; skipping GPS update.")


    # === SAVE ===
    # # Convert the modified EXIF data back to binary and save the image
    # exif_bytes = piexif.dump(exif_dict)
    # img.save(destinationfilepath, exif=exif_bytes)




    # === Save resolution ====
    try:
        # Attempt to dump the EXIF data first without any correction
        exif_bytes = piexif.dump(exif_dict)
        img.save(destinationfilepath, exif=exif_bytes)
        if isinstance(selected_date, str):
            new_datetime = datetime.datetime.strptime(selected_date, "%Y:%m:%d %H:%M:%S")
        else:
            new_datetime = selected_date
        
        timestamp = new_datetime.timestamp()

        # Update file system times
        os.utime(destinationfilepath, (timestamp, timestamp))
        print(f"\033[92mOVERRIDE COMPLETE! EXIF data successfully updated for {destinationfilepath}\033[0m")
        
        
        return  # Success, so return early
    except struct.error as e:
        print(f"\033[91mERROR: Initial EXIF dump failed! {e}\033[0m")
        print("=== DEBUG: Checking and Correcting GPS Data ===")
        if 'GPS' in exif_dict:
            # Correct Latitude (Tag: 2)
            if piexif.GPSIFD.GPSLatitude in exif_dict['GPS']:
                latitude = exif_dict['GPS'][piexif.GPSIFD.GPSLatitude]
                # Ensure latitude seconds are positive
                exif_dict['GPS'][piexif.GPSIFD.GPSLatitude] = [(abs(lat[0]), lat[1]) for lat in latitude]
                print(f"Corrected GPS Latitude: {exif_dict['GPS'][piexif.GPSIFD.GPSLatitude]}")

            # Correct Longitude (Tag: 4)
            if piexif.GPSIFD.GPSLongitude in exif_dict['GPS']:
                longitude = exif_dict['GPS'][piexif.GPSIFD.GPSLongitude]
                # Ensure longitude seconds are positive
                exif_dict['GPS'][piexif.GPSIFD.GPSLongitude] = [(abs(lon[0]), lon[1]) for lon in longitude]
                print(f"Corrected GPS Longitude: {exif_dict['GPS'][piexif.GPSIFD.GPSLongitude]}")

            # Correct Altitude (Tag: 27)
            if piexif.GPSIFD.GPSAltitude in exif_dict['GPS']:
                try:
                    altitude = exif_dict['GPS'][piexif.GPSIFD.GPSAltitude]
                    # Check if the altitude is stored as a string
                    if isinstance(altitude, bytes):
                        altitude = float(altitude.decode())
                    exif_dict['GPS'][piexif.GPSIFD.GPSAltitude] = int(altitude * 100)  # Store as integer meters
                    print(f"Corrected GPS Altitude: {exif_dict['GPS'][piexif.GPSIFD.GPSAltitude]}")
                except Exception as e:
                    print(f"Failed to correct GPS Altitude: {e}")

        # === TRY SAVING AGAIN AFTER CORRECTIONS ===
        try:
            exif_bytes = piexif.dump(exif_dict)
            img.save(destinationfilepath, exif=exif_bytes)
            if isinstance(selected_date, str):
                new_datetime = datetime.datetime.strptime(selected_date, "%Y:%m:%d %H:%M:%S")
            else:
                new_datetime = selected_date
            
            timestamp = new_datetime.timestamp()

            print(f"\033[92mOVERRIDE COMPLETE! EXIF data successfully updated for {destinationfilepath}\033[0m")
                # Update file system times
            os.utime(destinationfilepath, (timestamp, timestamp))
        except struct.error as e:
            print(f"\033[91mERROR: EXIF dump failed after corrections! {e}\033[0m")
            raise  # Let the error propagate and crash if it fails again
    



# def override_video_data(destinationfilepath, selected_date, selected_location):


def process_action(action, curr_file_path, curr_file_name, date_date_filename,date_time_filename,date_creation_date,date_modified_date,date_metadata,date_EXIF,date_dateAcquired,date_json):
    # Select Date

    print("-------")
    print("\nFile Processing Action started... Using value: ", action, type(action))


    selected_date = 0
    selected_time = 0
    selected_location = None
    selected_json_path = None

    # print("Curr File Name: " + curr_file_name)
    print("Curr File Path: " + curr_file_path)
    print("Curr JSON Data: ",  date_json)
    print("-------")
    action = str(action)

    if action == "1": #Date from file name
        selected_date = date_date_filename
        selected_time = date_time_filename
    elif action == "2":
        selected_date = date_creation_date
    elif action == "3":
        selected_date = date_modified_date
    elif action == "4":
        selected_date = date_metadata
    elif action == "5":
        selected_date = date_EXIF
    elif action == "6":
        selected_date = date_dateAcquired
    elif action == "9" or action == "8": 
        selected_location = date_json["locations"]
        selected_json_path = date_json["file_path"]
        if action == "8": 
            print("8 selected - creation time")
            selected_date = date_json["dates_times"][0][1]
        elif action == "9": 
            print("9 selected - phototaken time")
            selected_date = date_json["dates_times"][1][1]

    print("Selected date: " , selected_date)
    print("Selected location: " , selected_location)
    print("Selected jsonpath: " , selected_json_path)
    print("-------")
    
    newDateStr = str(selected_date).replace(" ", "_").replace(":", "-").replace(".", "-")
    newLocStr = ""
    if selected_location is not None and selected_location: 
        print("\033[92m", "!!!!! LOCATION HAS DATA !!!!")
        print("LA: ", str(selected_location[0]["latitude"]) )
        print("LO: ", str(selected_location[0]["longitude"]) )
        print("AL: ", str(selected_location[0]["altitude"]))

        newLocStr += "_LA-" +str(selected_location[0]["latitude"]) 
        newLocStr += "_LO-" +str(selected_location[0]["longitude"]) 
        newLocStr += "_AL-" +str(selected_location[0]["altitude"]) + "_"
        print(newLocStr, "\033[0m")
    else: 
        print("Location has no data")
    
    print("-------")
    newFileName = f"{str(newDateStr)}_{newLocStr}{curr_file_name}"
    newJSONName = f"{str(newDateStr)}_{newLocStr}{curr_file_name}.json"

    print("Renamed File Name: " + newFileName)
    print("Renamed JSON Name: " + newJSONName)
    print("-------")
    destinationjsonpath =  PROCESSED_PATH + "\\" + newJSONName
    destinationfilepath =  PROCESSED_PATH + "\\" + newFileName
    print("Dest File Path: " + destinationfilepath)
    print("Dest JSON path: " + destinationjsonpath)
    print("-------")


    print("Copy files: ")
    copy_and_check(curr_file_path, destinationfilepath)
    copy_and_check(selected_json_path, destinationjsonpath)
    print ("-----")

    # if selected_location is not None and selected_location: 
    #     input(" Proceed to override data? \n >>> ")

    print("Overriding data: ")

    image_extensions = {'.jpeg', '.jpg', '.bmp', '.png', '.cr2'}
    video_extensions = {'.mov', '.mp4', '.avi', '.mkv'}
    
    _, ext = os.path.splitext(curr_file_name)
    if ext in image_extensions: 
        override_image_data(destinationfilepath, selected_date, selected_location)
    if ext in video_extensions: 
        override_video_data(destinationfilepath, selected_date, selected_location)
    print("-------")
    print("Mmoving to next file!")
    return


def partial_match(curr_file_name, dest_path):
    # Get the base name of the current file without the extension
    base_name = os.path.splitext(curr_file_name)[0]

    # Iterate through all files in the destination path
    for file_name in os.listdir(dest_path):
        # Get the base name of the destination file without the extension
        dest_base_name = os.path.splitext(file_name)[0]

        # Check if the base name of the current file is a substring of any destination file's base name
        if base_name in dest_base_name:
            print(f"Partial match found: {file_name} matches with {curr_file_name}")
            return True

    # If no match is found, return False
    print(f"No partial match found for {curr_file_name} in {dest_path}")
    return False


def menu_system(file_path, file_name, source_path):
    while True:
        
        # Extract date from various places, print processing stuff
        print("--------------------")
        noneStr = '\033[91mNone\033[0m'
        date_date_filename = drf.get_date_from_filename(file_name)
        date_time_filename = drf.get_time_from_filename(file_name)
        date_creation_date = drf.get_date_from_creation_date(file_path)
        date_modified_date = drf.get_date_from_modified_date(file_path)
        date_metadata = drf.get_date_from_metadata(file_path)
        date_EXIF = drf.get_date_from_EXIF(file_path)
        date_dateAcquired = drf.get_date_from_dateAcquired(file_path)
        date_json = drf.get_date_from_JSON(source_path, file_name)
        print("--------------------\033[0m")

        
        #Print Menu
        noneStr = '\033[91mNone\033[0m'
        print(f"1-DateFileName  : {date_date_filename or noneStr}")
        print(f"1-TimeFileName  : {date_time_filename or noneStr}")
        print(f"2-CREATION      : {date_creation_date or noneStr}")
        print(f"3-MODIFIED      : {date_modified_date or noneStr}")
        print(f"4-METADATA      : {date_metadata or noneStr}")
        print(f"5-EXIF          : {date_EXIF or noneStr}")
        print(f"6-DATEACQUIRED  : {date_dateAcquired or noneStr}")
        print(f"8/9-JSON        : {str('Valid') if date_json else noneStr}")
        if date_json:
            print(print_readable_format(date_json))



        # ==== Automatic Process ====
        if date_json:
            action = '9'
            print("\033[94m >>> AUTO", action, "\033[0m")
            process_action(int(action), file_path, file_name, 
                            date_date_filename, date_time_filename,
                            date_creation_date, date_modified_date,
                            date_metadata, date_EXIF, 
                            date_dateAcquired, date_json)
            break
        # ==== Automatic Process ====

        # Prompt for input and handle accidental or invalid entries
        action = input("\033[94m>>> Enter 1-9 to select override date, 'r' to refresh, or 'x' to exit\n>>> \033[0m").strip().lower()

        if action in ['1', '2', '3', '4', '5', '6', '8', '9', 'x', 'r']:
            if action == 'x':
                print("Exiting...")
                exit(0)
            elif action == 'r':
                print("\033[94mRefreshing...\033[0m")
                continue  # Restart the loop to refresh the information
            else:
                # Process action based on the user's valid selection
                process_action(int(action), file_path, file_name, 
                            date_date_filename, date_time_filename,
                            date_creation_date, date_modified_date,
                            date_metadata, date_EXIF, 
                            date_dateAcquired, date_json)
                break
        else:
            # Print an error message for invalid input and re-ask the question
            print("\033[91mInvalid input! Please enter a number between 1-9 or 'x' to exit.\033[0m")

def main(): 

    #Create Processed folder if does not exist
    if not os.path.exists(PROCESSED_PATH):
        os.makedirs(PROCESSED_PATH)
        print(f"Folder created: {PROCESSED_PATH}")

    #Process all files in SOURCE_PATH
    counter = 1
    files = sorted(os.listdir(SOURCE_PATH))  # Sorts files by name in ascending order


    for file_name in files: 
        file_path = os.path.join(SOURCE_PATH, file_name)

        # If its a file with programmed FILE_TYPE --> attempt to process
        if os.path.isfile(file_path) and file_name.endswith(FILE_TYPE):
            
            #Print header            
            print("\n\033[92m" + "[" + str(counter) + "] Name: " + file_name)
            print("--------------------\033[0m")
            counter += 1

            #Check if theres a partially procesed/matched file in processed path. If true, prompt the partial process flow, else show the menu
            # partial_check = partial_match(file_name, PROCESSED_PATH)
            # if partial_check: 
            #     user_input = input("\033[94mPartial match detected in Processed directory. Please check. \nENTER = skip this file | p = process file\n>>> \033[0m").strip().lower()
            #     if user_input == "p":
            #         print(f"Processing file: {file_name}")
            #         pass
            #     else:
            #         print(f"Skipping file: {file_name}")
            #         continue
            menu_system(file_path, file_name, SOURCE_PATH)


if __name__ == "__main__": 
    main()