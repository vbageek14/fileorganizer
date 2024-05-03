# File Organizer

Have you ever had a hard time organizing your media archives? This program aims to assist you in cleaning up your data and freeing up some precious storage space.

## organizeMediaFiles.py

This script accomplishes the following tasks:

1. **Categorization of Media Files:**
   - Categorizes media files under the root directory by either year or month of creation date by accessing the Create Date property of the command-line tool ExifTool. If there's no such metadata, the file is moved to an "Uncategorized" folder.
   - Default categorization method is "year," but you can change it to "month" using the `-f` flag.
Usage example:
```bash
python organizeMediaFiles.py root_folder -f "month"
```

2. **Duplicate File Removal:**
   - Looks for and deletes duplicate files by computing an MD5 hash value of the file.
   - Provides an option to view duplicate files before deletion.

3. **Folder Cleanup:**
   - Deletes all folders and subfolders except for newly created ones that are used for categorizing data (year and/or month and "Uncategorized").

4. **Deletion of ".aae" Files:**
   - Looks for and deletes ".aae" files associated with Apple's photo-editing software.

5. **Deletion of Live Photos:**
   - Identifies and deletes accompanying videos for Live Photos.

6. **Extension Mismatch Fixing:**
   - Corrects extension mismatches in file names based on the MIME Type property of the ExifTool.

## removeShortVideos.py

This script is a supplementary feature for the removal of short videos:

- Allows deletion of all video files with a duration equal to or less than a specified length provided as an integer argument.

Usage example:
```bash
python removeShortVideos.py root_folder -d 4
