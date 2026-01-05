import torch
import numpy as np
import os
from PIL import Image, ImageOps


class LoadImageFromDir:
    """
    A custom node to load images from a directory.
    Iterates through all images in the folder.
    """

    def __init__(self):
        # Switched to instance variables so multiple nodes don't share the same counter
        self._current_index = 0
        self._last_reset_state = False

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
                "reset_sequence": ("BOOLEAN", {"default": False}),
                "reverse_order": ("BOOLEAN", {"default": False}), # ‼️ Added reverse toggle
            },
        }

    @classmethod
    def IS_CHANGED(s, **kwargs):
        return float("nan")


    RETURN_TYPES = ("IMAGE", "MASK", "STRING")
    RETURN_NAMES = ("image", "mask", "filename")
    FUNCTION = "load_image"
    CATEGORY = "Custom/Image"

    def load_image(self, directory, reset_sequence, reverse_order): # ‼️ Added reverse_order arg
        # Only reset if the boolean changed from False to True (Trigger logic)
        if reset_sequence and not self._last_reset_state:
            self._current_index = 0

        # Update last state
        self._last_reset_state = reset_sequence

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
            ],
            reverse=reverse_order # ‼️ Applied reverse sort based on input
        )

        if not files:
            raise ValueError(f"No valid images found in directory: {directory}")

        # Use self._current_index
        image_path = files[self._current_index % len(files)]


        filename = os.path.basename(image_path)

        self._current_index += 1

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
