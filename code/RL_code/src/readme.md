# Reinforcement Learning Approach

This section of the code is dedicated to the RL approach.

## Requirements

You need to install pybrain :
```
git clone git://github.com/pybrain/pybrain.git
cd pybrain
python setup.py install
```

## Train and visualize an agent

In this section we describe how to train an agent using a normalized version of the solar and wind production and electricity market price for France in September 2018. More specifically, the training set is composed of 26 days, 2 validation days and 2 test days.

##### With Q learning 

Using default setting :
```
python fitting_q.py
```
This will save the actions taken on the test days, which you can then visualize using the notebook visualize_q_agent.ipynb

##### With NFQ (neuro-fitted Q-iteration)

Using default setting :
```
python fitting_nfq.py
```
This will save the actions taken on the test days, which you can then visualize using the notebook visualize_nfq_agent.ipynb

## Author

Malik Boudiaf, mboudiaf@stanford.edu
