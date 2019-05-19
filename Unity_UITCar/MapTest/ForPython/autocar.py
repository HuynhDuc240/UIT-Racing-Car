import socket
import sys

import json

def jsonToString(speed, angle):
    jsonObject = {'speed': speed,
    'angle': angle,
    }

    jsonString = json.dumps(jsonObject)
    print(jsonString)
    return jsonString

port = 9999
ip = str(sys.argv[1])


try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip , port))
    print("Connected to ", ip, ":", port)

    ## image processing here
except Exception as ex:
    print(ex)
    sys.exit()

#while true:
try:
    ## send to server
    message = jsonToString(10, 20)
    #message = "Hello World"
    arr = bytes(message, 'ascii')
    sock.sendall(arr)
except Exception as ex:
    print(ex)
    sys.exit()