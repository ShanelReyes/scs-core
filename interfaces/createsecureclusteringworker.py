import json

"""
Notes:
    DTO (Data Transfer Object): Set of attributes that can be sent or retrieved from the server in a single invocation
"""
class CreateSecureClusteringWorker(object):
    def __init__(self,**kws):
        self.nodeId    = kws.get("nodeId")
        self.nodeIndex = kws.get("nodeIndex",0)
        self.image     = kws.get("image","secure-clustering-worker:latest")
        self.network   = kws.get("network", {"name":"test","driver":"bridge"})
        self.ports     = kws.get("ports")
        default_envs   = {
            "NODE_ID": self.nodeId,
            "NODE_PORT": str(self.ports["docker"]),
            "HOST_PORT": str(self.ports["host"]),
            "NODE_INDEX": str(self.nodeIndex),
            "SECURE_CLUSTERING_MANAGER_HOSTNAME": kws.get("SECURE_CLUSTERING_MANAGER_HOSTNAME","scm-0"),
            "SECURE_CLUSTERING_MANAGER_PORT": str(kws.get("SECURE_CLUSTERING_MANAGER_PORT","6000")),
            "LOG_PATH": "/logs",
            "SINK_PATH": "/sink"
        }
        
        _envs          = kws.get("envs",{})
        self.envs      = {**default_envs,**_envs}
        print("ENVS {}".format(self.envs))
        self.labels    = kws.get("labels",{})
        self.volumes   = kws.get("volumes",{
            kws.get("HOST_LOG_PATH","/log") : "/logs",
            kws.get("HOST_SINK_PATH","/test/sink/")+self.nodeId: "/sink"
        })
        self.resources = kws.get("resources",{
            "cpuCount":1,
            "cpuPeriod":0,
            "cpuQuota":0,
            "memory":1000000000
        })
        
    def serialize(self):
        return json.dumps(self.__dict__)


    def __str__(self):
        return str(self.__dict__)
