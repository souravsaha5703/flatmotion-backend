from uuid import uuid4
import subprocess
import os

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


def save_script(script:str) -> str:
    script_id = uuid4().hex
    script_path = f"outputs/scripts/{script_id}.py"
    with open(script_path,"w") as file:
        file.write(script)
    return script_path

def render_video(script_path:str) -> str:
    filename = uuid4().hex
    output_dir = "outputs/videos"
    command = f"manim {script_path} Animate -o {filename}.mp4 -qk --media_dir outputs"
    subprocess.run(command,shell=True,check=True)
    return f"{output_dir}/{filename}.mp4"

def get_video_url(video_path:str) -> str:
    filename = os.path.basename(video_path)
    return f"/videos/{filename}"