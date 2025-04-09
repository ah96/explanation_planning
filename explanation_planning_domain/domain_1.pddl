domain explanation_planning {

    types {
        explanation: object;
        task_step: object;
    };

    pvariables {
        // Fluents: State Variables
        human_confused: { state-fluent, bool, default = false };
        task_step_done(task_step): { state-fluent, bool, default = false };
        explanation_given(explanation): { state-fluent, bool, default = false };
        failure_occurred: { state-fluent, bool, default = false };

        // Probabilities of human confusion and failures per task step
        prob_confusion(task_step): { non-fluent, real, default = 0.2 };
        prob_failure(task_step): { non-fluent, real, default = 0.1 };

        // Actions
        execute_task_step(task_step): { action-fluent, bool, default = false };
        provide_explanation(explanation): { action-fluent, bool, default = false };
    };

    cpfs {
        // Human confusion evolves probabilistically
        human_confused' = if (exists_{?t: task_step} execute_task_step(?t)) then Bernoulli(prob_confusion(?t))
                          else human_confused;

        // Failure occurrence evolves probabilistically
        failure_occurred' = if (exists_{?t: task_step} execute_task_step(?t)) then Bernoulli(prob_failure(?t))
                            else failure_occurred;

        // Explanation resets confusion
        human_confused' = if (exists_{?e: explanation} provide_explanation(?e)) then false else human_confused;

        // Task step completion
        task_step_done'(?t) = if (execute_task_step(?t)) then true else task_step_done(?t);

        // Explanation state tracking
        explanation_given'(?e) = if (provide_explanation(?e)) then true else explanation_given(?e);
    };

    reward = if (failure_occurred) then -10.0
             else if (human_confused) then -5.0
             else if (exists_{?e: explanation} provide_explanation(?e)) then 3.0
             else -1.0;
}
