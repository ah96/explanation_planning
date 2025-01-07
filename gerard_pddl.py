import os
import subprocess
from datetime import datetime

class ExplanationPlanning:
    def __init__(self, domain_file, problem_file):
        """
        Initialize the explanation planning system with given PDDL or RDDL files.
        :param domain_file: Path to the domain file.
        :param problem_file: Path to the problem file.
        """
        self.domain_file_path = domain_file
        self.problem_file_path = problem_file
        self.plan_file_path = "plan.txt"

    def log(self, message):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

    def pre_hoc_explanation(self):
        """
        Include explanation actions proactively in the initial plan.
        """
        self.log("Generating plan with pre-hoc explanations.")
        plan = self._run_planner()
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

    def _detect_failure(self):
        self.log("Simulating failure detection.")
        # Simulate the detection of a failure (can involve checking logs, feedback, etc.)
        pass

    def _run_planner(self):
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

    def _retrieve_completed_plan(self):
        self.log("Retrieving the completed plan for post-hoc analysis.")
        # Simulate retrieving and analyzing the completed plan
        return "Action1 -> Action2 -> Action3"

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

# Writing files for demonstration
with open("example_domain.pddl", "w") as f:
    f.write(example_domain)

with open("example_problem.pddl", "w") as f:
    f.write(example_problem)

# Instantiate the explanation planning system
planner = ExplanationPlanning(domain_file="example_domain.pddl", problem_file="example_problem.pddl")

planner._run_planner()

# Execute the three strategies
#print("Pre-Hoc Explanation Plan:")
#print(planner.pre_hoc_explanation())

#print("Reactive Explanation Plan:")
#print(planner.reactive_explanation())

#print("Post-Hoc Explanation Plan:")
#print(planner.post_hoc_explanation())
