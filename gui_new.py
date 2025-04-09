# planning_gui_refactor.py

import tkinter as tk
from tkinter import ttk
import time
import threading
import subprocess
import re
from planner import PlanExecutor, PlannerInterface, RDDLAnalyzer

class PlanningGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Planning GUI")

        self.planner = PlannerInterface()
        self.executor = PlanExecutor(self)
        self.rddl_analyzer = RDDLAnalyzer()

        self.current_plan = []

        self.build_ui()

    def build_ui(self):
        ttk.Label(self.root, text="Select Planning Type:").grid(row=0, column=0, padx=10, pady=10, sticky="W")
        ttk.Button(self.root, text="Pre-hoc", command=self.run_pre_hoc).grid(row=1, column=0, padx=10, pady=5, sticky="W")
        ttk.Button(self.root, text="Reactive", command=self.run_reactive).grid(row=2, column=0, padx=10, pady=5, sticky="W")
        ttk.Button(self.root, text="Post-hoc", command=self.run_post_hoc).grid(row=3, column=0, padx=10, pady=5, sticky="W")
        ttk.Button(self.root, text="Mixed-Initiative", command=self.run_mixed_initiative).grid(row=4, column=0, padx=10, pady=5, sticky="W")
        ttk.Button(self.root, text="Anytime", command=self.run_anytime).grid(row=5, column=0, padx=10, pady=5, sticky="W")
        ttk.Button(self.root, text="Replay with Log", command=self.run_replay_log).grid(row=6, column=0, padx=10, pady=5, sticky="W")
        ttk.Button(self.root, text="Compare Plans", command=self.run_compare).grid(row=7, column=0, padx=10, pady=5, sticky="W")

        ttk.Label(self.root, text="Generated Plan:").grid(row=0, column=1, padx=10, pady=10, sticky="W")
        self.plan_text = tk.Text(self.root, width=60, height=15)
        self.plan_text.grid(row=1, column=1, rowspan=7, padx=10, pady=5)

        ttk.Label(self.root, text="Plan Execution:").grid(row=8, column=0, padx=10, pady=10, sticky="W")
        ttk.Label(self.root, text="Action Duration (seconds):").grid(row=9, column=0, padx=10, pady=5, sticky="W")
        self.duration_var = tk.DoubleVar(value=1.0)
        ttk.Scale(self.root, from_=0.5, to=5.0, variable=self.duration_var, orient="horizontal").grid(row=9, column=1, padx=10, pady=5, sticky="W")

        ttk.Button(self.root, text="Execute Plan", command=self.executor.start_execution).grid(row=10, column=0, padx=10, pady=5)
        ttk.Button(self.root, text="Pause", command=self.executor.pause_execution).grid(row=10, column=1, padx=10, pady=5, sticky="W")
        ttk.Button(self.root, text="Continue", command=self.executor.continue_execution).grid(row=10, column=1, padx=100, pady=5, sticky="W")
        ttk.Button(self.root, text="Stop", command=self.executor.stop_execution).grid(row=10, column=2, padx=10, pady=5, sticky="W")

        self.current_action_label = ttk.Label(self.root, text="Current Action: ")
        self.current_action_label.grid(row=11, column=0, columnspan=3, padx=10, pady=10)

    def display(self, text):
        self.plan_text.delete("1.0", tk.END)
        self.plan_text.insert(tk.END, "\n".join(text))

    def run_pre_hoc(self):
        self.display(["Running PROST!!"])
        self.root.update_idletasks()
        self.current_plan = self.planner.generate_plan("instance_prehoc")
        self.display(["Plan:"] + self.current_plan)

    def run_reactive(self):
        self.display(["Generating Initial Plan"])
        self.root.update_idletasks()
        pre_plan = self.planner.generate_plan("instance_posthoc")

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
        self.display(["Running PROST!!"])
        self.root.update_idletasks()
        plan = self.planner.generate_plan("instance_posthoc")
        plan_with_response = self.rddl_analyzer.insert_explanation(plan, "./testbed/benchmarks/explanation_planning/problem_posthoc.rddl")
        self.current_plan = plan_with_response
        self.display(["Plan with explanation:"] + self.current_plan)

    def run_mixed_initiative(self):
        options = self.planner.generate_alternative_plans("instance_mixed")
        self.current_plan = options[0]  # Placeholder: assume user picks first option
        self.display(["Option 1:"] + options[0])

    def run_anytime(self):
        self.display(["Generating Anytime Plan..."])
        self.current_plan = self.planner.generate_anytime_plan("instance_anytime", timeout=3)
        self.display(["Anytime Plan:"] + self.current_plan)

    def run_replay_log(self):
        self.current_plan = self.planner.load_from_log("./plans/executed_plan.txt")
        self.display(["Replaying Plan:"] + self.current_plan)

    def run_compare(self):
        plans = self.planner.compare_strategies()
        combined = ["Pre-hoc:"] + plans['pre'] + ["", "Reactive:"] + plans['reactive'] + ["", "Post-hoc:"] + plans['post']
        self.display(combined)


if __name__ == "__main__":
    root = tk.Tk()
    app = PlanningGUI(root)
    root.mainloop()
