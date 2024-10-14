
import os



# Paths to the directories using the mapped drives
synology_photo_path = r'Y:\PhotoLibrary'
ssd_photo_path = r'H:\MergedLibExport-PowerPhotos\DONE'

# List to store files missing from Synology Photo Path
missing_files = []



# def get_all_files(group, directory):
#     """Traverse directory and return a set of relative file paths."""
#     # file_set = set()
#     # for root, _, files in os.walk(directory):
#     #     for file in files:
#     #         # Store the relative file path
#     #         relative_path = os.path.relpath(os.path.join(root, file), directory)
#     #         file_set.add(relative_path)
#     #         print(str(group) + "adding relative path" + str(relative_path))
#     # return file_set



#     file_set = set()
#     for root, _, files in os.walk(directory):
#         for file in files:
#             # Only store the file name, not the full path
#             file_set.add(file)
#             relative_path = os.path.relpath(os.path.join(root, file), directory)
#             print(str(group) + "adding file" + str(file))
#     return file_set

print("Program start")










def get_file_info(group, directory):
    """
    Traverse directory and return a set of tuples containing file info.
    The tuple will include: (file_name, file_size, last_modified_time)
    """
    file_info_set = set()
    for root, _, files in os.walk(directory):
        current_subdirectory = os.path.relpath(root, directory)
        print(f"Traversing: {current_subdirectory}")
        for file in files:
            full_path = os.path.join(root, file)
            file_size = os.path.getsize(full_path)  # Get file size in bytes
            last_modified_time = os.path.getmtime(full_path)  # Get last modified time in seconds
            # Store file info as (file_name, file_size, last_modified_time)
            file_info_set.add((file, file_size))
            # print(str(group) + "adding fileset " + str((file, file_size, last_modified_time)))
    return file_info_set

# Get all file info (name, size, last modified) from both directories
synology_files = get_file_info("syno: ",synology_photo_path)
print("NUM OF SYNO FILES: " + str(len(synology_files)))
ssd_files = get_file_info("ssd:  ", ssd_photo_path)
print("NUM OF SSD FILES: " + str(len(ssd_files)))

# Find files that are in SSD Photo Path but not in Synology Photo Path (by file name, size, and last modified date)
for file_info in ssd_files:
    if file_info not in synology_files:
        missing_files.append(file_info)

# Output the result
print(f"Files missing from {synology_photo_path}:")
for file in missing_files:
    file_name, file_size, last_modified_time = file
    print(f"File: {file_name}, Size: {file_size} bytes, Last Modified: {last_modified_time}")

# Optionally, save the result to a text file
with open('missing_files_by_info.txt', 'w') as f:

    f.write("NUM OF SYNO FILES: " + str(len(synology_files)))
    f.write("NUM OF SSD FILES: " + str(len(ssd_files)))
    for file in missing_files:
        file_name, file_size, last_modified_time = file
        f.write(f"File: {file_name}, Size: {file_size} bytes, Last Modified: {last_modified_time}\n")

print(f"Total missing files: {len(missing_files)}")