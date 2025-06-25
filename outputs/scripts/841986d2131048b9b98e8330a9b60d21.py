from manim import *

class ParabolaAnimation(Scene):
    def construct(self):
        # Create axes with labels
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[0, 9, 1],
            x_length=6,
            y_length=6,
            axis_config={"include_tip": True},
            x_axis_config={"numbers_to_include": [-3, -2, -1, 0, 1, 2, 3]},
            y_axis_config={"numbers_to_include": [0, 1, 4, 9]},
        )
        x_label = axes.get_x_axis_label("x")
        y_label = axes.get_y_axis_label("y")

        # Define the parabola function
        parabola = axes.plot(lambda x: x**2, x_range=[-3, 3], color=BLUE)

        # Create a dot that will move along the parabola
        moving_dot = Dot(color=RED)

        # Set initial position of the dot
        moving_dot.move_to(axes.c2p(-3, (-3)**2))

        # Add axes, labels, and parabola with animations
        self.play(Create(axes), FadeIn(x_label), FadeIn(y_label))
        self.play(Create(parabola))
        self.play(FadeIn(moving_dot))

        # Create an updater function for the dot to move along the parabola
        def update_dot(mob, alpha):
            x = -3 + 6 * alpha  # x goes from -3 to 3
            y = x**2
            mob.move_to(axes.c2p(x, y))

        # Animate the dot moving along the parabola
        self.play(UpdateFromAlphaFunc(moving_dot, update_dot), run_time=6)

        self.wait()