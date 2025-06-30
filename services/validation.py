from dotenv import load_dotenv
from config import client
import os

load_dotenv()

allowed_keywords = [
    "animate", "draw", "show", "circle", "square", "move", "rotate",
    "graph", "function", "plot", "scene", "shape", "transform","animation","manim","display"
]

irrelevant_keywords = ["weather", "news", "recipe", "joke", "story", "code", "html"]

def is_prompt_valid(prompt:str) -> bool:
    prompt = prompt.lower()

    if any(word in prompt for word in irrelevant_keywords):
        return False
    
    if any(word in prompt for word in allowed_keywords):
        return True
    
    return is_prompt_valid_gpt(prompt)
    
def is_prompt_valid_gpt(prompt:str) -> bool:
    try:
        response = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a validator for a Manim animation generator. "
                        "Only return 'YES' if the user's prompt describes something that can be animated using Manim, "
                        "such as geometric objects, graphs, or visual scenes. Otherwise, return 'NO'."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=1
        )
        answer = response.choices[0].message.content.strip().upper()
        return answer == "YES"

    except Exception as e:
        print(f"GPT validation failed: {e}")
        return False
    
def validate_prompt(prompt:str = "") -> bool:
    if is_prompt_valid(prompt) == True:
        return True
    else:
        return False