from uuid import uuid4
import time
import json

class ClusteringRequestClient(object):
    def __init__(self,**kwargs):
        self.requestId        = kwargs.get("requestId",str(uuid4()))
        # __________________________________________________________
        self.startRequestTime = kwargs.get("startRequestTime",time.time())
        # __________________________________________________________
        # _________________________________________________________
        self.datasetId        = kwargs.get("encryptedDatasetId","encrypted-dataset-0")
        self.algorithm        = kwargs.get("algorithm","SK_MEANS")
        self.m                = kwargs.get("m",3)
        self.k                = kwargs.get("k",3)
        # self.metadata         = kwargs.get("metadata",{})
        # 
        
    def serialize(self):
        return json.dumps(self.__dict__)
    