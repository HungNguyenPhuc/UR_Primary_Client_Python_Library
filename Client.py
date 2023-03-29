import socket
import Package as p
import json

HOST = socket.gethostbyname(socket.gethostname())
PORT = 30001

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
    
    clientSocket.settimeout(4)
    try:
        clientSocket.connect((HOST, PORT))
    except socket.timeout as e:
        print(f"Timeout error: {e}")
    except socket.error as e:
        print(f"Could not connect to {HOST}:{PORT} Error: {e}")

    while True:
        robot_data = clientSocket.recv(4096)
        new_message = p.Package(robot_data)
    





