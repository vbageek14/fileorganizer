# fileorganizer

Have you ever had a hard time organizing your media archives? I'm talking sifting through all the photos and videos in random folders that you've backed up to your hard drive or cloud over the years. If so, this program should help you with cleaning up your data and freeing up some precious storage space. 

The organizeMediaFiles.py file accomplishes the following things:

1. Categorizes media files under root directory by either year or month of        creation date by accessing Create Date property of the command-line tool ExifTool. If there's no such metadata, the file is moved to an "Uncategorized" folder. Most of the time, this folder would contain files such as screenshots, gifs, and images sent via common instant messanging platforms such as Whatsapp or Telegram since they strip most metadata from files. The default cateogirzation method is "year" but you can change it to "month" but using the -f flag like this: -f "year-month".

2. Looks for and deletes duplicate files by computing an HD5 hash value of the file and then looking for files with the same value. You are given the option to view those duplicate files before proceeding with their deletion if you wish.

3. Deletes all folders and subfolders except for newly created ones that are used for categorizing data (year and/or month and "Uncategorized")

4. Looks for and deletes ".aae" files. These files are associated with Apple's photo-editing software, such as the Photos app on iOS and macOS. They are automatically generated when you make edits to a photo using Apple's editing tools, such as adjusting exposure, color balance, cropping, or applying filters and used for storing information about the edits. In most cases, these files aren't needed, so they can be safely removed. But if you do like to keep them, that is also an option.

5. Looks for and deletes live photos. On iOS when you capture an image using a "Live Photo" mode and then back it up on some kind of storage device/platform, you end up with two files for each image - a still image and a video. If you didn't notice that you were taking photos with that mode activated, it can be frustrating to have your archive folders be filled with a bunch of short videos accompanying the image. To deal with this afterthefact, this program attempts to identify those videos by:
    - looking for files with the same file name but different extension (such as       ".mov" or ".mp4")
    - looking for files with the same creation date where at least one of the          files is in a video format such as ".mov" or ".mp4"

6. Looks for files with extension mismatches and fixes them. It can happen that a media file ends up with a mismatched extension in their file name which in some cases can render the file unusable. For example, if a ".mov" video file has a ".jpeg" extension in their file name, you won't be able to view it unless you change the file extension to ".mov". This shouldn't happen often, but in my experience it has which is why I decided to include this feature. This program compares the file name extension with the extension obtained from the MIME Type property of the ExifTool and if the two don't align, renames the file with the appropriate extension.

The removeShortVideos.py file accomplishes the following:

1. Used as a supplementary feature to the point 5 from above. It allows to delete all short videos of specified length that you provide as an integer argument like so: python script_name.py root_folder -d 4. In this case, the program will delete all video files with the duration of 4 seconds or less.

  
