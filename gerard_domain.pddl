(define (domain robot_explanation)
  (:requirements :strips :probabilistic-effects)
  (:predicates
    (task_complete)                     ; Task successfully completed
    (failure_detected ?scenario)        ; A specific failure scenario detected
    (response_provided ?response)       ; A specific response was provided
    (needs_response)                    ; Robot needs to provide an explanation
  )

  (:action detect_failure
    :parameters (?scenario)
    :precondition (not (task_complete))
    :effect (and
      (failure_detected ?scenario)
      (needs_response)
    )
  )

  (:action provide_response
    :parameters (?response)
    :precondition (needs_response)
    :effect (and
      (response_provided ?response)
      (not (needs_response))
    )
  )

  (:action complete_task
    :precondition (not (task_complete))
    :effect (task_complete)
  )
)
