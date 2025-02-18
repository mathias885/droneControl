import json
import socket
from Message import Command, Message

HOST = "127.0.0.1"
PORT = 3000
NO_CONNECTION_TIMEOUT = 30 # timeout di mancanza connesione
INACTIVITY_TIMEOUT = 15  # timeout di inattività del ricevitore


# ------------ INSERISCI QUI TUTTI I TUOI INTRIGHI MATHIAS ----------------

def handle_msg(msg: Message):
    print(f"Handling message: {msg}")
    match msg.command:
        case Command.FLY_UP:
            print(f"Fly Up: {msg.values}")
        case Command.TRANSLATE:
            print(f"Translate: {msg.values}")
        case Command.LAND_AT:
            print(f"Land At: {msg.values}")
        case Command.LAND:
            print("Land")
        case Command.QUIT:
            # qui lasciami il return false che serve per poter uscire dal ciclo di ascolto
            print("Quit command received. Shutting down.")
            return False
        case _:
            print(f"Unknown command: {msg.command}")
    
    return True


# this function basically returns the corresponding message given by the JSON

def parse_message(data):
    try:
        parsed = json.loads(data)
        
        command = parsed.get("command")
        values = parsed.get("values", [])
        
        command_enum = Command(command)
        
        match command_enum:
            case Command.FLY_UP:
                return Message.fly_up(*values)
            case Command.TRANSLATE:
                return Message.translate(*values)
            case Command.LAND_AT:
                return Message.land_at(*values)
            case Command.LAND:
                return Message.land()
            case Command.QUIT:
                return Message.quit()
            case _:
                raise ValueError(f"Unknown command: {command}")
    
    except ValueError as e:
        print(f"Value error: {e}")
    except Exception as e:
        print(f"Unexpected error during message parsing: {e}")
    
    return None



# broadcast udp lato server
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as broadcast_server:
    broadcast_server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    broadcast_server.bind(('', 5000))

    print(f"Waiting for client broadcast...")

    while True:
        message, addr = broadcast_server.recvfrom(1024)
        if message.decode() == "DISCOVERY":
            print(f"Discovery request received from: {addr}")
            HOST = addr[0]
            server_ip = socket.gethostbyname(socket.gethostname())
            broadcast_server.sendto(f"SERVER_IP:{server_ip}".encode(), addr)
            break

print(f"Server started and listening on {HOST}:{PORT}")

#conenssione tcp per lo scalbio messaggi
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen()
    print("Server started. Waiting for connections...")
    server.settimeout(NO_CONNECTION_TIMEOUT)

    while True:
        try:
            conn, addr = server.accept()
            print(f"Connection from {addr}")
            # timeout da modificare a inizio file 
            conn.settimeout(INACTIVITY_TIMEOUT)

            with conn:
                while True:
                    try:
                        data_json = conn.recv(1024) # potrebbe andare in time out

                        if not data_json:
                            print("No data received. Closing connection.")
                            break

                        data_str = data_json.decode('utf-8')
                        print(f"Received data: {data_str}")

                        msg = parse_message(data_str)

                        if msg:
                            # chiamata all'handler
                            should_continue = handle_msg(msg)
                            if not should_continue:
                                print("Quitting connection still listening")
                                conn.send(f"QUIT".encode())
                                break
                            else:
                                # Ack al client se servisse (utile solo a noi per vedere che i messaggi ritornano)
                                conn.send(f"ACK".encode())
                        else:
                            print("Failed to parse message. Ignoring.")
                    except socket.timeout:
                        print("Inactivity timeout reached. Closing connection.")
                        conn.close()
                        break
        except socket.timeout:
            print("No new connection requests. shutting down")
            break