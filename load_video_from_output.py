import os
import torch
import numpy as np
import cv2
import folder_paths


def get_output_video_list():
    output_dir = folder_paths.get_output_directory()
    video_extensions = ['.mp4', '.mov', '.avi', '.webm', '.mkv']
    
    files = []
    # Simple recursive search for video files in output
    for root, dirs, files_in_dir in os.walk(output_dir):
        for file in files_in_dir:
            if any(file.lower().endswith(ext) for ext in video_extensions):
                # Create a relative path so the dropdown looks nice
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, output_dir)
                files.append(rel_path)
    

    return sorted(files, reverse=True)

class LoadVideoFromOutput:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):

        file_list = get_output_video_list()
        
        return {
            "required": {
                "video": (file_list,),
                "frame_limit": ("INT", {"default": 0, "min": 0, "max": 10000, "step": 1}),
            },
        }

    RETURN_TYPES = ("IMAGE", "INT")
    RETURN_NAMES = ("images", "frame_count")
    FUNCTION = "load_video"
    CATEGORY = "My Custom Nodes/Video"

    def load_video(self, video, frame_limit):

        video_path = os.path.join(folder_paths.get_output_directory(), video)
        
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
        
        print(f"‼️ Loaded {frame_count} frames from output: {video}")
        return (output_images, frame_count)