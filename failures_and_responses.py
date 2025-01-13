import random
from collections import defaultdict
import pandas as pd

class ScenarioResponseModel:
    def __init__(self):
        """
        Initialize the scenario-response model with predefined probabilities.
        """
        self.scenarios = [
            "success",  
            "error",
            "uncertainty",
            "inability",
            "suboptimal_behavior",
            "social_norm_violation",
            "unforeseen_circumstances",
        ]

        self.responses = [
            "apology",
            "why_explanation",
            "what_explanation",
            "narrate_next_action",
            "ask_for_help",
            "continue_without_comment",
        ]

        # Initial scenario-response probabilities based on the paper
        self.response_probability_table = self._initialize_response_probabilities()
        # Initial scenario probabilities based on the paper
        self.scenario_probability_table = self._initialize_scenario_probabilities()

    def _initialize_response_probabilities(self):
        """
        Create the initial probability table for scenario-response relationships.
        """
        table = defaultdict(dict)

        # Assigning probabilities based on paper findings
        # Values are manually normalized to sum to 1 for each scenario
        table["success"] = {
            "apology": 0.02,
            "why_explanation": 0.12,
            "what_explanation": 0.16,
            "narrate_next_action": 0.21,
            "ask_for_help": 0.04,
            "continue_without_comment": 0.45,
        }

        table["error"] = {
            "apology": 0.23,
            "why_explanation": 0.22,
            "what_explanation": 0.16,
            "narrate_next_action": 0.19,
            "ask_for_help": 0.17,
            "continue_without_comment": 0.03,
        }

        table["uncertainty"] = {
            "apology": 0.11,
            "why_explanation": 0.2,
            "what_explanation": 0.15,
            "narrate_next_action": 0.2,
            "ask_for_help": 0.28,
            "continue_without_comment": 0.06,
        }

        table["inability"] = {
            "apology": 0.13,
            "why_explanation": 0.23,
            "what_explanation": 0.19,
            "narrate_next_action": 0.17,
            "ask_for_help": 0.24,
            "continue_without_comment": 0.04,
        }

        table["suboptimal_behavior"] = {
            "apology": 0.04,
            "why_explanation": 0.24,
            "what_explanation": 0.2,
            "narrate_next_action": 0.19,
            "ask_for_help": 0.08,
            "continue_without_comment": 0.25,
        }

        table["social_norm_violation"] = {
            "apology": 0.23,
            "why_exfailure_probsplanation": 0.26,
            "what_explanation": 0.18,
            "narrate_next_action": 0.16,
            "ask_for_help": 0.07,
            "continue_without_comment": 0.1,
        }

        table["unforeseen_circumstances"] = {
            "apology": 0.08,
            "why_explanation": 0.27,
            "what_explanation": 0.24,
            "narrate_next_action": 0.17,
            "ask_for_help": 0.21,
            "continue_without_comment": 0.03,
        }

        return table
    
    def _initialize_scenario_probabilities(self):
        """
        Initialize probabilities for failures in each scenario.
        """
        return {
            "agent_error": 0.2,
            "suboptimal_behavior": 0.15,
            "agent_inability": 0.1,
            "unforeseen_circumstances": 0.25,
            "uncertainty": 0.2,
            "social_norm_violation": 0.05,
            "normal_interaction": 0.05,
        }
    
    def randomize_probabilities(self):
        """
        Randomize the probability values for response preferences and scenarios.
        """
        # Randomize scenario and response probabilities
        total_sc = 0.0
        scenario_probs = {}

        for scenario in self.scenarios:
            prob = random.random()
            scenario_probs[scenario] = prob
            total_sc += prob

            total = 0.0
            random_probs = {}

            for response in self.responses:
                prob = random.random()
                random_probs[response] = prob
                total += prob

            for response in self.responses:
                random_probs[response] /= total

            self.response_probability_table[scenario] = random_probs

        for scenario in self.scenarios:
            scenario_probs[scenario] /= total_sc

        self.scenario_probability_table = scenario_probs

    def get_response_probabilities(self):
        """
        Retrieve the current response probabilities
        """
        return self.response_probability_table

    def get_scenario_probabilities(self):
        """
        Retrieve the current scenario probabilities.
        """
        return self.scenario_probability_table

    def display_response_probabilities(self):
        """
        Display the response probability table
        """
        df = pd.DataFrame.from_dict(self.response_probability_table, orient="index", columns=self.responses)
        print(df)

    def display_scenario_probabilities(self):
        """
        Display the scenario probabilitie table
        """
        df = pd.DataFrame.from_dict(self.scenario_probability_table.items())
        print(df)

# Example Usage
if __name__ == "__main__":
    model = ScenarioResponseModel()

    print("\nInitial Scenario Probability Table:")
    model.display_scenario_probabilities()

    print("\nInitial Response Probability Table:")
    model.display_response_probabilities()

    # Randomization
    model.randomize_probabilities()
    
    print("\nRandomized Scenario Probability Table:")
    model.display_scenario_probabilities()

    print("\nRandomized Response Probability Table:")
    model.display_response_probabilities()
