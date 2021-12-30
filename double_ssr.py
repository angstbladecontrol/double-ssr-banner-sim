import numpy as np
import timeit

# Yuting Shen
# Gacha rolling simulation
# originally written for the FGO Apocrypha banner

# Explanation:
# I want to get copies of 2 different servants by rolling on their banners
# Each banner is like a lottery and each roll is like buying a lottery ticket. I only have a limited number of rolls.
# I want to determine my strategy for how I should roll on these banner
# I can roll on 3 banners but they are only available for a limited time. If i skip a banner, I cannot go back.
# The first banner gives me a chance at getting copies of the first servant
# The second banner gives me a chance at getting copies of the second servant
# the last banner gives me a chance at getting copies of both servants but at reduced rate for each

# first copy is the most important.
# addtional copies are valuable but beyond 2 copies has diminishing value for me
# I do not have an explicit utility for each outcome so I want to tabulate the probability of any result
# then I can make an intuitive decision on what strategy to go for

# RollSimulation object has the simulation parameters and the results stored as properties
# results are calculated lazily
# 2 strategies, soloForNP1 and duoOnly
# details of strategy in implementation
class RollSimulation:
    def __init__(self, **kwargs):
        # init simulation parameters
        self.trials = 500000 # sample size
        self.rollsPerTrial = 450 # the number of rolls i have in each simulation
        self.successChanceSingle = 0.007 # chance of getting any servant on their solo banner
        self.successChanceDouble_1 = 0.004 # chance of getting first servant on the duo banner
        self.successChanceDouble_2 = 0.004 # chance of getting second servant on the duo banner
        self.__dict__.update(kwargs)

        # init result properties as None but they will be a 3x3 matrix
        # axis 0 is first servant and axis 1 is second servant
        # index of axis corresponds to number of that servant rolled.
        # index 0 means num of trial resulted in np0 (total failure)
        # index 2 means num of trial resulted in >= np2.
        # eg. so the number in [1,2] is how many times trials got 1 of first servant and 2 or more of 2nd serv
        self._soloForNP1 = None
        self._duoOnly = None

    @property
    def soloForNP1(self, prob = True):
        if self._soloForNP1 is None:
            self._soloForNP1 = self.run_soloForNP1()

        return self._soloForNP1

    @property
    def duoOnly(self):
        if self._duoOnly is None:
            self._duoOnly = self.run_duoOnly()

        return self._duoOnly

    # set the values for the results tables.
    def runAllStrats(self):
        self._soloForNP1 = self.run_soloForNP1()
        self._duoOnly = self.run_duoOnly()

    # SIMULATIONS
    # function to do the simulation for each strategy
    # using numpy arrays for best efficiency
    def run_soloForNP1(self):
        # This strategy rolls on the first banner until i get 1 copy of the first servant
        # then roll on the second banner until i get 1 copy of the second servant
        # then roll on the last banner until i'm out of rolls
        _result_matrix = np.zeros((3, 3))
        for tn in range(self.trials):

            # initialize success counter
            m = 0  # axis 0
            n = 0  # axis 1

            # make pre roll array size ROLLS PER TRIAL
            roll_rns = np.random.rand(self.rollsPerTrial)

            roll_failed = roll_rns > self.successChanceSingle

            # get the first FALSE (roll did not fail) index
            first_succ = np.argmin(roll_failed) # using argmin kinda bad but i dont feel like implementing get first
            # confirm this is actually a FALSE
            if not roll_failed[first_succ]:
                m += 1
            else:
                # no success in array
                _result_matrix[m, n] += 1
                continue

            # we use try except value error because if we're on the last index,
            # then [(last_ind+1):] slice will give empty array
            try:
                # second_succ index is first_succ + 1 + index of first FALSE in the slice (slice starts at 0)
                # if the next success is right after the first succ,
                # then np.argmin will return 0 and second succ = first_succ+1
                second_succ = first_succ + 1 + np.argmin(roll_failed[(first_succ + 1):])
            except ValueError:  # value error because if i + 1 == length, array[length:] gives empty
                _result_matrix[m, n] += 1
                continue

            if not roll_failed[second_succ]:
                n += 1
            else:
                # no success in array.
                _result_matrix[m, n] += 1
                continue

            # do a check here so we dont have to try except the first iteration of np.argmin for m_roll_failed
            if (second_succ + 1) == self.rollsPerTrial:
                _result_matrix[m, n] += 1
                continue

            # now roll on duo rate up with remaining
            # get roll_rns and remake the mask with a slice
            m_roll_failed = roll_rns[(second_succ + 1):] > self.successChanceDouble_1
            n_roll_failed = roll_rns[(second_succ + 1):] <= (1 - self.successChanceDouble_2)
            # get the initial next roll failed is FALSE
            i = np.argmin(m_roll_failed)
            while not m_roll_failed[i]:  # terminate condition is the ith roll did not fail
                # if m == 30:
                # something bad happened. debugging
                #    print(tn)
                #    print(m_roll_failed[(i):])
                #    print(np.argmin(m_roll_failed[(i):]))
                #    raise RuntimeError()

                # increment
                m += 1

                # get next
                try:
                    i = i + 1 + np.argmin(m_roll_failed[(i + 1):])
                except ValueError:
                    # success is last index so break out of while loop
                    break

            i = np.argmin(n_roll_failed)
            while not n_roll_failed[i]:
                # if n == 30:
                # something bad happened
                #    print(tn)
                #    print(n_roll_failed[(i):])
                #    print(np.argmin(n_roll_failed[(i):]))
                #    raise RuntimeError()

                # increment
                n += 1

                # get next
                try:
                    i = i + 1 + np.argmin(n_roll_failed[(i + 1):])
                except ValueError:  # value error because if i + 1 == length, array[length:] gives empty
                    break

            _result_matrix[min(m, 2), min(n, 2)] += 1

        return _result_matrix

    def run_duoOnly(self):
        # This strategy rolls on the last banner until i'm out of roll ignoring the first 2 banners
        _result_matrix = np.zeros((3, 3))
        for tn in range(self.trials):

            # initialize success counter
            m = 0  # axis 0
            n = 0  # axis 1

            # make pre roll array size ROLLS PER TRIAL
            roll_rns = np.random.rand(self.rollsPerTrial)

            m_roll_failed = roll_rns > self.successChanceDouble_1
            n_roll_failed = roll_rns <= (1 - self.successChanceDouble_2)

            # get the initial next roll failed is FALSE
            i = np.argmin(m_roll_failed)
            while not m_roll_failed[i]:  # terminate condition is the ith roll did not fail
                # if m == 401:
                # debugging
                #    print(tn)
                #    raise RuntimeError()

                # increment
                m += 1

                # get next
                try:
                    i = i + 1 + np.argmin(m_roll_failed[(i + 1):])
                except ValueError:
                    # success is last index so break out of while loop
                    break

            i = np.argmin(n_roll_failed)
            while not n_roll_failed[i]:
                # if n == 401:
                # debugging
                #    print(tn)
                #    raise RuntimeError()

                # increment
                n += 1

                # get next
                try:
                    i = i + 1 + np.argmin(n_roll_failed[(i + 1):])
                except ValueError:  # value error because if i + 1 == length, array[length:] gives empty
                    break

            _result_matrix[min(m, 2), min(n, 2)] += 1

        return _result_matrix

    def whichStrat(self, m = 1, n = 1):
        # suggest which strat given target minimum n and m
        # I don't really need this but it makes it easy to get quick suggestion for different targets

        countSolo = np.sum(self.soloForNP1[m:, n:])
        countDuo = np.sum(self.duoOnly[m:, n:])

        if countDuo > countSolo:
            return "Roll only on duo banner. P(Duo): " + str(countDuo/self.trials)\
                   + " P(Solo): " + str(countSolo/self.trials)
        else:
            return "Roll on each single banner until np1 then roll duo. P(Duo): " + str(countDuo/self.trials)\
                   + " P(Solo): " + str(countSolo/self.trials)

if __name__ == "__main__":
    # set seed for testing
    np.random.seed(1)

    # test params
    TRIALS = 100000
    ROLLSPERTRIAL = 500

    sim = RollSimulation(trials = TRIALS, rollsPerTrial = ROLLSPERTRIAL)

    start_tm = timeit.default_timer()

    sim.runAllStrats()

    elapsed_tm = timeit.default_timer() - start_tm
    print('simulation run time:', str(elapsed_tm))

    print('roll solo m then solo n then duo')
    print(sim.soloForNP1/sim.trials)

    print('rolling only duo rate up')
    print(sim.duoOnly/sim.trials)

    print('i want at least 1 copy of both servants')
    print(sim.whichStrat(1,1))
