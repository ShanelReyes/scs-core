import numpy as np
import pandas as pd
import requests
# from constants import Constants
# from core.security.cryptosystem.liu import Liu
from uuid import uuid4
#from typing import deprecated
# ___________________________________________________


class Utils(object):
	def __init__(self):
		pass	
	
	def generate_centroids(**kwargs):
		k            = kwargs.get("k",3)
		plain_matrix = kwargs.get("plain_matrix")
		centroids    = []
		for x in range(k):
			centroids.append(plain_matrix[x])
		columns = Utils.getShapeOfMatrix(plain_matrix)[1]
		return np.array(centroids).reshape(k,columns)
	def fillLabelVector(**kwargs):
		label_vector = kwargs.get("label_vector",[])
		k = kwargs.get("k",2)
		lv = []
		for i in range(k):
			lv.append(i)
		label_vector = lv + label_vector
		return label_vector

	def repeatRequestByHeaders(**kwargs):
		STATUS          = {"COMPLETED":0,"START":1,"WORK_IN_PROGRESS":2}
		initial_headers = kwargs.get("headers",{})
		flag_key        = kwargs.get("flagKey","Status")
		request_fn      = kwargs.get("request_fn")
		flag_value      = initial_headers[flag_key]
		
		while(flag_value != STATUS.COMPLETED):
			response = request_fn()
			headers  = response.headers
			


	def loadMatrix(**kwargs):
		try:
			path         = kwargs.get("path")
			allow_pickle = kwargs.get("allow_pickle",False)
			xs           = np.load(path,allow_pickle=allow_pickle)
			return xs
		except Exception as e:
			print(str(e))
			raise e
	
	def getShapeOfMatrix(xs):
		xsType = type(xs)
		if(np.ndarray == xsType):
			return xs.shape
		else: 
			return np.array(xs).shape


	def downloadSaveAndLoad(**kwargs):
		try:
			Utils.downloadAndSaveFile(**kwargs)
			return Utils.loadMatrix(**kwargs)
		except Exception as e:
			print(str(e))
			raise e
			# return e
			# return None



	def downloadAndSaveFile(**kwargs):
		try:
			URL      = kwargs.get("URL")
			path     = kwargs.get("path")
			mode     = kwargs.get("mode","wb")
			response = requests.get(URL,timeout=100)
			# __________________________
			with open(path,mode) as f:
				f.write(response.content)
			return
		except Exception as e:
			print(str(e))
			raise e
			
	def downloadAndSaveFileV2(**kwargs):
		try:
			URL       = kwargs.get("URL")
			path      = kwargs.get("path")
			mode      = kwargs.get("mode","wb")
			chunkSize = kwargs.get("chunkSize",1024)
			response = requests.get(URL,timeout=100)
			# __________________________
			with open(path,mode) as f:
				for chunk in response.iter_content(chunkSize):
					f.write(chunk)
			return 
		except Exception as e:
			print(e)
			raise e
			# f.write(response.content)

	def saveMatrix(**kwargs):
		try:
			path   = kwargs.get("path")
			matrix = kwargs.get("matrix")
			mode   = kwargs.get("mode","wb")
			# _______________________________
			with open(path,mode) as f:
				np.save(f,matrix)
			return 
		except Exception as e:
			print(e)
			raise e
			


	def generateId(**kwargs):
		prefix    = kwargs.get("prefix")
		N         = kwargs.get("random_str_len",5)
		randomStr = str(uuid4())[:N]
		return "{}{}".format(prefix,randomStr)

	def prettyprint(x):
		xs = pd.DataFrame(x)
		print(xs)

	"""
	description: check that the shift matrix (S) is 0
	attributes:
		S: shift matrix
	"""
	def verifyZero(S) -> bool:
		return np.all( np.array(S) ==0 )

	"""
	description: Assign remaining registers of D1 to clusters
	attributes:
		rid: record id 
		U: Updatable distance matrix
		C: Set of clusters
		D1: Encrypted dataset 
		Cent_i: conjunto de centroides
		a: Number of attributes of D1
		k: Number of clusters
	"""
	def populateClusters(**kwargs):
		try:
			rid     = kwargs.get("record_id",0)
			U       = kwargs.get("UDM")
			C       = kwargs.get("clusters")
			D1      = kwargs.get("ciphertext_matrix")
			D1Shape = Utils.getShapeOfMatrix(D1)
			Cent_i  = kwargs.get("centroids",None)
			a       = kwargs.get("attributes",D1Shape[1])
			label_vector = []
			
			def calculateSimilarity(**kwargs):
				limit = kwargs.get("limit")
				sim   = kwargs.get("sim")
				x,y   = kwargs.get("xy",(0,0))
				for z in range(limit):
					sim += abs(U[x][y][z])
				return sim
			
			for x in range(rid,D1Shape[0]): #loop from k+1 to size of D1
				sim1 = []
				for y in range(len(C)): #from 0 to ks
					if y > x: #complete U is checked
						sim = calculateSimilarity(limit = a, sim = 0, xy = (y,x))
					else:
						sim = calculateSimilarity(limit = a, sim = 0, xy = (x,y))
					sim1.append(sim)
				min_index = sim1.index(min(sim1)) # the element with the least distance is located
				label_vector.append(min_index) #fill label_vector with the index of the shortest distance
				C[min_index].append(D1[x].tolist()) #the nearest element is placed in C
			return C, label_vector
		except Exception as e:
			print(e)
			raise e

	"""
	description: Generates a new set of centroids
	attributes:
		C: Set of clusters
		a: Number of attributes of D1
		k: Number of clusters
		m: number of attributes of SK
	"""
	def calculateCentroids(**kwargs):
		try:
			C    = kwargs.get("clusters")
			k    = kwargs.get("k")
			a    = kwargs.get("attributes")
			m    = kwargs.get("m")
			Liu  = kwargs.get("Liu")
			cent = np.zeros((k,a,m)).tolist() #define cent as an empty array
			for j in range(k):
				average = np.zeros((a,m)).tolist() #the average of the current cluster will be saved
				cjLen   = len(C[j]) #number of elements in the current cluster
				if(cjLen  == 0): #if the current cluster has no elements
					cent[j]= np.zeros((a,m)).tolist() #fill that cluster with zeros
				else: 
					for i in range(cjLen):  
						rec1 = C[j][i] #extract the first record from the cluster
						for q in range(a): #traverse the record
							E1 = average[q] #extract what is found in average
							E2 = rec1[q] #extract an attribute from the record
							average[q] = Liu.add(ciphertext_1 = E1, ciphertext_2 = E2) #make a homomorphic sum
					for q in range(a): # the attributes are traversed to do the multiplication
						v1 = 1/cjLen 
						E1 = average[q] #extract what is found in average
						cent[j][q] = Liu.multiply_c(scalar = v1, ciphertext_1 = E1) #make a homomorphic multiply
			return cent
		except Exception as e:
			print(e)
			raise e

   

	def dest_fx_vector(xs,i,x):
		xs.append(x)
		return xs
	
	def dest_fx_matrix(xs,i,x):
		xs[i].append(x)
		return xs
	
	"""
	Description: Move from source to dest
		Arguments:
		 dest: Destination list | matrix
		 dest_fx: Function to perform the appending operation over destination list|matrix
		 source: Source list | matrix
		 limit: Number of iteration to appending elementos from source to dest.
	"""
	def appends(**kwargs):
		xs      = kwargs.get("dest", [])
		dest_fx = kwargs.get("dest_fx",lambda x,i:x)
		ys      = kwargs.get("source",[])
		k       = kwargs.get("limit",0)
		for i in range(k):
			xs = dest_fx(xs,i,ys[i])
		return xs

	def fxTesis(*args):
		D    = args[0]
		x    = args[1]
		y    = args[2]
		z    = args[3] 
		return D[x][z] - D[y][z]
	
	def euclideanDistance(*args):
		D    = args[0]
		x    = args[1]
		y    = args[2]
		z    = args[3] 
		#return np.sqrt( (x[1] - x[0])**2 + (y[1] - y[0])**2  )
		return np.distance.euclidean(D[x][z],D[y][z])

	
	def empty_cluster(**kwargs):
		k = kwargs.get("k",3)
		return [[] for i in range(0,k)]


	"""
	description: EUDM matrix calculation
	attributes:
		D: numeric dataset
		a: number of attributes of D
	"""
	"""
	#@deprecated("se usaba para dbskmeans pero ahora usa el de skmeans")
	def calculateUDM(**kwargs): #Calculo de la matriz UDM
		D      = kwargs.get("plaintext_matrix")
		DShape = Utils.getShapeOfMatrix(D)
		a      = kwargs.get("attributes",DShape[1]) 
		EU     = []
		EU     = Utils.create_UDM(plaintext_matrix = D)
		for x in range(DShape[0]): #Llenado de U con distancias entre los datos en plano
			for y in range(x+1):
				for z in range(a):
					EU[x][y][z] = (D[x][z] - D[y][z]) #Calculo de distancias
		return np.array(EU)"""
	
	

if __name__ == "__main__":
	h = Utils.calculateDM(
		plaintext_matrix = 
		[ [0.73,8.84],  
		 [49.93,34.44],
	[0.57,65.04],
	[62.15,32.29],
	[59.47,36.04]
]
	)
	

