import json
import socket
from Message import message
# creating the socket

HOST = "127.0.0.1"
PORT = 3000

def handle_msg(msg: message):
   print(msg)


with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))

    while True:
        print("waiting for connection")
        server.listen()
        while True:
            # Accept client connection
            conn, addr = server.accept()
            with conn:
                print(f"Connection from {addr}")

                # Receive data from client
                data_json = conn.recv(1024)  # Receive data (up to 1024 bytes)

                if not data_json:
                    print("No data received. Closing connection.")
                    break  # No more data, break out of loop
                
                # Debug: Print raw received data
                print(f"Raw received data: {data_json}")

                try:
                    # Decode and load JSON
                    data_str = data_json.decode('utf-8')  # Convert bytes to string
                    print(f"Decoded data: {data_str}")  # Debugging line

                    # Attempt to load JSON from the string
                    data = json.loads(data_str)
                    print(f"Loaded data: {data}")

                    # Process the data (example processing)
                    match data['type']:
                        case "fly_up":
                            print(f"Received 'fly_up' with value: {data['value']}")
                        case "translate":
                            print(f"Received 'translate' with value: {data['value']}")
                        case "quit":
                            print("Received 'quit' command. Exiting.")
                            break
                        case _:
                            print(f"Unknown message type: {data['type']}")

                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e} - Received data: {data_json}")

                except Exception as e:
                    print(f"Unexpected error: {e}")


                


