import random
import numpy as np
from collections import Counter

"""
Description: Frequency Concealment and Distribution OPE (FDH-OPE) scheme, used to facilitate the required UDM operation.
"""
class Fdhope(object):

    """
    description: generates secret keys using the FDHOPE scheme.
    """
    def keygen(**kwargs): 
        D                    = kwargs.get("dataset")
        minVal               = kwargs.get("minValue", 0)
        max_range            = kwargs.get("max_range",5) #Maximum number of ranges
        proportion           = kwargs.get("proportion", 5)
        maxVal_messagespace  = round(Fdhope.findMax(D)) + 1 #+1 to be able to place the last element in the range
        maxVal_cipherspace   = maxVal_messagespace * proportion 
        lenTriangle          = len(D) * len(D[0])
        n_range              = random.randint(2,max_range) #Number of ranges
        messagespace,new_density = {}, {}

        _messagespace = Fdhope.generate_range_values( #Generate possible message space
            minValue = minVal, 
            maxValue = maxVal_messagespace, 
            n_range  = n_range
        )

        old_density  = Fdhope.calculate_dens( #Calculates the amount of data that is in each range
            dataset            = D, 
            messagespace       = _messagespace, 
            maxVal_cipherspace = maxVal_cipherspace
        )
        
        messagespace_filtered = dict(list(filter(lambda x: old_density.get(x[0],0) > 0, _messagespace.items()))) #Remove ranges where no data exists
        messagespace_list     = list(messagespace_filtered.items()) #Convert messagespace to list

        global_max = -1
        for index,key in enumerate(messagespace_filtered): #
            new_key                 = "RANGE_{}".format(index) # R
            message_space_pair      = messagespace_list[index] # Locate the element to be analyzed (RANGE_ID -> TUPLE_RANGE)
            old_key                 = message_space_pair[0] # Value in density[key]
            new_density[new_key]    = old_density[old_key]  # 
            rango                   =  message_space_pair[1] # TUPLA
            current_min,current_max = rango
            if(index==0 or current_min <= global_max):
                global_max = current_max
                messagespace[new_key]   =  (current_min,current_max)#
            else:
                if(current_min > global_max):
                    messagespace[new_key] = (global_max,current_max)#
                    global_max            = current_max
        intervalLength = Fdhope.calculate_intervalLength( #Calculates the size of the intervals for the ciphertextspace
            density            = new_density, 
            lenTriangle        = lenTriangle, 
            maxVal_cipherspace = maxVal_cipherspace
        )
        cipherspace  = Fdhope.generate_range_values( 
            minValue      = minVal,
            maxValue      = maxVal_cipherspace,
            n_range       = len(intervalLength), #New range size
            range_ids     = intervalLength.keys(), #Extract keys to intervalLength
            ranges_values = np.cumsum([0] + list(intervalLength.values())) #Make the cumulative sum of the elements in intervalLength
        )
        return messagespace, cipherspace
        
    
    """
    Description: FDH-OPE encryption algorithm
    """
    def encrypt(**kwargs):
        plaintext    = kwargs.get("plaintext") 
        sens         = kwargs.get("sens",0.01)
        messagespace = kwargs.get("messagespace")
        cipherspace  = kwargs.get("cipherspace")

        interval_id = Fdhope.getIntervalID(
            plaintext    = plaintext, 
            messagespace = messagespace
        )

        messagespace_min, messagespace_max = Fdhope.getBoundary(
            interval_id    = interval_id, 
            space = messagespace
        )
        
        cipherspace_min, cipherspace_max = Fdhope.getBoundary(
            interval_id    = interval_id, 
            space = cipherspace
        )

        scale      = (cipherspace_min - cipherspace_max) / (messagespace_min - messagespace_max)
        delta      = random.uniform(0,sens * scale)
        ciphertext = cipherspace_min + scale * (abs(plaintext) - messagespace_min) + delta

        if (plaintext < 0):
            ciphertext = ciphertext * (-1)

        return ciphertext


    """
    Description: Counts elements that belong to each defined range
    """
    def calculate_dens(**kwargs):
        D                  = kwargs.get("dataset")
        messagespace       = kwargs.get("messagespace")
        dens               = []

        for plaintext_vector in D:
            for plaintext in plaintext_vector:
                key = Fdhope.getIntervalID(plaintext = plaintext, messagespace = messagespace)
                dens.append(key)
        conteo = Counter(dens) 
        return dict(conteo.items())
        
    """
    Description: Calculate the jump for each of the cipherspace ranges
    """
    def calculate_intervalLength(**kwargs):
        density            = kwargs.get("density",{})
        lenTriangle        = kwargs.get("lenTriangle",1)
        maxVal_cipherspace = kwargs.get("maxVal_cipherspace")
        intervalLenght     = {}

        for key, value in density.items():
            ratio               = value/lenTriangle
            il                  = maxVal_cipherspace * ratio
            intervalLenght[key] = round(il)
    
        return intervalLenght


    """
    Description: Allows you to generate keys for the defined ranges
    """
    def generate_range_keys(**kwargs):
        n_range   = kwargs.get("n_range")
        range_ids = []
        for i in range(n_range):
            id = 'RANGE_{}'.format(i)
            range_ids.append(id)
        return range_ids


    """
    Description: Generates the values of each interval depending on the defined minimum and maximum value
    """
    def generate_range_values(**kwargs):
        minValue      = kwargs.get("minValue") # Minimum value for the range
        maxValue      = kwargs.get("maxValue") # Maximum value of the ranges.
        n_range       = kwargs.get("n_range")  # Number of ranks
        range_ids     = kwargs.get("range_ids",Fdhope.generate_range_keys(n_range = n_range)) # Generate array of ids
        ranges_values = kwargs.get("ranges_values",[minValue] + sorted([random.randint(2,maxValue) for _ in range(n_range-1)]) + [maxValue]) #Generate random ranges values
        rangos        = {} # Dictionary for ranges
        for index,range_id in enumerate(range_ids):
            minVal           = ranges_values[index]
            maxVal           = maxValue+1 if (index == n_range-1) else ranges_values[index+1]
            rangos[range_id] = (minVal, maxVal)  #Diccionario Rangos, key = range_id, value = tuple
        return rangos


    """
    Description: It allows to find the maximum value of the dataset 
    """
    def findMax(D):  #Obtiene el valor maximo en D para definir los intervalos
        return np.max(np.abs(np.array(D).flatten()))


    """
    Description: Returns the ID of the range in which the element is found
    """
    def getIntervalID(**kwargs):
        plaintext    = abs(kwargs.get("plaintext",0))
        messagespace = kwargs.get("messagespace")
        for key, value in messagespace.items():
            if (plaintext >= value[0] and plaintext < value[1]):
                return key


    """
    Description: Given "range_id" get min and max of message space
    """
    def getBoundary(**kwargs):
        interval_id    = kwargs.get("interval_id")
        space = kwargs.get("space")        
        value = space.get(interval_id)
        li    = value[0]
        hi    = value[1]
        return li, hi
        

if __name__ == "__main__":
    plaintext_matrix = [
        [0.73,8.84],
        [49.93,34.44],
        [0.57,65.04],
        [62.15,32.29],
        [59.47,36.04]
    ]

    messagespace, cipherspace = Fdhope.keygen(
        dataset = plaintext_matrix, 
        n_range = 4, 
        proportion = 3
    )
    print("Message space",messagespace)
    print("Cipher space",cipherspace)

    
    ciphertext = Fdhope.encrypt(
        plaintext    = 34.44,
        sens         = 0.01,
        messagespace = messagespace,
        cipherspace  = cipherspace
        )
    print(ciphertext)
