from manim import *

class GreenSquareRotation(Scene):
    def construct(self):
        square = Square(color=GREEN)
        self.play(FadeIn(square))
        self.play(Rotate(square, angle=-PI/2))
        self.wait()