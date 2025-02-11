# result_dict = {
#     "list_album_paths_to_process":  [], # Full Paths to process
#     "list_media_types_to_process" : [], # store list of file types being processed at this time
#     "logger_output_file_name": "output_results.json"
#     "total_mediacount_process" = 0
#     "current_processing_file": None
#     "progres_tracker":  
#         # each folder will have its own object here
#         {
            
#             "<folder_name>": 
#                 {
#                     "folder_path": "", 
#                     "total_media_count": 0,
#                     "detected_media_count": {
#                         "<type>": {
#                             "total_count": 0,
#                             "processed_count": 0,
#                             "last_processed_path": None,
#                             "processed_source_paths" :  [],
#                             "processed_destination_paths" :  [],
#                             "errors_source_paths" :  [],                              
#                         }
#                     }
#                 }, 
#         },   
# }





from datetime import datetime
import json
import os

class ProcessLogger:
    
    def __init__(self, output_file_name="processing_results.json"):
        
        #General 
        self.list_album_paths_to_process = []  # Full Paths to process
        self.list_media_types_to_process = []  # Store list of file types being processed at this time
        # self.processing_start_time = None  # Timestamp of when processing starts
        # self.processing_end_time = None
        self.logger_output_file_name = output_file_name  # File to persist results
        self.total_mediacount_process = 0
        # Tracking
        self.current_processing_file = None  # Track the file currently being processed
        self.progress_tracker = {}  # Dictionary indexed by folder path for fast lookup

    # def start_processing(self):
    #     self.processing_start_time = datetime.utcnow()
    #     self.save_results()

    # def end_processing(self):
    #     self.processing_end_time = datetime.utcnow()
    #     self.save_results()

    def set_total_paths(self, list_source_path_folders: list):
        """Sets a list of total paths that will be processed in this execution of the program by appending a valid list of paths to the list, and if a directory is incorrect, raises an error

        Args:
            list_source_path_folders (list): List of the album folders

        Raises:
            FileNotFoundError: raised if given directory is non-existent 
        """        
        for full_folder_path in list_source_path_folders:
            # Check if directory exists
            if os.path.isdir(full_folder_path):  
                self.list_album_paths_to_process.append(full_folder_path)
                
            else:
                raise FileNotFoundError(f"Directory does not exist: {full_folder_path}")
            
        self.save_results()

    def set_total_file_types(self, file_type_list: list):
        # Copy list into self.file_types_to_process
        self.list_media_types_to_process = list(set(file_type_list))
        self.save_results()


    
    def add_album_to_tracking(self, folder_path:str, total_count: int, media_count: dict):
        if folder_path not in self.progress_tracker: 
            
            detected_dict = {}
            
            for key in media_count: 
                detected_dict[key] = {
                        "total_count": media_count[key],
                        "processed_count": 0,
                        "last_processed_path": None,
                        "processed_source_paths" :  [],
                        "processed_destination_paths" :  [],
                        "errors_source_paths" :  [], 
                    }            
            
            self.progress_tracker[os.path.basename(folder_path)] = {
                "folder_path": folder_path,
                "total_media_count": total_count,
                "detected_media_count": detected_dict
            }
        self.save_results()
    
    def set_current_processing_file(self, filepath): 
        # base_filename = os.path.basename(filepath)
        # path_to_directory = os.path.dirname(filepath)
        # base_dirname = os.path.basename(path_to_directory)
        
        self.progress_tracker['current_processing_file'] = filepath
        self.save_results()
    
    def set_total_mediacount_process(self, full_total): 
        self.total_mediacount_process = full_total
        self.save_results()
    
    def get_current_processing_file(self):
        return self.progress_tracker['current_processing_file']


    def get_total_mediacount_of_currAlbum(self): 
        
        file_path = self.progress_tracker['current_processing_file']
        #base_filename = os.path.basename(file_path)
        path_to_directory = os.path.dirname(file_path)
        base_dirname = os.path.basename(path_to_directory)
        return self.progress_tracker[base_dirname]['total_media_count']
    
    def get_total_mediacount_of_currType(self): 
        file_path = self.progress_tracker['current_processing_file']
        #base_filename = os.path.basename(file_path)
        path_to_directory = os.path.dirname(file_path)
        base_dirname = os.path.basename(path_to_directory)
        file_ext = os.path.splitext(file_path)[-1].lower()
        return self.progress_tracker[base_dirname]['detected_media_count'][file_ext]['total_count']
        
    def get_total_mediacount_of_process(self):
        return self.total_mediacount_process
        
    
    # def add_folder_to_process(self, folder_path: str):
    #     if folder_path not in self.progress_tracker:
    #         self.progress_tracker[folder_path] = {
    #             "folder_name": "",
    #             "total_media_count": ,
    #             "detected_media_count": {},
    #             "current_processing_file": None
    #         }
    #     self.save_results()

    # def add_file_progress(self, folder_path: str, file_type: str):
    #     if folder_path in self.progress_tracker:
    #         if file_type not in self.progress_tracker[folder_path]["detected_media_count"]:
    #             self.progress_tracker[folder_path]["detected_media_count"][file_type] = {
    #                 "processed_count": 0,
    #                 "current_processing_file_path": None,
    #                 "processed_source_paths": [],
    #                 "processed_destination_paths": [],
    #                 "errors_source_paths": []
    #             }
    #     self.save_results()

    # def update_current_processing_file(self, folder_path: str, file_type: str, file_path: str):
    #     if folder_path in self.progress_tracker and file_type in self.progress_tracker[folder_path]["detected_media_count"]:
    #         self.progress_tracker[folder_path]["detected_media_count"][file_type]["current_processing_file_path"] = file_path
    #         self.current_processing_file = file_path
    #         self.save_results()

    # def finalize_processed_file(self, folder_path: str, file_type: str, source_path: str, dest_path: str):
    #     if folder_path in self.progress_tracker and file_type in self.progress_tracker[folder_path]["detected_media_count"]:
    #         file_data = self.progress_tracker[folder_path]["detected_media_count"][file_type]
    #         file_data["processed_count"] += 1
    #         file_data["processed_source_paths"].append(source_path)
    #         file_data["processed_destination_paths"].append(dest_path)
    #         file_data["current_processing_file_path"] = None
    #         self.current_processing_file = None
    #         self.save_results()

    def save_results(self):
        # return
        with open(self.logger_output_file_name, "w") as f:
            json.dump(self.summary(), f, indent=4, default=str)

    def summary(self):
        return {
            "list_album_paths_to_process": self.list_album_paths_to_process,
            "list_media_types_to_process": self.list_media_types_to_process,
            "logger_output_file_name": self.logger_output_file_name,
            "total_mediacount_process": self.total_mediacount_process,
            "current_processing_file": self.current_processing_file,
            "progress_tracker": self.progress_tracker,
        }
        

    def print_summary(self):
        print(json.dumps(self.summary(), indent=4, default=str))

    
    def get_total_paths_to_process(self): 
        return self.list_album_paths_to_process
    def get_total_file_types_to_process(self): 
        return self.list_media_types_to_process
    def get_processing_start_time(self): 
        return self.processing_start_time
    def get_processing_end_time(self): 
        return self.processing_end_time
    def get_progress_results_file_name(self): 
        return self.logger_output_file_name
    def get_progress_tracker(self): 
        return self.progress_tracker