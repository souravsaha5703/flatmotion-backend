from uuid import uuid4
from pydantic import BaseModel
import subprocess
import os
import shutil

class Video_data(BaseModel):
    video_path: str
    video_id: str

class Script_data(BaseModel):
    script_path_final: str
    script_id_final: str

def calculate_max_tokens(prompt: str, base: int = 300, max_limit: int = 1000) -> int:
    length = len(prompt.split())
    
    if length < 10:
        return 300
    elif length < 30:
        return 500
    elif length < 60:
        return 700
    else:
        return min(max_limit, 900 + (length // 5))


def save_script(script:str) -> Script_data:
    script_id = uuid4().hex
    script_path = f"outputs/scripts/{script_id}.py"
    with open(script_path,"w") as file:
        file.write(script)
    return Script_data(script_path_final=script_path,script_id_final=script_id)

def render_video(script_path:str,script_id:str) -> Video_data:
    filename = uuid4().hex
    output_dir = "outputs/videos"
    command = f"manim {script_path} Animate -o {filename}.mp4 -qk --media_dir outputs"
    subprocess.run(command,shell=True,check=True)
    return Video_data(video_path=f"{output_dir}/{script_id}/2160p60/{filename}.mp4",video_id=filename)

def cleanup_temp_files():
    target_dirs = [
        "outputs/scripts",
        "outputs/videos",
        "outputs/Tex",
        "outputs/texts",
        "outputs/images",
    ]

    for directory in target_dirs:
        if not os.path.exists(directory):
            continue  # Skip if the directory doesn't exist

        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                print(f"Deleted: {item_path}")
            except Exception as e:
                print(f"Failed to delete {item_path}: {e}")