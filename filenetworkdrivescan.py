import os
print("program start")
# Define the path to your PhotoLibrary folder
path = r"Z:\PhotoLibrary"

# Walk through the directory
for root, dirs, files in os.walk(path):
    for file in files:
        # Print the full path of each file
        print(os.path.join(root, file))



from pathlib import Path

# Define the path to your PhotoLibrary folder
path = Path(r"Z:\PhotoLibrary")

# Walk through the directory
for file_path in path.rglob('*'):
    if file_path.is_file():
        print(file_path)