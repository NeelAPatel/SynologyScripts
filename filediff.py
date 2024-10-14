# Sample lists of file paths
list_1 = [
    'E:\LocalProj\SynologyScripts\F--GPhotos-Takeout\jpg-files.log'
]

list_2 = [
    'E:\LocalProj\SynologyScripts\E--GPhotos-Metadatafixer-2024-09-27-150026315\jpg-files.log'
]

# Normalize the file names by extracting the file name from the full path
files_in_list_1 = {file.split('/')[-1] for file in list_1}
files_in_list_2 = {file.split('/')[-1] for file in list_2}

# Find the missing file
missing_files = files_in_list_1 - files_in_list_2

if missing_files:
    print("Missing file(s):", missing_files)
else:
    print("No missing files found!")