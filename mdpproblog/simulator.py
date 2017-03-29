# This file is part of MDP-ProbLog.

# MDP-ProbLog is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# MDP-ProbLog is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with MDP-ProbLog.  If not, see <http://www.gnu.org/licenses/>.

import random

from mdpproblog.fluent import StateSpace, ActionSpace


class Simulator(object):
    """
    Simulator class for MDPs. Given an `mdp` and a `policy`,
    it generates histories and its corresponding
    expected cummulative discounted rewards.

    :param mdp: an MDP formulation
    :type mdp: mdpproblog.mdp.MDP object
    :param policy: mapping from state to action
    :type policy: dict of (tuple, str)
    """

    def __init__(self, mdp, policy):
        self._mdp = mdp
        self._policy = policy

        self.__current_state_fluents = mdp.current_state_fluents()
        self.__actions = ActionSpace(mdp.actions())

    def run(self, trials, horizon, start_state, gamma=0.9):
        """
        Simulate a number of `trials` of given `horizon` from `start_state`
        following its policy. Compute the discounted expected reward using
        `gamma` as discount factor. Return average reward over all trials,
        a list of rewards received at each trial and list of sampled states
        for each trial.

        :param trials: number of trials
        :type trials: int
        :param horizon: number of timesteps
        :type horizon: int
        :param start_state: state from which the simulation starts
        :param gamma: discount factor
        :type gamma: float
        :rtype: tuple (float, list of list of floats, list of list of states)
        """
        rewards = []
        paths = []
        for i in range(trials):
            total_reward, trial_path = self.run_trial(horizon, start_state, gamma)
            rewards.append(total_reward)
            paths.append(trial_path)
        avg = sum(rewards) / trials
        return avg, rewards, paths

    def run_trial(self, horizon, start_state, gamma=0.9):
        """
        Simulate a single trial of given `horizon` from `start_state`
        following its policy. Compute the discounted expected reward using
        `gamma` as discount factor. Return total discounted reward over all
        steps of the horizon and a list of sampled states in the trial.

        :param trials: number of trials
        :type trials: int
        :param horizon: number of timesteps
        :type horizon: int
        :param start_state: state from which the simulation starts
        :param gamma: discount factor
        :type gamma: float
        :rtype: tuple (float, list of states)
        """
        state = start_state
        discount = 1.0
        total = 0.0
        path = [start_state]
        for step in range(horizon):
            action = self.__select_action(state)
            reward = self.__collect_reward(state, action)
            state  = self.__sample_next_state(state, action)
            total += discount * reward
            path.extend([action, state])
            discount *= gamma
        return total, path

    def __select_action(self, state):
        """
        Return the action prescribed by its policy for the given `state`.

        :param state: state represented as a valuation over fluents
        :type state: tuple of pairs (str, bool)
        :rtype: str
        """
        a = self._policy[state]
        for action in self.__actions:
            if action[a] == 1:
                return action

    def __collect_reward(self, state, action):
        """
        Return the reward for applying `action` to `state`.

        :param state: state represented as a valuation over fluents
        :type state: tuple of pairs (str, bool)
        :param action: action represented as a valuation over fluents
        :type action: tuple of pairs (str, bool)
        :rtype: float
        """
        state = StateSpace.state(state)
        cache = (StateSpace.index(state), ActionSpace.index(action))
        return self._mdp.reward(state, action, cache)

    def __sample_next_state(self, state, action):
        """
        Return next state sampled from the transition distribution
        given by applying `action` to `state`.

        :param state: state represented as a valuation over fluents
        :type state: tuple of pairs (str, bool)
        :param action: action represented as a valuation over fluents
        :type action: tuple of pairs (str, bool)
        :rtype: state represented as a valuation over fluents
        """
        valuation = []
        state = StateSpace.state(state)
        cache = (StateSpace.index(state), ActionSpace.index(action))
        probabilities = self._mdp.transition(state, action, cache)
        for (i, (term, probability)) in enumerate(probabilities):
            value = int(random.random() <= probability)
            valuation.append((self.__current_state_fluents[i], value))
        return tuple(valuation)
