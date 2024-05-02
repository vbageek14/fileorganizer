import argparse
import os
import subprocess
import shutil
import datetime
import filetype
import hashlib
import re

def is_media_file(file):
    if os.path.exists(file):
        file_type = filetype.guess(file)

        # Defines a tuple of media file extensions
        media_extensions = ("jpg", "jpeg", "png", "gif", "bmp",
                            "tif", "tiff", "webp", "heif", "heic",
                            "svg", "mp4", "mov", "avi", "wmv", "flv",
                            "mkv", "webm", "mpg", "mpeg", "3gp")
        
        if file_type is not None and file_type.extension in media_extensions:
            return True
        return False

def get_exif_create_date_and_extension(filepath, print_output = True):

    """ Extracts the creation date of a file using exiftool. """

    try:
        result = subprocess.run(['exiftool', '-CreateDate', '-mimetype', filepath], capture_output=True, text=True)
        if result.returncode == 0:

            # Splits the output by newlines to separate creation date and file extension
            output_lines = result.stdout.strip().split('\n')
            
            if output_lines:
                create_date = None
                file_extension = None

                # Loops through each line to find creation date and file extension
                for line in output_lines:
                    if line.startswith("Create Date"):
                        create_date = line.strip().split(': ')[-1]
                    elif line.startswith("MIME Type"):
                        file_extension = line.strip().split(': ')[1].split("/")[1]
                        if file_extension == "quicktime":
                            file_extension = "mov"
                
                # Checks if both creation date and file extension exist
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

    """ Extracts the year from the file name. """

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

    """ Delete empty folders within the specified root directory, excluding those listed in the set of created folders. """

    # Iterates over directories in the root directory
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        excepted_folders = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Uncategorized"]

        # Regular expression pattern to match four-digit numbers (years)
        year_pattern = re.compile(r'^\d{4}$')

        # Excludes directories that are in the created_folders set
        dirnames[:] = [dirname for dirname in dirnames if dirname not in created_folders and dirname not in excepted_folders and not year_pattern.match(dirname)]
        for dirname in dirnames:
            full_path = os.path.join(dirpath, dirname)
            
            # Checks if the directory is empty and if so, deletes it
            if not os.listdir(full_path): 
                print(f"Deleting folder {dirname}\n")
                os.rmdir(full_path)
            else:
                print(f"Could not delete the folder {dirname} as it is not empty.\n")
                try:
                    user_input = input("If you still would like to proceed, enter 'Yes' to force delete. Enter any other key to cancel: \n").strip().lower()
                    if user_input == "yes":
                        print(f"Deleting folder {dirname}\n")

                        # Force deletes the folder and its contents
                        shutil.rmtree(full_path)
                    else:
                        print("Folder was not deleted.\n")
                except Exception as e:
                    print(f"An error occurred while trying to delete the folder: {e}")

def categorize_files(file, args, created_folders):

    """ Categorizes the file into folders based on its creation year, or moves it to an 'Uncategorized' folder if creation date metadata is not available. """

    format  = args.format

    # Extracts creation date metadata from the file
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
                # If creation date exists, determines the directory name based on the year
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
            # If no creation date metadata exists, moves the file to the 'Uncategorized' folder
            directory_name = "/".join([args.target,"Uncategorized"])
            final_path = os.path.join(directory_name,file.split("/")[-1])
    else:
        # If no creation date metadata exists, move the file to the 'Uncategorized' folder
        directory_name = "/".join([args.target,"Uncategorized"])
        final_path = os.path.join(directory_name,file.split("/")[-1])

    if os.path.exists(directory_name) is False:
        # Creates the directory if it doesn't exist and update created_folders set
        os.makedirs(directory_name, exist_ok=True)
        components = directory_name.split("/")
        for component in components:
            created_folders.add(component)
        print("Folder " + directory_name + " created.")

    if os.path.exists(final_path) is False:
         # Moves the file to the final path or skips if it already exists
        print("Moving " + file + " to " + final_path)
        os.rename(file, final_path)
    else:
        print("Skipped " + file + ", already exists in " + directory_name)
    return created_folders

def compute_hash_value(file_path):

    """ 
    Copyright (c) 2017 Monro Coury

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the 'Software'), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

    """

    """
    Computes the MD5 hash value of a file.  
    
    This function has been obtained from the following project on GitHub that is under MIT license provided above: 
    https://github.com/MK-Ware/Duplicate-file-remover/tree/master 
       
    """

    # Creates an MD5 hash object
    md5Hash = hashlib.md5()

     # Opens the file in binary mode
    with open(file_path, 'rb') as f:
        # Iterate over the file in chunks of 4096 bytes
        for chunk in iter(lambda: f.read(4096), b""):
            # Updates the MD5 hash object with the data from the current chunk
            md5Hash.update(chunk)

    # Returns the hexadecimal representation of the hash value
    return md5Hash.hexdigest()


def find_duplicate_files(root_folder):
    
    """ 

    Finds duplicate files within a given root folder. 

    This function has been adapted from the following project on GitHub that is under MIT license provided above: 
    https://github.com/MK-Ware/Duplicate-file-remover/tree/master 

    """

    dups = {}

    # Recursively traverses the root folder and its subdirectories
    for folder_path, _, file_names in os.walk(root_folder):
        for file_name in file_names:
            file_path = os.path.join(folder_path, file_name)
            # Computes the hash value of the current file
            file_hash = compute_hash_value(file_path)
            if file_hash in dups:
                dups[file_hash].append(file_path)
            else:
                dups[file_hash] = [file_path]
    return dups

def find_and_fix_file_extension_mismatches(root_folder):
    """Finds and fixes file extension mismatches within a given root folder."""

    extension_mismatches_found = False

    # Recursively traverses the root folder and its subdirectories
    for folder_path, _, file_names in os.walk(root_folder):
        for file_name in file_names:
            # Checks that the file does not have the ".aae" extension
            if not file_name.lower().endswith(".aae"):
                file_path = os.path.join(folder_path, file_name)
                file_name_extension = file_name.strip().split(".")[1].upper()
                if file_name_extension == "JPG":
                    file_name_extension = "JPEG"

                # Gets EXIF data including creation date and extension
                exif_data = get_exif_create_date_and_extension(file_path, print_output = False)

                if exif_data is not None:
                    if isinstance(exif_data, tuple):
                        _, file_exif_extension = exif_data
                        
                    elif isinstance(exif_data, str):
                        if ":" not in exif_data:
                            file_exif_extension = exif_data
                    
                    # Compares file name extension with EXIF extension
                    if file_name_extension != file_exif_extension.upper():
                        if not extension_mismatches_found:
                            extension_mismatches_found = True
                            # Asks user if they want to correct extension mismatches
                            user_input = input("File(s) with extension mismatches have been identified. Would you like to correct them? (Yes/No): \n").strip().lower()
                            if user_input == "no":
                                print("No files were deleted.\n")
                            elif user_input != "yes":
                                print("Invalid input. No files were deleted.\n")
                        
                        # Generates the final path with corrected extension
                        file_name_without_extension = os.path.splitext(file_name)[0]
                        final_path = os.path.join(folder_path, file_name_without_extension) + "." + file_exif_extension.upper()
                        try:
                            # Renames the file
                            os.rename(file_path, final_path)
                            print(f"Renamed: {file_path} -> {final_path}\n")
                        except Exception as e:
                            print(f"Error renaming {file_path}: {e}")

    if not extension_mismatches_found:
        print("No file(s) with extension mismatches were found.")

def remove_aae_files(root_folder):
    """ Remove .aae files within a given root folder."""

    aae_files_found = False

    # Recursively traverses the root folder and its subdirectories
    for folder_path, _, file_names in os.walk(root_folder):
        for file_name in file_names:
            # Checks if the file has the ".aae" extension
            if file_name.lower().endswith(".aae"):
                aae_files_found = True
                break
        if aae_files_found:
            break

    if aae_files_found:
        # Asks user if they want to delete .aae files
        user_input = input("AAE files have been found. Would you like to delete them? (Yes/No):\n").strip().lower()
        if user_input == "yes":
            # Recursively traverses the root folder and its subdirectories again
            for folder_path, _, file_names in os.walk(root_folder):
                for file_name in file_names:
                    # Checks if the file has the ".aae" extension
                    if file_name.lower().endswith(".aae"):
                        file_path = os.path.join(folder_path, file_name)
                        # Deletes the .aae file
                        os.remove(file_path)
                        print(f"{file_path} has been deleted.\n")
        else:
            print("No AAE files have been deleted.\n")
    else:
        print("No AAE files found in the specified folder.\n")
    

def remove_duplicate_files(duplicates, root_folder):
    """Removes duplicate files withi a given root folder."""

    show_duplicates = False
    duplicates_found = False

     # Checks if duplicates are found
    for file_paths in duplicates.values():
        if len(file_paths) > 1:
            duplicates_found = True

    if duplicates_found: 
        # Prompts user to see duplicate files before deletion       
        user_input1 = input("Duplicate files have been found. Would you like to see the files before they are deleted? (Yes/No):\n").strip().lower()
        if user_input1 == "yes":
            # Iterate over duplicate file paths
            for file_paths in duplicates.values():
                if len(file_paths) > 1:
                    print(f"Duplicate files found:\n{file_paths}\n")
                    # Copies duplicate files to a separate folder
                    for file_path in file_paths[1:]:
                        duplicates_path = os.path.join(root_folder,"Duplicates")
                        if os.path.exists(duplicates_path) is False:
                            os.makedirs(duplicates_path, exist_ok=True)
                        copy_destination = os.path.join(duplicates_path, os.path.basename(file_path))
                        shutil.copy(file_path,copy_destination)
                        show_duplicates = True

            if show_duplicates:        
                # Prompts user to confirm deletion after copying duplicates
                user_input2 = input("Duplicate files have been copied to 'Duplicates' folder. If you are okay to proceed with their deletion, enter 'Yes'. To cancel the operation, press any key. \n\n").strip().lower()
                for file_paths in duplicates.values():
                    for file_path in file_paths[1:]:
                        # Deletes duplicate files if user confirms
                        if user_input2 == "yes":
                            os.remove(file_path)
                            print(f"{file_path} has been deleted.\n")
                        else:
                            print("Cancelling operation.")
                            exit

                if user_input2 == "yes":
                    shutil.rmtree(duplicates_path)
                            
        elif user_input1 == "no":
            # Deletes duplicate files without displaying them
            for file_paths in duplicates.values():
                for file_path in file_paths[1:]:
                    os.remove(file_path)
                    print(f"{file_path} has been deleted.\n")
        else:
            print("Cancelling operation.")
            exit
    else:
        print("No duplicates found.\n")

def identify_live_photos_IOS(root_folder):
    
    """ Traverses through the root folder and identifies live photos based on iOS file naming conventions. """
    
    # Initializes dictionaries to store live photo information
    livePhotos_filename = {}
    livePhotos_createdate = {}

    # Recursively traverses the root folder and its subdirectories
    for folder_path, _, file_names in os.walk(root_folder):
        for file_name in file_names:
            file_path = os.path.join(folder_path, file_name)
            file_name_without_extension = os.path.splitext(file_name)[0]
             # Gets EXIF data including creation date and extension
            exif_data = get_exif_create_date_and_extension(file_path, print_output = False)

            # Stores file paths based on filename
            if file_name_without_extension in livePhotos_filename:
                livePhotos_filename[file_name_without_extension].append(file_path)
            else:
                livePhotos_filename[file_name_without_extension] = [file_path]

            # Stores file paths based on creation date (if available)
            if exif_data is not None:
                createdate = None
                if isinstance(exif_data, tuple):
                    createdate, _ = exif_data

                elif isinstance(exif_data, str):
                    if ":" in exif_data:
                        createdate = exif_data

                # Adds file paths to dictionary based on creation date
                if createdate:
                    if createdate in livePhotos_createdate:
                        livePhotos_createdate[createdate].append(file_path)
                    else:
                        livePhotos_createdate[createdate] = [file_path]

    return livePhotos_filename, livePhotos_createdate

def delete_live_photo_files(livePhotos_filename, livePhotos_createdate):

    """ Deletes live photo files (".mov" or ".mp4") based on given dictionaries containing file paths. """
    
    live_photo_found = False

     # Checks if live photo files are found based on filenames
    for file_paths in livePhotos_filename.values():
        if len(file_paths) > 1 and (".mov" in file_paths or ".mp4" in file_paths):
            live_photo_found = True
            break

    # If live photo files are not found based on filenames, checks based on creation dates
    if not live_photo_found:
        for file_paths in livePhotos_createdate.values():
            if len(file_paths) > 1 and (".mov" in file_paths or ".mp4" in file_paths):
                live_photo_found = True
                break

    # If live photo files are found, prompts user to confirm deletion           
    if live_photo_found:
        user_input = input("Live photos have been found. Would you like to delete them? (Yes/No): \n").strip().lower()
        if user_input == "yes":
            for file_name, file_paths in livePhotos_filename.items():
                if len(file_paths) > 1:
                    # If multiple file paths exist for the same filename, iterates over each path
                    for file_path in file_paths:
                        if os.path.exists(file_path):
                            _, file_extension = os.path.splitext(file_path)
                            if file_extension.lower() in [".mov", ".mp4"]:
                                # Deletes the file if it meets the criteria
                                print(f"Live video(s) were found for '{file_name}':\n{file_paths}\n")
                                os.remove(file_path)
                                print(f"{file_path} has been deleted.\n")
            
            # Iterates over creation dates and file paths
            for createdate, file_paths in livePhotos_createdate.items():
                if len(file_paths) > 1:

                    # Checks if there are non-mov/mp4 files
                    other_files = [file_path for file_path in file_paths if os.path.splitext(file_path)[1].lower() not in [".mov", ".mp4"]]
                    
                    if other_files:
                        # If non-mov/mp4 files exist, deletes all mov/mp4 files
                        mov_mp4_files = [file_path for file_path in file_paths if os.path.splitext(file_path)[1].lower() in [".mov", ".mp4"]]
                        for file_path in mov_mp4_files:
                            if os.path.exists(file_path):
                                print(f"Multiple files were found with creation date '{createdate}':\n{file_paths}\n")
                                os.remove(file_path)
                                print(f"{file_path} has been deleted.\n")
                    else:
                        # If only mov/mp4 files exist, keeps one and deletes the rest
                        mov_mp4_files = [file_path for file_path in file_paths if os.path.splitext(file_path)[1].lower() in [".mov", ".mp4"]]
                        for file_path in mov_mp4_files[:-1]:
                            print(f"Multiple files were found with creation date '{createdate}':\n{file_paths}\n")
                            os.remove(file_path)
                            print(f"{file_path} has been deleted.\n")

        elif user_input == "no":
            print("No files were deleted.")
        else:
            print("Invalid input. No files were deleted.")
    else:
        print("No live photos found.\n")


def run_process(path, created_folders, args):

    """ Processes the target path (either a directory or a file), organizing media files into folders by their creation year. """

    if (os.path.isdir(path)):
            directory = path

            # Recursively traverses the root folder and its subdirectories
            for root, dirs, files in os.walk(directory):
                for name in files:
                    file = os.path.join(root, name)
                    if is_media_file(file):
                        created_folders.update(categorize_files(file, args, created_folders))
            delete_empty_folders(directory, created_folders)
    else:
        print("Error: Please input a valid directory.")

def main():
    # Parses command-line arguments
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

    # Initializes a set to keep track of created folders
    created_folders = set()

     # Runs the file organization process
    run_process(args.target, created_folders, args)

    # After organizing files, finds and removes duplicates
    print("Searching for duplicate files...\n")
    duplicates = find_duplicate_files(args.target)
    remove_duplicate_files(duplicates, args.target)

    # Identifies and deletes live photos
    print("Searching for live photo files...\n")
    livePhotos_filename, livePhotos_createdate = identify_live_photos_IOS(args.target)
    delete_live_photo_files(livePhotos_filename, livePhotos_createdate)

    # Identifies and deletes "aae" files
    print("Searching for '.aae' files...\n")
    remove_aae_files(args.target)

    # Identifies and corrects file extension mismatches
    print("Searching for files with extension mismatches...\n")
    find_and_fix_file_extension_mismatches(args.target)

if __name__ == "__main__":
    main()