import numpy as np

"""
Description: Interface used for the expected result of the liu scheme
"""
class CipherschemeResult(object):
	def __init__(self,**kwargs):
		self.matrix         = kwargs.get("matrix",np.array([]))
		self.time           = kwargs.get("time",0)
		self.operation_type = kwargs.get("operation_type","encrypt")
	
	def __str__(self):
		return "MatrixStats({}s)".format(self.time)
