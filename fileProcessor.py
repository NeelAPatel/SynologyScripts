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


# Hardcoded path to the directory you want to access
folder_path = r'../../GPhotos-Metadatafix-ErrorIdentical/Errors'


# Function to extract date from filename (you already have this, slightly optimized)
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
                return datetime(year, month, day)
    
    print("    > No date found in filename")
    return None

# Function to extract time from filename
def get_time_from_filename(filename):
    time_patterns = [
        r'(\d{2})(\d{2})(\d{2})',    # HHMMSS
        r'(\d{2}):(\d{2}):(\d{2})',  # HH:MM:SS
        r'(\d{2})_(\d{2})_(\d{2})'   # HH_MM_SS (common format)
    ]
    for pattern in time_patterns:
        match = re.search(pattern, filename)
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

# Function to handle metadata display and matching
def process_file(file_path, filename):
    print(f"\nProcessing file: {filename}")
    
    # Skip .json files
    if filename.endswith('.json'):
        print("  > Skipping JSON file")
        return

    # Extract EXIF data
    exif_data = get_exif_data(file_path)
    if exif_data:
        print("  > EXIF Data: ")
        for key, value in exif_data.items():
            print(f"    {key}: {value}")
    else:
        print("\033[91m  > No EXIF data found or unable to read.\033[0m")

    # Try extracting date from filename
    file_date = get_date_from_filename(filename)
    
    if file_date:
        # If a date is found, remove that portion of the filename before extracting time
        date_str = file_date.strftime('%Y%m%d')  # Format the date as YYYYMMDD
        # Remove the date string from the filename before passing to time extractor
        filename_without_date = filename.replace(date_str, '')
        
        # Now extract time from the remaining part of the filename
        file_time = get_time_from_filename(filename_without_date)
    else:
        file_time = None

    if file_date and file_time:
        file_datetime = datetime.combine(file_date, file_time)
        print(f"  > DateTime extracted from filename: {file_datetime}")
    elif file_date:
        print(f"  > Date extracted from filename: {file_date}")
    else:
        print("\033[91m  > No valid date or time found in filename.\033[0m")

    # Match EXIF/Metadata with file name
    if exif_data and 'DateTime' in exif_data:
        exif_datetime = exif_data['DateTime']
        exif_dt_obj = datetime.strptime(exif_datetime, '%Y:%m:%d %H:%M:%S')
        print(f"  > EXIF DateTime: {exif_dt_obj}")

        if file_date and file_time:
            if exif_dt_obj == file_datetime:
                print("\033[92m  > Datetime matches!\033[0m")
            else:
                print("\033[91m  > Datetime mismatch.\033[0m")
    else:
        print("\033[91m  > No EXIF/Metadata datetime found.\033[0m")

    # Check if location data exists
    if exif_data and 'GPSInfo' in exif_data:
        print("\033[92m  > Location found!\033[0m")
    else:
        print("\033[91m  > No location data found.\033[0m")

    # User action choices
    action = input("What do you want to do? (y = move, s = skip, o = overwrite): ")
    if action == 'y':
        move_to_processed(file_path, filename)
    elif action == 'o':
        if file_date and file_time:
            overwrite_metadata(file_path, file_datetime)
        else:
            print("\033[91m  > No valid date/time to overwrite.\033[0m")
    # Skip action does nothing, moves to next file
    print()

# Move file to /Processed directory
def move_to_processed(file_path, filename):
    processed_dir = "../../GPhotos-Metadatafix-ErrorIdentical/Errors/Processed"
    os.makedirs(processed_dir, exist_ok=True)
    dest_path = os.path.join(processed_dir, filename)
    shutil.move(file_path, dest_path)
    print(f"  > Moved to {processed_dir}")



# Function to overwrite EXIF metadata with a new datetime extracted from the filename
def overwrite_metadata(file_path, new_datetime):
    print(f"  > Overwriting metadata with new datetime: {new_datetime}")

    try:
        # Load the image and its EXIF data
        img = Image.open(file_path)
        exif_dict = piexif.load(img.info['exif'])

        # Convert new_datetime to the correct string format for EXIF (YYYY:MM:DD HH:MM:SS)
        new_datetime_str = new_datetime.strftime('%Y:%m:%d %H:%M:%S')

        # Overwrite the DateTime fields in EXIF data
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = new_datetime_str.encode()
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = new_datetime_str.encode()
        exif_dict['0th'][piexif.ImageIFD.DateTime] = new_datetime_str.encode()

        # Dump the modified EXIF data back to binary format
        exif_bytes = piexif.dump(exif_dict)

        # Save the image with the modified EXIF data
        img.save(file_path, "jpeg", exif=exif_bytes)
        print("  > Metadata successfully overwritten.")
    except Exception as e:
        print(f"\033[91m  > Failed to overwrite metadata: {e}\033[0m")

# Main function to scan the directory
def scan_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            process_file(file_path, filename)

# Execute the scan
if __name__ == "__main__":
    scan_directory("../../GPhotos-Metadatafix-ErrorIdentical/Errors")
