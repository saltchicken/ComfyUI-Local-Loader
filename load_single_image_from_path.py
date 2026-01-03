import torch
import numpy as np
import os
from PIL import Image, ImageOps


class LoadSingleImageFromPath:
    """
    A custom node to load a single image from a specific file path.
    Does not iterate or maintain an internal counter.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image_path": (
                    "STRING",
                    {
                        "multiline": False,
                        "default": "C:\\path\\to\\image.png",
                    },
                ),
            },
        }

    @classmethod
    def IS_CHANGED(s, image_path):

        # If the file on disk changes, the node will re-execute.
        if not os.path.exists(image_path):
            return float("nan")
        return os.path.getmtime(image_path)

    RETURN_TYPES = ("IMAGE", "MASK", "STRING")
    RETURN_NAMES = ("image", "mask", "filename")
    FUNCTION = "load_image"
    CATEGORY = "Custom/Image"

    def load_image(self, image_path):
        # Remove quotes if user added them by mistake
        image_path = image_path.strip('"')

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"File not found: {image_path}")

        filename = os.path.basename(image_path)

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

        return (image, mask, filename)