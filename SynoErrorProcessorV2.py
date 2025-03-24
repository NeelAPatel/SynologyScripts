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
import shutil
from PIL import Image, ImageFile
from PIL.ExifTags import TAGS
import piexif
import ffmpeg
import struct
from datetime import datetime, timezone
from collections import defaultdict
# Global Vars

LIST_FILE_TYPE = [".jpg", ".png", ".jpeg", ".mp4", ".gif", ".dng", ".webp", ".mov", ".heic"]

LIST_SOURCE_PATH_FOLDERS = [
    # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\White Coat Ceremony _26",
    # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Vicky_s Surprise Sweet Sixteen!",
    r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Untitled",
    r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\SUGA _ AGUST D 4-27",
    r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\SUGA _ AGUST D @ UBS 4-27",
    r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Quotes n Stuff",
    r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Senior 2020",
    r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Six Flags-Delaware Trip!",
    r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Sixteenth Birthday"
    # "E:\Apps"
]


_results = None
_curr_source_path = None
_curr_file_type = None
_curr_processed_path = None
# processed_path = curr_source_path + "\\Processed"
# skipped_path = curr_source_path + "\\Skipped"


# ========= OVERRIDE HELPERS ==========

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


def update_video_location_with_ffmpeg(input_file_path, output_file_path, exif_date_str, new_lat, new_lon):

    try:
        # Convert the latitude and longitude into the correct format
        location_tag = f"+{new_lat:.4f}{new_lon:.4f}/"
        # # Extract the directory and the filename
        # directory, filename = os.path.split(output_file_path)
        # # Prepend 'FFMPEG_' to the filename
        # new_filename = "FFMPEG_" + filename
        # # Combine the directory and the new filename
        # output_file_path = os.path.join(directory, new_filename)


        # Update metadata with the new location using ffmpeg
        ffmpeg.input(input_file_path).output(
            output_file_path,
            **{
                'metadata': f'creation_time={exif_date_str}',
                'metadata:s:v': f'location={location_tag}'  # Embedding location metadata
            },
            vcodec='copy',  # Copy the video stream without re-encoding
            acodec='copy'   # Copy the audio stream without re-encoding
        ).global_args('-hide_banner',  '-loglevel', 'info').run(overwrite_output=True)
        # , 'quiet', '-loglevel'
        
        print(f"File saved with updated ffmpeg location to: {output_file_path}")
    except ffmpeg.Error as e:
        print(f"\033[91mFFmpeg error: {e}\033[0m")


# ========= OVERRIDE VIDEO PROCESSING ===============
def override_video_data(curr_file_path, destinationfilepath, selected_date, selected_location):
    print("---------- Overriding Video Data -------------- ")
    # Convert the selected date to the appropriate format for video metadata
    exif_date_str = selected_date.strftime("%Y-%m-%dT%H:%M:%S")  # ffmpeg uses this format for metadata

    print("GPS Location DEBUG CHECK")
    print(selected_location)
    print(selected_location is None)


    if selected_location: 
        # GPS Data exists
        # Extract latitude and longitude from the selected location
        new_lat = selected_location[0]["latitude"]
        new_lon = selected_location[0]["longitude"]

        try:
            print("3")
            # Using ffmpeg-python to extract metadata
            probe = ffmpeg.probe(curr_file_path)
            format_info = probe.get('format', {})
            tags = format_info.get('tags', {})
            location = tags.get('location', None)
            
        except Exception as e:
            # print(f"FFmpeg error: {e}")
            return None

        print(location)

        update_video_location_with_ffmpeg(curr_file_path, destinationfilepath,exif_date_str,  new_lat, new_lon)

    else: 
        # No GPS data, only do dates

        print(">>>>>>>>> DEBUG <<<<<<<<<<<<<")
        print("FFmpeg module:", ffmpeg)
        print("Current file path:", curr_file_path)
        print("Destination file path:", destinationfilepath)
        print(">>>>>>>>> DEBUG <<<<<<<<<<<<<")

        ffmpeg.input(curr_file_path).output(destinationfilepath,
        **{
            'metadata': f'creation_time={exif_date_str}',  # Set video creation time
        }
        ).global_args('-hide_banner', '-loglevel', 'info', '-y').run()

        print(f"\033[92mVideo metadata updated for {destinationfilepath}\033[0m")
        
    

    if isinstance(selected_date, str):
        new_datetime = datetime.datetime.strptime(selected_date, "%Y:%m:%d %H:%M:%S")
    else:
        new_datetime = selected_date
    
    timestamp = new_datetime.timestamp()

    # Update file system access and modification times
    os.utime(destinationfilepath, (timestamp, timestamp))
    print("---------- Finished Overriding Video Data -------------- ")

# ========= OVERRIDE IMAGE PROCESSING ===============

def override_image_save_resolution(img, exif_dict, selected_date, selected_time, selected_location, dest_media_path, dest_json_path):
    # === Save resolution ====
    try:
        # Attempt to dump the EXIF data first without any correction
        exif_bytes = piexif.dump(exif_dict)
        img.save(dest_media_path, exif=exif_bytes)
        if isinstance(selected_date, str):
            new_datetime = datetime.datetime.strptime(selected_date, "%Y:%m:%d %H:%M:%S")
        else:
            new_datetime = selected_date
        
        timestamp = new_datetime.timestamp()

        # Update file system times
        os.utime(dest_media_path, (timestamp, timestamp))
        print(f"\033[92mOVERRIDE COMPLETE! EXIF data successfully updated for {dest_media_path}\033[0m")
        
        
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
            img.save(dest_media_path, exif=exif_bytes)
            if isinstance(selected_date, str):
                new_datetime = datetime.datetime.strptime(selected_date, "%Y:%m:%d %H:%M:%S")
            else:
                new_datetime = selected_date
            
            timestamp = new_datetime.timestamp()

            print(f"\033[92mOVERRIDE COMPLETE! EXIF data successfully updated for {dest_media_path}\033[0m")
                # Update file system times
            os.utime(dest_media_path, (timestamp, timestamp))
        except struct.error as e:
            print(f"\033[91mERROR: EXIF dump failed after corrections! {e}\033[0m")
            raise  # Let the error propagate and crash if it fails again

def override_image_gps_values(exif_dict, selected_location):
    
    # === OVERRIDE GPS IF NEEDED === 

    # if GPS in exif
        # do nothing
    # if GPS not in exif and GPS in selected
        # add
    # if gps not in exif and GPS not in selected
        # do nothing
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
        

    
    
    if exif_dict['GPS'] and selected_location: 
        print("GPS data found in Photo and JSON  = No Overwrite, checking exactness")
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
        print("GPS data found in JSON Only = Overwring with Matching GPS Data")

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


    return exif_dict

def override_image_date_values(img, exif_dict, selected_date, selected_time): 
    # Seems to only work with jpeg and jpg
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

    # === OVERRIDE DATE ====
    exif_date_str = selected_date.strftime("%Y:%m:%d %H:%M:%S")

    # Update EXIF date values
    exif_dict['0th'][piexif.ImageIFD.DateTime] = exif_date_str
    exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = exif_date_str
    exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = exif_date_str

    
    # print("EXIF data overridden", str(exif_dict))
    print("EXIF data overridden!")
    return img, exif_dict

def override_image_exif_existence(img): 
        # ==== RESOLVE EXIF existence ====
    if 'exif' not in img.info: 
        pwrap("r", "EXIF data not found")
        print("Exif data needs to be created with date time data")
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}, "thumbnail": None}
    else: 
        pwrap("g", "EXIF data exists!")
        exif_dict = piexif.load(img.info['exif'])
    
    return exif_dict

def copy_and_check(source, destination):
    print("---------- Copying Files to Destination -------------- ")
    if source is None: 
        print("No Source value provided to copy")
        print("---------- Copy Files end! -------------- ")
        return
    
    
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
                print(f"{swrap("g", "Copy Successful (Overwrite)!")} : File [{os.path.basename(source)}] --> {destination}")
            else:
                print(f"{swrap("y", "Copy Skipped (Pre-existing)!")} : File [{os.path.basename(source)}]  EXISTS at {destination}")
        else:
            print(f"{swrap("g", "Copy Successful (New File)!")} : File [{os.path.basename(source)}] --> {destination}")
    else:
        print(swrap("r", "Error: File was not copied."))
    print("---------- Copy Files end! -------------- ")

# ========= ACTION PROCESSING =================

def create_destination_paths(action, selected_date,selected_time, selected_location, selected_json_path, file_path): 
    print ("---------- Creating Destination Paths Names -------------")
    print(swrap("under", "Current Media Path: "), file_path)
    print(swrap("under", "Selected Date"), selected_date)
    print(swrap("under", "Location Detection: "), selected_location)
    print(swrap("under", "JSON Path if used: "), selected_json_path)
    
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
    # print("Date handling: ", selected_date , " >> " , clean_date)
    # print("Time handling: ", selected_time , " >> " , clean_time)
    
    # Get Original File Name
    base_filename = os.path.basename(file_path)   
    
    dest_final_media_name = dest_datetime_str + dest_loc_str + base_filename
    dest_final_media_path = os.path.join(_curr_processed_path, dest_final_media_name)
    
    print(swrap("under", "Destination File Name: "), dest_final_media_name)
    print(swrap("under", "Destination File Path: "), dest_final_media_path)
    
    dest_final_json_path = None
    if selected_json_path is not None: 
        base_jsonname = os.path.basename(selected_json_path)
        dest_final_json_name = dest_datetime_str + dest_loc_str + base_jsonname
        dest_final_json_path = os.path.join(_curr_processed_path, dest_final_json_name)
        print(swrap("under", "Destination JSON name: "), dest_final_json_name)
        print(swrap("under", "Destination JSON Path: "), dest_final_json_path)
    else: 
        print("No JSON option was selected")
    
    
    print ("----------  Destination Path created! -------------")
    return dest_final_media_path, dest_final_json_path
    
        
def process_user_action(action:int, curr_media_path:str, date_extractions):
    print("---------- Processing User Selection --------------")
    # Take the User's Selection and determine selected date/json/time/location values
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
    # 1. Create names for destination file name and save path ( based on date, time, location.)
    #     if JSON --> create destination stuff for media AND json
    #     else: --> create destination stuff for media only
    # 2. Check if media is Image or Video
    # 3. process accordingly
        # custom file types need to be handled 
    

    # 1. Create names for destination media and optionally JSON
    dest_media_path, dest_json_path = create_destination_paths(action, selected_date,selected_time, selected_location, selected_json_path, curr_media_path)
    
    # 2. Copy file to new destination
    copy_and_check(curr_media_path, dest_media_path)
    copy_and_check(selected_json_path, dest_json_path)
    
    known_image_extensions = {'.jpeg', '.jpg', '.bmp', '.png', '.cr2', '.webp', '.dng', '.heic'}
    known_video_extensions = {'.mov', '.mp4', '.avi', '.mkv', '.gif'}
    _, curr_ext = os.path.splitext(curr_media_path.lower())
    # if (curr_ext.lower() in known_image_extensions): 
    #     # process as image
    # elise
    
    if curr_ext.lower() in known_image_extensions: 
        # if curr_ext in {'.jpeg', '.jpg', '.bmp', '.png', '.cr2', '.webp', '.dng', '.heic'}: 
            # Open the image and load existing EXIF data
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        img = Image.open(dest_media_path)
        exif_dict = {}
        exif_dict = override_image_exif_existence(img)
        img, exif_dict = override_image_date_values(img, exif_dict, selected_date, selected_time)
        exif_dict = override_image_gps_values(exif_dict, selected_location)
        override_image_save_resolution(img, exif_dict, selected_date, selected_time, selected_location, dest_media_path, dest_json_path)
        # elif curr_ext in {}:
            
        #     return
    elif curr_ext.lower() in known_video_extensions: 
        override_video_data(curr_media_path, dest_media_path, selected_date, selected_location)
        # return
    
    #Update Logs
    _results.add_new_processed_media(curr_media_path,dest_media_path)
    
        

# ========== MENU BUILDING ===============
def parse_json_dategeo_response(data):
    # Parses through JSON data to locate creationTime, photoTakenTime, LocationData and the path of json itself. 
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

        return creationTime, photoTakenTime, locationData, json_path

def show_menuselection_for_current_file(date_extractors: dict): 
    # Generates menu selection of different dates using the dictionary of dates provided
    myIndex = 1
    for key in date_extractors: 
        #JSON related data has to be handled seperately for clarity's sake
        if (key == "JSON - Location Data"  or key == 'JSON - Path'):
            print(swrap("b", f"    {key:<22} : "), swrap("g",f"{date_extractors[key]}") if date_extractors[key] is not None else swrap("r", "None"))
        else: 
            strResponse = date_extractors[key]
            print(swrap("b", f"[{myIndex}] {key:<22} : "), swrap("g", f"{strResponse}") if strResponse is not None else swrap("r", "None"))
            myIndex += 1


def extract_dates_from_file(file_path:str):
    # Using the file path provided, extract all variations of date values that can exist within a file. 
    # JSON Sidecar files from Google Photos are handled seperately, but gives the preferred Photo Taken Time value
    json_response = drf.get_dategeo_from_JSON(file_path)
    
    print(json_response)
    
    
    if json_response is None: 
        creationTime = None 
        photoTakenTime = None
        locationData = None
        json_path = None
    else: 
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
    }, creationTime, photoTakenTime   


def pad_counter_header_integer(total_count: int, index: int):
    # Pads the integer value with prefixed zeros so all the text lines up 
    strCount = ""
    for _ in range(len(str(total_count)) - len(str(index))): 
        # Char Length of denominator value minus length of current value 
        strCount+= "0" 
    strCount += str(index)
    return strCount

def show_header_for_current_file(file_path: str, total_index): 
    # Counter Header: shows count of current file type and count of total files to process in the album
    total_mediacount_of_type = _results.get_total_mediacount_of_currType()
    total_mediacount_of_album = _results.get_total_mediacount_of_currAlbum()
    
    index = _results.get_processed_count_per_extention(file_path) + 1
    
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
    _curr_processed_path = _curr_source_path + "\\XProcessed" + "_" + _curr_file_type.replace(".", "")
    
    #If doesn't exist, create one. 
    if not os.path.exists(_curr_processed_path):
        os.makedirs(_curr_processed_path)
        pwrap("m",f"Folder created: {_curr_processed_path}")

def sort_files_by_extension_and_name(directory):
    # Get the list of files
    files = os.listdir(directory)
    
    # Create a dictionary to group files by their extension
    grouped_files = defaultdict(list)
    
    # Group files by their extension
    for file in files:
        # Split the file name to get the extension (handles files with no extension)
        extension = file.split('.')[-1] if '.' in file else 'no_extension'
        grouped_files[extension].append(file)
    
    # Sort each group alphabetically
    for extension in grouped_files:
        grouped_files[extension].sort()
    
    # Create a sorted list of all files, first by extension, then alphabetically within each extension
    sorted_files = []
    for extension in sorted(grouped_files.keys()):
        sorted_files.extend(grouped_files[extension])
    
    return sorted_files




def process_all_albums(): 
    # Global values to edit in this function scope
    global _results
    global _curr_source_path
    #global _curr_processed_path
    #global _curr_file_type
    automationFlag = False
    # For each folder
    pwrap("reset", "------- PROCESSING ALBUMS STARTED --------------")
    
    # files = os.listdir(source_path)
    # for file in files:
    #     file_path = os.path.join(source_path, file)
    #     if os.path.isfile(file_path):
    
    for source_path in LIST_SOURCE_PATH_FOLDERS: 
        #Global set
        _curr_source_path = source_path # album
        total_album_index = 1
        
        # files = sort_files_by_extension_and_name(_curr_source_path)
        
        # for root, _, files in os.walk(source_path): 
            #For each traversal, 
            
        #Sort all the files
        files = sort_files_by_extension_and_name(_curr_source_path)
        # files = sorted(os.listdir(_curr_source_path))
        # index = 1            
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
                show_header_for_current_file(file_path, total_album_index)
                
                
                while True: 
                    # Header and Menu
                    
                    date_extractions, json_creation_time, json_photo_taken_time = extract_dates_from_file(file_path)
                    show_menuselection_for_current_file(date_extractions)
                    if automationFlag == False: 
                        action = input(swrap("y", "Enter 1-8 to select override date, 'r' to refresh, 'x' to exit: \n >>> "))
                    elif (automationFlag == True and date_extractions['JSON - CreationTime'] is not None):
                        action = '8'
                    
                    indexed_keys = dict(enumerate(date_extractions.keys()))
                    # action = '1' # AUTO LOOPER
                    
                    if action in ['1', '2', '3', '4', '5', '6', '7', '8', 'x', 'r', 'a']:
                        if action == 'a':
                            if (json_creation_time is not None or json_photo_taken_time is not None): 
                                # action = 8
                                action = '8'
                                automationFlag = True
                            else:
                                automationFlag = False
                                action = "r"
                                pwrap("rbg", f"{json_creation_time is not None}: {json_creation_time}")
                                pwrap("rbg", f"{json_photo_taken_time is not None}: {json_photo_taken_time}")
                                pwrap("rbg", f"{(json_creation_time is not None or json_photo_taken_time is not None)}")
                                pwrap("rbg", "ERROR: Could not automate, json flag is None")
                                continue
                            
                            
                        if action == 'x':
                            pwrap("rbg", "Exiting...")
                            automationFlag = False
                            exit(0)
                        elif (date_extractions[indexed_keys[int(action)-1]] is None): 
                            
                            pwrap("rbg", f"Selected Date override [{indexed_keys[int(action)-1]}] is marked as [None].  Refreshing...")
                            automationFlag = False
                            continue  # Restart the loop to refresh the information
                        elif action == 'r':
                            pwrap("cbg", "Refreshing...")
                            # automationFlag = False
                            continue  # Restart the loop to refresh the information
                        else:
                            # Process action based on the user's valid selection
                            process_user_action(int(action), file_path, date_extractions)
                            
                            
                            break
                    else:
                        # Print an error message for invalid input and re-ask the question
                        pwrap("r","Invalid input! Please enter a number between 1-8, 'r' to refresh, 'x'to exit.")
                total_album_index += 1
    pwrap("reset", "------- PROCESSING ALBUMS ENDED --------------")
    return

def scan_all_album_sources():
    print("-------- SCANNING SOURCE PATHS -------------")
    
    full_total = 0 # Count all media detected for the logs
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
        files = os.listdir(source_path)
        for file in files:
            file_path = os.path.join(source_path, file)
            if os.path.isfile(file_path):
                file_ext = os.path.splitext(file)[-1].lower()
                if file_ext in LIST_FILE_TYPE:
                    media_type_aggr[file_ext] += 1
                    total_media_count += 1
        
        # for root, _, files in os.walk(source_path):
        #     for file in files:
        #         file_ext = os.path.splitext(file)[-1].lower()  # Extract file extension
        #         if file_ext in LIST_FILE_TYPE:
        #             media_type_aggr[file_ext] += 1
        #             total_media_count += 1
        # Print results
        print(f"Total count: {total_media_count} -- Type breakdown:", dict(media_type_aggr))
        
        # Add findings to tracker
        _results.add_new_album_for_tracking(source_path, total_media_count, media_type_aggr)
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
    _results.set_list_album_paths_to_process(LIST_SOURCE_PATH_FOLDERS)
    _results.set_list_media_types_to_process(LIST_FILE_TYPE)
    print("--------------SETUP END ---------------\n")
    
    #Overall Procedure: Scan the folders --> Start going through folders and media one by one
    scan_all_album_sources()
    process_all_albums()
    

if __name__ == "__main__": 
    main()