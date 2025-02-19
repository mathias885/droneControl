import tkinter as tk
from tkinter import ttk
import socket
from Message import Command, Message

global HOST
HOST = '127.0.0.1'

global PORT
PORT = 3000  

# ------------ MODIFICA QUI PER CAMBIARE TIMEOUT BROADCAST ----------------
global TIMEOUT
TIMEOUT = 5

global BROADCAST
BROADCAST = None

global CLIENT
CLIENT = None

# -------------- Parte fatta dal nostro amico chat GPT --------------
class MessageApp:
    def __init__(self, root):
        self.root = root 
        self.root.title("Message Creator")

        # Dropdown for message type
        self.msg_type = tk.StringVar()
        self.msg_type.set("FLY_UP")
        tk.Label(root, text="Select Message Type:").grid(row=0, column=0)

        # Get Enum names for dropdown
        self.dropdown = ttk.Combobox(root, textvariable=self.msg_type)
        self.dropdown['values'] = [cmd.name for cmd in Command] 
        self.dropdown.grid(row=0, column=1)
        self.dropdown.bind("<<ComboboxSelected>>", self.update_inputs)

        # Input fields
        self.input1 = tk.Entry(root)
        self.input2 = tk.Entry(root)
        self.input3 = tk.Entry(root)
        self.input4 = tk.Entry(root)
        self.input1.grid(row=1, column=1)
        self.input2.grid(row=2, column=1)
        self.input3.grid(row=3, column=1)
        self.input4.grid(row=4, column=1)
        
        tk.Label(root, text="Input 1:").grid(row=1, column=0)
        tk.Label(root, text="Input 2:").grid(row=2, column=0)
        tk.Label(root, text="Input 3:").grid(row=3, column=0)
        tk.Label(root, text="Input 4:").grid(row=4, column=0)
        
        # Button to create message
        self.create_button = tk.Button(root, text="Create Message", command=self.create_message)
        self.create_button.grid(row=5, column=0, columnspan=2)

        # Button to send "quit" message
        self.quit_button = tk.Button(root, text="Send Quit Message", command=self.send_quit_message)
        self.quit_button.grid(row=5, column=2)

        # Button for sending broadcast
        self.reconnect_button = tk.Button(root, text="Reconnect", command=self.reconnect)
        self.reconnect_button.grid(row=5, column=3)

        # Output area
        self.output = tk.Label(root, text="")
        self.output.grid(row=6, column=0, columnspan=4)

        self.update_inputs()  # Initialize input fields

    def reconnect(self, event=None):
        reconnect()

    def update_inputs(self, event=None):
        """ Update input fields based on selected message type """
        msg_type = self.msg_type.get()

        if msg_type == "FLY_UP":
            self.input1.grid()
            self.input2.grid_remove()
            self.input3.grid_remove()
            self.input4.grid_remove()
        elif msg_type == "TRANSLATE":
            self.input1.grid()
            self.input2.grid()
            self.input3.grid()
            self.input4.grid()
        elif msg_type == "LAND_AT":
            self.input1.grid()
            self.input2.grid()
            self.input3.grid()
            self.input4.grid()
        elif msg_type in ["LAND", "QUIT"]:
            self.input1.grid_remove()
            self.input2.grid_remove()
            self.input3.grid_remove()
            self.input4.grid_remove()
        elif msg_type == "CUSTOM":
            self.input1.grid()
            self.input2.grid()
            self.input3.grid()
            self.input4.grid()

    def create_message(self):
        """ Create the message and send it """
        msg_type = self.msg_type.get()
        try:
            if msg_type == "FLY_UP":
                value = int(self.input1.get())
                message_instance = Message.fly_up(value)
            elif msg_type == "TRANSLATE":
                value1 = int(self.input1.get())
                value2 = int(self.input2.get())
                value3 = int(self.input3.get())
                value4 = int(self.input4.get())
                message_instance = Message.translate(value1, value2, value3, value4)
            elif msg_type == "LAND_AT":
                value1 = int(self.input1.get())
                value2 = int(self.input2.get())
                value3 = int(self.input3.get())
                value4 = int(self.input4.get())
                message_instance = Message.land_at(value1, value2, value3, value4)
            elif msg_type == "LAND":
                message_instance = Message.land()
            elif msg_type == "QUIT":
                message_instance = Message.quit()
            elif msg_type == "CUSTOM":
                value1 = int(self.input1.get())
                value2 = int(self.input2.get())
                value3 = int(self.input3.get())
                value4 = int(self.input4.get())
                message_instance = Message.custom(value1, value2, value3, value4)
            else:
                raise ValueError("Invalid message type")

            # Display result
            self.output.config(text=f"Message: {message_instance}\nJSON: {message_instance.to_json()}")

            # Send message over the open socket
            data = message_instance.to_json().encode('utf-8')
            CLIENT.sendall(data)

            # Receive response from the server
            try:
                data_rcv = CLIENT.recv(1024)
                if data_rcv:
                    print(data_rcv.decode('utf-8'))
                else:
                    print("No response from server.")
            except socket.error as e:
                print(f"Error receiving data: {e}")

        except ValueError as e:
            self.output.config(text=f"Error: {e}")

    def send_quit_message(self):
        """ Send a quit message """
        message_instance = Message.quit()
        self.output.config(text=f"Message: {message_instance}\nJSON: {message_instance.to_json()}")

        # Send quit message over the open socket
        data = message_instance.to_json().encode('utf-8')
        CLIENT.sendall(data)

        # Receive server response
        try:
            data_rcv = CLIENT.recv(1024)
            if data_rcv:
                shutdown()
            else:
                print("No response from server.")
        except socket.error as e:
            print(f"Error receiving data: {e}")

# -------------- FINE Parte fatta dal nostro amico chat GPT --------------

#inizializza il broadcast udp per capire quale è il server
def start_broadcast():
    global HOST
    global BROADCAST
    BROADCAST = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    BROADCAST.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    BROADCAST.sendto("DISCOVERY".encode(), ('<broadcast>', 5000))
    BROADCAST.settimeout(TIMEOUT) 
    print(f"broadcasting for server.. timeout in {TIMEOUT} seconds")

    try:
        data, addr = BROADCAST.recvfrom(1024)
        if data.decode().startswith("SERVER_IP:"):
            server_ip = data.decode().split(':')[1]
            print(f"Server IP found: {server_ip}")
            HOST = server_ip
            start_client()
        else:
            print("No valid server found.")
            return
    except socket.timeout:
        print("No response from server.")
        return

# permette di riconnettersi se andato in inactivity timeout
def reconnect():
    global CLIENT  # Serve per modificare la variabile globale
    if CLIENT:
        print("Connessione già attiva. Chiudo e riapro...")
        shutdown()  # Chiude prima la connessione esistente nel caso lo si clicki per sbaglio
    
    # Richiama start_client per riaprire la connessione
    start_client()
    print("Riconnessione completata.")


def start_client():
    global CLIENT
    # Verifica se CLIENT è già attivo e chiudilo se necessario
    if CLIENT:
        print("Connessione già aperta, la chiudo prima di riconnettermi.")
        try:
            CLIENT.close()
        except socket.error as e:
            print(f"Errore durante la chiusura: {e}")
        finally:
            CLIENT = None  # Imposta a None per forzare la ricreazione

    # Ricrea il socket TCP
    try:
        CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        CLIENT.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Per riutilizzare la porta subito
        CLIENT.connect((HOST, PORT))
        print(f"Connesso a {HOST}:{PORT}")
    except socket.error as e:
        print(f"Errore durante la connessione: {e}")
    except Exception as e:
        print(f"Errore imprevisto: {e}")

def shutdown():
    global CLIENT
    if CLIENT:
        try:
            CLIENT.close()
            print("Connessione chiusa.")
        except socket.error as e:
            print(f"Errore durante la chiusura della connessione: {e}")
        finally:
            CLIENT = None
    else:
        print("Nessuna connessione attiva da chiudere.")


#fa partire il broadcast e setta client
start_broadcast()


#fa partire l'app grafica
root = tk.Tk()
app = MessageApp(root)
root.mainloop()


#chiusura connessioni
BROADCAST.close()
CLIENT.close()