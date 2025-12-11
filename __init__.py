import os
import torch
import numpy as np
from PIL import Image, ImageOps
import folder_paths

IMAGE_DIRECTORY = "/home/saltchicken/.local/share/ComfyUI/output"


class LoadImageFromSpecificFolder:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        # Scan the folder for images when the node is loaded
        files_list = []

        if os.path.exists(IMAGE_DIRECTORY) and os.path.isdir(IMAGE_DIRECTORY):
            valid_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff"}
            # Get all files and filter by extension
            all_files = os.listdir(IMAGE_DIRECTORY)
            files_list = [
                f
                for f in all_files
                if os.path.splitext(f)[1].lower() in valid_extensions
            ]
            files_list.sort()
        else:
            files_list = ["Error: Folder Not Found (Check Code)"]

        return {
            "required": {
                "image_file": (files_list,),  # This creates the dropdown menu
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK", "STRING")
    RETURN_NAMES = ("image", "mask", "filename")
    FUNCTION = "load_image"
    CATEGORY = "Custom/Image"

    def load_image(self, image_file):
        # 1. Construct Full Path
        image_path = os.path.join(IMAGE_DIRECTORY, image_file)

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"File not found: {image_path}")

        # 2. Load Image
        img = Image.open(image_path)
        img = ImageOps.exif_transpose(img)  # Fix rotation

        # 3. Process to Tensor (IMAGE)
        image = img.convert("RGB")
        image = np.array(image).astype(np.float32) / 255.0
        image = torch.from_numpy(image)[None,]

        # 4. Process Mask (MASK)
        if "A" in img.getbands():
            mask = np.array(img.getchannel("A")).astype(np.float32) / 255.0
            mask = 1.0 - torch.from_numpy(mask)
        else:
            mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")

        # 5. PREVIEW LOGIC
        # Copy to temp so the web browser can see it
        temp_dir = folder_paths.get_temp_directory()
        preview_filename = f"preview_{image_file}"
        preview_path = os.path.join(temp_dir, preview_filename)

        img.save(preview_path)

        # UI Update Info
        preview_result = {"filename": preview_filename, "subfolder": "", "type": "temp"}

        return {"ui": {"images": [preview_result]}, "result": (image, mask, image_file)}


# Node Registration
NODE_CLASS_MAPPINGS = {"LoadImageFromSpecificFolder": LoadImageFromSpecificFolder}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadImageFromSpecificFolder": "Load Local File (Dropdown)"
}
