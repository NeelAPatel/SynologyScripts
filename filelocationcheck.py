import os
import json
import shutil
from PIL import Image
from datetime import datetime
from os.path import join, isfile
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
import os
import re
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
import shutil
import piexif

import piexif
from PIL import Image

import win32com.client


# folder_path = r'../../GPhotos-Metadatafixer/2024-10-01-173418557/AAATotal/Part1'
folder_path = r"Z:\PhotoLibrary\2024\09"


def get_date_acquired(filepath):
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
        print(f"    > Date acquired not found for: {filepath}")
        return None
    

# Function to extract date and return the last index of the matched date
def get_date_from_filename(filename):
    print("  > FileName: ", filename)
    date_patterns = [
        r'(\d{4})(\d{2})(\d{2})',    # YYYYMMDD
        r'(\d{4})-(\d{2})-(\d{2})'   # YYYY-MM-DD
    ]
    for pattern in date_patterns:
        match = re.search(pattern, filename)
        print(f'    > Checking pattern {pattern} in filename {filename}')  # Debug info
        if match:
            year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
            current_year = datetime.now().year
            # Ensure valid date components
            print(f'    > Extracted year: {year}, month: {month}, day: {day}')
            if 1 <= month <= 12 and 1 <= day <= 31 and year <= current_year:
                # Return both the date and the last index of the matched date portion
                return datetime(year, month, day), match.end()  # match.end() gives the index of the last character in the date
    
    print("    > No date found in filename")
    return None, None  # Return None if no date is found

# Function to extract time from filename, starting after the given index
def get_time_from_filename(filename, start_index):
    time_patterns = [
        r'(\d{2})(\d{2})(\d{2})',    # HHMMSS
        r'(\d{2}):(\d{2}):(\d{2})',  # HH:MM:SS
        r'(\d{2})_(\d{2})_(\d{2})'   # HH_MM_SS (common format)
    ]
    
    # Only consider the part of the filename after the date portion
    filename_time_part = filename[start_index:]  # Start scanning after the date portion
    
    for pattern in time_patterns:
        match = re.search(pattern, filename_time_part)
        if match:
            hour, minute, second = int(match.group(1)), int(match.group(2)), int(match.group(3))
            # Ensure valid time components
            if 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59:
                return datetime(1, 1, 1, hour, minute, second).time()
    
    print("    > No time found in filename")
    return None


# Function to extract EXIF data from image files
def get_exif_data(file_path):
    try:
        image = Image.open(file_path)
        info = image._getexif()
        if info:
            exif_data = {}
            for tag, value in info.items():
                tag_name = TAGS.get(tag, tag)
                exif_data[tag_name] = value
            return exif_data
        return None
    except Exception as e:
        print(f"Error reading EXIF data: {e}")
        return None

def process_file(file_path, file_name): 
    # Get Filename
    # Get Date from filename
    # Get Location from exif/metadata


    print()
    # print(f'FILE: {file_name}')
    # print(f'EXIF: {get_exif_data(file_path)}')
    file_date, date_end_index = get_date_from_filename(file_name)
    print(f'Filename Date: {file_date}')
    # print(f'Filename Time: {get_time_from_filename(file_name, date_end_index)}')
    print(f'File Acquired: {get_date_acquired(file_path)}')


def main(folder_path):
    #Scan directory
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if os.path.isfile(file_path):
            process_file(file_path, filename)
    return 0

    # for name in os.listdir(folder_path):
    # # Open file
    #     with open(os.path.join(folder_path, name)) as f:
    #         print(f"Content of '{name}'")
    #         # Read content of file
    #         print(f.read())

    # print()



if __name__ == "__main__": 
    main(folder_path)