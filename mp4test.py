import os
import ffmpeg
import piexif
from pymediainfo import MediaInfo

# File path
SOURCE_PATH = r"E:\\GPhotos-Metadatafixer\\2024-10-01-173418557\\AAATotal\\ErrorMP4"

def extract_location_with_ffmpeg(file_path):
    try:
        # Using ffmpeg-python to extract metadata
        probe = ffmpeg.probe(file_path)
        format_info = probe.get('format', {})
        tags = format_info.get('tags', {})
        location = tags.get('location', None)
        return location
    except Exception as e:
        # print(f"FFmpeg error: {e}")
        return None







import ffmpeg

def update_location_in_file(input_file_path, output_file_path, new_lat, new_lon):
    try:
        # Format the location as per ffmpeg requirements (e.g., "+40.2544-74.5766/")
        formatted_location = f"{'+' if new_lat >= 0 else ''}{new_lat}{'-' if new_lon >= 0 else ''}{abs(new_lon)}/"
        
        # Use ffmpeg to update the metadata with the new location
        (
            ffmpeg
            .input(input_file_path)
            .output(output_file_path, 
                    **{'metadata:s:v:0': f'location={formatted_location}'})  # Setting the location tag
            .overwrite_output()  # Overwrite output file if it exists
            .run()
        )
        print(f"Location updated in file: {output_file_path}")
    except Exception as e:
        print(f"Error occurred while updating location: {e}")

# Example usage
input_file_path = "E:/GPhotos-Metadatafixer/2024-10-01-173418557/AAATotal/ErrorMP4/testing/Processed/2024-09-05_22-30-37.mp4"
output_file_path = "E:/GPhotos-Metadatafixer/Updated_Location_2024-09-05_22-30-37.mp4"
new_lat = 40.2544
new_lon = -74.5766

update_location_in_file(input_file_path, output_file_path, new_lat, new_lon)

















def extract_location_with_exiftool(file_path):
    try:
        # Using piexif to extract GPS data
        exif_data = piexif.load(file_path)
        gps_ifd = exif_data.get('GPS', {})

        if gps_ifd:
            lat = gps_ifd.get(piexif.GPSIFD.GPSLatitude)
            lon = gps_ifd.get(piexif.GPSIFD.GPSLongitude)
            alt = gps_ifd.get(piexif.GPSIFD.GPSAltitude)
            return {"latitude": lat, "longitude": lon, "altitude": alt}
        input("OMG 1>>> ")
        return None
    except Exception as e:
        # print(f"Exiftool error: {e}")
        return None

def extract_location_with_pymediainfo(file_path):
    try:
        media_info = MediaInfo.parse(file_path)
        location_data = None
        for track in media_info.tracks:
            if track.track_type == "General" and hasattr(track, 'other_file_name'):
                location_data = track.other_file_name

        # Check for GPS related metadata in other tracks
        if not location_data:
            for track in media_info.tracks:
                if track.track_type == "Video" or track.track_type == "Image":
                    gps_data = {
                        'latitude': getattr(track, 'latitude', None),
                        'longitude': getattr(track, 'longitude', None),
                        'altitude': getattr(track, 'altitude', None)
                    }
                    # input("OMG 2>>> ")
                    if gps_data['latitude'] and gps_data['longitude']:
                        location_data = gps_data
                        input("OMG 3>>> ")
                        break
        return location_data
    except Exception as e:
        # print(f"pymediainfo error: {e}")
        return None

# Main loop to process files
counter = 1
files = sorted(os.listdir(SOURCE_PATH))
for file_name in files:
    file_path = os.path.join(SOURCE_PATH, file_name)

    # If it's a file, attempt to process
    if os.path.isfile(file_path):
        # Print header            
        # print(f"\n\033[92m[{counter}] Name: {file_name}\n--------------------\033[0m")
        counter += 1

        # Extract location using pymediainfo
        location_data = extract_location_with_pymediainfo(file_path)
        ffmpeg_location = extract_location_with_ffmpeg(file_path)
        exif_location = extract_location_with_exiftool(file_path)


        if location_data or ffmpeg_location or exif_location: 
            print(f"\n\033[92m[{counter}] Name: {file_name}\n--------------------\033[0m")
        if location_data: 
            print(f"pymediainfo LOCATION: {location_data}")

        # Extract location using ffmpeg-python
        if ffmpeg_location: 
            print(f"ffmpeg LOCATION: {ffmpeg_location}")

        # Extract location using piexif
        if exif_location: 
            print(f"exiftool LOCATION: {exif_location}")
