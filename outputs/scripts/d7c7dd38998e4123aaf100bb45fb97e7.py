from manim import *

class ParabolaWithMovingPoint(Scene):
    def construct(self):
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[0, 9, 1],
            axis_config={"include_tip": True},
            x_axis_config={"numbers_to_include": [-3, -2, -1, 0, 1, 2, 3]},
            y_axis_config={"numbers_to_include": [0, 1, 4, 9]},
        )
        x_label = axes.get_x_axis_label(Tex("x"))
        y_label = axes.get_y_axis_label(Tex("y"))

        parabola = axes.plot(lambda x: x**2, x_range=[-3, 3], color=BLUE)
        parabola_label = axes.get_graph_label(parabola, label="y = x^2", x_val=2, direction=UR)

        self.play(Create(axes), FadeIn(x_label), FadeIn(y_label))
        self.play(Create(parabola), Write(parabola_label))

        moving_dot = Dot(color=RED)
        self.play(FadeIn(moving_dot))

        def update_dot(mob, alpha):
            x = interpolate(-3, 3, alpha)
            y = x**2
            mob.move_to(axes.coords_to_point(x, y))

        self.play(
            UpdateFromAlphaFunc(moving_dot, update_dot),
            run_time=6,
            rate_func=linear,
        )

        self.wait()