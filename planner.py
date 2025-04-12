# planner.py

import subprocess
import re
import time
import threading
import os
import logging

# Configure logging to write to a file with timestamped messages
logging.basicConfig(filename='planner.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PlannerInterface:
    """
    Provides interface for interacting with the PROST planner and generating plans
    for different strategies and RDDL problem instances.
    """

    def generate_plan(self, instance_name):
        """Run the planner on a specific RDDL instance and return extracted actions."""
        try:
            planner_settings = "[Prost -s 1 -se [IPC2014]]"
            prost_command = ["/home/robolab/planning_ws/planners/prost/prost.py", instance_name, planner_settings]
            result = subprocess.run(prost_command, capture_output=True, text=True, check=True)
            actions = re.findall(r"[a-zA-Z_]+\([^()0-9]*\)", result.stdout)
            plan = [a for a in actions[-len(actions)//2:] if a != 'noop()']
            logging.info(f"Generated plan for {instance_name}: {plan}")
            return plan
        except subprocess.CalledProcessError as e:
            logging.error(f"Error generating plan for {instance_name}: {e.stderr}")
            return []

    def generate_alternative_plans(self, instance_name):
        """Simulate user-selectable plan alternatives."""
        plan1 = ["goto(robot, room1, library)", "fetch(robot, book1, visitor)"]
        plan2 = ["goto(robot, room2, storage)", "fetch(robot, book2, visitor)"]
        logging.info(f"Generated alternative plans for {instance_name}")
        return [plan1, plan2]

    def generate_anytime_plan(self, instance_name, timeout):
        """Run planner in a separate thread with a timeout to simulate anytime planning."""
        result = []

        def run_planner():
            nonlocal result
            result = self.generate_plan(instance_name)

        thread = threading.Thread(target=run_planner)
        thread.start()
        thread.join(timeout)
        final = result if result else ["partial(plan) due to timeout"]
        logging.info(f"Anytime plan result for {instance_name}: {final}")
        return final

    def load_from_log(self, path):
        """Load and return plan from previously saved log file."""
        if not os.path.exists(path):
            logging.warning(f"Log file not found: {path}")
            return ["Log file not found"]
        with open(path, 'r') as f:
            plan = [line.strip() for line in f.readlines() if line.strip()]
        logging.info(f"Loaded plan from log {path}")
        return plan

    def compare_strategies(self):
        """Generate and return plans for pre-hoc, reactive, and post-hoc for comparison."""
        plans = {
            'pre': self.generate_plan("instance_prehoc"),
            'reactive': self.generate_plan("instance_reactive"),
            'post': self.generate_plan("instance_posthoc")
        }
        logging.info("Compared strategies")
        return plans


class PlanExecutor:
    """
    Executes a given plan action-by-action in a background thread, 
    allowing pausing, resuming, and stopping.
    """

    def __init__(self, gui):
        self.gui = gui
        self.execution_thread = None
        self.is_paused = False
        self.is_stopped = False

    def start_execution(self):
        """Begin execution in a separate thread."""
        if not self.gui.current_plan:
            self.gui.current_action_label.config(text="Current Action: No plan to execute!")
            return
        if self.execution_thread and self.execution_thread.is_alive():
            return

        self.is_paused = False
        self.is_stopped = False
        self.execution_thread = threading.Thread(target=self.execute_plan)
        self.execution_thread.start()
        logging.info("Started plan execution")

    def execute_plan(self):
        """
        Execute each action in the current plan, respecting pause/stop conditions
        and updating the GUI with status labels.
        """
        duration = self.gui.duration_var.get()

        for index, action in enumerate(self.gui.current_plan):
            # Stop immediately if user requested stop
            if self.is_stopped:
                self.gui.current_action_label.config(text="Current Action: Execution stopped!")
                logging.info("Execution stopped early by user")
                return

            # Wait while paused
            while self.is_paused:
                time.sleep(0.1)

            # Update UI with current action
            self.gui.current_action_label.config(text=f"Current Action: {action}")
            self.gui.root.update_idletasks()
            logging.info(f"Executing step {index + 1}/{len(self.gui.current_plan)}: {action}")
            time.sleep(duration)

        # Final UI update once done
        if not self.is_stopped:
            self.gui.current_action_label.config(text="Current Action: Execution completed!")
            logging.info("Plan execution completed successfully")

    def pause_execution(self):
        """Pause the plan execution."""
        self.is_paused = True
        self.gui.current_action_label.config(text="Current Action: Execution paused!")
        logging.info("Execution paused")

    def continue_execution(self):
        """Continue execution if paused."""
        self.is_paused = False
        self.gui.current_action_label.config(text="Current Action: Execution resumed!")
        logging.info("Execution resumed")

    def stop_execution(self):
        """Stop execution and reset paused state."""
        self.is_stopped = True
        self.is_paused = False
        logging.info("Execution forcefully stopped")


class RDDLAnalyzer:
    """
    Analyzes RDDL domain/problem files to embed explanations into plans
    based on failure-response probabilities.
    """

    def insert_explanation(self, plan, problem_file_path):
        """Embed a response action into the plan based on a detected failure."""
        failure = self.extract_failure(plan)
        if not failure:
            logging.warning("No failure found in plan to explain")
            return plan

        failure_probs, response_probs = self.parse_problem_file(problem_file_path)
        response = max(response_probs.get(failure, {}), key=response_probs.get(failure, {}).get, default=None)
        if not response:
            logging.warning(f"No valid response for failure: {failure}")
            return plan

        robot, visitor = self.extract_names(plan)
        response_action = f"give_response({robot}, {response}, {failure}, {visitor})"
        updated_plan = []

        for action in plan:
            updated_plan.append(action)
            if "goto_waypoint" in action and "visitor_area" in action:
                updated_plan.append(response_action)
                logging.info(f"Inserted explanation action: {response_action}")

        return updated_plan

    def extract_failure(self, plan):
        """Identify the failure type from a failure_happens action in the plan."""
        pattern = re.compile(r"failure_happens\(\s*\w+,\s*\w+,\s*(\w+)\s*\)")
        for action in plan:
            match = pattern.search(action)
            if match:
                return match.group(1)
        return None

    def extract_names(self, plan):
        """Extract robot and visitor names from fetch_book actions."""
        pattern = re.compile(r"fetch_book\(\s*(\w+),\s*\w+,\s*(\w+)\s*\)")
        for action in plan:
            match = pattern.match(action)
            if match:
                return match.group(1), match.group(2)
        return "robot1", "visitor1"

    def parse_problem_file(self, path):
        """Parse failure and response probabilities from the problem file."""
        failure_probs = {}
        response_probs = {}

        with open(path, 'r') as f:
            content = f.read()

        failure_matches = re.findall(r"prob_failure\((\w+)\)\s*=\s*([\d.]+);", content)
        for f, p in failure_matches:
            failure_probs[f] = float(p)

        response_matches = re.findall(r"prob_response\((\w+),\s*(\w+)\)\s*=\s*([\d.]+);", content)
        for r, f, p in response_matches:
            response_probs.setdefault(f, {})[r] = float(p)

        return failure_probs, response_probs
