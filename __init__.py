import torch
import numpy as np
from PIL import Image, ImageOps


class LoadImageFromPath:
    """
    A custom node to load an image from a specific file path.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image_path": (
                    "STRING",
                    {"multiline": False, "default": "C:\\path\\to\\image.png"},
                ),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "load_image"
    CATEGORY = "Custom/Image"

    def load_image(self, image_path):
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


# Node Registration
NODE_CLASS_MAPPINGS = {"LoadImageFromPath": LoadImageFromPath}

NODE_DISPLAY_NAME_MAPPINGS = {"LoadImageFromPath": "Load Image (Path)"}
