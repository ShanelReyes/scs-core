import numpy as np

"""
Description: Interface used for the expected result of the clustering algorithms used
"""
class ClusteringResult(object):
    def __init__(self,**kwargs):
        self.label_vector    = kwargs.get("label_vector",np.array(()))
        self.n_iterations    = kwargs.get("n_iterations",0)
        self.response_time   = kwargs.get("response_time",0)
        self.service_time    = kwargs.get("service_time",0)
        self.clustering_time = kwargs.get("clustering_time",0)
        self.udm_time        = kwargs.get("udm_time",0)
        self.cipher_time     = kwargs.get("cipher_time",0)