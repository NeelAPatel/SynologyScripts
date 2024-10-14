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


Source_folder_path= r"Y:\Neel\Part7_TimelineErrorItems"

Client_folder_path = r"E:\GPhotos-Metadatafixer\2024-10-01-173418557\AAATotal\Part7"

Destination_path =  r"E:\GPhotos-Metadatafixer\2024-10-01-173418557\AAATotal\Part7_ErrorFiles"

# Goal: 
# Scan Y directory, for EACH file in Y directory, find file in Z directory and move it to a seperate folder

def read_file_paths(folder_path):
    
    counter = 0
    #Scan directory
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if os.path.isfile(file_path):
            print(filename)
            counter+=1
            # process_file(file_path, filename)


    print("Total files " + str(counter))
    return 0





def match_and_move(): 
    
    source = []
    client = []

    print("Counting Source...")

    for Source_filename in os.listdir(Source_folder_path):
        file_path = os.path.join(Source_folder_path, Source_filename)

        if os.path.isfile(file_path):
            print("SOURCE: ", Source_filename)
            source.append((file_path, Source_filename))
            
    print("Source Count Complete!")
    print("Counting Client...")

    for Client_filename in os.listdir(Client_folder_path):
        file_path = os.path.join(Client_folder_path, Client_filename)

        if os.path.isfile(file_path):
            print("CLIENT: ", Client_filename)
            client.append((file_path, Client_filename))



    print("Matching paths...")
    # Extract second elements from A
    second_elements_A = {x[1] for x in source}

    # Filter pairs in B where the second element exists in second_elements_A
    result = [pair for pair in client if pair[1] in second_elements_A]

    print(len(source))

    print(len(client))
    # Output the result
    # print(result)
    print(len(result))


    # Ensure the destination directory exists
    if not os.path.exists(Destination_path):
        os.makedirs(Destination_path)

    # Iterate over the list and move each file
    for path, filename in result:
        source_file = path  # Get the full source file path
        destination_file = os.path.join(Destination_path, filename)  # Create the destination path with the same filename
        print()
        print(filename)

        # action = input("What do you want to do? (y = move, s = skip, o = overwrite): ")
        # if action == 'y':
        #     # Move the file to the destination directory
        shutil.move(source_file, destination_file)
        print(f"Moved {source_file} to {destination_file}")


def main(): 
    match_and_move()


if __name__ == "__main__": 
    main()