import torch
import numpy as np
from PIL import Image, ImageOps



class LoadImageFromPath:
    """
    A custom node to load an image from a specific file path.
    Now supports multiple paths and iterates through them.
    """

    _current_index = 0

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "file_paths": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "C:\\path\\to\\image1.png\nC:\\path\\to\\image2.png",
                    },
                ),
            },
        }

    # This allows the counter to increment on each queue even if inputs haven't changed.
    @classmethod
    def IS_CHANGED(s, **kwargs):
        return float("nan")

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "load_image"
    CATEGORY = "Custom/Image"

    def load_image(self, file_paths):
        paths = [p.strip() for p in file_paths.split("\n") if p.strip()]

        if not paths:
            raise ValueError("No valid file paths provided.")

        image_path = paths[LoadImageFromPath._current_index % len(paths)]

        LoadImageFromPath._current_index += 1

        # 1. Open the image using PIL
        try:
            i = Image.open(image_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"The file at {image_path} could not be found.")
        except Exception as e:
            raise Exception(f"Error opening image: {e}")

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

        # 5. Convert numpy array to torch tensor (ComfyUI format: Batch, Height, Width, Channels)
        image = torch.from_numpy(image)[None,]

        return (image, mask)