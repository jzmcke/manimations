from manim import *

config.max_files_cached = -1

CODE_LEN = 20
BLOCK_SIZE_SAMPLES = 60
CODE_BUF_START = 25
CODE = np.random.randint(0, 2, CODE_LEN) * 2 - 1
AXIS_X_LENGTH = 10
RAW_CODE = np.concatenate([np.zeros(CODE_LEN), CODE, np.zeros(BLOCK_SIZE_SAMPLES - CODE_LEN)])
CODE_BUFFER = np.concatenate([np.zeros(CODE_BUF_START), CODE, np.zeros(BLOCK_SIZE_SAMPLES - CODE_BUF_START - CODE_LEN)])
noise = np.random.normal(0, 0.1, BLOCK_SIZE_SAMPLES)

xcorr_calced = np.concatenate([np.convolve(CODE_BUFFER + noise, RAW_CODE[CODE_LEN:(CODE_LEN+CODE_LEN)][::-1]), np.zeros(BLOCK_SIZE_SAMPLES)])

def clean_process(x):
    return CODE_BUFFER[int(x % BLOCK_SIZE_SAMPLES)]

def noise_process(x):
    return CODE_BUFFER[int(x % BLOCK_SIZE_SAMPLES)] + noise[int(x % BLOCK_SIZE_SAMPLES)]


class XcorrAnim(Scene):
    def construct(self):        
        title = Text("Detecting a modulated sequence", font_size=24).move_to([0, 1.25, 0])
        self.play(FadeIn(title))

        # Draw axis for a sin plot
        ax = Axes(x_range=[0, BLOCK_SIZE_SAMPLES, 1], y_range=[-1, 1], x_length=10, y_length=1.5,
                  x_axis_config={"tick_size": 0.05},
                  tips=False).next_to(title, DOWN, buff=0.5)
        
        rx_plot = ax.plot(clean_process, x_range=[0, BLOCK_SIZE_SAMPLES], color="#CFC7D2", use_smoothing=False)
        self.play(DrawBorderThenFill(ax))
        
        new_title = Text("This is a sequence we modulate onto a carrier", font_size=24).move_to([0, 1.25, 0])
        self.play(Create(rx_plot), FadeOut(title), Write(new_title), run_time=2)
    
        group = VGroup(ax, rx_plot, new_title)
        self.play(group.animate.to_edge(UP), run_time=1)
        self.wait(2)
        
        # Corrupt with noise
        noise_title = Text("But it becomes corrupted by noise in the receiver", font_size=24).next_to(ax, UP, buff=0.5)
        rx_plot_new = ax.plot(noise_process, x_range=[0, BLOCK_SIZE_SAMPLES], color="#CFC7D2", use_smoothing=False)
        self.play(Transform(rx_plot, rx_plot_new), FadeOut(new_title), Write(noise_title), run_time=2)
        self.wait(2)
        
        # We can use knowledge of the transmitted code to detect it
        xcorr_title = Text("We can use knowledge of the sequence to detect it", font_size=24).next_to(ax, UP, buff=0.5)
        
        ax_template = Axes(x_range=[0, BLOCK_SIZE_SAMPLES, 1], y_range=[-1, 1], x_length=10, y_length=1.5,
                            x_axis_config={"tick_size": 0.05},
                            tips=False).next_to(ax, DOWN, buff=0.5)

        xcorr_delay = ValueTracker(0)
    
        def raw_code(x):
            return np.roll(RAW_CODE, int(xcorr_delay.get_value()))[int((x + CODE_LEN) % len(RAW_CODE))]

        def xcorr(x):
            return xcorr_calced[int(x + CODE_LEN - 1)]

        code_template = always_redraw(lambda: ax_template.plot(raw_code, x_range=[0, BLOCK_SIZE_SAMPLES], color="#CFC7D2", use_smoothing=False))

        xcorr_ax = Axes(x_range=[0, BLOCK_SIZE_SAMPLES, 1], y_range=[-10, 25], x_length=10, y_length=1.5,
                        x_axis_config={"tick_size": 0.05},
                        y_axis_config={"include_ticks": False},
                        tips=False).next_to(ax_template, DOWN, buff=0.5)

        xcorr_out = always_redraw(lambda: xcorr_ax.plot(xcorr, x_range=[0, BLOCK_SIZE_SAMPLES], color="#CFC7D2", use_smoothing=False))
        self.play(Transform(noise_title, xcorr_title), run_time=0.5)
        self.play(Create(code_template), Create(ax_template), Create(xcorr_ax), run_time=1)
        self.wait(2)

        self.play(xcorr_delay.animate.set_value(BLOCK_SIZE_SAMPLES), Create(xcorr_out), run_time=10, rate_func=linear)
        self.wait(2)

        self.play(FadeOut(code_template), FadeOut(ax_template), FadeOut(ax), FadeOut(rx_plot), xcorr_ax.animate.to_edge(UP, buff=2.0), run_time=1.0)
        
        arr = Arrow(start=[0, -0.5, 0],
              end=[xcorr_ax.coords_to_point(CODE_BUF_START, xcorr(CODE_BUF_START))[0],
                   xcorr_ax.coords_to_point(CODE_BUF_START, xcorr(CODE_BUF_START))[1],
                   0],
              color="#FE4A49")
        
        info = Text("The peak location determines how far away the object is", font_size=24).next_to(arr, DOWN, buff=0.5)
        self.play(Create(arr), Write(info), run_time=2)
        self.wait(2)
