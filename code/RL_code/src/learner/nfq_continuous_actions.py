from scipy import r_

from learner.valuebased import ValueBasedLearner
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers.rprop import RPropMinusTrainer
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.utilities import one_to_n


class NFQ_test(ValueBasedLearner):
    """ Neuro-fitted Q-learning"""

    def __init__(self, maxEpochs=50, epsilon = 0.3, gamma = 0.99,id2action = None, alpha=0.5):
        ValueBasedLearner.__init__(self,epsilon)
        self.gamma = gamma
        self.maxEpochs = maxEpochs
        self.id2action = id2action
        self.alpha= alpha

    def learn(self):
        # convert reinforcement dataset to NFQ supervised dataset
        supervised = SupervisedDataSet(self.module.network.indim, 1)

        for seq in self.dataset:
            lastexperience = None
            for state, action, reward in seq:
                if not lastexperience:
                    # delay each experience in sequence by one
                    lastexperience = (state, action, reward)
                    continue
         
                # use experience from last timestep to do Q update
                (state_, id_action_, reward_) = lastexperience
                action_ = self.id2action[int(id_action_)]
                #print(int(id_action_))
                Q = self.module.getValue_test(state_, action_)
                

                #inp = r_[state_, one_to_n(int(action_[0]), self.module.numActions)]
                inp = r_[state_, action_]
                tgt = Q + self.alpha*(reward_ + self.gamma * max(self.module.getActionValues_test(state)) - Q)
                supervised.addSample(inp, tgt)

                # update last experience with current one
                lastexperience = (state, action, reward)

        # train module with backprop/rprop on dataset
        trainer = RPropMinusTrainer(self.module.network, dataset=supervised, batchlearning=True, verbose=True)
        trainer.trainUntilConvergence(maxEpochs=self.maxEpochs)

        # alternative: backprop, was not as stable as rprop
        # trainer = BackpropTrainer(self.module.network, dataset=supervised, learningrate=0.005, batchlearning=True, verbose=True)
        # trainer.trainUntilConvergence(maxEpochs=self.maxEpochs)



