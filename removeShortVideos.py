import subprocess
import os
import sys

def get_exif_duration(filepath, print_output = True):

    """ Extracts the creation date of a file using exiftool. """

    try:
        result = subprocess.run(['exiftool', '-Duration', filepath], capture_output=True, text=True)
        if result.returncode == 0:
            duration_info = result.stdout.strip().split(": ")[1]

            # Checks if duration is in format '0:00:00'
            if ':' in duration_info:
                duration_parts = duration_info.split(":")
                hours = int(duration_parts[0])
                minutes = int(duration_parts[1])
                seconds = int(duration_parts[2])
                total_seconds = hours * 3600 + minutes * 60 + seconds
                return total_seconds

            # Checks if duration is in format '00.00 s'
            elif 's' in duration_info:
                duration_seconds = float(duration_info.split()[0])
                rounded_seconds = round(duration_seconds)
                return rounded_seconds

            else:
                if print_output:
                    print("Unknown duration format:", duration_info)
                return None

        else:
            if print_output:
                print("Error:", result.stderr)
            return None
        
    except Exception as e:
        if print_output:
            print("An error occurred:", e)
        return None
    
def delete_short_videos(root_folder, threshold):

    short_videos_found = False

    # Recursively traverses the root folder and its subdirectories
    for folder_path, _, file_names in os.walk(root_folder):
        for file_name in file_names:
            file_path = os.path.join(folder_path, file_name)
            exif_data = get_exif_duration(file_path, print_output = False)
            if exif_data is not None:
                exif_duration = exif_data

                # Converts the duration value to a floating-point number if needed
                duration_time = float(exif_duration)
                
                if duration_time < threshold:
                    short_videos_found = True
                    os.remove(file_path)
                    print(f"{file_path} has been deleted.\n")

    if not short_videos_found:
        print(f"No vidoes with the length of {threshold} or less were found")
                
def main():
    if len(sys.argv) != 4 or sys.argv[2] != "-d":
        print("Usage: python script_name.py root_folder -d integer_for_duration_threshold")
        sys.exit(1)
    
    root_folder = sys.argv[1]

    if sys.argv[3].isdigit():
        threshold = int(sys.argv[3])
    else:
        print("Threshold value must be an integer.")
        sys.exit(1)
    print(f"Searching for videos with the length of {threshold} seconds or less...\n")
    delete_short_videos(root_folder, threshold)

if __name__ == "__main__":
    main()