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

    # Normalize the file name to handle variations
    base_name, ext = os.path.splitext(file_name)
    normalized_base_name = normalized_name = re.sub(r' \(\d+\)|-edited', '', base_name)

    # Reconstruct the file name with ".json" extension
    json_file_name = f"{normalized_base_name}{ext}.json"
    
    print(json_file_name)
    # Full path for the file in the current directory
    currdir_json_path = os.path.join(source_path, json_file_name)

    gphotos_json_path = "F:\\GPhotos\\Takeout\\Google Photos"

    fileFoundFlag = 0
    for root, dirs, files in os.walk(gphotos_json_path):
        for file in files:
            if file == json_file_name:
                file_path = os.path.join(root, file)
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