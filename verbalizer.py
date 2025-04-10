# verbalizer.py

import logging
import random

# Optional: connect to OpenAI API
import openai
#openai.api_key = 'your-api-key'

# Toggle between mock and real LLM usage
USE_MOCK = True

class ExplanationVerbalizer:
    """
    Generates natural language explanations based on planning strategy
    and failure-response context using either a mock system or an LLM.
    """

    def __init__(self):
        logging.info("ExplanationVerbalizer initialized")

    def verbalize(self, ctx):
        """Creates an explanation prompt and returns a verbalized explanation."""
        prompt = self.build_prompt(ctx)
        logging.info(f"Generated prompt:\n{prompt}")

        if USE_MOCK:
            return self.mock_response(ctx)
        else:
            return self.call_llm(prompt)

    def build_prompt(self, ctx):
        """
        Create a prompt string for the LLM based on the strategy and context.
        """
        strategy = ctx.get("strategy", "unknown")
        failure = ctx.get("failure", None)
        response = ctx.get("response", None)

        base = f"You are a helpful robot using a planning strategy: {strategy}.\n"

        if strategy == "pre-hoc":
            return base + "You created a plan in advance to achieve a goal. Explain the plan and its purpose in 1-2 sentences."
        elif strategy == "reactive":
            return base + f"You detected a failure during execution and replanned. The failure was '{failure}'. Explain how you adapted."
        elif strategy == "post-hoc":
            return base + f"After executing the plan, a failure of type '{failure}' was found. You responded with '{response}'. Explain this to the user."
        elif strategy == "mixed-initiative":
            return base + "The user selected one of several options. Explain how their choice shaped the plan."
        elif strategy == "anytime":
            return base + "You generated the best plan possible under a time limit. Explain the trade-offs and decisions you made."
        elif strategy == "replay":
            return base + "This plan was replayed from a log. Describe what the robot did and why."
        elif strategy == "compare":
            return base + "You compared multiple strategies. Summarize their key differences."
        else:
            return base + "Explain your behavior clearly in context."

    def call_llm(self, prompt):
        """
        Call the actual LLM (e.g., OpenAI) using the prompt (requires API key).
        """
        # Uncomment below if using OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        #return response.choices[0].message.content.strip()
        return "[LLM response would go here]"

    def mock_response(self, ctx):
        """
        Generate a fake response for testing without LLM calls.
        """
        strategy = ctx.get("strategy")
        failure = ctx.get("failure", "a problem")
        response = ctx.get("response", "a solution")

        mock_templates = {
            "pre-hoc": "I planned ahead to ensure everything ran smoothly.",
            "reactive": f"I encountered {failure}, so I replanned and adjusted to continue.",
            "post-hoc": f"After noticing {failure}, I responded with {response} to resolve it.",
            "mixed-initiative": "You picked a plan variant. I followed that to match your preference.",
            "anytime": "Time was short, so I picked a fast but effective strategy.",
            "replay": "I'm showing you what I previously did so you can review it.",
            "compare": "Here are different plans. Each has pros and cons."
        }

        return mock_templates.get(strategy, "I'm explaining my decision in the best way I can.")


# Example usage for testing the verbalizer
if __name__ == "__main__":
    explainer = ExplanationVerbalizer()

    context = {
        "strategy": "post-hoc",
        "failure": "unavailable",
        "response": "suggest_alternative",
        "plan": [
            "goto(robot1, room1, library)",
            "fetch_book(robot1, bookA, visitor1)",
            "failure_happens(robot1, bookA, unavailable)",
            "goto(robot1, library, visitor_area)",
            "give_response(robot1, suggest_alternative, unavailable, visitor1)"
        ]
    }

    print("\nGenerated Explanation:")
    print(explainer.verbalize(context))
