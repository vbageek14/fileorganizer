import argparse
import os
import subprocess
import shutil
import datetime
import filetype
import hashlib

def is_media_file(file):
    if os.path.exists(file):
        file_type = filetype.guess(file)
        media_extensions = ("jpg", "jpeg", "png", "gif", "bmp",
                            "tif", "tiff", "webp", "heif", "heic",
                            "svg", "mp4", "mov", "avi", "wmv", "flv",
                            "mkv", "webm", "mpg", "mpeg", "3gp")
        if file_type is not None and file_type.extension in media_extensions:
            return True
        return False

def get_exif_create_date_and_extension(filepath, print_output = True):
    '''
    Extracts the creation date of a file using exiftool.

    Args:
        filepath (str): The path to the file.
        
    Returns:
        str: The creation date of the file, or None if no EXIF metadata exists or an error occurs.

    '''
    try:
        result = subprocess.run(['exiftool', '-CreateDate', '-mimetype', filepath], capture_output=True, text=True)
        if result.returncode == 0:

            # Split the output by newlines to separate creation date and file extension
            output_lines = result.stdout.strip().split('\n')
            
            if output_lines:
                create_date = None
                file_extension = None

                # Loop through each line to find creation date and file extension
                for line in output_lines:
                    if line.startswith("Create Date"):
                        create_date = line.strip().split(': ')[-1]
                    elif line.startswith("MIME Type"):
                        file_extension = line.strip().split(': ')[1].split("/")[1]
                        if file_extension == "quicktime":
                            file_extension = "mov"
                
                # Check if both creation date and file extension exist
                if create_date and file_extension:
                    return create_date, file_extension
                elif create_date and not file_extension:
                    return create_date
                elif file_extension and not create_date:
                    return file_extension
                else:
                    if print_output:
                        print("No EXIF metadata exists")
                    return None
            else:
                if print_output:
                    print("No output received from exiftool")
                return None
        else:
            if print_output:
                print("Error running exiftool")
            return None
        
    except Exception as e:
        print("An error occurred:", e)
        return None


def extract_year_from_file(file):
    '''
    Extracts the year from the file name.

    Args:
        file (str): The file name.
    Returns:
        str: The year extracted from the file name.
    '''
    year = str(file)[:4]
    if year != "0000":
        return year
    else:
        return None

def extract_month_from_file(file):
    month_num = str(file)[5:7]
    if month_num != "00":
        datetime_object = datetime.datetime.strptime(month_num, "%m")
        month_name = datetime_object.strftime("%b")
        return month_name
    else:
        return None
    
def delete_empty_folders(root, created_folders):
    """
    Delete empty folders within the specified root directory, excluding those listed in the set of created folders.

    Args:
        root (str): The root directory to start deleting empty folders from.
        created_folders (set): A set containing names of folders created during the process.
    """

    # Iterate over directories in the root directory
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        # Exclude directories that are in the created_folders set
        dirnames[:] = [dirname for dirname in dirnames if dirname not in created_folders]
        for dirname in dirnames:
            full_path = os.path.join(dirpath, dirname)
            # Check if the directory is empty and if so, delete it
            if not os.listdir(full_path): 
                print(f"Deleting folder {dirname}\n")
                os.rmdir(full_path)
            else:
                print(f"Could not delete the folder {dirname} as it is not empty.\n")
                try:
                    user_input = input("If you still would like to proceed, enter 'Yes' to force delete. Enter any other key to cancel: \n").strip().lower()
                    if user_input == "yes":
                        print(f"Full Path: {full_path}")
                        print(f"Deleting folder {dirname}")
                        # Force delete the folder and its contents
                        shutil.rmtree(full_path)
                    else:
                        print("Folder was not deleted")
                except Exception as e:
                    print(f"An error occurred while trying to delete the folder: {e}")

def categorize_files(file, args, created_folders):

    """
    Categorize the file into folders based on its creation year, or move it to an 'Uncategorized' folder if creation date metadata is not available.

    Args:
        file (str): The path to the file being categorized.
        args: Arguments parsed from the command line.
        created_folders (set): A set containing names of folders created during the process.

    Returns:
        set: Updated set of created folders after categorization.

    """

    format  = args.format

    # Extract creation date metadata from the file
    file_data = get_exif_create_date_and_extension(file)

    if file_data is not None:
        file_date = None
        file_extension = None

        if isinstance(file_data, tuple):
            file_date, file_extension = file_data

        elif isinstance(file_data, str):
            if ":" in file_data:
                file_date = file_data
    
        if file_date:
            if format == "year":
                # If creation date exists, determine the directory name based on the year
                if extract_year_from_file(str(file_date)):
                    directory_name = "/".join([args.target,str(extract_year_from_file(str(file_date)))])
                else:
                    directory_name = "/".join([args.target,"Uncategorized"])
            elif format == "year-month":
                if extract_month_from_file(str(file_date)):
                    directory_name = "/".join([args.target,str(extract_year_from_file(str(file_date))), str(extract_month_from_file(str(file_date)))])
                else:
                    directory_name = "/".join([args.target,"Uncategorized"])
            
            final_path = os.path.join(directory_name, file.split("/")[-1])
            
        else:
            # If no creation date metadata exists, move the file to the 'Uncategorized' folder
            directory_name = "/".join([args.target,"Uncategorized"])
            final_path = os.path.join(directory_name,file.split("/")[-1])
    else:
        # If no creation date metadata exists, move the file to the 'Uncategorized' folder
        directory_name = "/".join([args.target,"Uncategorized"])
        final_path = os.path.join(directory_name,file.split("/")[-1])

    if os.path.exists(directory_name) is False:
        # Create the directory if it doesn't exist and update created_folders set
        os.makedirs(directory_name, exist_ok=True)
        components = directory_name.split("/")
        for component in components:
            created_folders.add(component)
        print("Folder " + directory_name + " created.")

    if os.path.exists(final_path) is False:
         # Move the file to the final path or skip if it already exists
        print("Moving " + file + " to " + final_path)
        os.rename(file, final_path)
    else:
        print("Skipped " + file + ", already exists in " + directory_name)
    return created_folders

def calculate_file_hash(file_path):
    """Calculates the hash value of a file's content."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def find_duplicate_files(root_folder):
    """Traverses through the root folder and identifies duplicate files."""
    duplicates = {}
    for folder_path, _, file_names in os.walk(root_folder):
        for file_name in file_names:
            file_path = os.path.join(folder_path, file_name)
            file_hash = calculate_file_hash(file_path)
            if file_hash in duplicates:
                duplicates[file_hash].append(file_path)
            else:
                duplicates[file_hash] = [file_path]
    return duplicates

def find_and_fix_file_extension_mismatches(root_folder):
    extension_mismatches_found = False

    for folder_path, _, file_names in os.walk(root_folder):
        for file_name in file_names:
            file_path = os.path.join(folder_path, file_name)
            file_name_extension = file_name.strip().split(".")[1].upper()
            if file_name_extension == "JPG":
                file_name_extension = "JPEG"
            exif_data = get_exif_create_date_and_extension(file_path, print_output = False)

            if exif_data is not None:
                if isinstance(exif_data, tuple):
                    _, file_exif_extension = exif_data
                    
                elif isinstance(exif_data, str):
                    if ":" not in exif_data:
                        file_exif_extension = exif_data
                
                if file_name_extension != file_exif_extension.upper():
                    if not extension_mismatches_found:
                        extension_mismatches_found = True
                        user_input = input("File(s) with extension mismatches have been identified. Would you like to correct them? (Yes/No): \n").strip().lower()
                        if user_input == "no":
                            print("No files were deleted.\n")
                        elif user_input != "yes":
                            print("Invalid input. No files were deleted.\n")
                    file_name_without_extension = os.path.splitext(file_name)[0]
                    final_path = os.path.join(folder_path, file_name_without_extension) + "." + file_exif_extension.upper()
                    try:
                        # Rename the file
                        os.rename(file_path, final_path)
                        print(f"Renamed: {file_path} -> {final_path}\n")
                    except Exception as e:
                        print(f"Error renaming {file_path}: {e}")

    if not extension_mismatches_found:
        print("No file(s) with extension mismatches were found.")
    

def remove_duplicate_files(duplicates, root_folder):
    """Removes duplicate files from the file system."""

    show_duplicates = False
    duplicates_found = False

    for file_paths in duplicates.values():
        if len(file_paths) > 1:
            duplicates_found = True
    if duplicates_found:        
        user_input1 = input("Duplicate files have been found. Would you like to see the files before they are deleted? (Yes/No):\n").strip().lower()
        if user_input1 == "yes":
            for file_paths in duplicates.values():
                if len(file_paths) > 1:
                    print(f"Duplicate files found:\n{file_paths}\n")
                        
                    for file_path in file_paths[1:]:
                        duplicates_path = os.path.join(root_folder,"Duplicates")
                        if os.path.exists(duplicates_path) is False:
                            os.makedirs(duplicates_path, exist_ok=True)
                        copy_destination = os.path.join(duplicates_path, os.path.basename(file_path))
                        shutil.copy(file_path,copy_destination)
                        show_duplicates = True

            if show_duplicates:        
                user_input2 = input("Duplicate files have been copied to 'Duplicates' folder. If you are okay to proceed with their deletion, enter 'Yes'. To cancel the operation, press any key. \n\n").strip().lower()
                for file_paths in duplicates.values():
                    for file_path in file_paths[1:]:

                        if user_input2 == "yes":
                            os.remove(file_path)
                            print(f"{file_path} has been deleted.\n")
                            
                        else:
                            print("Cancelling operation.")
                            exit

                if user_input2 == "yes":
                    shutil.rmtree(duplicates_path)
                            
        elif user_input1 == "no":
            for file_paths in duplicates.values():
                for file_path in file_paths[1:]:
                    os.remove(file_path)
                    print(f"{file_path} has been deleted.\n")
        else:
            print("Cancelling operation.")
            exit
    else:
        print("No duplicates found.")

def identify_live_photos_IOS(root_folder):
    """Traverses through the root folder and identifies duplicate files."""
    livePhotos_filename = {}
    livePhotos_createdate = {}
    for folder_path, _, file_names in os.walk(root_folder):
        for file_name in file_names:
            file_path = os.path.join(folder_path, file_name)
            file_name_without_extension = os.path.splitext(file_name)[0]
            exif_data = get_exif_create_date_and_extension(file_path, print_output = False)

            if file_name_without_extension in livePhotos_filename:
                livePhotos_filename[file_name_without_extension].append(file_path)
            else:
                livePhotos_filename[file_name_without_extension] = [file_path]

            if exif_data is not None:
                if isinstance(exif_data, tuple):
                    createdate, _ = exif_data

            elif isinstance(exif_data, str):
                if ":" in exif_data:
                    createdate = exif_data

                if createdate:
                    if createdate in livePhotos_createdate:
                        livePhotos_createdate[createdate].append(file_path)
                    else:
                        livePhotos_createdate[createdate] = [file_path]

    return livePhotos_filename, livePhotos_createdate

def delete_live_photo_files(livePhotos_filename, livePhotos_createdate):
    live_photo_found = False

    for file_paths in livePhotos_filename.values():
        if len(file_paths) > 1:
            live_photo_found = True
            break

    if not live_photo_found:
        for file_paths in livePhotos_createdate.values():
            if len(file_paths) > 1:
                live_photo_found = True
                break

    if live_photo_found:
        user_input = input("Live photos have been found. Would you like to delete them? (Yes/No): \n").strip().lower()
        if user_input == "yes":
            for file_name, file_paths in livePhotos_filename.items():
                if len(file_paths) > 1:
                    for file_path in file_paths:
                        if os.path.exists(file_path):
                            _, file_extension = os.path.splitext(file_path)
                            if file_extension.lower() in [".mov", ".aae"]:
                                print(f"Live video(s) were found for '{file_name}':\n{file_paths}\n")
                                os.remove(file_path)
                                print(f"{file_path} has been deleted.\n")
            
            for createdate, file_paths in livePhotos_createdate.items():
                if len(file_paths) > 1:

                    # Check if there are non-mov/aae files
                    other_files = [file_path for file_path in file_paths if os.path.splitext(file_path)[1].lower() not in [".mov", ".aae"]]
                    
                    if other_files:
                        # Delete all mov/aae files
                        mov_aae_files = [file_path for file_path in file_paths if os.path.splitext(file_path)[1].lower() in [".mov", ".aae"]]
                        for file_path in mov_aae_files:
                            if os.path.exists(file_path):
                                print(f"Multiple files were found with creation date '{createdate}':\n{file_paths}\n")
                                os.remove(file_path)
                                print(f"{file_path} has been deleted.\n")
                    else:
                        # Keep one mov/aae file and delete the rest
                        mov_aae_files = [file_path for file_path in file_paths if os.path.splitext(file_path)[1].lower() in [".mov", ".aae"]]
                        for file_path in mov_aae_files[:-1]:
                            print(f"Multiple files were found with creation date '{createdate}':\n{file_paths}\n")
                            os.remove(file_path)
                            print(f"{file_path} has been deleted.\n")

        elif user_input == "no":
            print("No files were deleted.")
        else:
            print("Invalid input. No files were deleted.")
    else:
        print("No live photos found.")


def run_process(path, created_folders, args):
    """
    Process the target path (either a directory or a file), organizing media files into folders by their creation year.

    Args:
        path (str): The target directory or file path.
        created_folders (set): A set to keep track of folders created during the process.
        args: Arguments parsed from the command line.

    """
    if (os.path.isdir(path)):
            directory = path
            for root, dirs, files in os.walk(directory):
                for name in files:
                    file = os.path.join(root, name)
                    if is_media_file(file):
                        created_folders.update(categorize_files(file, args, created_folders))
            delete_empty_folders(directory, created_folders)
    else:
        print("Error: Please input a valid directory.")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Organize pictures and videos into folders by year")
    parser.add_argument(
        "target",
        help="directory or individual file")
    parser.add_argument(
        "-f", "--format", default="year",
        help="custom format for folder names. "
        "Default is year.")
        
    args = parser.parse_args()

    # Initialize a set to keep track of created folders
    created_folders = set()

     # Run the file organization process
    run_process(args.target, created_folders, args)

    # After organizing files, find and remove duplicates
    print("Searching for duplicate files...\n")
    duplicates = find_duplicate_files(args.target)
    remove_duplicate_files(duplicates, args.target)

    # Identify and delete live photos
    print("Searching for live photo files...\n")
    livePhotos_filename, livePhotos_createdate = identify_live_photos_IOS(args.target)
    delete_live_photo_files(livePhotos_filename, livePhotos_createdate)

    # Identify and correct file extension mismatches
    print("Searching for files with extension mismatches...\n")
    find_and_fix_file_extension_mismatches(args.target)

if __name__ == "__main__":
    main()