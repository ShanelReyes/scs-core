from uuid import uuid4
import time

class ClusteringRequestManager(object):
    def __init__(self,**kwargs):
        self.requestId         = kwargs.get("requestId",str(uuid4()))
        self.arrivalTime       = kwargs.get("arrivalTime", int(time.time()) )
        self.startRequestTime  = kwargs.get("startRequestTime",0)
        self.latency           = self.arrivalTime - self.startRequestTime
        self.algorithm         = kwargs.get("algorithm","SKMEANS")
        self.encryptedMatrixId = kwargs.get("encryptedMatrixId","MATRIX_ID")
        self.metadata          = kwargs.get("metadata",{})