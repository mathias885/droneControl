import tkinter as tk
from tkinter import ttk
import socket
from Message import message

HOST = 'localhost'  # Update with your actual server host
PORT = 3000  # Update with your actual server port

print(message.quit)

class MessageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Message Creator")

        # Dropdown for message type
        self.msg_type = tk.StringVar()
        self.msg_type.set("fly_up")  # Default value
        tk.Label(root, text="Select Message Type:").grid(row=0, column=0)

        # Getting Enum names correctly
        self.dropdown = ttk.Combobox(root, textvariable=self.msg_type)
        self.dropdown['values'] = [m.name for m in message]  # Ensuring all enum names, including 'quit', are displayed
        self.dropdown.grid(row=0, column=1)
        self.dropdown.bind("<<ComboboxSelected>>", self.update_inputs)

        # Input fields
        self.input1 = tk.Entry(root)
        self.input2 = tk.Entry(root)
        self.input1.grid(row=1, column=1)
        self.input2.grid(row=2, column=1)
        
        tk.Label(root, text="Input 1:").grid(row=1, column=0)
        tk.Label(root, text="Input 2:").grid(row=2, column=0)
        
        # Button to create message
        self.create_button = tk.Button(root, text="Create Message", command=self.create_message)
        self.create_button.grid(row=3, column=0, columnspan=2)

        # Button to send "quit" message
        self.quit_button = tk.Button(root, text="Send Quit Message", command=self.send_quit_message)
        self.quit_button.grid(row=3, column=2)

        # Output area
        self.output = tk.Label(root, text="")
        self.output.grid(row=4, column=0, columnspan=3)

        self.update_inputs()  # Initialize the input fields

    def update_inputs(self, event=None):
        """ Update input fields based on message type """
        msg_type = self.msg_type.get()
        
        if msg_type in ["fly_up", "translate"]:
            self.input1.grid()
            self.input2.grid_remove()
        elif msg_type == "land_at":
            self.input1.grid()
            self.input2.grid()
        elif msg_type == "land":
            self.input1.grid_remove()
            self.input2.grid_remove()
        elif msg_type == "quit":
            self.input1.grid()
            self.input2.grid_remove()

    def create_message(self):
        """ Create the message and display the result """
        msg_type = self.msg_type.get()
        try:
            if msg_type in ["fly_up", "translate"]:
                value = int(self.input1.get())
                message_instance = message[msg_type](value)
            elif msg_type == "land_at":
                x = int(self.input1.get())
                y = int(self.input2.get())
                message_instance = message[msg_type](x, y)
            elif msg_type == "land":
                message_instance = message[msg_type]()
            elif msg_type == "quit":
                message_instance = message[msg_type]()
            else:
                raise ValueError("Invalid message type")

            self.output.config(text=f"Message: {message_instance}\nValue: {message_instance.getValue()}")
            print(message_instance.getJson())
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect((HOST, PORT))
                data = message_instance.getJson().encode('utf-8')
                client.sendall(data) 
                data_rcv = client.recv(1024)
                print(data_rcv)
        
        except ValueError as e:
            self.output.config(text=f"Error: {e}")

    def send_quit_message(self):
        """ Send a quit message """
        message_instance = message.quit()
        self.output.config(text=f"Message: {message_instance}\nValue: {message_instance.getValue()}")
        print(message_instance.getJson())
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((HOST, PORT))
            data = message_instance.getJson().encode('utf-8')
            client.sendall(data) 
            data_rcv = client.recv(1024)
            print(data_rcv)

# Run the application
root = tk.Tk()
app = MessageApp(root)
root.mainloop()
