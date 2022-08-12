import random
import numpy as np


"""
Description: 
	class to represent a symmetric encryption scheme
Attributes:
    _round: Flag to know if decryption needs to be rounded based on plaintext type
"""

class Liu(object):
	def __init__(self,**kwargs):
		self.round = kwargs.get("round",False)

	""" 
	description: Generate a uniform distributed numbers [0,1]
	"""
	def generateRandom(self):
		self.r = random.uniform(0,1)
		return self.r


	"""
    description: Generates the secret key (SK) used to encrypt and decrypt
    attributes: 
		m: mumber of attributes of SK
	constraints:
        1. m >= 3
		2. the last tp: if (km + sm + tm)==0 it must be generated again.
		3. sk -> [(k_1,s_1,t_1)...(k_m,s_m,t_m)]
    """
	def secretKey(self, **kwargs): 
		m = kwargs.get("m",3)
		self.sk = []
		zero_tp = (0,0,0)
		for i in range(m):
			# Se generan las tripletas
			tp = self.generateRandom(),self.generateRandom(),self.generateRandom() 
			if(i==(m-1)): 
				while(zero_tp == tp):
					tp = self.generateRandom(), self.generateRandom(), self.generateRandom()
			self.sk.append(tp)
		return self.sk


	"""
	description: split a plaintext matrix into vectors
    """
	def encryptMatrix(self,**kwargs):
		vss = kwargs.get("plaintext_matrix",[])
		new_kwargs = lambda vs: {**{"plaintext_vector":vs},**kwargs}
		return [ self.encryptVector(**new_kwargs(vs)) for vs in vss ]


	"""
	description: split a plaintext vector into scalars
    """
	def encryptVector(self,**kwargs):
		vs = kwargs.get("plaintext_vector",[])
		new_kwargs = lambda v: {**{"plaintext":v},**kwargs}
		return [ self.encryptScalar(**new_kwargs(v)) for v in vs ]


	"""
	description: Encrypt a plaintext using SK
	attributes:
		v: plaintext
		sk: secret key
		m: number of attributes of SK
	constraints:
		1. E1: sk[0][0] * sk[0][2] * v + sk[0][1] * self.R[m-1] + sk[0][0] * (self.R[0] - self.R[m-2])
		2. Ei: sk[i][0] * sk[i][2] * v + sk[i][1] * self.R[m-1] + sk[i][0] * (self.R[i] - self.R[i-1])
		3. Em: sk[m-1][0] + sk[m-1][1] + sk[m-1][2]) * self.R[m-1]
    """
	def encryptScalar(self,**kwargs): 
		v          = kwargs.get("plaintext") 
		self.round = True if(type(v) == int or type(v) == np.int64) else False
		sk         = kwargs.get("secret_key")
		m          = kwargs.get("m",3)
		self.E     = []
		self.R     = [ self.generateRandom() for i in range (m) ]
		#E1 formula
		e1         =  self.__eEncrypt(
			ki = sk[0][0],
			ti = sk[0][2],
			v  = v, 
			si = sk[0][1],
			rm = self.R[m-1],
			rrdiff = (self.R[0]-self.R[m-2])
		)
		self.E.append(e1) 
		#Ei formula
		for i in range(1,m-1):
			ei =  self.__eEncrypt(
				ki = sk[i][0],
				ti = sk[i][2],
				v  = v, 
				si = sk[i][1],
				rm = self.R[m-1],
				rrdiff = (self.R[i]-self.R[i-1])
			)
			self.E.append(ei)	
		#Em Formula
		self.E.append((sk[m-1][0] + sk[m-1][1] + sk[m-1][2]) * self.R[m-1]) 
		return self.E


	"""
    description: Generates the necessary tp for the encrypt method
    attributes:
        ki, ti, si:  real numbers
        v: plaintext
        rm: record at position m
		rrdiff: resta de r1 - rm-1
	"""
	def __eEncrypt(self,**kwargs):
		ki     = kwargs.get("ki")
		ti     = kwargs.get("ti")
		v      = kwargs.get("v")
		si     = kwargs.get("si")
		rm     = kwargs.get("rm")
		rrdiff = kwargs.get("rrdiff")
		return ki * ti * v + si * rm + ki * rrdiff


	"""
	description: split a ciphertext matrix into vectors
    """
	def decryptMatrix(self,**kwargs):
		css = kwargs.get("ciphertext_matrix",[])
		new_kwargs = lambda cs: {**{"ciphertext_vector":cs},**kwargs}
		return [ self.decryptVector(**new_kwargs(cs)) for cs in css ]
		

	"""
	description: split a ciphertext vector into scalars
    """
	def decryptVector(self,**kwargs):
		cs = kwargs.get("ciphertext_vector",[])
		new_kwargs = lambda c: {**{"ciphertext":c},**kwargs}
		return [ self.decryptScalar(**new_kwargs(c)) for c in cs ]


	"""    
    description: Decrypt a ciphertext using SK
	attributes:
		E: ciphertext
		sk: secret key
		m: number of attributes of SK
	"""
	def decryptScalar(self,**kwargs): 
		E  = kwargs.get("ciphertext")
		sk = kwargs.get("secret_key")
		m  = kwargs.get("m")
		t,e = 0,0
		for i in range(m-1):
			ti = sk[i][2]
			t += ti
		s = (E[m-1]) / (sk[m-1][0] + sk[m-1][1] + sk[m-1][2])
		for i in range(m-1):
			ei = (E[i] - s * sk[i][1])/ sk[i][0]
			e += ei
		v = float(e)/float(t)
		# print(self.round)
		return int(np.around(v,decimals=2)) if(self.round) else v


	"""
	description: Addition of two ciphertexts
	attributes:
		E1: first ciphertext
		E2: second ciphertext
    """
	def add(E1, E2):
		return (np.array(E1) + np.array(E2)).tolist()

	# self.E3 = []
	# for i in range(m):
	# 	self.E3.append(E1[i] + E2[i])
	# return self.E3
	"""
	description: Multiplication of two ciphertexts
	attributes:
		E1: first ciphertext
		E2: second ciphertext
    """
	def multiply(E1, E2):
		E3 = []
		m  = len(E1)
		for i in range(m):
			for j in range(m):
				E3.append(E1[i] * E2[j])
		return E3


	"""
	description: Check multiplication of two ciphertexts
	attributes:
		E: ciphertext
		sk: secret key
		m: number of attributes of SK
    """
	def verify_mult(self, E, sk, m):
		v1,v = [],[]
		for i in range(len(E)):
			v1.append(E[i])
			if ((i%m)==(m-1)):
				v.append(self.decrypt(v1, sk, m))
				v1 = []
		self.E3 = self.decrypt(v, sk, m)
		return self.E3


	""" 
	description: Multiply a ciphertext by a plaintext
	attributes:
		v1: plaintext
		E1: ciphertext
    """
	def multiply_c(v1, E1):
		E3 = []
		m  = len(E1)
		for i in range(m):
			E3.append(v1 * E1[i])
		return E3


	"""
	description: Subtract two ciphertexts
	attributes:
		E1: first ciphertext
		E2: second ciphertext
		m: number of attributes of SK
	"""
	def subtract(E1, E2):
		E3 = []
		m  = len(E1)
		s1 = Liu.multiply_c(-1, E2)
		E3 = Liu.add(E1, s1)
		return E3