from manim import *

class ParabolaAnimation(Scene):
    def construct(self):
        plane = NumberPlane(
            x_range=[-3, 3, 1],
            y_range=[-1, 9, 1],
            x_length=6,
            y_length=6,
            axis_config={"include_tip": True},
        )
        plane.add_coordinates()

        self.play(Create(plane))

        parabola = plane.plot(lambda x: x**2, x_range=[-3, 3], color=BLUE)
        self.play(Create(parabola))

        x_label = MathTex("x").next_to(plane.get_x_axis().get_end(), DOWN)
        y_label = MathTex("y").next_to(plane.get_y_axis().get_end(), LEFT)
        self.play(FadeIn(x_label), FadeIn(y_label))

        moving_dot = Dot(color=RED)
        self.play(FadeIn(moving_dot))

        def update_point(mob, dt):
            mob.time += dt
            x = -3 + 6 * (mob.time % 1)
            y = x**2
            mob.move_to(plane.c2p(x, y))

        moving_dot.time = 0
        moving_dot.add_updater(update_point)

        self.wait(6)

        moving_dot.remove_updater(update_point)
        self.wait()