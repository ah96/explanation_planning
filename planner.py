# planner.py

import subprocess
import re
import time
import threading
import os
import logging

logging.basicConfig(filename='planner.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PlannerInterface:
    def generate_plan(self, instance_name):
        try:
            planner_settings = "[Prost -s 1 -se [IPC2014]]"
            prost_command = ["/home/robolab/git/planning_ws/prost/prost.py", instance_name, planner_settings]
            result = subprocess.run(prost_command, capture_output=True, text=True, check=True)
            actions = re.findall(r"[a-zA-Z_]+\([^()0-9]*\)", result.stdout)
            plan = [a for a in actions[-len(actions)//2:] if a != 'noop()']
            logging.info(f"Generated plan for {instance_name}: {plan}")
            return plan
        except subprocess.CalledProcessError as e:
            logging.error(f"Error generating plan for {instance_name}: {e.stderr}")
            return []

    def generate_alternative_plans(self, instance_name):
        plan1 = ["goto(robot, room1, library)", "fetch(robot, book1, visitor)"]
        plan2 = ["goto(robot, room2, storage)", "fetch(robot, book2, visitor)"]
        logging.info(f"Generated alternative plans for {instance_name}")
        return [plan1, plan2]

    def generate_anytime_plan(self, instance_name, timeout):
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
        if not os.path.exists(path):
            logging.warning(f"Log file not found: {path}")
            return ["Log file not found"]
        with open(path, 'r') as f:
            plan = [line.strip() for line in f.readlines() if line.strip()]
        logging.info(f"Loaded plan from log {path}")
        return plan

    def compare_strategies(self):
        plans = {
            'pre': self.generate_plan("instance_prehoc"),
            'reactive': self.generate_plan("instance_reactive"),
            'post': self.generate_plan("instance_posthoc")
        }
        logging.info("Compared strategies")
        return plans


class PlanExecutor:
    def __init__(self, gui):
        self.gui = gui
        self.execution_thread = None
        self.is_paused = False
        self.is_stopped = False

    def start_execution(self):
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
        duration = self.gui.duration_var.get()
        for action in self.gui.current_plan:
            if self.is_stopped:
                self.gui.current_action_label.config(text="Current Action: Execution stopped!")
                logging.info("Execution stopped")
                break
            while self.is_paused:
                time.sleep(0.1)
            self.gui.current_action_label.config(text=f"Current Action: {action}")
            self.gui.root.update_idletasks()
            logging.info(f"Executing action: {action}")
            time.sleep(duration)
        else:
            if not self.is_stopped:
                self.gui.current_action_label.config(text="Current Action: Execution completed!")
                logging.info("Execution completed")

    def pause_execution(self):
        self.is_paused = True
        self.gui.current_action_label.config(text="Current Action: Execution paused!")
        logging.info("Execution paused")

    def continue_execution(self):
        self.is_paused = False
        self.gui.current_action_label.config(text="Current Action: Execution resumed!")
        logging.info("Execution resumed")

    def stop_execution(self):
        self.is_stopped = True
        self.is_paused = False
        logging.info("Execution forcefully stopped")


class RDDLAnalyzer:
    def insert_explanation(self, plan, problem_file_path):
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
        pattern = re.compile(r"failure_happens\(\s*\w+,\s*\w+,\s*(\w+)\s*\)")
        for action in plan:
            match = pattern.search(action)
            if match:
                return match.group(1)
        return None

    def extract_names(self, plan):
        pattern = re.compile(r"fetch_book\(\s*(\w+),\s*\w+,\s*(\w+)\s*\)")
        for action in plan:
            match = pattern.match(action)
            if match:
                return match.group(1), match.group(2)
        return "robot1", "visitor1"

    def parse_problem_file(self, path):
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
