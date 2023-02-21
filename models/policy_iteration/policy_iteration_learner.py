import numpy as np
from models.policy_iteration.base_model import BaseModel


class PolicyIteration(BaseModel):
    def __init__(self, env, gamma=0.95, theta=1e-9, max_iter_eval=100):
        super().__init__(env)
        self.gamma = gamma
        self.theta = theta
        self.max_iter_eval = max_iter_eval

    # Recursive step
    def eval_state(self, s, improve_policy=False):
        # take max action
        v = self.get_values(s)

        max_a = -1
        max_v = -np.inf
        if improve_policy:
            # iterate all next states
            for a in range(self.env.num_actions):
                a_value = 0
                for s_ in range(self.env.num_states):
                    a_value += self.env.p(s_, s, a) * (self.env.r(s, a) + self.gamma * self.get_values(s_))
                if a_value > max_v:
                    max_v = a_value
                    max_a = a

            assert max_a != -1, 'max_a should not be -1'
            self.set_policy(s, max_a)

        # iterate all next states
        a = self.get_policy(s)
        new_value = 0
        for s_ in range(self.env.num_states):
            new_value += self.env.p(s_, s, a) * (self.env.r(s, a) + self.gamma * self.get_values(s_))
        self.set_values(s, new_value)

        return np.abs(v - self.get_values(s))

    def policy_eval(self):
        i = 0
        delta = 0
        for i in range(self.max_iter_eval):
            delta = 0
            # iterate all states
            for s in range(self.env.num_states):
                delta = max(delta, self.eval_state(s, improve_policy=False))

            # calculate the difference between new value and old value
            # if the difference is smaller than theta, stop the iteration
            if delta < self.theta:
                break

            # add to log
            self.log.add('mean_value', self.get_mean_value())

        print(f'policy evaluation finished after {i + 1} iterations with delta= {delta}')

    def policy_improvement(self):
        self.env.reset()
        policy_stable = True
        old_policy = self.get_policy_mat().copy()

        for s in range(self.env.num_states):
            self.eval_state(s, improve_policy=True)

        policy_delta = np.linalg.norm(self.get_policy_mat() - old_policy)

        if policy_delta != 0:
            policy_stable = False
        print(f'policy improvement finished with policy delta: {policy_delta}')

        return policy_stable
