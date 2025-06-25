from manim import *

class HelloManimScene(Scene):
    def construct(self):
        text = Text("Hello Manim!")
        self.play(FadeIn(text))
        self.wait()
        circle = Circle(color=BLUE)
        self.play(Create(circle))
        self.wait()
        self.play(FadeOut(circle))
        self.wait()