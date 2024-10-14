import os
from collections import defaultdict

photo_dir = r'F:\GPhotos\Takeout'
photo_dir = r'E:\GPhotos-Metadatafixer\2024-09-27-150026315'
photo_dir = r'E:\GPhotos-Metadatafixer\2024-10-01-173418557'
# photo_dir = r'E:\GPhotos-Metadatafixer\2024-09-27-150026315\Completed'
# photo_dir = r'E:\GPhotos-Metadatafixer\2024-09-27-150026315\Errors'
# photo_dir = r'E:\GPhotos-Metadatafixer\2024-09-27-150026315\Files with identical names'
# photo_dir = r'F:\GPhotos\Takeout'

def traverse_and_count_files(directory):
    file_count = defaultdict(int)
    file_paths = defaultdict(list)

    for root, _, files in os.walk(directory):
        for file in files:
            file_extension = os.path.splitext(file)[1].lower()
            file_path = os.path.join(root, file)
            file_count[file_extension] += 1
            file_paths[file_extension].append(file_path)

    return file_count, file_paths

def write_logs(file_paths, log_folder):
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    # Prepare the summary log file and clear its content at the beginning
    summary_log_file_name = "SUMMARY-files.log"
    summary_log_file_path = os.path.join(log_folder, summary_log_file_name)

    with open(summary_log_file_path, 'w') as summary_file:
        summary_file.write("Summary of file types and paths logged:\n")
    
    # Iterate through file types and write logs
    for file_type, paths in file_paths.items():
        log_file_name = f"{file_type[1:] if file_type else 'no_extension'}-files.log"
        log_file_path = os.path.join(log_folder, log_file_name)

        with open(log_file_path, 'w') as log_file:
            for path in paths:
                log_file.write(path + '\n')

        # Append summary information to the summary log file
        with open(summary_log_file_path, 'a') as summary_file:
            summary_file.write(f"Written {len(paths)} paths to {log_file_path}\n")

        print(f"Written {len(paths)} paths to {log_file_path}")



def main():
    directory = photo_dir

    # Create log folder name by replacing backslashes with dashes
    log_folder_name = photo_dir.replace("\\", "-")
    log_folder_name = log_folder_name.replace(":", "-")
    
    # Get file counts and paths
    file_count, file_paths = traverse_and_count_files(directory)

    # Print the counts
    for file_type, count in file_count.items():
        print(f"{file_type}: {count} file(s)")

    total_files = sum(file_count.values())
    print(f"Total files: {total_files}")

    # Write logs to the log folder
    write_logs(file_paths, log_folder_name)

if __name__ == "__main__":
    main()