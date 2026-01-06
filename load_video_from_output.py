import os
import torch
import numpy as np
import cv2
import folder_paths


def get_video_output_dirs():
    output_dir = folder_paths.get_output_directory()
    dirs = [""] # Represents the root output directory
    
    if not os.path.exists(output_dir):
        return dirs

    for root, subdirs, files in os.walk(output_dir):
        for d in subdirs:
            full_path = os.path.join(root, d)
            rel_path = os.path.relpath(full_path, output_dir)
            dirs.append(rel_path)
            
    return sorted(dirs)


def get_videos_in_dir(subdir):
    output_dir = folder_paths.get_output_directory()
    
    if subdir == "":
        target_dir = output_dir
    else:
        target_dir = os.path.join(output_dir, subdir)

    if not os.path.exists(target_dir):
        return []

    video_extensions = {'.mp4', '.mov', '.avi', '.webm', '.mkv'}
    files = []
    
    try:
        for f in os.listdir(target_dir):
            if os.path.isfile(os.path.join(target_dir, f)):
                if any(f.lower().endswith(ext) for ext in video_extensions):
                    files.append(f)
    except Exception:
        pass

    return sorted(files, reverse=True)


class LoadVideoFromOutput:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):

        directories = get_video_output_dirs()
        
        # Default to root or first available
        first_dir = directories[0] if directories else ""
        videos = get_videos_in_dir(first_dir)
        
        return {
            "required": {
                "directory": (directories,),
                "video": (videos,),
                "frame_limit": ("INT", {"default": 0, "min": 0, "max": 10000, "step": 1}),
                "force_reload": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("IMAGE", "INT")
    RETURN_NAMES = ("images", "frame_count")
    FUNCTION = "load_video"
    CATEGORY = "My Custom Nodes/Video"

    @classmethod
    def IS_CHANGED(s, directory, video, frame_limit, force_reload):

        video_path = os.path.join(folder_paths.get_output_directory(), directory, video)
        
        if force_reload:
            return float("nan")
            
        if not os.path.exists(video_path):
            return float("nan")

        return os.path.getmtime(video_path)

    def load_video(self, directory, video, frame_limit, force_reload):

        video_path = os.path.join(folder_paths.get_output_directory(), directory, video)
        
        cap = cv2.VideoCapture(video_path)
        frames = []
        
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Stop if we hit the user-defined limit
            if frame_limit > 0 and frame_count >= frame_limit:
                break

            # Convert BGR (OpenCV standard) to RGB (ComfyUI standard)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Normalize to 0-1 range (ComfyUI expects floats 0-1 for images)
            frame = frame.astype(np.float32) / 255.0
            
            # Convert to Tensor
            frame_tensor = torch.from_numpy(frame)
            frames.append(frame_tensor)
            frame_count += 1
            
        cap.release()

        if len(frames) == 0:
            raise FileNotFoundError(f"Could not load video or video is empty: {video_path}")

        # Stack frames into batch: (Batch_Size, Height, Width, Channels)
        output_images = torch.stack(frames)
        
        print(f"Loaded {frame_count} frames from output: {os.path.join(directory, video)}")
        return (output_images, frame_count)