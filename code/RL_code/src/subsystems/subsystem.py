author = 'Malik Boudiaf, mboudiaf@stanford.edu'

import numpy as np

class Subsystem(object):

    def find_closest_discrete_load(self,discrete_table,value):
        idx = (np.abs(discrete_table- value)).argmin()
        return discrete_table[idx]