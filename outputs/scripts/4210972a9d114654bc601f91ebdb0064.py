from manim import *

class GreenSquareAnimation(Scene):
    def construct(self):
        # Create a green square
        square = Square(color=GREEN)

        # Initially set the square's opacity to 0 (invisible)
        square.set_opacity(0)

        # Add the square to the scene
        self.add(square)

        # Fade in the square
        self.play(FadeIn(square))

        # Rotate the square 90 degrees clockwise (clockwise rotation is negative angle)
        self.play(Rotate(square, angle=-PI/2))

        # Keep the final frame for a moment
        self.wait()