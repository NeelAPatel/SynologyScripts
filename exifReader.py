from PIL import Image
import piexif
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

FILE_TYPE = ".JPG".lower()
SOURCE_PATH = str(r"E:\GPhotos-Metadatafixer\2024-10-01-173418557\AAATotal\Error" + FILE_TYPE.replace('.', "")+ "\\bleh")

PROCESSED_PATH = SOURCE_PATH + "\\Processed"
SKIPPED_PATH = SOURCE_PATH + "\\Skipped"


def get_gps_coordinates(exif_data):
    """Helper function to extract GPS coordinates if they exist in the EXIF data."""
    for x in exif_data: 
        print(x, exif_data.get(x))


    gps_info = exif_data.get('GPS', None)
    
    if not gps_info:
        return None
    
    def convert_rational_to_degrees(rational):
        """Converts the rational GPS coordinates into degrees."""
        d = rational[0][0] / rational[0][1]
        m = rational[1][0] / rational[1][1]
        s = rational[2][0] / rational[2][1]
        return d + (m / 60.0) + (s / 3600.0)

    # Extract latitude and longitude data
    lat = convert_rational_to_degrees(gps_info[piexif.GPSIFD.GPSLatitude])
    lon = convert_rational_to_degrees(gps_info[piexif.GPSIFD.GPSLongitude])

    # Adjust for N/S and E/W directions
    lat_ref = gps_info[piexif.GPSIFD.GPSLatitudeRef].decode('utf-8')
    lon_ref = gps_info[piexif.GPSIFD.GPSLongitudeRef].decode('utf-8')
    
    if lat_ref == 'S':
        lat = -lat
    if lon_ref == 'W':
        lon = -lon
    
    return lat, lon




# 43.6532° N, 79.3832° W
# + and -
def processfile(): 
    # Load the image and extract the EXIF data
    image_path = r"E:\GPhotos-Metadatafixer\2024-10-01-173418557\AAATotal\ErrorJPG\bleh\FDM with love me lift up tray.jpg"
    img = Image.open(image_path)
    exif_data = piexif.load(img.info.get('exif', {}))

    # Get the GPS coordinates
    gps_coordinates = get_gps_coordinates(exif_data)

    if gps_coordinates:
        print(f"Latitude: {gps_coordinates[0]}, Longitude: {gps_coordinates[1]}")
    else:
        print("No GPS data found in the EXIF.")

def main(): 

    processfile()

if __name__ == "__main__": 
    main()