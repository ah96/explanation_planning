import os
import subprocess
from datetime import datetime
import time

class ExplanationPlanning:
    def __init__(self, domain_file, problem_file, pddl=True):
        """
        Initialize the explanation planning system with given PDDL or RDDL files.
        :param domain_file: Path to the domain file.
        :param problem_file: Path to the problem file.
        """
        self.domain_file_path = domain_file
        self.problem_file_path = problem_file
        self.pddl_used = pddl
        if pddl == False:
            self.benchmark_path = "./example/"
    
    def log(self, message):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

    def pre_hoc_explanation(self):
        """
        Include explanation actions proactively in the initial plan.
        """
        self.log("Generating plan with pre-hoc explanations.")
        if self.pddl_used
            plan = self._run_planner_pddl()
        else:
            plan = self._run_planner_rddl()
        self.log(f"Generated Plan: \n{plan}")
        return plan

    def reactive_explanation(self):
        """
        Generate a plan reactively when a failure occurs, including explanations.
        """
        self.log("Detecting failure... replanning with reactive explanations.")
        plan = self._run_planner()
        self._detect_failure()
        plan = self._run_planner()
        self.log(f"Generated Plan: \n{plan}")
        return plan

    def post_hoc_explanation(self):
        """
        Analyze the completed plan to include explanations where necessary.
        """
        self.log("Analyzing completed plan for post-hoc explanations.")
        completed_plan = self._retrieve_completed_plan()
        plan = self._run_planner()
        self.log(f"Generated Plan: \n{plan}")
        return plan

    def _modify_problem_file_with_explanations(self):
        self.log("Updating the problem file to include explanation actions.")
        # Update self.problem_file_path to include explanation actions proactively
        pass

    def _modify_problem_file_with_post_hoc_explanations(self, completed_plan):
        self.log("Modifying problem file for post-hoc explanations based on completed plan.")
        # Add explanation actions to the problem file after plan execution
        pass

    def _detect_failure(self):
        self.log("Simulating failure detection.")
        # Simulate the detection of a failure (can involve checking logs, feedback, etc.)
        pass

    def _run_planner_rddl(self):
        """
        Run the Prost planner with a server in one method.

        :param benchmark_path: Path to the benchmark directory for the server.
        :param problem_instance: Name of the problem instance for Prost.
        :param settings: Planner settings as a string.
        """

        self.log("Running the planner on the domain and problem files.")

        try:
            # Step 1: Start the server
            #print("\nStarting the server...")
            #server_command = ["./run-server.py", "-b", self.benchmark_path]
            #server_result = subprocess.run(server_command, capture_output=True, text=True, check=True)
            #server_result = subprocess.Popen(server_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            #print("Server Output:")
            #print(server_result.stdout)

            # Allow the server to initialize
            #time.sleep(2)  # Adjust this delay based on how long the server takes to start

            # Step 2: Run Prost planner
            print("\nRunning Prost planner...")
            problem_instance = "EXAMPLE_PROBLEM" # this must be automated
            settings = str("[Prost -s 1 -se [IPC2014]]") # this can be hardcoded
            prost_command = ["./prost.py", problem_instance, settings]
            prost_result = subprocess.run(prost_command, capture_output=True, text=True, check=True)
            #prost_result = subprocess.Popen(prost_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            print("Prost Output:")
            if prost_result.stderr != '':
                print(prost_result.stderr)
            else:
                print(prost_result.stdout)
            return prost_result.stdout  # Return the planner's output for further processing if needed

            # Step 3: Wait for both processes to complete
            #prost_stdout, prost_stderr = prost_result.communicate()
            #server_stdout, server_stderr = server_result.communicate()

            # Print outputs from both processes
            #print("\nServer Output:")
            #print(server_stdout)
            #if server_stderr:
            #    print("\nServer Errors:")
            #    print(server_stderr)

            #print("\nProst Output:")
            #print(prost_stdout)
            #if prost_stderr:
            #    print("\nProst Errors:")
            #    print(prost_stderr)

            #return prost_stdout  # Return the planner's output for further processing if needed

        except subprocess.CalledProcessError as e:
            print("An error occurred:")
            print(e.stderr)
            return None    

    def _run_planner_pddl(self):
        self.log("Running the planner on the domain and problem files.")
        try:
            command = [
                "python3", "fast-downward.py",
                "--alias", "seq-sat-lama-2011",
                "--plan-file", self.plan_file_path,
                self.domain_file_path,
                self.problem_file_path
            ]
            
            # Run the command and capture output
            result = subprocess.run(command, capture_output=True, text=True, check=True)

            print("Planner Output (Python):")
            print(result.stdout)

            # Read the generated plan file
            with open(self.plan_file_path+".1", "r") as plan_file_obj:
                plan = plan_file_obj.read()
                print("\nGenerated Plan:")
                print(plan)
                return result.stdout, plan


            # Example call to an external planner (adjust command as needed for your planner)
            result = subprocess.run(
                ["fast-downward", "--domain", self.domain_file_path, "--problem", self.problem_file_path, "--search", "astar(blind)"],
                capture_output=True, text=True, check=True
            )
            plan = result.stdout
        except subprocess.CalledProcessError as e:
            self.log(f"Planner execution failed: {e.stderr}")
            plan = "No plan generated."
        return plan
    
def generate_example_domain_and_problem_rddl():
    """
    Generate example domain and problem files
    """

    # Example domain and problem files for RDDL
    example_domain = """
    domain EXAMPLE_DOMAIN {
        types { state : finite; action : finite; }
        pvariables {
            task_success : state -> {true, false};
            explanation_needed : state -> {true, false};
            explanation_action : action -> bool;
        }
        cpfs {
            explanation_needed' = task_success == false;  // Explanation needed when task fails
        }
        reward = explanation_action ? 1.0 : 0.0;  // Reward for including explanation actions
    }
    """

    example_problem = """
    instance EXAMPLE_PROBLEM {
        domain = EXAMPLE_DOMAIN;
        init-state {
            task_success = true;
            explanation_needed = false;
        }
        non-fluents {}
        horizon = 10;
        discount = 1.0;
    }
    """

    return example_domain, example_problem

def generate_example_domain_and_problem_pddl():
    """
    Generate example domain and problem files
    """

    # Example domain and problem files for PDDL
    example_domain = """
    (define (domain explanation-domain)
    (:requirements :strips)
    (:predicates
        (task-success)
        (explanation-needed)
        (explanation-action)
    )

    (:action perform-task
        :precondition (not (task-success))
        :effect (and (task-success) (not (explanation-needed)))
    )

    (:action provide-explanation
        :precondition (explanation-needed)
        :effect (and (not (explanation-needed)) (explanation-action))
    )
    )
    """

    example_problem = """
    (define (problem explanation-problem)
    (:domain explanation-domain)
    (:init
        (not (task-success))
        (explanation-needed)
    )
    (:goal (and (task-success) (explanation-action)))
    )
    """

    return example_domain, example_problem
    
##########################################################################    
"""
MAIN
"""
##########################################################################

# Example domain and problem files for RDDL
example_domain, example_problem = generate_example_domain_and_problem_rddl()

# Writing files for demonstration
with open("./example_domain.rddl", "w") as f:
    f.write(example_domain)

with open("./example_problem.rddl", "w") as f:
    f.write(example_problem)

# Instantiate the explanation planning system
explanation_planner = ExplanationPlanning(domain_file="./example_domain.rddl", problem_file="./example_problem.rddl", pddl=False)

# Execute the three strategies
print("Pre-Hoc Explanation Plan:")
print(explanation_planner.pre_hoc_explanation())

#print("Reactive Explanation Plan:")
#print(explanation_planner.reactive_explanation())

#print("Post-Hoc Explanation Plan:")
#print(explanation_planner.post_hoc_explanation())
