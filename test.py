print("Hello, bitch.")

# from pymediainfo import MediaInfo

# def get_media_creation_date(filepath):
#     """
#     Extracts the 'Media Created' (creation date) metadata from the media file.
#     """
#     media_info = MediaInfo.parse(filepath)
    
#     # Search for the 'creation_time' or similar date metadata in media tracks
#     for track in media_info.tracks:
#         if track.track_type == "General":  # General track contains creation time
#             # Check if recorded_date (common field for 'Media Created') is present
#             if track.recorded_date:
#                 return track.recorded_date
#             # Some files may use the 'encoded_date' or 'tagged_date' field
#             if track.tagged_date:
#                 return track.tagged_date
#             if track.encoded_date:
#                 return track.encoded_date
#             if track.other_creation_time:
#                 return track.other_creation_time[0]
    
#     return None

# # Example usage
# file_path = r"Z:\PhotoLibrary\2024\09\MVI_4206.MOV"
# creation_date = get_media_creation_date(file_path)

# if creation_date:
#     print(f"Media created date: {creation_date}")
# else:
#     print("Could not retrieve media creation date.")
