from manim import *
from scipy.signal import argrelextrema

config.max_files_cached = -1

CODE_LEN = 20
BLOCK_SIZE_SAMPLES = 60
CODE_BUF_START = 25
CODE = np.random.randint(0, 2, CODE_LEN) * 2 - 1
AXIS_X_LENGTH = 10
RAW_CODE = np.concatenate([np.zeros(CODE_LEN), CODE, np.zeros(BLOCK_SIZE_SAMPLES - CODE_LEN)])
CODE_BUFFER = np.concatenate([np.zeros(CODE_BUF_START), CODE, np.zeros(BLOCK_SIZE_SAMPLES - CODE_BUF_START - CODE_LEN)])


def clean_process(x):
    return CODE_BUFFER[int(x % BLOCK_SIZE_SAMPLES)]




class FalseAlarmAnim(Scene):
    def construct(self):        
        title = Text("Here is our noisy sequence again.", font_size=24).to_edge(UP, buff=1.0)
        self.play(FadeIn(title))

        noise_level = ValueTracker(0.1)
        signal_level = ValueTracker(1.0)
        def noise_process(x):
            noise = np.random.normal(0, 1.0, BLOCK_SIZE_SAMPLES)
            if isinstance(x, np.ndarray):
                return signal_level.get_value() * CODE_BUFFER[x.astype(int) % BLOCK_SIZE_SAMPLES] + noise_level.get_value() * noise[x.astype(int) % BLOCK_SIZE_SAMPLES]
            else:
                return signal_level.get_value() * CODE_BUFFER[int(x % BLOCK_SIZE_SAMPLES)] + noise_level.get_value() * noise[int(x % BLOCK_SIZE_SAMPLES)]

        # Draw axis for a received plot
        ax = Axes(x_range=[0, BLOCK_SIZE_SAMPLES, 1], y_range=[-1, 1], x_length=10, y_length=2,
                  x_axis_config={"tick_size": 0.05},
                  tips=False).next_to(title, DOWN, buff=1)
        
        rx_plot = always_redraw(lambda: ax.plot(noise_process, x_range=[0, BLOCK_SIZE_SAMPLES], color="#CFC7D2", use_smoothing=False))

        xcorr_ax = Axes(x_range=[0, BLOCK_SIZE_SAMPLES, 1], y_range=[-10, 25], x_length=10, y_length=2,
                        x_axis_config={"tick_size": 0.05},
                        y_axis_config={"include_ticks": False},
                        tips=False).next_to(ax, DOWN, buff=1)

        def xcorr(x):
            noise_seq = noise_process(np.arange(BLOCK_SIZE_SAMPLES))
            xcorr_calced = np.concatenate([np.convolve(noise_seq, RAW_CODE[CODE_LEN:(CODE_LEN+CODE_LEN)][::-1]), np.zeros(BLOCK_SIZE_SAMPLES)])
            if isinstance(x, np.ndarray):
                return xcorr_calced[x.astype(int) + CODE_LEN - 1]
            else:
                return xcorr_calced[int(x + CODE_LEN - 1)]

        xcorr_out = always_redraw(lambda: xcorr_ax.plot(xcorr, x_range=[0, BLOCK_SIZE_SAMPLES], color="#CFC7D2", use_smoothing=False))

        self.play(DrawBorderThenFill(ax), DrawBorderThenFill(xcorr_ax))
        self.play(Create(rx_plot), Create(xcorr_out), run_time=1)
        self.wait(1)
        
        noise_motiv_title = Text("But what happens as the SNR decreases?", font_size=24).to_edge(UP, buff=1.0)
        
        self.play(FadeOut(title), run_time=1)
        self.play(Write(noise_motiv_title), run_time=2)
        self.wait(1)
        self.play(Unwrite(noise_motiv_title), run_time=1)
        
        xcorr_title = Text("... The peak becomes harder to locate", font_size=24).to_edge(UP, buff=1)
        self.play(noise_level.animate.set_value(0.2), signal_level.animate.set_value(0.5), Write(xcorr_title), rate_func=linear, run_time=2)
        self.play(noise_level.animate.set_value(0.5), signal_level.animate.set_value(0.05), run_time=6)

        threshold_motivation_title =  Text("How do we distinguish our target...", font_size=24).to_edge(UP, buff=1)
        
        self.play(Unwrite(xcorr_title), run_time=0.5)

        target_arrow = Arrow(start=threshold_motivation_title.get_center(),
              end=[xcorr_ax.coords_to_point(CODE_BUF_START, xcorr(CODE_BUF_START))[0],
                   xcorr_ax.coords_to_point(CODE_BUF_START, xcorr(CODE_BUF_START))[1],
                   0],
              color="#00FF00")

        self.play(Write(threshold_motivation_title), FadeIn(target_arrow), run_time=2)
        self.play(Unwrite(threshold_motivation_title), FadeOut(target_arrow), run_time=1)

        threshold_motivation_title_p2 =  Text("... from all of the false peaks?", font_size=24).to_edge(UP, buff=1)
        
        xcorr_seq = xcorr(np.arange(BLOCK_SIZE_SAMPLES))
        local_max = argrelextrema(xcorr_seq, np.greater)

        noise_arrow = Arrow(start=threshold_motivation_title_p2.get_center(),
              end=[xcorr_ax.coords_to_point(local_max[0][5], xcorr_seq[local_max[0][5]])[0],
                   xcorr_ax.coords_to_point(local_max[0][5], xcorr_seq[local_max[0][5]])[1],
                   0],
              color="#FF0000")

        noise_arrow2 = Arrow(start=threshold_motivation_title_p2.get_center(),
              end=[xcorr_ax.coords_to_point(local_max[0][-5], xcorr_seq[local_max[0][-5]])[0],
                   xcorr_ax.coords_to_point(local_max[0][-5], xcorr_seq[local_max[0][-5]])[1],
                   0],
              color="#FF0000")

        self.play(Write(threshold_motivation_title_p2), FadeIn(noise_arrow), FadeIn(noise_arrow2), run_time=2) 
        self.wait(1)
