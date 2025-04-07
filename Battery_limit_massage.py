from pymavlink import mavutil
import socket

# Connessione MAVLink al Pixhawk
master = mavutil.mavlink_connection('udp:localhost:14550')

# Setup socket per inviare il messaggio al PC
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
PC_IP = '192.168.4.2'  # Cambia con l'IP del computer collegato alla Wi-Fi del drone
PC_PORT = 5005

while True:
    msg = master.recv_match(type='BATTERY_STATUS', blocking=True)
    if msg:
        battery_remaining = msg.battery_remaining  # percentuale batteria

        if battery_remaining <= 20:
            alert_message = "WARNING: Drone battery low - {}%".format(battery_remaining)
            sock.sendto(alert_message.encode(), (PC_IP, PC_PORT))
