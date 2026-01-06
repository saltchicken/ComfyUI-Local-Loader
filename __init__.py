from .load_image_from_path import LoadImageFromPath
from .load_image_from_dir import LoadImageFromDir
from .load_single_image_from_path import LoadSingleImageFromPath
from .load_video_from_output import LoadVideoFromOutput, get_output_video_list

from .load_image_from_output import LoadImageFromOutput, get_output_dirs, get_images_in_dir
from server import PromptServer
from aiohttp import web

@PromptServer.instance.routes.get("/my_custom_nodes/refresh_video_list")
async def refresh_video_list(request):
    files = get_output_video_list()
    return web.json_response(files)


@PromptServer.instance.routes.get("/my_custom_nodes/output_directories")
async def get_output_directories(request):
    dirs = get_output_dirs()
    return web.json_response(dirs)


@PromptServer.instance.routes.get("/my_custom_nodes/output_images")
async def get_output_images(request):
    # Get 'dir' from query parameters (default to empty string for root)
    target_dir = request.rel_url.query.get("dir", "")
    files = get_images_in_dir(target_dir)
    return web.json_response(files)

# Node Registration
NODE_CLASS_MAPPINGS = {
    "LoadImageFromPath": LoadImageFromPath,
    "LoadImageFromDir": LoadImageFromDir,
    "LoadSingleImageFromPath": LoadSingleImageFromPath,
    "LoadVideoFromOutput": LoadVideoFromOutput,
    "LoadImageFromOutput": LoadImageFromOutput,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadImageFromPath": "Local-Loader: Image (Path Sequence)",
    "LoadImageFromDir": "Local-Loader: Image (Directory Sequence)",
    "LoadSingleImageFromPath": "Local-Loader: Single Image (Path)",
    "LoadVideoFromOutput": "Load Video (From Output)",
    "LoadImageFromOutput": "Load Image (From Output)",
}

WEB_DIRECTORY = "./js"