(define (problem robot_explanation_problem)
  (:domain robot_explanation)
  (:objects
    agent_error suboptimal_behavior agent_inability unforeseen_circumstances uncertainty social_norm_violation normal_interaction - scenario
    why_explanation what_explanation apology ask_for_help narrate_next_action continue_without_comment - response
  )
  (:init
    (not (task_complete))
  )
  (:goal
    (and
      (task_complete)
      (response_provided apology)  ; Example goal requiring specific response
    )
  )
)
