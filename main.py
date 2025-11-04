import os
import subprocess
import glob
import time
import shutil
import random

# Import everything from colorama (using this style for compatibility with original code)
from colorama import Fore, Back, Style, init

# Use os.path.join for path construction to ensure cross-platform compatibility
path_to_videos = 'Input' # Path Directory
path_out_to_videos = 'Output' # Path Directory
video_extensions = ['.mp4', '.avi', '.mkv', '.mov'] # Videos Extensions Allowed

# Font Fix: Use a known system font in Colab (which runs Linux). 
# DejaVuSans-Bold.ttf is usually available in the system's font folder.
FONT_FILE_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def main():
    init()
    
    # 🚨 FIX 1: glob requires forward slashes, even on Windows, and works fine on Linux (Colab)
    # The original search pattern was problematic due to the use of '[]' with '|' on some systems.
    # We will search by iterating over extensions.
    video_files = []
    for ext in video_extensions:
        video_files.extend(glob.glob(os.path.join(path_to_videos, f"*{ext}")))
    
    # Search for subdirectories correctly
    subdirectories = [subdir for subdir in os.listdir(path_to_videos) 
                      if os.path.isdir(os.path.join(path_to_videos, subdir))]
    
    if not subdirectories and not video_files: # If there is no video available
        print(Fore.RED + "The input folder cannot be empty!" + Style.RESET_ALL)
        exit()

    # noinspection PyBroadException
    try:
        random_video = input("Random WaterMark Number (Default 0 (Without Random) - Just Number): " + Fore.GREEN)
        random_video = 0 if random_video == '' else int(random_video)

        user_text = input("Your Phone Number (list.txt): " + Fore.GREEN)
        user_text = 'list.txt' if user_text == '' else user_text

        user_time = input(Style.RESET_ALL + "Time to change the text (Just Number/Second - Default 60 Second) : " + Fore.GREEN)
        user_time = 60 if user_time == '' else int(user_time)
        user_time = user_time if user_time != 0 else 60

        user_opacity = input(Style.RESET_ALL + "Please Enter Opacity (Between 0.0 to 1.0 - Default 0.2) : " + Fore.GREEN)
        user_opacity = 0.2 if user_opacity == '' else float(user_opacity)
        user_opacity = user_opacity if (1.0 >= user_opacity > 0) else 0.5

        user_size = input(Style.RESET_ALL + "Please Enter Font Size (Default 22) : " + Fore.GREEN)
        user_size = 22 if user_size == '' else int(user_size)
        user_size = user_size if (80 >= user_size >= 6) else 22 # Changed min/max check range

        user_color = input(Style.RESET_ALL + "Please Enter Text Color (hex => #ffffff Or color => white - default white) : " + Fore.GREEN)
        user_color = 'white' if user_color == '' else user_color
        user_bg_color = input(Style.RESET_ALL + "Please Enter Background Color (hex => #000000 or color => black - default black) : " + Fore.GREEN)
        user_bg_color = 'black' if user_bg_color == '' else user_bg_color
        print(Style.RESET_ALL)
    except:
        print('')
        print(Back.BLACK + Fore.RED + 'Be sure to pay attention to the type of value you enter' + Style.RESET_ALL)
        exit()

    lines = []

    if os.path.exists(user_text) and user_text != 'list.txt': # Check Existed Text User (UserFile => list.txt)
         with open(user_text, 'r') as file:
            for line in file:
                cleaned_line = line.strip()
                lines.append(cleaned_line)
    elif user_text == 'list.txt' and os.path.exists(user_text):
        with open(user_text, 'r') as file:
            for line in file:
                cleaned_line = line.strip()
                lines.append(cleaned_line)
    else:
        # Use a default watermark if no list is provided and list.txt doesn't exist
        lines.append('WaterMark')

    if video_files:
        for line in lines:
            # 🚨 FIX 2: Use os.path.join for output directory creation
            output_dir = os.path.join(path_out_to_videos, line)
            os.makedirs(output_dir, exist_ok=True)
            
            loopWaterMark(video_files, line, user_size, user_color, user_opacity, user_time, user_bg_color, random_video)

    if subdirectories:
        for line in lines:
            # 🚨 FIX 3: Use os.path.join for output directory creation
            output_dir_base = os.path.join(path_out_to_videos, line)
            os.makedirs(output_dir_base, exist_ok=True)

            for subdir in subdirectories:
                input_subdir = os.path.join(path_to_videos, subdir)
                output_subdir = os.path.join(output_dir_base, subdir)

                os.makedirs(output_subdir, exist_ok=True)

                # Find video files in the subdirectory
                subdir_video_files = []
                for ext in video_extensions:
                    subdir_video_files.extend(glob.glob(os.path.join(input_subdir, f"*{ext}")))

                if not subdir_video_files:
                    print(Fore.RED + f"No video files found in {input_subdir}" + Style.RESET_ALL)
                    continue

                loopWaterMark(subdir_video_files, line, user_size, user_color, user_opacity, user_time, user_bg_color, random_video)

                # Copy non-video files
                all_files = os.listdir(input_subdir)
                for file_name in all_files:
                    source_file_path = os.path.join(input_subdir, file_name)
                    destination_file_path = os.path.join(output_subdir, file_name)

                    file_extension = os.path.splitext(file_name)[1].lower()

                    if file_extension not in video_extensions:
                        if os.path.isfile(source_file_path):
                            shutil.copy(source_file_path, destination_file_path)
                        elif os.path.isdir(source_file_path):
                            shutil.copytree(source_file_path, destination_file_path)

    print("Finish")


def loopWaterMark(videos_file, line, user_size, user_color, user_opacity, user_time, user_bg_color, random_waterMark=0):
    all_video = []
    videos_not_selected = []
    if random_waterMark:
        number_all_videos = len(videos_file)
        if random_waterMark > number_all_videos:
            print(Back.BLACK + Fore.RED + 'The random number is larger than all videos' + Style.RESET_ALL)
            exit()
        all_video = random.sample(videos_file, random_waterMark)
        videos_not_selected = [vid for vid in videos_file if vid not in all_video]
    else:
        all_video = videos_file

    for video in all_video:
        # Construct the output path correctly using os.path.join
        # 🚨 FIX 4: Corrected path replacement logic to use os.path.join
        relative_path_to_video = os.path.relpath(video, path_to_videos)
        output_dir = os.path.join(path_out_to_videos, line, os.path.dirname(relative_path_to_video))
        os.makedirs(output_dir, exist_ok=True) # Ensure output directories exist
        output_path = os.path.join(output_dir, os.path.basename(video))
        
        # Changing the position of the text according to the user's second as animation
        # 🚨 FIX 5: Use FONT_FILE_PATH for the font file (instead of the non-existent local one)
        ffmpeg_cmd = [
            "ffmpeg",
            "-i", video,
            "-vf",
            f"drawtext=text='{line}':fontsize={user_size}:fontcolor={user_color}@{user_opacity}:fontfile={FONT_FILE_PATH}"
            f":x='if(eq(mod(t,{user_time}),0),rand(0,(w-text_w)),x')"
            f":y='if(eq(mod(t,{user_time}),0),rand(0,(h-text_h)),y)'"
            f":box=1:boxcolor={user_bg_color}@{user_opacity}:boxborderw=10",
            "-c:a", "copy",
            "-y", # Overwrite output files without asking
            output_path
        ]
        
        try:
             # Execute the FFmpeg command
            process = subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True)
            print(" ")
            print(Fore.GREEN + f"{video} complete! Output saved to: {output_path}" + Style.RESET_ALL)
            print(" ")
            time.sleep(2)
        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"❌ FFmpeg Error for {video}:" + Style.RESET_ALL)
            # print(e.stderr) # Optionally print the detailed FFmpeg error output
        except FileNotFoundError:
            print(Fore.RED + "❌ FFmpeg not found. Ensure it is installed." + Style.RESET_ALL)


    if len(videos_not_selected) != 0:
        for video in videos_not_selected:
            # Construct output path for copying the un-watermarked video
            relative_path_to_video = os.path.relpath(video, path_to_videos)
            output_dir = os.path.join(path_out_to_videos, line, os.path.dirname(relative_path_to_video))
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, os.path.basename(video))
            
            shutil.copy(video, output_path)

if __name__ == "__main__":
    main()
