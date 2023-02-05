import numpy as np

"""
Description: Interface used for the expected result of the dataowner
"""
class DataownerResult(object):
	def __init__(self,**kwargs):
		self.udm_time              = kwargs.get("udm_time",0)
		self.UDM                   = kwargs.get("UDM",np.array([]))
		self.encrypted_matrix      = kwargs.get("encrypted_matrix",np.array([]))
		self.encrypted_matrix_time = kwargs.get("encrypted_matrix_time",np.array([]))
		self.messageIntervals      = kwargs.get("messageIntervals",{})
		self.cypherIntervals       = kwargs.get("cypherIntervals",{})
		self.encrypted_threshold   = kwargs.get("encrypted_threshold",0)