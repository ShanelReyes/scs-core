from requests import Session,Response
from utils.constants import Constants

class DumbClusteringWorker(object):
    def __init__(self,**kwargs):
        self.workerId  = kwargs.get("workerId")
        self.port      = kwargs.get("port",9000)

    def kmeans(self,**kwargs) -> Response:
        return self.session.post(
            "http://{}:{}/clustering/kmeans".format(self.workerId,self.port),
             headers = kwargs,
        )

    def DBSkMeans(self,**kwargs):
        return Response()

    def SKMeans(self,**kwargs) -> Response:
        return Response()


class SecureClusteringWorker(object):
    def __init__(self,**kwargs):
        self.workerId  = kwargs.get("workerId","localhost")
        self.port      = kwargs.get("port",9000)
        self.session   = kwargs.get("session")
        self.algorithm = kwargs.get("algorithm",Constants.ClusteringAlgorithms.SKMEANS)  

    def run(self,*args,**kwargs) -> Response:
        if(self.algorithm == Constants.ClusteringAlgorithms.SKMEANS):
            return self.__skmeans(**kwargs)
        elif(self.algorithm == Constants.ClusteringAlgorithms.KMEANS):
            return self.__kmeans(**kwargs)
        elif (self.algorithm == Constants.ClusteringAlgorithms.DBSKMEANS): 
            return self.__dbskmeans(**kwargs)
        elif (self.algorithm == Constants.ClusteringAlgorithms.DBSNNC):
            return self.__dbsnnc(**kwargs)
        else:
            return Response(
                response = None,
                status   = 503)


    def __kmeans(self,**kwargs) -> Response:
        return self.session.post(
            "http://{}:{}/clustering/kmeans".format(self.workerId,self.port),
             headers = kwargs.get("headers",{})
        )

    def __skmeans(self,**kwargs) -> Response:
        return self.session.post(
            "http://{}:{}/clustering/skmeans".format(self.workerId,self.port),
             headers = kwargs.get("headers",{})
        )

    def __dbskmeans(self, **kwargs) -> Response:
        return self.session.post(
            "http://{}:{}/clustering/dbskmeans".format(self.workerId,self.port),
            headers = kwargs.get("headers",{})
        )

    def __dbsnnc(self,**kwargs) -> Response:
        return self.session.post(
            "http://{}:{}/clustering/dbsnnc".format(self.workerId,self.port),
            headers = kwargs.get("headers",{})
        )