import torch
import numpy as np
import os
from PIL import Image, ImageOps



class LoadImageFromDir:
    """
    A custom node to load images from a directory.
    Iterates through all images in the folder.
    """

    _current_index = 0

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "directory": (
                    "STRING",
                    {
                        "multiline": False,
                        "default": "/path/to/directory",
                    },
                ),
            },
        }

    @classmethod
    def IS_CHANGED(s, **kwargs):
        return float("nan")

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "load_image"
    CATEGORY = "Custom/Image"

    def load_image(self, directory):
        if not os.path.isdir(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")

        # Filter for common image extensions
        valid_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}
        files = sorted(
            [
                os.path.join(directory, f)
                for f in os.listdir(directory)
                if os.path.isfile(os.path.join(directory, f))
                and os.path.splitext(f)[1].lower() in valid_extensions
            ]
        )

        if not files:
            raise ValueError(f"No valid images found in directory: {directory}")

        # Select file based on index
        image_path = files[LoadImageFromDir._current_index % len(files)]

        LoadImageFromDir._current_index += 1

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
        image = i.convert("RGB")
        image = np.array(image).astype(np.float32) / 255.0

        # 5. Convert numpy array to torch tensor
        image = torch.from_numpy(image)[None,]

        return (image, mask)