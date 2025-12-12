from .load_image_from_path import LoadImageFromPath
from .load_image_from_dir import LoadImageFromDir

# Node Registration
NODE_CLASS_MAPPINGS = {
    "LoadImageFromPath": LoadImageFromPath,
    "LoadImageFromDir": LoadImageFromDir,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadImageFromPath": "Local-Loader: Image (Path Sequence)",
    "LoadImageFromDir": "Local-Loader: Image (Directory Sequence)",
}

