import tkinter as tk
from tkinter import ttk
import time
import threading
import subprocess
import re
import time

class PlanningGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Planning GUI")

        # Planning type buttons
        self.plan_type_label = ttk.Label(root, text="Select Planning Type:")
        self.plan_type_label.grid(row=0, column=0, padx=10, pady=10, sticky="W")

        self.pre_hoc_button = ttk.Button(root, text="Pre-hoc", command=self.run_pre_hoc)
        self.pre_hoc_button.grid(row=1, column=0, padx=10, pady=5, sticky="W")

        self.reactive_button = ttk.Button(root, text="Reactive", command=self.run_reactive)
        self.reactive_button.grid(row=2, column=0, padx=10, pady=5, sticky="W")

        self.post_hoc_button = ttk.Button(root, text="Post-hoc", command=self.run_post_hoc)
        self.post_hoc_button.grid(row=3, column=0, padx=10, pady=5, sticky="W")

        # Plan display
        self.plan_label = ttk.Label(root, text="Generated Plan:")
        self.plan_label.grid(row=0, column=1, padx=10, pady=10, sticky="W")

        self.plan_text = tk.Text(root, width=60, height=10)
        self.plan_text.grid(row=1, column=1, rowspan=3, padx=10, pady=5)

        # Execution controls
        self.execution_label = ttk.Label(root, text="Plan Execution:")
        self.execution_label.grid(row=4, column=0, padx=10, pady=10, sticky="W")

        self.duration_label = ttk.Label(root, text="Action Duration (seconds):")
        self.duration_label.grid(row=5, column=0, padx=10, pady=5, sticky="W")

        self.duration_var = tk.DoubleVar(value=1.0)
        self.duration_slider = ttk.Scale(root, from_=0.5, to=5.0, variable=self.duration_var, orient="horizontal")
        self.duration_slider.grid(row=5, column=1, padx=10, pady=5, sticky="W")

        self.execute_button = ttk.Button(root, text="Execute Plan", command=self.start_execution)
        self.execute_button.grid(row=6, column=0, padx=10, pady=5)

        self.pause_button = ttk.Button(root, text="Pause", command=self.pause_execution)
        self.pause_button.grid(row=6, column=1, padx=10, pady=5, sticky="W")

        self.continue_button = ttk.Button(root, text="Continue", command=self.continue_execution)
        self.continue_button.grid(row=6, column=1, padx=100, pady=5, sticky="W")

        self.stop_button = ttk.Button(root, text="Stop", command=self.stop_execution)
        self.stop_button.grid(row=6, column=2, padx=10, pady=5, sticky="W")

        # Action display during execution
        self.current_action_label = ttk.Label(root, text="Current Action: ")
        self.current_action_label.grid(row=7, column=0, columnspan=3, padx=10, pady=10)

        # Placeholder for plan and execution controls
        self.current_plan = []
        self.execution_thread = None
        self.is_paused = False
        self.is_stopped = False

    def run_pre_hoc(self):
        """Generate a pre-hoc plan."""

        """
        Run PROST and extract the sequence of actions (final plan).

        :param problem_instance: Name of the problem instance.
        :param planner_settings: Settings for the planner.
        :return: A list of actions forming the plan.
        """
        text = ["Running PROST!!"]
        self.display(text)
        self.root.update_idletasks()  # Force the GUI to update immediately

        # Function to start the server
        def start_server():
            try:
                print("Starting the server...")
                server_command = ["./run-server.py", "-b", "./testbed/benchmarks/explanation_planning_2/"]
                self.server_process = subprocess.Popen(server_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return self.server_process
            except Exception as e:
                print(f"Error starting server: {e}")

        # Function to run PROST
        def run_prost():
            try:
                # Run PROST
                print('Running PROST!!')
                self.display(['Running PROST!!'])
                self.root.update_idletasks()  # Force the GUI to update immediately

                planner_settings="[Prost -s 1 -se [IPC2014]]"
                problem_instance_name = "instance_failures_responses"
                prost_command = ["/home/robolab/planning_ws/planners/prost/prost.py", problem_instance_name, planner_settings]
                result = subprocess.run(prost_command, capture_output=True, text=True, check=True)

                # Extract actions from the output
                action_pattern = re.compile(r"[a-zA-Z_]+\([^()0-9]*\)") #re.compile(r"\([^\d()]*\)")  # Match actions in parentheses
                actions = action_pattern.findall(result.stdout)

                plan_length = int(len(actions) / 2)
                #print(plan_length)
                plan = actions[len(actions)-plan_length:len(actions)]
                #print(plan)
                plan_final = ['Plan:']
                for a in plan:
                    if a != 'noop()':
                        plan_final.append(a)
                print(plan_final)

                self.current_plan = plan_final[1:]
                self.display(['Plan received!'])
                self.root.update_idletasks()  # Force the GUI to update immediately
                time.sleep(2)
                
                self.display(plan_final)
                self.root.update_idletasks()  # Force the GUI to update immediately

            except subprocess.CalledProcessError as e:
                print("An error occurred while running PROST:")
                print(e.stderr)
                return []

        #print(start_server())
        #time.sleep(5)
        run_prost()

        '''
        # Start the server in a separate thread
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        print('DONE!!!!!!!')
        # Wait a few seconds to ensure the server is running
        time.sleep(2)

        # Start PROST after the server is up
        prost_thread = threading.Thread(target=run_prost)
        prost_thread.start()

        # Wait for both threads to complete
        server_thread.join()
        prost_thread.join()

        # Optionally, clean up the server process
        if hasattr(self, "server_process"):
            self.server_process.terminate()
            print("Server process terminated.")
        '''
        
    def run_reactive(self):
        """Generate a reactive plan."""
        def run_prost(problem_instance_name):
            try:
                # Run PROST
                print('Running PROST!!')
                self.display(['Running PROST!!'])
                self.root.update_idletasks()  # Force the GUI to update immediately

                planner_settings="[Prost -s 1 -se [IPC2014]]"
                #problem_instance_name = "instance_reactive"
                prost_command = ["/home/robolab/planning_ws/planners/prost/prost.py", problem_instance_name, planner_settings]
                result = subprocess.run(prost_command, capture_output=True, text=True, check=True)

                # Extract actions from the output
                action_pattern = re.compile(r"[a-zA-Z_]+\([^()0-9]*\)") #re.compile(r"\([^\d()]*\)")  # Match actions in parentheses
                actions = action_pattern.findall(result.stdout)

                plan_length = int(len(actions) / 2)
                #print(plan_length)
                plan = actions[len(actions)-plan_length:len(actions)]
                #print(plan)
                plan_final = ['Plan:']
                for a in plan:
                    if a != 'noop()':
                        plan_final.append(a)
                print(plan_final)

                self.current_plan = plan_final[1:]
                self.display(['Plan received!'])
                self.root.update_idletasks()  # Force the GUI to update immediately
                time.sleep(2)

            except subprocess.CalledProcessError as e:
                print("An error occurred while running PROST:")
                print(e.stderr)
                return []

        run_prost("instance_posthoc")
        l = ["Executing Plan:"]   
        for a in self.current_plan:
            if 'failure' in a:
                
                l.append(a)
                self.display(l)
                self.root.update_idletasks()  # Force the GUI to update immediately
                time.sleep(1)
                
                l.append('Failure happened!')
                self.display(l)
                self.root.update_idletasks()  # Force the GUI to update immediately
                time.sleep(2)
                
                break
            l.append(a)
            self.display(l)
            self.root.update_idletasks()  # Force the GUI to update immediately
            time.sleep(2)

        self.display(['Replanning...'])
        self.root.update_idletasks()  # Force the GUI to update immediately
        time.sleep(2)
        run_prost("instance_reactive")
        l = ["New plan (from the failure point):"]
        for a in self.current_plan:
            l.append(a)
            self.display(l)
            self.root.update_idletasks()  # Force the GUI to update immediately
            time.sleep(2)


    def run_post_hoc(self):
        """Generate a pre-hoc plan."""

        """
        Run PROST and extract the sequence of actions (final plan).

        :param problem_instance: Name of the problem instance.
        :param planner_settings: Settings for the planner.
        :return: A list of actions forming the plan.
        """
        try:
            # Run PROST
            print('Running PROST!!')
            self.display(['Running PROST!!'])
            self.root.update_idletasks()  # Force the GUI to update immediately

            planner_settings="[Prost -s 1 -se [IPC2014]]"
            problem_instance_name = "instance_posthoc"
            prost_command = ["/home/robolab/planning_ws/planners/prost/prost.py", problem_instance_name, planner_settings]
            result = subprocess.run(prost_command, capture_output=True, text=True, check=True)

            # Extract actions from the output
            action_pattern = re.compile(r"[a-zA-Z_]+\([^()0-9]*\)") #re.compile(r"\([^\d()]*\)")  # Match actions in parentheses
            actions = action_pattern.findall(result.stdout)

            plan_length = int(len(actions) / 2)
            #print(plan_length)
            plan = actions[len(actions)-plan_length:len(actions)]
            #print(plan)
            plan_final = ['Plan found:']
            for a in plan:
                if a != 'noop()':
                    plan_final.append(a)
                    #print(a)
            print(plan_final)
            self.current_plan = plan_final[1:]
            self.display(plan_final)
            self.root.update_idletasks()  # Force the GUI to update immediately
            
            time.sleep(5)  # Pause the program for N seconds
            self.display(['Analyzing the plan...'])
            self.root.update_idletasks()  # Force the GUI to update immediately
            time.sleep(3)  # Pause the program for N seconds
            
            # Add response action to the original plan
            problem_file = "./testbed/benchmarks/explanation_planning/problem_posthoc.rddl"
            self.current_plan = self.get_response(self.current_plan, problem_file)
            self.current_plan.insert(0, 'Plan with explanation:')
            print(self.current_plan)
            self.display(self.current_plan)
            self.root.update_idletasks()  # Force the GUI to update immediately
            self.current_plan = self.current_plan[1:]

        except subprocess.CalledProcessError as e:
            print("An error occurred while running PROST:")
            print(e.stderr)
            return []

    def display(self, text):
        """Display the generated plan in the text area."""
        self.plan_text.delete("1.0", tk.END)
        self.plan_text.insert(tk.END, "\n".join(text))

    def start_execution(self):
        """Start executing the plan in a separate thread."""
        if not self.current_plan:
            self.current_action_label.config(text="Current Action: No plan to execute!")
            return

        if self.execution_thread and self.execution_thread.is_alive():
            return  # Prevent starting multiple threads

        self.is_paused = False
        self.is_stopped = False
        self.execution_thread = threading.Thread(target=self.execute_plan)
        self.execution_thread.start()

    def execute_plan(self):
        """Execute the current plan action-by-action."""
        action_duration = self.duration_var.get()

        for action in self.current_plan:
            if self.is_stopped:
                self.current_action_label.config(text="Current Action: Execution stopped!")
                break

            while self.is_paused:
                time.sleep(0.1)  # Wait while paused

            self.current_action_label.config(text=f"Current Action: {action}")
            self.root.update_idletasks()
            time.sleep(action_duration)

        if not self.is_stopped:
            self.current_action_label.config(text="Current Action: Execution completed!")

    def pause_execution(self):
        """Pause the execution of the plan."""
        self.is_paused = True
        self.current_action_label.config(text="Current Action: Execution paused!")

    def continue_execution(self):
        """Resume the execution of the plan after a pause."""
        if self.is_paused:
            self.is_paused = False
            self.current_action_label.config(text="Current Action: Execution resumed!")

    def stop_execution(self):
        """Stop the execution of the plan."""
        self.is_stopped = True
        self.is_paused = False  # Ensure it doesn't hang in paused state

    def parse_problem_file(self, problem_file_path):
        """
        Parse the RDDL problem file to extract failure probabilities and response probabilities.

        :param problem_file_path: Path to the RDDL problem file.
        :return: Tuple of failure probabilities and response probabilities.
        """
        failure_probabilities = {}
        response_probabilities = {}

        with open(problem_file_path, 'r') as file:
            content = file.read()

        # Extract failure probabilities
        failure_matches = re.findall(r"prob_failure\((\w+)\)\s*=\s*([\d.]+);", content)
        for failure, prob in failure_matches:
            failure_probabilities[failure] = float(prob)

        # Extract response probabilities for each failure
        response_matches = re.findall(r"prob_response\((\w+),\s*(\w+)\)\s*=\s*([\d.]+);", content)
        for response, failure, prob in response_matches:
            if failure not in response_probabilities:
                response_probabilities[failure] = {}
            response_probabilities[failure][response] = float(prob)

        return failure_probabilities, response_probabilities
    
    def extract_failure_from_plan(self, plan):
        """
        Parse the current plan to extract the failure type from `failure_happens` actions.

        :param plan: List of strings representing the current plan.
        :return: Extracted failure type, or None if no failure is found.
        """
        failure_type = None

        # Regex to match `failure_happens` and extract the third argument (failure type)
        failure_pattern = re.compile(r"failure_happens\(\s*\w+,\s*\w+,\s*(\w+)\s*\)")

        # Iterate through the plan to find failure-related actions
        for action in plan:
            match = failure_pattern.search(action)
            if match:
                failure_type = match.group(1)  # Extract the failure type (third argument)
                break  # Stop after finding the first failure type

        return failure_type

    def get_response(self, plan, problem_file_path):
        """
        Identify a failure type and the most probable response based on the problem file,
        then add the response to the plan after a `goto_waypoint` action to `visitor_area`.

        :param plan: List of strings representing the current plan.
        :param problem_file_path: Path to the RDDL problem file.
        :return: Updated plan with the response action added.
        """
        # Identify the failure type from a plan
        failure = self.extract_failure_from_plan(plan)

        if failure != '':
            self.display(['Found a failure in the plan: ' + failure])
            self.root.update_idletasks()  # Force the GUI to update immediately
            time.sleep(5)

        # Parse the problem file
        failure_probabilities, response_probabilities = self.parse_problem_file(problem_file_path)

        # Step 1: Identify the most probable failure type
        #failure = max(failure_probabilities, key=failure_probabilities.get)

        # Step 2: Identify the most probable response for the failure
        response_probs = response_probabilities.get(failure, {})
        response = max(response_probs, key=response_probs.get) if response_probs else None

        if not response:
            print("No valid response found for failure:", failure)
            self.display(["No valid response found for failure:" + failure])
            self.root.update_idletasks()  # Force the GUI to update immediately
            return plan

        self.display(["Found a response for the failure " + failure + ". It is " + response])
        self.root.update_idletasks()  # Force the GUI to update immediately
        time.sleep(5)
        # Step 3: Extract robot and visitor names from the `fetch_book` action. 
        # Add the response action to the plan after the relevant `goto_waypoint` action
        robot_name, visitor_name = None, None
        fetch_book_pattern = re.compile(r"fetch_book\(\s*(\w+),\s*\w+,\s*(\w+)\s*\)")
        for action in plan:
            match = fetch_book_pattern.match(action)
            if match:
                robot_name = match.group(1)
                visitor_name = match.group(2)
                break
        response_action = f"give_response({robot_name}, {response}, {failure}, {visitor_name})"
        updated_plan = []

        self.display(['Embedding the response in the original plan...'])
        self.root.update_idletasks()  # Force the GUI to update immediately
        time.sleep(5)  # Pause the program for N seconds

        # Regex to parse `goto_waypoint` actions and extract destination
        goto_pattern = re.compile(r"goto_waypoint\(\s*\w+,\s*\w+,\s*(\w+)\s*\)")

        for action in plan:
            updated_plan.append(action)

            # Check if the action is a `goto_waypoint` with destination `visitor_area`
            match = goto_pattern.match(action)
            if match:
                destination = match.group(1)
                if destination == "visitor_area":
                    updated_plan.append(response_action)  # Add the response action after it

        return updated_plan


# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = PlanningGUI(root)
    root.mainloop()

