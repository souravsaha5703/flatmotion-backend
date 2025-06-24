from uuid import uuid4
import subprocess
import os

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