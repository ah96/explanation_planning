domain explanation_planning {
  
  // List the requirements for a discrete MDP with non-fluents, state/action fluents, reward, cpfs, and initial state
  requirements: [ "discrete-MDP", "non-fluents", "state-fluents", "action-fluents", "reward", "cpfs", "init-state" ];

  // Define a custom type for levels of human understanding.
  // Here: 0 = low, 1 = medium, 2 = high.
  types {
    Level = {0, 1, 2};
  }

  // State fluents: 
  // - human_understanding tracks the human’s comprehension level.
  // - task_progress tracks progress toward task completion.
  state fluents {
    human_understanding: Level;
    task_progress: {0, 1, 2, 3, 4, 5};  // 5 represents task completion.
  }

  // Action fluent:
  // - The only decision is whether to generate an explanation.
  action fluents {
    explain: boolean;
  }

  // Non-fluents: These parameters define the dynamics.
  non-fluents {
    p_improve: real;   // Probability that an explanation improves understanding.
    p_decay:   real;   // Probability that understanding decays if no explanation is given.
    p_progress: real;  // Probability that the task advances if no explanation is given.
    max_progress: int; // Maximum progress (should equal 5 in this example).
  }

  // Initial state: Assume the human starts with low understanding and the task is at the beginning.
  init state {
    human_understanding = 0;
    task_progress = 0;
  }

  // CPFs (Conditional Probability Functions):
  cpfs {
    // Human understanding update:
    // - If an explanation is given then with probability p_improve the understanding improves by 1 (capped at 2),
    //   and with probability 1-p_improve it stays the same.
    // - If no explanation is given and the human is not already at 0, then with probability p_decay the understanding drops by 1.
    human_understanding' =
      if (explain) then {
        min(human_understanding + 1, 2): p_improve,
        human_understanding: 1 - p_improve
      }
      else {
        if (human_understanding > 0) then {
          human_understanding - 1: p_decay,
          human_understanding: 1 - p_decay
        } else {
          human_understanding: 1.0
        }
      };

    // Task progress update:
    // - If an explanation is given, no progress is made.
    // - Otherwise, if the task is not yet complete (i.e. task_progress < max_progress), progress increases by 1 with probability p_progress.
    task_progress' =
      if (explain) then {
        task_progress: 1.0
      }
      else {
        if (task_progress < max_progress) then {
          task_progress + 1: p_progress,
          task_progress: 1 - p_progress
        } else {
          task_progress: 1.0
        }
      };
  }

  // Reward function:
  // - There is a penalty (-2) for generating an explanation.
  // - Each step of task progress earns +10 reward.
  // - When the task is complete (task_progress == max_progress), the human’s understanding is rewarded (+5 per level).
  reward =
    (-2 * (if (explain) then 1 else 0)) +
    (10 * task_progress) +
    (if (task_progress == max_progress) then (5 * human_understanding) else 0);
}
