import copy
import numpy as np
from security.cryptosystem.liu import Liu
from utils.constants import Constants
from utils.Utils import Utils
from security.cryptosystem.FDHOpe import Fdhope


"""
Description:
	Distributed skmeans algorithm.
	Divide skmeans into two parts. The first ends when client interaction is required. The second ends when the matrix S is zero.
"""
class DBSKMeans(object):

	"""
	Description:
		The skmeans algorithm is started up to where the decryption of the matrix S is required
	"""
	def run1(self,**kwargs):
		try:
			status  = kwargs.get("status",Constants.ClusteringStatus.START)
			k       = kwargs.get("k",3)
			m       = kwargs.get("m",3)
			D1     = kwargs.get("encryptedMatrix")
			D1Shape = Utils.getShapeOfMatrix(D1)
			#D1      = _D1.tolist()
			U      = kwargs.get("UDM")
			#U       = _U.tolist()
			a       = kwargs.get("num_attributes",D1Shape[1])
			C_empty = Utils.empty_cluster(k = k)
			
			# Cuando va iniciando DBSKMeans 
			if( status == Constants.ClusteringStatus.START ):
				C              = list(map(lambda x:[D1[x].tolist()],list(range(0,k)))) #add the first k records of D to C
				C,label_vector = Utils.populateClusters(
					record_id         = k,
					UDM               = U,
					clusters          = C,
					ciphertext_matrix = D1,
				)
				Cent_i = [D1[i] for i in range(k)] # initializes the set of centroids with the first record in D
				Cent_j = Utils.calculateCentroids(
					clusters   = C,
					k          = k,
					attributes = a,
					m          = m,
					Liu        = Liu
				)
				S1  = self.generateShifMatrix(
					k = k,
					m = m,
					a = a,
					previous_centroids = Cent_i, 
					current_centroids  = Cent_j
				)
				self.label_vector = Utils.fillLabelVector(
					label_vector = label_vector,
					k            = k
				)
				return S1,Cent_i,Cent_j,self.label_vector
			else:
				Cent_j  = kwargs.get("Cent_j") 
				C, label_vector =  Utils.populateClusters(
					record_id = 0,
					UDM       = U,
					clusters  = C_empty,
					ciphertext_matrix = D1,
					centroids = Cent_j,
				)
				Cent_i = copy.copy(Cent_j) #Reasigna los elementos de cent_j a cent_i
				_Cent_j = Utils.calculateCentroids(
					clusters   = C,
					k          = k,
					attributes = a,
					m          = m,
					Liu        = Liu
				)
				S1     = self.generateShifMatrix(
					k = k,
					m =m,
					a = a,
					previous_centroids = Cent_i,
					current_centroids  = _Cent_j,
				)
				return  S1,Cent_i,Cent_j,label_vector
		except Exception as e:
			print(e)
			raise e


	"""
	description:  Update UDM matrix.
		A UDM matrix is a 3D matrix containing distances between the attribute values in each record
		and the corresponding attribute values in all other records.
	attributes:
		U: Updatable distance matrix
		Cent_i: previous set of centroids
		Cent_j: next set of centroids
		m: number of attributes of SK
	"""
	def run_2(self,**kwargs):
		status = kwargs.get("status",1)
		k      = kwargs.get("k",3)
		_U     = kwargs.get("UDM")
		U      = _U.tolist()
		a      = kwargs.get("attributes")
		_S     = kwargs.get("shiftMatrix")
		S      = _S.tolist()
		U1 = []
		for x in range(len(U)):
			U1.append([])
			for y in range(k):
				U1[x].append([])
				for z in range(a):
					U1[x][y].append([])
					if y > x: #Se revisa U completa.
						U1[x][y][z] = ((-U[y][x][z] + S[y][z])) #Suma de cada elemento de U con S
					else:
						U1[x][y][z] = (U[x][y][z] + S[y][z]) #Suma de cada elemento de U con S
		return U1


	"""
	Description:
		Generate encrypted shift matrix.
	"""
	def generateShifMatrix(self,**kwargs):
		Cent_i = kwargs.get("previous_centroids")
		Cent_j = kwargs.get("current_centroids")
		k      = kwargs.get("k",3)
		m      = kwargs.get("m",3)
		a      = kwargs.get("a",3)
		S1     = np.zeros((k,a,m)).tolist()
		for i in range(len(Cent_i)):
			for j in range(len(Cent_i[i])):
				S1[i][j] = Liu.subtract(
					ciphertext_1 = Cent_i[i][j], 
					ciphertext_2 = Cent_j[i][j]
					) #Resta con el esquema de Liu
		return S1