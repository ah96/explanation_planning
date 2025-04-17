import tkinter as tk
from tkinter import ttk, filedialog
import time
import threading
import subprocess
import re
import os
from planner import PlanExecutor, PlannerInterface, RDDLAnalyzer
import prehoc
import posthoc
import start_rosplan
import reactive_rosplan
import signal

class PlanningGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Planning Control Panel")
        self.root.geometry("900x600")
        self.root.configure(bg="#f2f2f2")

        self.planner = PlannerInterface()
        self.executor = PlanExecutor(self)
        self.rddl_analyzer = RDDLAnalyzer()
        self.current_plan = []

        self.domain_file = tk.StringVar(value="./domain.rddl")
        self.instance_file = tk.StringVar(value="./instance_failures_responses.rddl")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        style.configure("TLabel", font=("Segoe UI", 10), background="#f2f2f2")

        self.build_ui()

    def build_ui(self):
        frame = ttk.Frame(self.root)
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        frame.columnconfigure(0, weight=0)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=0)

        # === Strategy Buttons ===
        strategy_frame = ttk.LabelFrame(frame, text="Planning Strategies")
        strategy_frame.grid(row=0, column=0, sticky="ns", padx=(0, 10), pady=5)

        ttk.Button(strategy_frame, text="Initialize", width=20, command=self.initialize).pack(pady=5, fill="x")
        ttk.Button(strategy_frame, text="Pre-hoc", width=20, command=self.run_pre_hoc).pack(pady=5, fill="x")
        ttk.Button(strategy_frame, text="Reactive", width=20, command=self.run_reactive).pack(pady=5, fill="x")
        ttk.Button(strategy_frame, text="Post-hoc", width=20, command=self.run_post_hoc).pack(pady=5, fill="x")

        # === File Selection ===
        file_frame = ttk.LabelFrame(frame, text="Domain & Instance")
        file_frame.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=5)

        ttk.Button(file_frame, text="Select Domain File", command=self.select_domain_file).pack(fill="x", pady=3)
        ttk.Label(file_frame, textvariable=self.domain_file, wraplength=200).pack(fill="x")

        ttk.Button(file_frame, text="Select Instance File", command=self.select_instance_file).pack(fill="x", pady=3)
        ttk.Label(file_frame, textvariable=self.instance_file, wraplength=200).pack(fill="x")

        # === Plan Display ===
        display_frame = ttk.LabelFrame(frame, text="Generated Plan")
        display_frame.grid(row=0, column=1, sticky="nsew", pady=5)

        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)

        text_frame = ttk.Frame(display_frame)
        text_frame.grid(row=0, column=0, sticky="nsew")
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.plan_text = tk.Text(text_frame, wrap="word", font=("Consolas", 10), yscrollcommand=scrollbar.set)
        self.plan_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.config(command=self.plan_text.yview)
        self.plan_text.config(state='disabled')

        # === Execution Controls ===
        control_frame = ttk.LabelFrame(frame, text="Plan Execution Controls")
        control_frame.grid(row=1, column=1, sticky="ew", pady=5)

        for i in range(4):
            control_frame.columnconfigure(i, weight=1)

        ttk.Label(control_frame, text="Action Duration (seconds):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.duration_var = tk.DoubleVar(value=1.0)
        ttk.Scale(control_frame, from_=0.5, to=5.0, variable=self.duration_var, orient="horizontal", length=200).grid(row=0, column=1, padx=10, pady=5, sticky="w")

        ttk.Button(control_frame, text="Execute Plan", command=self.execute_and_log).grid(row=1, column=0, padx=10, pady=10)
        ttk.Button(control_frame, text="Pause", command=self.executor.pause_execution).grid(row=1, column=1, padx=10, pady=10)
        ttk.Button(control_frame, text="Continue", command=self.executor.continue_execution).grid(row=1, column=2, padx=10, pady=10)
        ttk.Button(control_frame, text="Stop", command=self.executor.stop_execution).grid(row=1, column=3, padx=10, pady=10)

        self.current_action_label = ttk.Label(control_frame, text="Current Action: None")
        self.current_action_label.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="w")

    def select_domain_file(self):
        path = filedialog.askopenfilename(filetypes=[("RDDL files", "*.rddl")])
        if path:
            self.domain_file.set(path)

    def select_instance_file(self):
        path = filedialog.askopenfilename(filetypes=[("RDDL files", "*.rddl")])
        if path:
            self.instance_file.set(path)

    def display(self, text):
        MAX_LINES = 300
        lines = text if isinstance(text, list) else text.splitlines()
        if len(lines) > MAX_LINES:
            lines = lines[:MAX_LINES]
            lines.append("...[output truncated due to display limits]")

        self.plan_text.config(state='normal')
        self.plan_text.delete("1.0", tk.END)
        self.plan_text.insert(tk.END, "\n".join(lines))
        self.plan_text.config(state='disabled')

    def display_incrementally(self, lines, delay=10):
        self.plan_text.config(state='normal')
        self.plan_text.delete("1.0", tk.END)

        def add_line(i=0):
            if i < len(lines):
                self.plan_text.insert(tk.END, lines[i] + "\n")
                self.plan_text.see(tk.END)
                self.root.after(delay, add_line, i + 1)
            else:
                self.plan_text.config(state='disabled')

        add_line()

    def save_plan_to_log(self):
        os.makedirs("./plans", exist_ok=True)
        with open("./plans/executed_plan.txt", "w") as f:
            for action in self.current_plan:
                f.write(action + "\n")

    def execute_and_log(self):
        self.save_plan_to_log()
        self.executor.start_execution()

    def initialize(self):
        #start_rosplan.main()

        self.roslaunch_proc = self.launch_rosplan()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def launch_rosplan(self):
        print("Launching ROSPlan (explanation_planning.launch)...")
        return subprocess.Popen(
            ["roslaunch", "explanation_planning.launch"],
            preexec_fn=os.setsid  # Ensures we can kill the whole process group
    )

    def on_close(self):
        print("Closing GUI and shutting down ROSPlan...")

        # Kill roslaunch and all its child nodes
        if self.roslaunch_proc and self.roslaunch_proc.poll() is None:
            os.killpg(os.getpgid(self.roslaunch_proc.pid), signal.SIGTERM)
            self.roslaunch_proc.wait()

        self.root.destroy()

    def run_pre_hoc(self):
        self.display_incrementally(["Running Pre-hoc Planner..."])
        self.root.update_idletasks()

        def run():
            from io import StringIO
            import sys
            old_stdout = sys.stdout
            sys.stdout = mystdout = StringIO()
            self.current_plan = prehoc.main_gui(domain_path=self.domain_file.get(), instance_path=self.instance_file.get())
            sys.stdout = old_stdout
            output = mystdout.getvalue()
            #self.current_plan = re.findall(r"[a-z_]+\([^)]*\)", output)
            self.display_incrementally(output.splitlines())

        threading.Thread(target=run).start()

    def run_post_hoc(self):
        self.display_incrementally(["Running Post-hoc Planner..."])
        self.root.update_idletasks()

        def run():
            from io import StringIO
            import sys
            old_stdout = sys.stdout
            sys.stdout = mystdout = StringIO()
            self.current_plan = posthoc.main_gui(domain_path=self.domain_file.get(), instance_path=self.instance_file.get())
            sys.stdout = old_stdout
            output = mystdout.getvalue()
            #self.current_plan = re.findall(r"[a-z_]+\([^)]*\)", output)
            self.display_incrementally(output.splitlines())

        threading.Thread(target=run).start()

    def run_reactive(self):
        self.display_incrementally(["Running Reactive Planner..."])
        self.root.update_idletasks()

        def run():
            from io import StringIO
            import sys
            old_stdout = sys.stdout
            sys.stdout = mystdout = StringIO()
            self.current_plan = reactive_rosplan.main_gui(domain_path=self.domain_file.get(), instance_path=self.instance_file.get())
            sys.stdout = old_stdout
            output = mystdout.getvalue()
            #self.current_plan = re.findall(r"[a-z_]+\([^)]*\)", output)
            self.display_incrementally(output.splitlines())

        #threading.Thread(target=run).start()
        run()


if __name__ == "__main__":
    root = tk.Tk()
    app = PlanningGUI(root)
    root.mainloop()
