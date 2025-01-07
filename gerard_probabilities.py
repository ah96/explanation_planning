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

        # Initial probabilities based on the paper
        self.probability_table = self._initialize_probabilities()

    def _initialize_probabilities(self):
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
            "why_explanation": 0.26,
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

    def randomize_probabilities(self):
        """
        Randomize the probability values for each scenario-response pair.
        Ensure probabilities for each scenario sum to 1.
        """
        for scenario in self.scenarios:
            total = 0.0
            random_probs = {}

            # Generate random probabilities for each response
            for response in self.responses:
                prob = random.random()
                random_probs[response] = prob
                total += prob

            # Normalize probabilities
            for response in self.responses:
                random_probs[response] /= total

            self.probability_table[scenario] = random_probs

    def get_probabilities(self):
        """
        Retrieve the current probability table.
        """
        return self.probability_table

    def get_response_distribution(self, scenario):
        """
        Get the probability distribution for a specific scenario.
        :param scenario: The scenario for which the distribution is required.
        :return: Dictionary of responses with their probabilities.
        """
        if scenario not in self.probability_table:
            raise ValueError(f"Unknown scenario: {scenario}")
        return self.probability_table[scenario]

    def display_probabilities_as_table(self):
        """
        Display the probability table as a pandas DataFrame for better readability.
        """
        df = pd.DataFrame.from_dict(self.probability_table, orient="index", columns=self.responses)
        print(df)

# Example Usage
if __name__ == "__main__":
    model = ScenarioResponseModel()

    print("Initial Probability Table:")
    model.display_probabilities_as_table()

    print("\nRandomized Probability Table:")
    model.randomize_probabilities()
    model.display_probabilities_as_table()
