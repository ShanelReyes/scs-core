
class Constants(object):
    
    class ClusteringStatus(object):
        COMPLETED        = 0
        START            = 1
        WORK_IN_PROGRESS = 2

    class ClusteringAlgorithms(object):
        SKMEANS   = "SKMEANS"
        DBSKMEANS = "DBSKMEANS"
        KMEANS    = "KMEANS"
        DBSNNC    = "DBSNNC"