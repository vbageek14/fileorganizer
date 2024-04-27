import os
import hashlib
import shutil

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

def remove_duplicate_files(duplicates):
    """Removes duplicate files from the file system."""

    show_duplicates = False
    duplicates_found = False

    for file_paths in duplicates.values():
        if len(file_paths) > 1:
            duplicates_found = True
    if duplicates_found:        
        user_input1 = input("Would you like to see the duplicate files before they are deleted? Input 'Yes' if so, otherwise press 'No'. To cancel operation, press any key. \n").strip().lower()
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
                user_input2 = input("Duplicate files have been copied to 'Duplicates' folder. If you are okay to proceed with their deletion, enter 'Yes'. To cancel the operation, press any key\n").strip().lower()
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
            os.remove(file_path)
            print(f"{file_path} has been deleted.\n")
        else:
            print("Cancelling operation.")
            exit
            
if __name__ == '__main__':
    root_folder = '/Users/konstimac/Desktop/Iphone 2019-2020'
    duplicates = find_duplicate_files(root_folder)
    remove_duplicate_files(duplicates)