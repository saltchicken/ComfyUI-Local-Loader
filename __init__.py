from .load_image_from_path import LoadImageFromPath
from .load_image_from_dir import LoadImageFromDir
from .load_single_image_from_path import LoadSingleImageFromPath

from .load_video_from_output import LoadVideoFromOutput, get_video_output_dirs, get_videos_in_dir
from .load_image_from_output import LoadImageFromOutput, get_output_dirs, get_images_in_dir
from server import PromptServer
from aiohttp import web

# --- Image Routes ---

@PromptServer.instance.routes.get("/my_custom_nodes/output_directories")
async def get_output_directories(request):
    dirs = get_output_dirs()
    return web.json_response(dirs)

@PromptServer.instance.routes.get("/my_custom_nodes/output_images")
async def get_output_images(request):
    target_dir = request.rel_url.query.get("dir", "")
    files = get_images_in_dir(target_dir)
    return web.json_response(files)




@PromptServer.instance.routes.get("/my_custom_nodes/output_video_directories")
async def get_output_video_directories(request):
    dirs = get_video_output_dirs()
    return web.json_response(dirs)


@PromptServer.instance.routes.get("/my_custom_nodes/output_videos")
async def get_output_videos(request):
    target_dir = request.rel_url.query.get("dir", "")
    files = get_videos_in_dir(target_dir)
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