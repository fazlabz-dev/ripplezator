import sys
import subprocess
import os

from config import *

def get_executable_path(filename):
    """Get the full path of an executable located in a specific subdirectory of the script's directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.join(script_dir, filename)
    if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
        return exe_path
    return None

def check_executables():
    """Check if the required executables are available in the specified directories."""
    if cur_os == "windows":
        magick_path = get_executable_path('imagemagick\\magick.exe')
        exiftool_path = get_executable_path('exiftool\\exiftool.exe')
    if cur_os == "linux":
        magick_path = get_executable_path('imagemagick/magick')
        exiftool_path = get_executable_path('exiftool/exiftool')

    if magick_path is None:
        print("ImageMagick executable (magick.exe) not found in the specified directory.")
        sys.exit(1)

    if exiftool_path is None:
        print("ExifTool executable (exiftool.exe) not found in the specified directory.")
        sys.exit(2)

    return magick_path, exiftool_path

def validate_args():
    """Validate the input and output arguments."""
    if len(sys.argv) != 3:
        print("error : missing args: <input.jpg> <output.jpg>")
        sys.exit(3)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    if not os.path.isfile(input_path):
        print(f"error : {input_path} not found")
        sys.exit(4)

    if os.path.isfile(output_path):
        print(f"error : {output_path} already present")
        sys.exit(5)

    return input_path, output_path

def create_thumbnail(input_path, output_path, magick_path, exiftool_path):
    """Create thumbnail and process image."""
    thumb_path = f"{os.path.splitext(output_path)[0]}_thumb.jpg"

    try:
        # Use ImageMagick to compress and convert the image
        subprocess.run([magick_path, '-colorspace', 'sRGB', '-sampling-factor', '4:2:2', '-define', 'jpeg:extent=1300kb', input_path, output_path], check=True)
        
        # Copy EXIF data
        subprocess.run([exiftool_path, '-overwrite_original', '-all=', '-exifbyteorder=little-endian', '-tagsFromFile', input_path, '-Make', '-Model', '-DateTimeOriginal', '-CreateDate', output_path], check=True)
        
        # Insert missing EXIF data
        subprocess.run([exiftool_path, '-overwrite_original', '-wm', 'cg', '-exifbyteorder=little-endian', '-Make=Make', '-Model=Model', '-DateTimeOriginal=now', '-CreateDate=now', '-InteropIndex=R98', '-ColorSpace=sRGB', '-ExifImageHeight<ImageHeight', '-ExifImageWidth<ImageWidth', output_path], check=True)
        
        # Generate thumbnail
        subprocess.run([magick_path, output_path, '-resize', '160x120', '-background', 'black', '-gravity', 'center', '-extent', '160x120', '-colorspace', 'sRGB', '-sampling-factor', '4:2:2', '-strip', thumb_path], check=True)
        
        # Strip thumbnail EXIF data
        subprocess.run([exiftool_path, '-overwrite_original', '-all=', thumb_path], check=True)
        
        # Insert thumbnail into output image
        subprocess.run([exiftool_path, '-overwrite_original', f'-ThumbnailImage<={thumb_path}', output_path], check=True)

        # Remove seperate thumbnail file
        os.remove(thumb_path)

        print("Image processing completed successfully.")
    
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        sys.exit(6)

def main():
    magick_path, exiftool_path = check_executables()
    input_path, output_path = validate_args()
    create_thumbnail(input_path, output_path, magick_path, exiftool_path)

if __name__ == "__main__":
    main()
