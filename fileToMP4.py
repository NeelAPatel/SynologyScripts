import os
from datetime import datetime
import subprocess

def get_file_metadata(input_file_path):
    """
    Reads and prints out all date-related metadata from a .TOD file using ffmpeg's ffprobe.

    Parameters:
        input_file_path (str): The path to the input .TOD file.
    """
    try:
        metadata = subprocess.check_output(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format_tags",
                "-of", "default=noprint_wrappers=1:nokey=0",
                input_file_path
            ]
        ).decode("utf-8")
        
        print("Date-related metadata found:")
        for line in metadata.splitlines():
            if "date" in line.lower() or "time" in line.lower():
                print(line)
    except subprocess.CalledProcessError as e:
        print(f"Error reading metadata: {e}")

def convert_tod_to_mp4_with_modified_date(input_file_path, output_file_path):
    last_modified_time = datetime.fromtimestamp(os.path.getmtime(input_file_path)).isoformat()
    print(f"\nLast modified date of input file: {last_modified_time}")

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-i", input_file_path,
                "-map_metadata", "0",
                "-c:v", "copy",
                "-c:a", "copy",
                "-metadata", f"creation_time={last_modified_time}",
                output_file_path
            ],
            check=True
        )
        print(f"Conversion complete. Output file created at: {output_file_path}")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred during conversion: {e}")

def batch_convert_tod_to_mp4_with_date_prefix(directory_path):
    """
    Loops through all .TOD files in a directory, converts each to .MP4, and adds the last modified
    date as a prefix in the output filename.

    Parameters:
        directory_path (str): Path to the directory containing .TOD files.
    """
    for filename in os.listdir(directory_path):
        if filename.lower().endswith(".tod"):
            input_file_path = os.path.join(directory_path, filename)
            
            # Get last modified date and format as YYYYMMDD
            last_modified_time = datetime.fromtimestamp(os.path.getmtime(input_file_path)).strftime("%Y%m%d")
            output_filename = f"{last_modified_time}-{filename.rsplit('.', 1)[0]}.mp4"
            output_file_path = os.path.join(directory_path, output_filename)
            
            print(f"Converting '{filename}' to '{output_filename}'...")
            convert_tod_to_mp4_with_modified_date(input_file_path, output_file_path)

# Example usage
batch_convert_tod_to_mp4_with_date_prefix("F:\\MoviesFolderFromMac - Copy\\New folder (3)")
