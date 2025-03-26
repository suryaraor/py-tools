import os
import subprocess
import random
import string
import warnings
import time
from PIL import Image
#Global count variable
total_files_processed = 0

def generate_random_filename(prefix="temp_metadata", extension=".json", length=3):
    random_str = ''.join(random.choices(string.digits, k=length))
    return f"{prefix}{random_str}{extension}"

def get_exif_data(input_path):
    """Get the metadata of an image using exiftool."""
    try:
        warnings.filterwarnings("ignore")
        # Run exiftool to get the metadata as JSON
        result = subprocess.run(
            ['exiftool', '-json', input_path],
            capture_output=True, text=True, check=True
        )
        metadata = result.stdout.strip()
        return metadata
    except subprocess.CalledProcessError as e:
        print(f"Error extracting metadata for {input_path}: {e}")
        return None

def compress_image(input_path, output_path, quality=70):
    global total_files_processed  # Use the global counter
    """Compress the image and save it to the output path along with metadata."""
    try:
        with Image.open(input_path) as img:
            img = img.convert('RGB')  # Ensure it's in RGB mode
            
            # Get metadata using exiftool
            metadata = get_exif_data(input_path)
            
            # Save the image with the desired quality
            img.save(output_path, quality=quality)
            print(f"✔ Compressed and saved: {output_path}")
            
            if metadata:
                # Save the metadata using exiftool (overwrite existing metadata)
                file_name = generate_random_filename()
                with open(file_name, 'w') as f:
                    f.write(metadata)
                subprocess.run(
                    ['exiftool', '-overwrite_original', '-tagsFromFile', file_name, output_path],
                    check=True
                )
                os.remove(file_name)
                print(f"✔ Metadata copied")
            # Increment the global counter
            total_files_processed += 1
            print(f"✔ Files processed so far: {total_files_processed}")  # Print the current count
    except Exception as e:
        print(f"Error compressing {input_path}: {e}")
    

def batch_compress_images(src_folder, tgt_folder, quality=70):
    start_time = time.time()  # Start time to measure elapsed time
    """Recursively compress images in all subfolders and recreate folder structure in the target directory, copying metadata."""
    for root, dirs, files in os.walk(src_folder):
        for file in files:
            # Check if the file is an image (you can add more extensions here)
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                # Construct the full path of the source image
                src_image_path = os.path.join(root, file)
                
                try:
                    # Open the image to check if it's a valid format
                    with Image.open(src_image_path) as img:
                        # Create the corresponding target directory structures
                        relative_path = os.path.relpath(root, src_folder)
                        tgt_image_dir = os.path.join(tgt_folder, relative_path)
                        
                        # Create the target directory if it doesn't exist
                        os.makedirs(tgt_image_dir, exist_ok=True)
                        
                        # Construct the full path of the target image
                        tgt_image_path = os.path.join(tgt_image_dir, file)
                        
                        # Compress and save the image with metadata
                        compress_image(src_image_path, tgt_image_path, quality)
                except Exception as e:
                    print(f"Error processing {src_image_path}: {e}")
        end_time = time.time()  # End time
        elapsed_time = end_time - start_time  # Total time elapsed in seconds
        print(f"✔ Total files processed: {total_files_processed}")
        print(f"✔ Total time elapsed: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    src_folder = "C:/Surya/Photo Library/111 All Time Best Photos"
    tgt_folder = "C:/Surya/Photo Library/111 All Time Best Photos/compressed"
    
    # Run batch compression
    batch_compress_images(src_folder, tgt_folder, quality=70)
