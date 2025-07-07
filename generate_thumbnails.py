import os
from PIL import Image
from tqdm import tqdm

# Define directories
source_dirs = ["stocks", "pictures/archived"]
thumbnail_dir = "thumbnails"
thumbnail_size = (500, 500)

# Create thumbnail directory if it doesn't exist
if not os.path.exists(thumbnail_dir):
    os.makedirs(thumbnail_dir)

def create_thumbnail(source_path, dest_path):
    """Creates a thumbnail for an image."""
    try:
        base, ext = os.path.splitext(os.path.basename(source_path))
        thumbnail_filepath = os.path.join(dest_path, f"{base}.webp")

        if os.path.exists(thumbnail_filepath):
            # No need to print here, it will clutter the progress bar
            return

        with Image.open(source_path) as img:
            img.thumbnail(thumbnail_size)
            # Save with a .webp extension
            img.save(thumbnail_filepath, "WEBP")
    except IOError as e:
        print(f"Cannot create thumbnail for {source_path}: {e}")

# Collect all images to process
all_images = []
for directory in source_dirs:
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                all_images.append(os.path.join(directory, filename))

# Process images with a progress bar
for image_path in tqdm(all_images, desc="Generating Thumbnails"):
    create_thumbnail(image_path, thumbnail_dir)

print("\nThumbnail generation complete.")
