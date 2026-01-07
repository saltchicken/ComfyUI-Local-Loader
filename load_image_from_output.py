import os
import torch
import numpy as np
import folder_paths
from PIL import Image, ImageOps

def get_output_dirs():
    """Returns a sorted list of subdirectories in the output folder."""
    output_dir = folder_paths.get_output_directory()
    dirs = [""] # Represents the root output directory
    
    if not os.path.exists(output_dir):
        return dirs

    # Recursive walk to find all subdirectories
    for root, subdirs, files in os.walk(output_dir):
        for d in subdirs:
            full_path = os.path.join(root, d)
            # Create relative path from output_dir
            rel_path = os.path.relpath(full_path, output_dir)
            dirs.append(rel_path)
            
    return sorted(dirs)

def get_images_in_dir(subdir):
    """Returns a sorted list of images in the specified subdirectory of output."""
    output_dir = folder_paths.get_output_directory()
    
    # Handle the "root" case safely
    if subdir == "":
        target_dir = output_dir
    else:
        target_dir = os.path.join(output_dir, subdir)

    if not os.path.exists(target_dir):
        return []

    valid_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}
    files = []
    
    try:
        # Just list files in this specific directory (not recursive)
        # Because the user selects specific subdirectories via the widget
        for f in os.listdir(target_dir):
            if os.path.isfile(os.path.join(target_dir, f)):
                if os.path.splitext(f)[1].lower() in valid_extensions:
                    files.append(f)
    except Exception:
        pass

    return sorted(files, reverse=True)


class LoadImageFromOutput:
    """
    Loads an image from the ComfyUI output directory.
    Allows selecting a specific subdirectory.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        # Initial population of widgets
        # The JS extension will handle dynamic updates afterwards
        directories = get_output_dirs()
        
        # Default to images in root or the first available directory
        first_dir = directories[0] if directories else ""
        images = get_images_in_dir(first_dir)

        return {
            "required": {
                "directory": (directories, ),
                "image": (images, ),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "load_image"
    CATEGORY = "My Custom Nodes/Image"

    @classmethod
    def IS_CHANGED(s, directory, image):
        # Trigger re-execution if the file path or modification time changes
        output_dir = folder_paths.get_output_directory()
        image_path = os.path.join(output_dir, directory, image)
        
        if not os.path.exists(image_path):
            return float("nan")
        return os.path.getmtime(image_path)

    def load_image(self, directory, image):
        output_dir = folder_paths.get_output_directory()
        image_path = os.path.join(output_dir, directory, image)

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        # 1. Open the image using PIL
        try:
            i = Image.open(image_path)
        except Exception as e:
            raise Exception(f"Error opening image {image_path}: {e}")

        # 2. Handle Orientation (EXIF data)
        i = ImageOps.exif_transpose(i)

        # 3. Handle Alpha Channel for Mask
        if "A" in i.getbands():
            mask = np.array(i.getchannel("A")).astype(np.float32) / 255.0
            mask = 1.0 - torch.from_numpy(mask)
        else:
            mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")

        # 4. Convert Image to RGB and normalize to 0-1 range
        image_rgb = i.convert("RGB")
        image_rgb = np.array(image_rgb).astype(np.float32) / 255.0

        # 5. Convert numpy array to torch tensor
        image_tensor = torch.from_numpy(image_rgb)[None,]

        return (image_tensor, mask)
