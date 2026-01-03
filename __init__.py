from .load_image_from_path import LoadImageFromPath
from .load_image_from_dir import LoadImageFromDir
from .load_single_image_from_path import LoadSingleImageFromPath

# Node Registration
NODE_CLASS_MAPPINGS = {
    "LoadImageFromPath": LoadImageFromPath,
    "LoadImageFromDir": LoadImageFromDir,
    "LoadSingleImageFromPath": LoadSingleImageFromPath,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadImageFromPath": "Local-Loader: Image (Path Sequence)",
    "LoadImageFromDir": "Local-Loader: Image (Directory Sequence)",
    "LoadSingleImageFromPath": "Local-Loader: Single Image (Path)",
}