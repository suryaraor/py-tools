import os
import subprocess
from PIL import Image
from multiprocessing import Pool

def get_exif_data(input_path):
    """Get the metadata of an image using exiftool."""
    try:
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

def compress_image_and_copy_metadata(args):
    """Compress an image and copy metadata using exiftool."""
    input_path, output_path, quality = args
    
    try:
        with Image.open(input_path) as img:
            img = img.convert('RGB')  # Ensure it's in RGB mode
            
            # Get metadata using exiftool
            metadata = get_exif_data(input_path)
            
            # Save the image with the desired quality
            img.save(output_path, quality=quality)
            print(f"Compressed and saved: {output_path}")
            
            if metadata:
                # Save the metadata using exiftool (overwrite existing metadata)
                with open('temp_metadata.json', 'w') as f:
                    f.write(metadata)
                subprocess.run(
                    ['exiftool', '-overwrite_original', '-tagsFromFile', 'temp_metadata.json', output_path],
                    check=True
                )
                os.remove('temp_metadata.json')
                print(f"Metadata copied to: {output_path}")
    except Exception as e:
        print(f"Error compressing {input_path}: {e}")

def batch_compress_images(src_folder, tgt_folder, quality=70):
    """Recursively compress images in all subfolders and recreate folder structure in the target directory, copying metadata."""
    
    # Collect all image file paths that need to be processed
    tasks = []
    for root, dirs, files in os.walk(src_folder):
        for file in files:
            # Check if the file is an image (you can add more extensions here)
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                # Construct the full path of the source image
                src_image_path = os.path.join(root, file)
                
                # Create the corresponding target directory structures
                relative_path = os.path.relpath(root, src_folder)
                tgt_image_dir = os.path.join(tgt_folder, relative_path)
                
                # Create the target directory if it doesn't exist
                os.makedirs(tgt_image_dir, exist_ok=True)
                
                # Construct the full path of the target image
                tgt_image_path = os.path.join(tgt_image_dir, file)
                
                # Add the task (input_path, output_path, quality) to the list
                tasks.append((src_image_path, tgt_image_path, quality))
    
    # Use multiprocessing to process the tasks in parallel
    with Pool() as pool:
        pool.map(compress_image_and_copy_metadata, tasks)

if __name__ == "__main__":
    src_folder = "D:/Family Photos"
    tgt_folder = "E:/Photo Library"
    
    # Run batch compression with parallel processing
    batch_compress_images(src_folder, tgt_folder, quality=70)
