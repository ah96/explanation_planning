# planning_gui_refactor.py

import tkinter as tk
from tkinter import ttk
import time
import threading
import subprocess
import re
import os
from planner import PlanExecutor, PlannerInterface, RDDLAnalyzer

class PlanningGUI:
    def __init__(self, root):
        # Setup the main application window
        self.root = root
        self.root.title("AI Planning Control Panel")
        self.root.geometry("900x600")
        self.root.configure(bg="#f2f2f2")

        # Initialize the planner interfaces
        self.planner = PlannerInterface()
        self.executor = PlanExecutor(self)
        self.rddl_analyzer = RDDLAnalyzer()

        # Holds the currently loaded plan
        self.current_plan = []

        # Define UI styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        style.configure("TLabel", font=("Segoe UI", 10), background="#f2f2f2")

        self.build_ui()  # Build the GUI

    def build_ui(self):
        # Root frame layout
        frame = ttk.Frame(self.root)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        # === STRATEGY BUTTONS ===
        strategy_frame = ttk.LabelFrame(frame, text="Planning Strategies")
        strategy_frame.grid(row=0, column=0, sticky="nsw", padx=10, pady=10)

        # Each button triggers a different planning strategy
        ttk.Button(strategy_frame, text="Pre-hoc", width=20, command=self.run_pre_hoc).grid(row=0, column=0, pady=5)
        ttk.Button(strategy_frame, text="Reactive", width=20, command=self.run_reactive).grid(row=1, column=0, pady=5)
        ttk.Button(strategy_frame, text="Post-hoc", width=20, command=self.run_post_hoc).grid(row=2, column=0, pady=5)
        ttk.Button(strategy_frame, text="Mixed-Initiative", width=20, command=self.run_mixed_initiative).grid(row=3, column=0, pady=5)
        ttk.Button(strategy_frame, text="Anytime", width=20, command=self.run_anytime).grid(row=4, column=0, pady=5)
        ttk.Button(strategy_frame, text="Replay with Log", width=20, command=self.run_replay_log).grid(row=5, column=0, pady=5)
        ttk.Button(strategy_frame, text="Compare Plans", width=20, command=self.run_compare).grid(row=6, column=0, pady=5)

        # === PLAN DISPLAY AREA ===
        display_frame = ttk.LabelFrame(frame, text="Generated Plan")
        display_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(0, weight=1)

        self.plan_text = tk.Text(display_frame, width=60, height=20, font=("Consolas", 10))
        self.plan_text.pack(padx=10, pady=10, fill="both", expand=True)

        # === EXECUTION CONTROLS ===
        control_frame = ttk.LabelFrame(frame, text="Plan Execution Controls")
        control_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        # Execution speed slider
        ttk.Label(control_frame, text="Action Duration (seconds):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.duration_var = tk.DoubleVar(value=1.0)
        ttk.Scale(control_frame, from_=0.5, to=5.0, variable=self.duration_var, orient="horizontal", length=200).grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # Buttons for execution control
        ttk.Button(control_frame, text="Execute Plan", command=self.execute_and_log).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        ttk.Button(control_frame, text="Pause", command=self.executor.pause_execution).grid(row=1, column=1, padx=10, pady=10, sticky="w")
        ttk.Button(control_frame, text="Continue", command=self.executor.continue_execution).grid(row=1, column=2, padx=10, pady=10, sticky="w")
        ttk.Button(control_frame, text="Stop", command=self.executor.stop_execution).grid(row=1, column=3, padx=10, pady=10, sticky="w")

        # Label to show currently executing action
        self.current_action_label = ttk.Label(control_frame, text="Current Action: None")
        self.current_action_label.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="w")

    def display(self, text):
        """Display a list of lines in the plan display area."""
        self.plan_text.delete("1.0", tk.END)
        self.plan_text.insert(tk.END, "\n".join(text))

    def save_plan_to_log(self):
        """Save current plan to a log file for replaying later."""
        os.makedirs("./plans", exist_ok=True)
        with open("./plans/executed_plan.txt", "w") as f:
            for action in self.current_plan:
                f.write(action + "\n")

    def execute_and_log(self):
        """Save the plan and start executing it."""
        self.save_plan_to_log()
        self.executor.start_execution()

    def run_pre_hoc(self):
        """Generate and display a pre-hoc plan."""
        self.display(["Running PROST (Pre-hoc)..."])
        self.root.update_idletasks()
        self.current_plan = self.planner.generate_plan("instance_prehoc")
        self.display(["Plan:"] + self.current_plan)

    def run_reactive(self):
        """Simulate failure detection and replan reactively."""
        self.display(["Generating Initial Plan (Reactive)..."])
        self.root.update_idletasks()
        pre_plan = self.planner.generate_plan("instance_posthoc")

        # If failure is detected in initial plan
        for action in pre_plan:
            if 'failure' in action:
                self.display(["Failure occurred at: " + action])
                self.root.update_idletasks()
                break

        self.display(["Replanning..."])
        self.root.update_idletasks()
        self.current_plan = self.planner.generate_plan("instance_reactive")
        self.display(["Replanned:"] + self.current_plan)

    def run_post_hoc(self):
        """Generate a plan and then add explanation based on outcome."""
        self.display(["Running PROST (Post-hoc)..."])
        self.root.update_idletasks()
        plan = self.planner.generate_plan("instance_posthoc")
        plan_with_response = self.rddl_analyzer.insert_explanation(plan, "./testbed/benchmarks/explanation_planning/problem_posthoc.rddl")
        self.current_plan = plan_with_response
        self.display(["Plan with explanation:"] + self.current_plan)

    def run_mixed_initiative(self):
        """Generate multiple options and pick the first (simulated user input)."""
        options = self.planner.generate_alternative_plans("instance_mixed")
        self.current_plan = options[0]
        self.display(["Option 1:"] + options[0])

    def run_anytime(self):
        """Generate a plan under time constraints (best-effort)."""
        self.display(["Generating Anytime Plan..."])
        self.current_plan = self.planner.generate_anytime_plan("instance_anytime", timeout=3)
        self.display(["Anytime Plan:"] + self.current_plan)

    def run_replay_log(self):
        """Replay a plan that was saved earlier."""
        self.current_plan = self.planner.load_from_log("./plans/executed_plan.txt")
        self.display(["Replaying Plan:"] + self.current_plan)

    def run_compare(self):
        """Compare multiple strategies (pre, reactive, post) side-by-side."""
        plans = self.planner.compare_strategies()
        combined = ["Pre-hoc:"] + plans['pre'] + ["", "Reactive:"] + plans['reactive'] + ["", "Post-hoc:"] + plans['post']
        self.display(combined)


if __name__ == "__main__":
    # Launch the GUI
    root = tk.Tk()
    app = PlanningGUI(root)
    root.mainloop()
