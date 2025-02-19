import json
import socket
import asyncio
import subprocess
import os
from mavsdk import System
from Message import Command, Message

HOST = "127.0.0.1"
PORT = 3000
NO_CONNECTION_TIMEOUT = 30 # timeout di mancanza connesione
INACTIVITY_TIMEOUT = 60  # timeout di inattività del ricevitore
drone = System()

async def start():
    # Connessione al drone tramite MAVSDK
    await drone.connect(system_address="udpin://127.0.0.1:14550") # qui devi mettere l'indirizzo della scheda di volo
    print("In attesa del drone...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone connesso!")
            break

    return None

async def handle_msg(msg: Message):
    print(f"Handling message: {msg}")
    match msg.command:
        case Command.FLY_UP:
            print(f"Fly Up: {msg.values}")
            await drone.action.set_takeoff_altitude(msg.values[0]) #imposta l'altitudine relativa a quella corrente a cui cerca di arrivare iniziato il takeoff
            await drone.action.takeoff()

        case Command.TRANSLATE:
            print(f"Translate: {msg.values}") #da ripensare, opzioni: 1) goto_location ()coordinate globali | 2)impostare una certa velocità nelle 3 dimensioni, mantenendola per x secondi
            try:
                dx = msg.values[0]  # Offset in avanti/indietro (NED: North)
                dy = msg.values[1]  # Offset laterale (NED: East)
                dz = msg.values[2]  # Offset in altezza (NED: Down)
                yaw = msg.values[3]  # Yaw (rotazione)

                # Avvia il controllo offboard
                await drone.offboard.set_position_ned(PositionNedYaw(dx, dy, dz, yaw))
                await drone.offboard.start()
                await asyncio.sleep(5)  # dopo 5 secondi si ferma
                await drone.offboard.stop()

            except OffboardError as e:
                print(f"Errore nella traslazione: {e}")

        case Command.LAND_AT:
            print(f"Land At: {msg.values}")
            try:
                dx = msg.values[0]  # Offset in avanti/indietro (NED: North)
                dy = msg.values[1]  # Offset laterale (NED: East)
                dz = msg.values[2]  # Offset in altezza (NED: Down)
                yaw = msg.values[3]  # Yaw (rotazione)

                # Avvia il controllo offboard
                await drone.offboard.set_position_ned(PositionNedYaw(dx, dy, dz, yaw))
                await drone.offboard.start()
                await asyncio.sleep(5)  # dopo 5 secondi si ferma
                await drone.offboard.stop()

            except OffboardError as e:
                print(f"Errore nella traslazione: {e}")

            #una volta traslato, atterra
            await drone.action.land()

        case Command.LAND:
            print("Land")
            await drone.action.land()

        case Command.QUIT:
            # qui lasciami il return false che serve per poter uscire dal ciclo di ascolto
            print("Quit command received. Shutting down.")
            return False

        case _:
            print(f"Unknown command: {msg.command}")
    
    return True

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

async def main():
    # avvio del drone
    await start()

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

    # connessione tcp per lo scambio messaggi
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
                                print(f"msg: {msg}")

                                should_continue = await handle_msg(msg)
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

# Esegui il server
asyncio.run(main())