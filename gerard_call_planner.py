import subprocess

class PDDLPlanner:
    def __init__(self, domain_file, problem_file, planner_path="./downward"):
        """
        Initialize the PDDL planner integration.
        :param domain_file: Path to the PDDL domain file.
        :param problem_file: Path to the PDDL problem file.
        :param planner_path: Path to the Fast Downward planner.
        """
        self.domain_file = domain_file
        self.problem_file = problem_file
        self.planner_path = planner_path

    def run_planner(self):
        """
        Run the PDDL planner and return the generated plan.
        """
        command = [
            f"{self.planner_path}/fast-downward.py",
            "--alias", "seq-sat-lama-2011",
            "--plan-file", "sas_plan",
            self.domain_file,
            self.problem_file
        ]

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            print("Planner Output:")
            print(result.stdout)
            
            # Read the generated plan
            with open("sas_plan", "r") as f:
                plan = f.read()
            return plan
        except subprocess.CalledProcessError as e:
            print("Planner failed:")
            print(e.stderr)
            return None
