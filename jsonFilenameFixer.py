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
import logging
import subprocess
import datetime
import os
from pathlib import Path

import difflib  # <-- ADD THIS at the top

import os
import re

# Define your media extensions here
MEDIA_EXTENSIONS = {".jpg", ".png", ".jpeg", ".mp4", ".gif", ".dng", ".webp", ".mov", ".heic", '.mp3', '.wav', '.avi', '.mkv'}

def is_simple_json(filename):
    """
    Check if the file ends with .json and does NOT follow the pattern *.ext.json
    """
    if filename.endswith('.json'): 
        if not re.match(r'.+\.[^.]+\.(json)$', filename): 
            # # print("File: ", filename)
            # # print("Renaming this")
            return True
        else: 
            return False
    else: 
        return False
    
    # return filename.endswith('.json') and not re.match(r'.+\.[^.]+\.(json)$', filename)

def find_matching_media(basename, files):
    """
    Given a basename (e.g., 'abc'), find a matching media file in the list of files.
    """
    # Strategy 1: Normal "starts with" matching
    for file in files:
        name, ext = os.path.splitext(file)
        if name.startswith(basename) and ext.lower() in MEDIA_EXTENSIONS:
            return file
    
    
    # # Strategy 2: Handle misformatted names like abc.mp4(1).json
    # # # print(basename)
    # misplaced_copy = re.match(r"^(.*)\.([a-z]{2,4})\((\d+)\)$", basename)
    # if misplaced_copy:
    #     # # print("something matched", basename)
    #     base_part, ext_candidate, copy_number = misplaced_copy.groups()
    #     corrected_ext = f".{ext_candidate}"
    #     if corrected_ext == ".jp":
    #         corrected_ext = ".jpg"
    #     if corrected_ext in MEDIA_EXTENSIONS:
    #         # Now look for a media file that ends with the correct ext
    #         for file in files:
    #             name, ext = os.path.splitext(file)
    #             if ext.lower() != corrected_ext:
    #                 continue
    #             if f"({copy_number})" not in name:
    #                 continue
    #             # Use difflib to match base_part loosely against name
    #             similarity = difflib.SequenceMatcher(None, base_part, name).ratio()
    #             if similarity > 0.8:
    #                 return file
    
    # # Existing fix: .jp(1).json → .jpg
    # pattern = re.match(r'^(.*)\.([a-z]{2,4})(\(\d+\))$', basename)
    # if pattern:
    #     base, wrong_ext, copy_suffix = pattern.groups()
    #     corrected_ext = f".{wrong_ext}"
    #     if corrected_ext == ".jp":
    #         corrected_ext = ".jpg"  # Specific correction for jp → jpg
    #     if corrected_ext in MEDIA_EXTENSIONS:
    #         corrected_name = f"{base}{copy_suffix}{corrected_ext}"
    #         if corrected_name in files:
    #             return corrected_name

    return None
def find_matching_media_for_misnamed_copy_json(basename, media_files):
    """
    Handles .ext(n).json files by looking for media that ends in (n).<ext>
    and starts with a similar prefix.
    """
    import difflib
    pattern = re.match(r"^(.*)\.([a-z]{2,4})\((\d+)\)$", basename)
    if pattern:
        base, ext_candidate, copy_number = pattern.groups()
        corrected_ext = f".{ext_candidate}"
        if corrected_ext == ".jp":
            corrected_ext = ".jpg"
        if corrected_ext not in MEDIA_EXTENSIONS:
            return None

        for file in media_files:
            name, ext = os.path.splitext(file)
            if ext.lower() != corrected_ext:
                continue
            if f"({copy_number})" not in name:
                continue
            # Fuzzy prefix match
            similarity = difflib.SequenceMatcher(None, base, name).ratio()
            if similarity > 0.8:
                return file
    return None

def is_naming_order_mismatched(filename):
    """
    Returns True for things like: file.mp4(1).json — where (1) should be part of filename, not extension.
    """
    if not filename.endswith('.json'):
        return False

    base = filename[:-5]  # strip .json
    # Match *.ext(n)
    pattern = re.match(r'^(.+)\.([a-z]{2,4})\(\d+\)$', base)
    if pattern:
        _, ext_candidate = pattern.groups()
        corrected_ext = f".{ext_candidate}"
        if corrected_ext == ".jp":
            corrected_ext = ".jpg"
        return corrected_ext in MEDIA_EXTENSIONS
    return False
def find_matching_media_for_partial_extension_json(basename, media_files):
    """
    Fixes files like photo.j.json, photo.jp.json, photo.mp.json
    by finding a real file like photo.jpg, photo.mp4, etc.
    """
    pattern = re.match(r"^(.*)\.([a-z]{1,3})$", basename)
    if not pattern:
        return None

    base, partial_ext = pattern.groups()
    for ext in MEDIA_EXTENSIONS:
        if ext[1:].startswith(partial_ext):  # match "j" to "jpg", etc.
            candidate_filename = f"{base}{ext}"
            if candidate_filename in media_files:
                return candidate_filename
    return None

def is_partial_extension_json(filename):
    """
    Detects malformed files like photo.j.json or video.mp.json
    """
    if not filename.endswith('.json'):
        return False

    base = filename[:-5]  # remove ".json"
    pattern = re.match(r"^(.*)\.([a-z]{1,3})$", base)
    if pattern:
        _, partial_ext = pattern.groups()
        # Manually check if adding a char makes it match a valid extension
        for ext in MEDIA_EXTENSIONS:
            if ext[1:].startswith(partial_ext):  # Remove leading dot
                return True
    return False

def rename_json_files_in_folders(folders):
    for folder_path in folders:
        print(f"\n--- Scanning folder: {folder_path} ---")
        if not os.path.isdir(folder_path):
            # print(f"Skipped (not a directory): {folder_path}")
            continue
    
        all_files = os.listdir(folder_path)
        for file in all_files:
            # # print("File: ", file)
            match = False
            match1 = False
            match2 = False
            if is_simple_json(file):
                base = file[:-5]  # strip '.json'
                match = find_matching_media(base, all_files)
                # if match:
                #     # print("\nMatch Found", file, " == ", match)
                #     new_json_name = f"{match}.json"
                #     src = os.path.join(folder_path, file)
                #     dst = os.path.join(folder_path, new_json_name)
                #     # print(f"Renaming: {file} -> {new_json_name}")
                #     # input("BREAKER")
                #     os.rename(src, dst)
            elif is_naming_order_mismatched(file):
                base = file[:-5]
                match1 = find_matching_media_for_misnamed_copy_json(base, all_files)
            elif is_partial_extension_json(file):  # ✅ NEW CONDITION
                base = file[:-5]
                match2 = find_matching_media_for_partial_extension_json(base, all_files)
            else:
                continue
            
            if match:
                print("\nMatch Found", file, "==", match)
                new_json_name = f"{match}.json"
                src = os.path.join(folder_path, file)
                dst = os.path.join(folder_path, new_json_name)
                print(f"Renaming: {file} -> {new_json_name}")
                os.rename(src, dst)
            if match1:
                print("\nMatch1 Found", file, "==", match1)
                new_json_name = f"{match1}.json"
                src = os.path.join(folder_path, file)
                dst = os.path.join(folder_path, new_json_name)
                print(f"Renaming: {file} -> {new_json_name}")
                os.rename(src, dst)
            if match2:
                new_json_name = f"{match2}.json"
                src = os.path.join(folder_path, file)
                dst = os.path.join(folder_path, new_json_name)
                if os.path.abspath(src) == os.path.abspath(dst):
                    continue  # 🔥 Skip renaming to the same file
                print("\nMatch2 Found", file, "==", match2)
                print(f"Renaming: {file} -> {new_json_name}")
                os.rename(src, dst)

if __name__ == "__main__":

    folder_paths = [
        r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Pavan_s Engagement",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Neel_s 22 Birthday",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\New York Trip",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Nidhi, A",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Old Photos",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Pavan Weds Dimple!",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Pavan_s Engagement",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\MIT Splash",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Navratri Garba HSN",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Formal-Point Pleasant Beach",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Freshmen Selfies",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Garba Gals",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Homecoming Week",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\India Trip-Wedding",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\JProm",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Lettering",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Line Deco-wallpapers",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Manan weds Mansi- Ohio Trip",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Medieval Times- Aansh_s Birthday Party",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\2020 Graduation - HSS",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Archive",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Arunima_s Sweet at Brio",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\ASHP Midyear 23 - Anaheim, CA",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Baby Shower",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\BU",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Bulletproof",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Canada 2019",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Canada 2022",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Canada Trip",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Delaware Trip",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Dhruval & Laura_s Wedding",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Drawings!",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\EMSOP YEARS",
        # r"F:\GPhotos Takeout - Nidhi - Dec31\Takeout\Google Photos - Copy\NEEDSFIXING\Florida Trip_ Urvesh Mama_s Wedding",
        # Add more folders here if needed
    ]
    rename_json_files_in_folders(folder_paths)