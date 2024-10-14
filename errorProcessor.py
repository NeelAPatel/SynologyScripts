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


# CONSTANTS

FILE_TYPE = ".JPEG".lower()
SOURCE_PATH = r"E:\GPhotos-Metadatafixer\2024-10-01-173418557\AAATotal\Error" + FILE_TYPE.replace('.', "")

PROCESSED_PATH = SOURCE_PATH + "\\Processed"
SKIPPED_PATH = SOURCE_PATH + "\\Skipped"


def check_constants(): 
    print(FILE_TYPE)
    print(SOURCE_PATH)


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

def get_date_from_filename(file_name):
    date_patterns = [
        r'(\d{4})(\d{2})(\d{2})',    # YYYYMMDD
        r'(\d{4})-(\d{2})-(\d{2})'   # YYYY-MM-DD
    ]
    for pattern in date_patterns:
        match = re.search(pattern, file_name)
        # print(f'    > Checking pattern {pattern} in filename {file_name}')  # Debug info
        if match:
            year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
            current_year = datetime.now().year
            # Ensure valid date components
            # print(f'    > Extracted year: {year}, month: {month}, day: {day}')
            if 1 <= month <= 12 and 1 <= day <= 31 and year <= current_year:
                return datetime(year, month, day)
    
    # print("    > No date found in filename")
    return None

def get_time_from_filename(file_name):
    time_patterns = [
        r'(\d{2})(\d{2})(\d{2})',    # HHMMSS
        r'(\d{2}):(\d{2}):(\d{2})',  # HH:MM:SS
        r'(\d{2})_(\d{2})_(\d{2})'   # HH_MM_SS (common format)
    ]
    for pattern in time_patterns:
        match = re.search(pattern, file_name)
        if match:
            hour, minute, second = int(match.group(1)), int(match.group(2)), int(match.group(3))
            # Ensure valid time components
            if 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59:
                return datetime(1, 1, 1, hour, minute, second).time()
    
    # print("    > No time found in filename")
    return None

def get_date_from_creation_date(file_path):
    # print("  > FileCreation Date: ")
    try:
        creation_time = os.path.getctime(file_path)
        # print(f"    > Date Found : {str(creation_time)}")
        return datetime.fromtimestamp(creation_time)
    except Exception as e:
        print(f"    > ERROR @ FileCreation: Cannot get file creation date for {file_path}: {e}")
    return None

def get_date_from_modified_date(file_path):
    # print("  > FileModified Date: ")
    try:
        modified_time = os.path.getmtime(file_path)
        # print(f"    > Date Found: {modified_time}")
        return datetime.fromtimestamp(modified_time)
    except Exception as e:
        print(f"    > ERROR @ FileModified: Cannot get file modified date for {file_path}: {e}")
    return None

def get_date_from_metadata(file_path):
# Function to extract metadata date using hachoir
    print("> Metadata: ")
    try:
        parser = createParser(file_path)
        if not parser:
            print(f"  > @Metadata: Unable to create parser for {file_path}")
            return None

        metadata = extractMetadata(parser)
        if not metadata:
            print(f"  > Metadata: No metadata found for {file_path}")
            return None

        # Try to get the creation date from metadata
        create_date = metadata.get('creation_date')
        if create_date:
            # print("    > Date Found: "+ create_date)
            return create_date
        else:
            print("  > Metadata: Metadata does not contain 'creation_date'")
    except Exception as e:
        print(f"  > @Metadata : Metadata extraction failed for {file_path}: {e}")
    
    return None

def get_date_from_EXIF(file_path):
    print("> EXIF: ")
    try:
        image = Image.open(file_path)
        info = image._getexif()
        if info:
            print("  > EXIF Data found ")
            # print(info)
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                if decoded == 'DateTimeOriginal':
                    print("  > Date found: " + datetime.strptime(value, '%Y:%m:%d %H:%M:%S'))
                    return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
    except Exception as e:
        print(f"  > ERROR @ EXIF: Error extracting EXIF data from {file_path}: {e}")
    return None

def get_date_from_dateAcquired(filepath):
    """
    Retrieves the 'Date acquired' property for a file in Windows Explorer.
    """
    # Ensure file exists
    if not os.path.exists(filepath):
        print(f"    > File acquired: file does not exist: {filepath}")
        return None
    
    # Use Windows Shell COM object to get file properties
    shell = win32com.client.Dispatch("Shell.Application")
    
    # Get the folder and file name
    folder_path, file_name = os.path.split(filepath)
    
    # Get the folder object
    folder = shell.Namespace(folder_path)
    
    # Find the index for the "Date acquired" property (property index 217)
    # Note: Index might vary by Windows version, but 217 is common for "Date acquired"
    date_acquired_idx = 217
    
    # Get file item
    item = folder.ParseName(file_name)
    
    # Retrieve the "Date acquired" property
    date_acquired = folder.GetDetailsOf(item, date_acquired_idx)
    
    if date_acquired:
        return date_acquired
    else:
        # print(f"    > Date acquired not found for: {filepath}")
        return None

def get_date_from_JSON(source_path, file_name):

    json_file_name = str(file_name + ".json")
    currdir_json_path = os.path.join(source_path, str(file_name + ".json"))

    gphotos_json_path = "F:\\GPhotos\\Takeout\\Google Photos"


    fileFoundFlag = 0
    for root, dirs, files in os.walk(gphotos_json_path): 
        for file in files: 
            # print(file)
            if file == json_file_name: 
                # print("File Found: ", file_path)
                file_path = os.path.join(root, file)
                # print("File Found: ", file_path)
                info = parse_json(file_path) 
                return info



    return None

def parse_json(file_path): 
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)

            # Extract date/time and location information
            info = {
                "file_path": file_path,
                "dates_times": [],
                "locations": []
            }
            

            format1 = '%Y:%m:%d %H:%M:%S'
            format2 = "%b %d, %Y, %I:%M:%S\u202f%p %Z"

            # print(type(data["creationTime"]["formatted"]))
            # Scan the JSON for date/time fields

            
            if "creationTime" in data and "formatted" in data["creationTime"]:
                rawdate = data["creationTime"]["formatted"]
                datetime_value = datetime.strptime(rawdate, format2)
                datetime_value = datetime_value.replace(tzinfo=timezone.utc)
                info["dates_times"].append(("creationTime", datetime_value))

            if "photoTakenTime" in data and "formatted" in data["photoTakenTime"]:
                rawdate =  data["photoTakenTime"]["formatted"]
                datetime_value = datetime.strptime(rawdate, format2)
                datetime_value = datetime_value.replace(tzinfo=timezone.utc)
                info["dates_times"].append(("photoTakenTime",datetime_value))

            # Scan for location data
            if "geoData" in data:
                geo = data["geoData"]
                if geo["latitude"] != 0.0 or geo["longitude"] != 0.0:
                    info["locations"].append({
                        "latitude": geo["latitude"],
                        "longitude": geo["longitude"],
                        "altitude": geo["altitude"]
                    })
            if "geoDataExif" in data:
                geo_exif = data["geoDataExif"]
                if geo_exif["latitude"] != 0.0 or geo_exif["longitude"] != 0.0:
                    info["locations"].append({
                        "latitude": geo_exif["latitude"],
                        "longitude": geo_exif["longitude"],
                        "altitude": geo_exif["altitude"]
                    })
            
            return info
            
        except json.JSONDecodeError:
            print(f"Error decoding JSON from file: {file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")
    return None

def print_readable_format(data):

    if data is None: 
        return None
    else:
        print()
        print(f"  File Path: {data['file_path']}")
        print("  Dates/Times:")
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



def get_date_from_datefield():
    return 


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
    print("COpying from: ", source)
    print("Copying to: ", destination)
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

def convert_degrees_to_rational(degrees):
    # Converts decimal degrees into a rational format needed by EXIF
    return (int(degrees[0]), 1), (int(degrees[1]), 1), (int(degrees[2] * 100), 100)

def override_data(destinationfilepath, selecteddate, selectedlocation): 
    # Open the image and load existing EXIF data
    img = Image.open(destinationfilepath)
    # Check if EXIF data is present
    if 'exif' in img.info:
        exif_dict = piexif.load(img.info['exif'])
    else:
        # Print statement if EXIF data is not present and create a new EXIF dictionary
        print("\033[91mEXIF data not present\033[0m")
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}, "thumbnail": None}
        print("\033[95mEXIF data created\033[0m")



    exif_date_str = selecteddate.strftime("%Y:%m:%d %H:%M:%S")


    # Update EXIF date values
    exif_dict['0th'][piexif.ImageIFD.DateTime] = exif_date_str
    exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = exif_date_str
    exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = exif_date_str


    if selectedlocation is not None and selectedlocation: 
        # Update GPS information
        gps_ifd = {
            # piexif.GPSIFD.GPSLatitudeRef: b'N' if new_lat[0] >= 0 else b'S',
            # piexif.GPSIFD.GPSLatitude: convert_degrees_to_rational(new_lat),
            # piexif.GPSIFD.GPSLongitudeRef: b'E' if new_lon[0] >= 0 else b'W',
            # piexif.GPSIFD.GPSLongitude: convert_degrees_to_rational(new_lon),
        }
        exif_dict['GPS'] = gps_ifd

    # Convert the modified EXIF data back to binary
    exif_bytes = piexif.dump(exif_dict)

    # Save the image with the updated EXIF data
    img.save(destinationfilepath, exif=exif_bytes)

    if isinstance(selecteddate, str):
        new_datetime = datetime.datetime.strptime(selecteddate, "%Y:%m:%d %H:%M:%S")
    else:
        new_datetime = selecteddate
    
    timestamp = new_datetime.timestamp()

    # Update file system times
    os.utime(destinationfilepath, (timestamp, timestamp))


def process_action(action, curr_file_path, curr_file_name, date_date_filename,date_time_filename,date_creation_date,date_modified_date,date_metadata,date_EXIF,date_dateAcquired,date_json):
    # Select Date
    print("Action process...")
    print("Curr File Name: " + curr_file_name)
    print("Curr File Path: " + curr_file_path)
    print("Curr JSON Data: ",  date_json)


    selecteddate = 0
    selectedlocation = None
    selectedjsonpath = None

    print("Entered Value: " , action, type(action))
    # print(type(action))
    action = str(action)
    if action == "9" or action == "8": 
        selectedlocation = date_json["locations"]
        selectedjsonpath = date_json["file_path"]
        if action == "8": 
            print("8selected - creation time")
            selecteddate = date_json["dates_times"][0][1]
        elif action == "9": 
            print("9 selected - phototaken time")
            selecteddate = date_json["dates_times"][1][1]

    print("-------")
    print("Selected date: " , selecteddate)
    print("Selected location: " , selectedlocation)
    print("Selected jsonpath: " , selectedjsonpath)
    
    
    newDateStr = str(selecteddate).replace(" ", "_").replace(":", "-")
    newLocStr = ""
    if selectedlocation is not None and selectedlocation: 
        print("Location has data")
        newLocStr = str(selectedlocation) + "_"
    else: 
        print("Location has no data")
    
    newFileName = f"{str(newDateStr)}_{newLocStr}{curr_file_name}"
    newJSONName = f"{str(newDateStr)}_{newLocStr}{curr_file_name}.json"

    print("Renamed File Name: " + newFileName)
    print("Renamed JSON Name: " + newJSONName)

    destinationjsonpath =  PROCESSED_PATH + "\\" + newJSONName
    destinationfilepath =  PROCESSED_PATH + "\\" + newFileName
    print("Dest File Path: " + destinationfilepath)
    print("Dest JSON path: " + destinationjsonpath)

    # input(" Proceed to copying files? \n>>> ")
    
    # if not os.path.exists(PROCESSED_PATH):
    #     os.makedirs(PROCESSED_PATH)
    #     print(f"Folder created: {PROCESSED_PATH}")


    print("Copy files: ")
    copy_and_check(curr_file_path, destinationfilepath)
    copy_and_check(selectedjsonpath, destinationjsonpath)
    print ("-----")

    # input(" Proceed to override data? \n >>> ")
    override_data(destinationfilepath, selecteddate, selectedlocation)

    print("Override complete, moving to next file!")
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


def process_files(source_path):
    #Processing

    if not os.path.exists(PROCESSED_PATH):
        os.makedirs(PROCESSED_PATH)
        print(f"Folder created: {PROCESSED_PATH}")
    counter = 1
    for file_name in os.listdir(source_path): 
        file_path = os.path.join(source_path, file_name)


        if os.path.isfile(file_path) and file_name.endswith(FILE_TYPE):
            print()
            
            print("\033[92m" + "[" + str(counter) + "] Name: " + file_name)
            print("--------------------\033[0m")
            counter += 1

            partial_check = partial_match(file_name, PROCESSED_PATH)

            if partial_check: 
                user_input = input("\033[94mPartial match detected in Processed directory. Please check. \nENTER = skip this file | p = process file\n>>> \033[0m").strip().lower()
                if user_input == "p":
                    print(f"Processing file: {file_name}")
                    pass
                else:
                    print(f"Skipping file: {file_name}")
                    continue



            # print("--------------------\033[0m")


            menu_system(file_path, file_name, source_path)
            # date_date_filename, date_time_filename,                date_creation_date, date_modified_date, date_metadata,                 date_EXIF, date_dateAcquired, date_json, noneStr

            

def menu_system(file_path, file_name, source_path):
    while True:

                #continue processing
        print("--------------------")
        noneStr = '\033[91mNone\033[0m'
        date_date_filename = get_date_from_filename(file_name)
        date_time_filename = get_time_from_filename(file_name)
        date_creation_date = get_date_from_creation_date(file_path)
        date_modified_date = get_date_from_modified_date(file_path)
        date_metadata = get_date_from_metadata(file_path)
        date_EXIF = get_date_from_EXIF(file_path)
        date_dateAcquired = get_date_from_dateAcquired(file_path)
        date_json = get_date_from_JSON(source_path, file_name)
        # print(date_json)
        # print("----")

        print("--------------------\033[0m")
        noneStr = '\033[91mNone\033[0m'
        print(f"1-DateName      : {date_date_filename or noneStr}")
        print(f"1-TimeName      : {date_time_filename or noneStr}")
        print(f"2-CREATION      : {date_creation_date or noneStr}")
        print(f"3-MODIFIED      : {date_modified_date or noneStr}")
        print(f"4-METADATA      : {date_metadata or noneStr}")
        print(f"5-EXIF          : {date_EXIF or noneStr}")
        print(f"6-DATEACQUIRED  : {date_dateAcquired or noneStr}")
        print(f"8/9-JSON        : {str('Valid') if date_json else noneStr}")
        if date_json:
            print(print_readable_format(date_json))

        # Prompt for input and handle accidental or invalid entries
        action = input("\033[94m>>> Enter 1-9 to select override date, 'r' to refresh, or 'x' to exit\n>>> \033[0m").strip().lower()

        # Validate the input
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
    check_constants()
    # walk_directory(str(SOURCE_PATH), 1,1)

    process_files(str(SOURCE_PATH))

    









if __name__ == "__main__": 
    main()