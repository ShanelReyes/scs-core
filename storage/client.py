
# * This block of code MUST be executed first.  
# _______________________________________________________
# import os
# import sys
# from pathlib import Path
# path_root      = Path(__file__).parent.absolute()
# (path_root, _) = os.path.split(path_root)
# sys.path.append(str(path_root))
# print(sys.path)
# _______________________
import funcy
import math
import socket as S
from storage.doa.parameters import PutParameters,GetParameters
import uuid 
import numpy as np
import json
import hashlib
import pandas as pd
import time

class Client(object):
    def __init__(self,**kwargs):
        self.client_id = str(uuid.uuid4())
        self.hostname  = kwargs.get("hostname","localhost")
        self.port      = kwargs.get("port",3000)
        self.INT_BYTES    = 1
        self.USIZE_BYTES  = 8
        self.TOKENS       = {
            "PUT":1,
            "GET": 2,
        }
    def __recvall(self,socket, n):
        # Helper function to recv n bytes or return None if EOF is hit
        data = bytearray()
        while len(data) < n:
            packet = socket.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data
    
    def __alltofile(self,socket, n,**kwargs):
        # Helper function to recv n bytes or return None if EOF is hit
        path = kwargs.get("path")
        m = hashlib.sha256()
        received =0
        with open(path,"wb") as f:
            while received < n:
                packet = socket.recv(n - received)
                if not packet:
                    break 
                received+= len(packet)
                m.update(packet)
                f.write(packet)
        return m.hexdigest()
    
    def __check_integrity(**kwargs):
        _bytes              = kwargs.get("_bytes")
        metadata_checksum   = kwargs.get("checksum")
        checksum            = hashlib.sha256(_bytes).hexdigest()
        return checksum == metadata_checksum

    def get_to_file(self,**kwargs):
        with S.socket(S.AF_INET,S.SOCK_STREAM) as socket:
            socket.connect((self.hostname,self.port))
            sink_path = kwargs.get("sink_path","/test/sink")
            CMD_BYTES    = self.TOKENS["GET"].to_bytes(self.INT_BYTES, "big")
            # SEND CMD.
            socket.sendall(CMD_BYTES)
            # SEND GET-PARAMETERS.
            parameters   = kwargs.get("params",GetParameters(
                id = kwargs.get("id"),
                _from = kwargs.get("_from",None)
            )).to_json()
            params_bytes = bytes(parameters,encoding="utf8")
            params_size  = len(params_bytes)
            # SEND PARAMS SIZE 
            socket.sendall(params_size.to_bytes(self.USIZE_BYTES,"big"))
            # SEND PARAMS.
            socket.sendall(params_bytes)
            # READ METADATA SIZE
            response_size_bytes = self.__recvall(socket,self.USIZE_BYTES)
            response_size       = int.from_bytes(response_size_bytes,"big")
            response_bytes      = self.__recvall(socket,response_size).decode("utf8")
            response      = json.loads(response_bytes)
            # READ BYTES
            bytes_size    = response["metadata"]["size"]
            checksum = self.__alltofile(socket,bytes_size,path = "{}/{}".format(sink_path,response["metadata"]["id"]))
            return response

    def get(self,**kwargs):
        with S.socket(S.AF_INET,S.SOCK_STREAM) as socket:
            socket.connect((self.hostname,self.port))
            CMD_BYTES    = self.TOKENS["GET"].to_bytes(self.INT_BYTES, "big")
            # socket = self.socket
            # SEND CMD.
            socket.sendall(CMD_BYTES)
            # SEND GET-PARAMETERS.
            parameters   = kwargs.get("params",GetParameters(
                id = kwargs.get("id"),
                _from = kwargs.get("_from",None)
            )).to_json()
            params_bytes = bytes(parameters,encoding="utf8")
            params_size  = len(params_bytes)
            # SEND PARAMS SIZE 
            socket.sendall(params_size.to_bytes(self.USIZE_BYTES,"big"))
            # SEND PARAMS.
            socket.sendall(params_bytes)
            # READ METADATA SIZE
            response_size_bytes = self.__recvall(socket,self.USIZE_BYTES)
            response_size       = int.from_bytes(response_size_bytes,"big")
            response_bytes      = self.__recvall(socket,response_size).decode("utf8")
            response      = json.loads(response_bytes)
            bytes_size    = response["metadata"]["size"]
            _bytes        = self.__recvall(socket,bytes_size)
            preversed_integrity = Client.__check_integrity(_bytes=_bytes, checksum= response["metadata"]["checksum"])
            if not preversed_integrity:
                raise Exception("INTEGRITY ISSUE")

            return response,_bytes

    def get_matrix(self,**kwargs):
        # Get metadata and bytes
        response = self.get_to_file(**kwargs)
        # Extract tags (shape and dtype)
        metadata         = response["metadata"]
        tags             = metadata["tags"]
        # Interpret shape 
        shape            = eval(tags["shape"])
        # Extract dtype
        dtype            = tags["dtype"]
        # Get matrix using bytes, shape and dtype
        path             = "{}/{}".format(kwargs.get("sink_path"),metadata["id"])
        matrix           = np.fromfile(path,dtype=dtype).reshape(shape)
        return response,matrix
        
    def put(self,**kwargs):
        with S.socket(S.AF_INET,S.SOCK_STREAM) as socket:
            try:
                socket.connect((self.hostname,self.port))
                _bytes         = kwargs.get("_bytes")
                parameters       = kwargs.get("parameters",
                PutParameters(
                    id = "ball-{}".format(str(uuid.uuid4())[:4] ),
                    size = len(_bytes),
                    client_id = self.client_id )
                ).to_json()
                # CMD          = 1
                CMD_BYTES    = self.TOKENS["PUT"].to_bytes(self.INT_BYTES, "big")
                params_bytes = bytes(parameters,encoding="utf8")
                params_size  = len(params_bytes)
                # SEND CMD.
                socket.sendall(CMD_BYTES)
                # SEND PARAMS LEN.
                socket.sendall(params_size.to_bytes(self.USIZE_BYTES,"big"))
                # SEND PARAMS.
                socket.sendall(params_bytes)
                # SEND BYTES.
                socket.sendall(_bytes)
                # READ RESPONSE BYTES.
                response_bytes = self.__recvall(socket,self.USIZE_BYTES)
                response_size = int.from_bytes(response_bytes,"big")
                response      = self.__recvall(socket,response_size).decode("utf8")
                return json.loads(response)
            except Exception as e:
                print(e)
                raise e

    
    def __hash(self,_bytes,**kwargs):
        chunk_size     = kwargs.get("chunk_size",4096)
        len_bytes      = len(_bytes)
        chunks_counter = math.ceil(len_bytes/chunk_size)
        chunks         = funcy.chunks(chunks_counter,_bytes)
        h = hashlib.sha256()
        for chunk in chunks:
            h.update(chunk)
        return h.hexdigest()

    def put_matrix(self,**kwargs):
        try:
            matrix           = kwargs.get("matrix",np.array([]))
            _bytes           = matrix.tobytes()
            matrix_id_suffix = str(uuid.uuid4())[:4]
            checksum         = hashlib.sha256(_bytes).hexdigest()
            put_parmeters    = PutParameters(
                id        = kwargs.get("id","matrix-{}".format(matrix_id_suffix )), 
                size      = len(_bytes),
                client_id = self.client_id,
                checksum  = checksum,
                tags      = {
                    "dtype":str(matrix.dtype) ,
                    "shape": str(matrix.shape)
                }
            )
            return self.put(
                _bytes = _bytes,
                parameters = put_parmeters,
            )
        except Exception as e :
            print(e)
            raise e

if __name__ == "__main__":
    c1 = Client(
        hostname = "localhost",
        port = 6001
    )