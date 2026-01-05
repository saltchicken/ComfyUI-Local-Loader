from .load_image_from_path import LoadImageFromPath
from .load_image_from_dir import LoadImageFromDir
from .load_single_image_from_path import LoadSingleImageFromPath
from .load_video_from_output import LoadVideoFromOutput

# Node Registration
NODE_CLASS_MAPPINGS = {
    "LoadImageFromPath": LoadImageFromPath,
    "LoadImageFromDir": LoadImageFromDir,
    "LoadSingleImageFromPath": LoadSingleImageFromPath,
    "LoadVideoFromOutput": LoadVideoFromOutput,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadImageFromPath": "Local-Loader: Image (Path Sequence)",
    "LoadImageFromDir": "Local-Loader: Image (Directory Sequence)",
    "LoadSingleImageFromPath": "Local-Loader: Single Image (Path)",
    "LoadVideoFromOutput": "Load Video (From Output)",
}
