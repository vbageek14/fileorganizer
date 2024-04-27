import os
def identify_live_photos_IOS(root_folder):
    """Traverses through the root folder and identifies duplicate files."""
    livePhotos = {}
    for folder_path, _, file_names in os.walk(root_folder):
        for file_name in file_names:
            file_name_without_extension = os.path.splitext(file_name)[0]
            file_path = os.path.join(folder_path, file_name)
            if file_name_without_extension in livePhotos:
                livePhotos[file_name_without_extension].append(file_path)
            else:
                livePhotos[file_name_without_extension] = [file_path]
    return livePhotos

def delete_live_photo_files(livePhotos):
    live_photo_found = False
    for file_name, file_paths in livePhotos.items():
        if len(file_paths) > 1:
            live_photo_found = True
    if live_photo_found:
        user_input = input("Live photos have been found. Would you like to delete them? (Yes/No): ").strip().lower()
        if user_input == "yes":
            for file_name, file_paths in livePhotos.items():
                if len(file_paths) > 1:
                    print(f"Duplicate files found for '{file_name}':\n{file_paths}\n")
                    for file_path in file_paths:
                        _, file_extension = os.path.splitext(file_path)
                        if file_extension.lower() in [".mov", ".aae"]:
                            os.remove(file_path)
                            print(f"{file_path} has been deleted.")
        elif user_input == "no":
            print("No files were deleted.")
        else:
            print("Invalid input. No files were deleted.")
    else:
        print("No live photos found.")
        
def main():
    root_folder = "/Users/konstimac/Desktop/Iphone 2019-2020"
    livePhotos = identify_live_photos_IOS(root_folder)
    delete_live_photo_files(livePhotos)

if __name__ == "__main__":
    main()