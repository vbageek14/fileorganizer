import argparse
import os
import subprocess
import shutil
import datetime
import filetype

def is_media_file(file):
    file = filetype.guess("/Users/konstimac/Desktop/Screenshot 2024-04-12 at 1.06.56 PM.png")
    media_extensions = ("jpg", "jpeg", "png", "gif", "bmp",
                        "tif", "tiff", "webp", "heif", "heic",
                        "svg", "mp4", "mov", "avi", "wmv", "flv",
                        "mkv", "webm", "mpg", "mpeg", "3gp")
    if file.extension in media_extensions:
        return True

def get_exif_create_date(filepath):
    '''
    Extracts the creation date of a file using exiftool.

    Args:
        filepath (str): The path to the file.
        
    Returns:
        str: The creation date of the file, or None if no EXIF metadata exists or an error occurs.

    '''

    try:
        result = subprocess.run(['exiftool', '-CreateDate', filepath], capture_output=True, text=True)
        if result.returncode == 0:
            create_date = result.stdout.strip().split(': ')[-1]
            if create_date:
                return create_date
            else:
                print("No EXIF metadata exists")
                return None
        else:
            print("Error:", result.stderr)
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
    return year

def extract_month_from_file(file):
    month_num = str(file)[5:7]
    datetime_object = datetime.datetime.strptime(month_num, "%m")
    month_name = datetime_object.strftime("%b")
    return month_name

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
                print(f"Deleting folder {dirname}")
                os.rmdir(full_path)
            else:
                print(f"Could not delete the folder {dirname} as it is not empty.")
                try:
                    user_input = input("If you've checked that it's empty and may contain hidden or duplicate files, enter 'Yes' to force delete. Enter any other key to cancel: \n")
                    if user_input == "Yes":
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
    file_date = get_exif_create_date(file)
    
    if file_date:
        if format == "year":
            # If creation date exists, determine the directory name based on the year
            directory_name = "/".join([args.target,str(extract_year_from_file(str(file_date)))])
        elif format == "year-month":
            directory_name = "/".join([args.target,str(extract_year_from_file(str(file_date))), str(extract_month_from_file(str(file_date)))])
        
        final_path = os.path.join(directory_name, file.split("/")[-1])
        
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
                    if is_media_file(name):
                        file = os.path.join(root, name)
                        created_folders.update(categorize_files(file, args, created_folders))
            delete_empty_folders(directory, created_folders)
    else:
        print("Error: Please input a valid directory.")
    # elif (os.path.isfile(path)):
    #     if is_media_file(path):
    #         created_folders.update(categorize_files(path, args))
    #         delete_empty_folders(os.path.dirname(path), created_folders)

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

if __name__ == "__main__":
    main()