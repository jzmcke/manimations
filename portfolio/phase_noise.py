from manim import *

config.max_files_cached = -1

BLOCK_SIZE_SAMPLES = 60

seed_noise_sequence = np.random.normal(0, 1.0, BLOCK_SIZE_SAMPLES)
phase_noise = np.cumsum(seed_noise_sequence)

CODE_LEN = 10
BLOCK_SIZE_SAMPLES = 60
CODE_BUF_START = 25
CODE_BUF = np.concatenate([np.repeat(np.random.randint(0, 2, CODE_LEN), 2), np.zeros(BLOCK_SIZE_SAMPLES - CODE_LEN + 1)])

TRANSITIONS = np.where(np.diff(CODE_BUF) != 0)

class PhaseNoiseAnim(Scene):
    def construct(self):        
        title = Text("What is laser phase noise?", font_size=24).move_to([0, 1.25, 0])
        self.play(FadeIn(title))
        self.wait()

        # Draw axis for a sin plot
        ax = Axes(x_range=[0, BLOCK_SIZE_SAMPLES, 1], y_range=[-1, 1], x_length=10, y_length=1.5,
                  x_axis_config={"tick_size": 0.05},
                  tips=False).next_to(title, DOWN, buff=0.5)


        def sin_plot(x):
            def phase_noise(x):
                new_phase = np.random.normal(0, 1.0, 1)
                phase_noise.prev_phase = phase_noise.prev_phase + new_phase

            return np.exp(1j * 3 * x + phase_noise(x)).imag

        def phase_noise(x):
            new_phase = np.random.normal(0, 1.0, 1)[0] * phase_noise.scale
            phase_noise.prev_phase = phase_noise.prev_phase + new_phase
            return phase_noise.prev_phase
        phase_noise.prev_phase = 0
        phase_noise.scale = 0

        def sin_plot(x):
            phase_noise(x)
            return np.exp(1j * 3 * x + 1j * phase_noise(x)).imag

        def modulated_sin_plot(x):
            return np.exp(1j * 3 * x + 1j * phase_noise(x) + 1j * np.pi * CODE_BUF[int(x)]).imag
        
        
        phase_buff = np.array([phase_noise(x) for x in range(10 * BLOCK_SIZE_SAMPLES)])
        
        def code_real(x, phase=phase_buff):
            cplx = CODE_BUF[int(x)] * np.exp(1j * phase[int(x)])
            return cplx.real
        
        def code_imag(x, phase=phase_buff):
            cplx = CODE_BUF[int(x)] * np.exp(1j * phase[int(x)])
            return cplx.imag

        pure_sine_title = Text("This is a pure laser tone", font_size=24).move_to([0, 1.25, 0])
        rx_plot = ax.plot(sin_plot, x_range=[0, BLOCK_SIZE_SAMPLES], color="#CFC7D2", use_smoothing=False)
        self.play(DrawBorderThenFill(ax), Unwrite(title), run_time=1)
        self.wait(0.5)
        self.play(Create(rx_plot), Write(pure_sine_title), run_time=2)
        self.wait(2)
        
        modulated_sine_title = Text("Let's phase modulate it with an in-phase sequence", font_size=24).move_to([0, 3, 0])

        self.play(Unwrite(pure_sine_title), Uncreate(rx_plot), run_time=1)
        self.play(Write(modulated_sine_title), ax.animate.next_to(modulated_sine_title, DOWN, buff=0.5), run_time=1)
        self.wait(0.5)
        
        ax_code_i = Axes(x_range=[0, BLOCK_SIZE_SAMPLES, 1], y_range=[-1, 1], x_length=10, y_length=1.5,
                       x_axis_config={"tick_size": 0.05},
                       tips=False).next_to(ax, DOWN, buff=0.5)
        ax_code_i_labels = ax_code_i.get_axis_labels(y_label=Text("In-phase").scale(0.45))
        self.add(ax_code_i, ax_code_i_labels)
        ax_code_q = Axes(x_range=[0, BLOCK_SIZE_SAMPLES, 1], y_range=[-1, 1], x_length=10, y_length=1.5,
                       x_axis_config={"tick_size": 0.05},
                       tips=False).next_to(ax_code_i, DOWN, buff=0.5)
        ax_code_q_labels = ax_code_q.get_axis_labels(y_label=Text("Quadrature").scale(0.45))
        self.add(ax_code_q, ax_code_q_labels)
        
        modulated_code_plot_i = ax_code_i.plot(lambda x: code_real(x, phase_buff), x_range=[0, BLOCK_SIZE_SAMPLES], color="#FF0000", use_smoothing=False)
        
        modulated_code_plot_q = ax_code_q.plot(lambda x: code_imag(x, phase_buff), x_range=[0, BLOCK_SIZE_SAMPLES], color="#FF0000", use_smoothing=False)

        modulated_rx_plot = ax.plot(modulated_sin_plot, x_range=[0, BLOCK_SIZE_SAMPLES], color="#CFC7D2", use_smoothing=False)
        self.play(Create(modulated_rx_plot),
                  Create(ax_code_i), Create(modulated_code_plot_i),
                  Create(ax_code_q), Create(modulated_code_plot_q),
                  run_time=2)
        self.wait(2)
        
        
        phase_noise.scale = 1/2
        modulated_noisy_rx_plot = ax.plot(modulated_sin_plot, x_range=[0, BLOCK_SIZE_SAMPLES], color="#CFC7D2", use_smoothing=False)

        phase_buff = np.array([phase_noise(x) for x in range(10 * BLOCK_SIZE_SAMPLES)])
        modulated_noisy_code_plot_i = ax_code_i.plot(lambda x: code_real(x, phase_buff), x_range=[0, BLOCK_SIZE_SAMPLES], color="#FF0000", use_smoothing=False)
        modulated_noisy_code_plot_q = ax_code_q.plot(lambda x: code_imag(x, phase_buff), x_range=[0, BLOCK_SIZE_SAMPLES], color="#FF0000", use_smoothing=False)

        noise_sine_title = Text('''Phase noise distorts the waveform, causing the phase to wander unpredictably''', font_size=24).move_to([0, 3, 0])
        self.play(Transform(modulated_rx_plot, modulated_noisy_rx_plot), Transform(modulated_sine_title, noise_sine_title),
                  run_time=2)
        self.wait(2)
        
        noise_baseband_title = Text('''This also rotates and distorts the waveform of the baseband signal''', font_size=24).move_to([0, 3, 0])
        self.play(Unwrite(noise_sine_title), Unwrite(modulated_sine_title), run_time=0.5)
        self.play(Write(noise_baseband_title),
                  Transform(modulated_code_plot_i, modulated_noisy_code_plot_i),
                  Transform(modulated_code_plot_q, modulated_noisy_code_plot_q),
                  run_time=2)
        self.wait(5)
