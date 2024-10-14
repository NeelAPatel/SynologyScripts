import os
import shutil
from datetime import datetime
from time import time
from PIL import Image
from PIL.ExifTags import TAGS
import re
import subprocess
import json
from datetime import datetime
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from datetime import datetime


# Global variable for ignored directories
IGNORED_DIRECTORIES = ['@eaDir', 'PhotoLibrary']

# Get paths from environment variables or set defaults
SOURCE_PHOTOS_DIRECTORY = os.getenv('SOURCE_PHOTOS_DIRECTORY', '/volume1/photo')
IMPORT_BUCKET_DIRECTORY = '/volume1/ImportBucket'
DESTINATION_PHOTOS_DIRECTORY = os.getenv('DESTINATION_PHOTOS_DIRECTORY', '/volume1/photo/OrganizedLibrary')
UNSUPPORTED_FILE_DIRECTORY = os.getenv('UNSUPPORTED_FILE_DIRECTORY', 'Unsupported File Format')
# LOGS_DIRECTORY = os.getenv('LOGS_DIRECTORY', '/volume2/ServerLogs/Logs')

# Supported formats for images and videos
SUPPORTED_IMAGE_FORMATS = [
    '.bmp', '.gif', '.jpeg', '.jpg', '.png', '.webp', '.tif', '.tiff',
    '.arw', '.srf', '.sr2', '.dcr', '.k25', '.kdc', '.cr2', '.cr3', '.crw',
    '.nef', '.mrw', '.ptx', '.pef', '.raf', '.raw', '.3fr', '.erf', '.mef',
    '.mos', '.orf', '.rw2', '.dng', '.x3f'
]
SUPPORTED_VIDEO_FORMATS = ['.mov', '.mp4', '.flv', '.360']
SUPPORTED_FORMATS = SUPPORTED_IMAGE_FORMATS + SUPPORTED_VIDEO_FORMATS

# Initialize stats
stats = {
    'total_files_detected': 0,
    'photos_moved': 0,
    'unsupported_files_moved': 0,
    'errors_encountered': 0
}
# Function to extract metadata date using exiftool
def get_date_from_metadata(file_path):
# Function to extract metadata date using hachoir
    print("  > Metadata: ")
    try:
        parser = createParser(file_path)
        if not parser:
            print(f"    > Unable to create parser for {file_path}")
            return None

        metadata = extractMetadata(parser)
        if not metadata:
            print(f"    > No metadata found for {file_path}")
            return None

        # Try to get the creation date from metadata
        create_date = metadata.get('creation_date')
        if create_date:
            print("    > Date Found: "+ create_date)
            return create_date
        else:
            print("    > Metadata does not contain 'creation_date'")
    except Exception as e:
        print(f"    > ERROR @ Metadata: Metadata extraction failed for {file_path}: {e}")
    
    return None

    # try:
    #     result = subprocess.run(['exiftool', '-j', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #     metadata = json.loads(result.stdout.decode('utf-8'))[0]
    #     if 'CreateDate' in metadata:
    #         create_date = metadata['CreateDate']
    #         return datetime.strptime(create_date, '%Y:%m:%d %H:%M:%S')
    # except Exception as e:
    #     print(f"  > Metadata extraction failed for {file_path}: {e}")
    # return None

# Function to extract EXIF data
def get_date_from_exif(file_path):
    print("  > EXIF: ")
    try:
        image = Image.open(file_path)
        info = image._getexif()
        if info:
            print("    > EXIF Data found ")
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                if decoded == 'DateTimeOriginal':
                    print("    > Date found: " + datetime.strptime(value, '%Y:%m:%d %H:%M:%S'))
                    return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
    except Exception as e:
        print(f"    > ERROR @ EXIF: Error extracting EXIF data from {file_path}: {e}")
    return None

# Function to check if a filename contains a valid date
def get_date_from_filename(filename):
    print("  > FileName: ")
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
            # Log the extracted values to ensure correct extraction
            print(f'    > Extracted year: {year}, month: {month}, day: {day} from filename {filename}')
            if 1 <= month <= 12 and 1 <= day <= 31 and year <= current_year:
                print("    > Proper date found: " + str(datetime(year, month,day)))
                return datetime(year, month, day)
    
    print("    > No date found")
    return None

# Function to get file creation date
def get_file_creation_date(file_path):
    print("  > FileCreation Date: ")
    try:
        creation_time = os.path.getctime(file_path)
        print(f"    > Date Found : {str(creation_time)}")
        return datetime.fromtimestamp(creation_time)
    except Exception as e:
        print(f"    > ERROR @ FileCreation: Cannot get file creation date for {file_path}: {e}")
    return None

# Function to get file creation date
def get_file_modified_date(file_path):
    print("  > FileModified Date: ")
    try:
        modified_time = os.path.getmtime(file_path)
        print(f"    > Date Found: {modified_time}")
        return datetime.fromtimestamp(modified_time)
    except Exception as e:
        print(f"    > ERROR @ FileModified: Cannot get file modified date for {file_path}: {e}")
    return None


# Function to determine the earliest sorting date
def determine_sorting_date(file_path):
    
    filename = os.path.basename(file_path)
    
    print(" Date determination...")
    # Collect all dates and their sources
    exif_date     = get_date_from_exif(file_path)
    metadata_date = get_date_from_metadata(file_path)
    filename_date = get_date_from_filename(filename)
    creation_date = get_file_creation_date(file_path)
    modified_date = get_file_modified_date(file_path)

    # Store dates with their source labels
    date_sources = []
    if exif_date:
        date_sources.append((exif_date, "EXIF Date"))
    if metadata_date:
        date_sources.append((metadata_date, "Metadata Date"))
    if filename_date:
        date_sources.append((filename_date, "Filename Date"))
    if creation_date:
        date_sources.append((creation_date, "File Creation Date"))
    if modified_date: 
        date_sources.append((modified_date, "File Modified Date"))
    
    print("--> Final Date List:")
    for date_extract in date_sources: 
        print(f"  > {date_extract[1]} = {date_extract[0]}")
    # Find the earliest date
    if date_sources:
        earliest_date, date_source = min(date_sources, key=lambda x: x[0])
        print(f"-->> Using earliest date ({date_source}) | ({earliest_date}) for {file_path}")
        return earliest_date
    else:
        print(f" >> No valid date found for {file_path}")
        return None

# Function to log messages
# def print(message):
#     print(message)
#     try:
#         with open(log_file_path, 'a') as log_file:
#             log_file.write(f"{datetime.now()}: {message}\n")
#     except Exception as e:
#         print(f"Error writing to log file: {e}")


# Function to move unsupported files
def move_to_unsupported(file_path, unsupported_dir):
    try:
        os.makedirs(unsupported_dir, exist_ok=True)
        dest_file_path = os.path.join(unsupported_dir, os.path.basename(file_path))
        shutil.move(file_path, dest_file_path)
        stats['unsupported_files_moved'] += 1
        print(f"--> Moved unsupported file {file_path} to {unsupported_dir}")
    except Exception as e:
        stats['errors_encountered'] += 1
        print(f"  --> Error moving unsupported file {file_path}: {e}")

# Function to organize files by date
def organize_files_by_date(src_dir, dest_dir, unsupported_dir):
    try:
        for root, dirs, files in os.walk(src_dir):
            # Skip directories in the IGNORED_DIRECTORIES list
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES]
            
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                print("\n")
                print(f"Checking {file} @ {file_path}")
                
                if file_ext not in SUPPORTED_FORMATS:
                    print(f" ERROR: Unsupported file format {file}")
                    continue
                

                stats['total_files_detected'] += 1
                sorting_date = determine_sorting_date(file_path)
                
                if sorting_date:
                    year = sorting_date.strftime('%Y')
                    month = sorting_date.strftime('%m')

                    year_month_dir = os.path.join(dest_dir, year, month)
                    os.makedirs(year_month_dir, exist_ok=True)

                    dest_file_path = os.path.join(year_month_dir, file)
                    if not os.path.exists(dest_file_path):
                        try:
                            shutil.move(file_path, dest_file_path)
                            stats['photos_moved'] += 1
                            print(f" > Moved {file} to {year_month_dir}")
                        except Exception as e:
                            stats['errors_encountered'] += 1
                            print(f" > Error moving {file}: {e}")
                    else:
                        print(f" > {file} already exists in {year_month_dir}")
                else:
                    stats['errors_encountered'] += 1
                    print(f" > No valid sorting date for {file}, skipping.")
    except Exception as e:
        stats['errors_encountered'] += 1
        print(f"Error organizing files: {e}")



# # Set up custom log file
# def setup_logging():
#     try:
#         os.makedirs(LOGS_DIRECTORY, exist_ok=True)
#         log_filename = datetime.now().strftime("SynologySharedOrganizer_%Y-%m-%d.log")
#         # log_file_path = os.path.join(LOGS_DIRECTORY, log_filename)

#         with open(log_file_path, 'a') as log_file:
#             log_file.write(f"{datetime.now()}: Log initiated.\\n")
#         return log_file_path
#     except Exception as e:
#         print(f"Error setting up logging: {e}")
#         raise

# # Function to log to both Task Scheduler and custom log file
# def print(message):
#     print(message)  # This will be captured by Task Scheduler's native logging
#     try:
#         with open(log_file_path, 'a') as log_file:
#             log_file.write(f"{datetime.now()}: {message}\\n")
#     except Exception as e:
#         print(f"Error writing to log file: {e}")

# #    

# Function to generate final ASCII report
def generate_final_report(start_time, end_time):
    duration = end_time - start_time
    duration_str = f"{int(duration // 60)} minutes and {int(duration % 60)} seconds"
    
    report = (
        "\n----------------------------------\n"
        "Final Report\n"
        f"Files detected: {stats['total_files_detected']}\n"
        f"Photos moved: {stats['photos_moved']}\n"
        f"Unsupported files moved: {stats['unsupported_files_moved']}\n"
        f"Errors encountered: {stats['errors_encountered']}\n"
        f"Time taken: {duration_str}\n"
        "----------------------------------\n"
        "\n"
    )

    # Log the final report to console and log file
    print(report)
    # print(report)

if __name__ == "__main__":
    # Record start time
    start_time = time()

    # Set up custom logging and get the log file path
    # log_file_path = setup_logging()

    # Set the unsupported directory path
    unsupported_directory = os.path.join(SOURCE_PHOTOS_DIRECTORY, UNSUPPORTED_FILE_DIRECTORY)

    # Organize the files
    organize_files_by_date(SOURCE_PHOTOS_DIRECTORY, DESTINATION_PHOTOS_DIRECTORY, unsupported_directory)
    organize_files_by_date(IMPORT_BUCKET_DIRECTORY, DESTINATION_PHOTOS_DIRECTORY, unsupported_directory)

    end_time = time()
    # Generate the final report
    generate_final_report(start_time, end_time)



# # Function to determine the sorting date for a file
# def determine_sorting_date(file_path, log_file_path):
#     filename = os.path.basename(file_path)
#     print(f"\n#### Checking for file: {filename}")  # Log filename

#     # First check EXIF date
#     exif_date = get_exif_date(file_path)
#     if exif_date:
#         print(f"Using EXIF Date for {file_path}: {exif_date}")
#         return exif_date

#     # Then check filename for date
#     filename_date = extract_date_from_filename(filename)
#     if filename_date:
#         print(f"Using Filename Date for {file_path}: {filename_date}")
#         return filename_date

#     # Finally, check file creation date
#     file_creation_date = get_file_creation_date(file_path)
#     file_modified_date = get_file_modified_date(file_path)
#     if file_modified_date < file_creation_date:
#         print(f"Using File modified Date for {file_path}: {file_modified_date}")
#         return file_modified_date
#     elif file_creation_date:
#         print(f"Using File Creation Date for {file_path}: {file_creation_date}")
#         return file_creation_date
    
#     # Log if no valid date is found
#     print(f"No valid date found for {file_path}")
#     return None




# Adding the rest of the script back




# # Function to get the file's creation date
# def get_creation_date(file_path):
#     try:
#         image = Image.open(file_path)
#         info = image._getexif()
#         if info:
#             print(" > EXIF found ")
#             for tag, value in info.items():
#                 decoded = TAGS.get(tag, tag)
#                 if decoded == 'DateTimeOriginal':
#                     return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
#     except Exception as e:
#         print("No EXIF")
#         pass
#     return datetime.fromtimestamp(os.path.getctime(file_path))






# # Function to organize files by date
# def organize_files_by_date(src_dir, dest_dir, unsupported_dir, log_file_path):
#     try:
#         for root, dirs, files in os.walk(src_dir):
#             # Skip ignored directories
#             dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES]

#             # Ensure only root directories are processed
#             if not is_root_directory(root):
#                 continue

#             for file in files:
#                 file_path = os.path.join(root, file)
#                 file_ext = os.path.splitext(file_path)[1].lower()

#                 stats['total_files_detected'] += 1

#                 # Check if the file is supported
#                 if file_ext in SUPPORTED_FORMATS:
#                     # Get the original creation date
#                     creation_date = get_creation_date(file_path)

#                     # Extract year and month
#                     year = creation_date.strftime('%Y')
#                     month = creation_date.strftime('%m')

#                     # Create the year/month directory in the destination folder
#                     year_month_dir = os.path.join(dest_dir, year, month)
#                     os.makedirs(year_month_dir, exist_ok=True)

#                     # Move the file to the appropriate folder
#                     dest_file_path = os.path.join(year_month_dir, file)
#                     if not os.path.exists(dest_file_path):
#                         try:
#                             shutil.move(file_path, dest_file_path)
#                             stats['photos_moved'] += 1
#                             print(f"Moved {file} from {file_path} to {year_month_dir}")
#                         except Exception as e:
#                             stats['errors_encountered'] += 1
#                             print(f"Error moving {file}: {e}")
#                     else:
#                         print(f"{file} already exists in {year_month_dir}")
#                 else:
#                     # Move unsupported files to the "Unsupported File Format" folder
#                     move_to_unsupported(file_path, unsupported_dir, log_file_path)
#     except Exception as e:
#         stats['errors_encountered'] += 1
#         print(f"Error organizing files: {e}")
#         raise