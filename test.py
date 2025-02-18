import asyncio
import subprocess
import os
from mavsdk import System

async def main():
    
    # Controlla se mavsdk_server è già in esecuzione, altrimenti lo avvia
    if not is_mavsdk_running():
        print("Avvio di mavsdk_server...")
        server_process = subprocess.Popen(
            ["./mavsdk_server_win32.exe", "-p", "50051"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        # Controllo del server avviato
        #out, err = server_process.communicate(timeout=10)  # Tempo massimo di attesa
        #print(f"Output: {out.decode()}")
        #print(f"Error: {err.decode()}")

        if not is_mavsdk_running():
            print("Errore: il server mavsdk non si è avviato correttamente.")
            return

        await asyncio.sleep(2)  # Attendere un momento affinché il server si avvii

    # Connessione al drone tramite MAVSDK
    drone = System(mavsdk_server_address="localhost", port=14540)
    await drone.connect(system_address="udpin://127.0.0.1:14540")    
    print("arrivato fino a qui")

    print("In attesa del drone...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone connesso!")
            break

    while True:
        cmd = input("Inserisci comando (arm/takeoff/land/exit): ").strip().lower()

        if cmd == "arm":
            await drone.action.arm()
            print("Drone armato")
        elif cmd == "takeoff":
            await drone.action.takeoff()
            print("Decollo in corso...")
            await asyncio.sleep(5)  # Aspetta per dare tempo al drone di salire
        elif cmd == "land":
            await drone.action.land()
            print("Atterraggio in corso...")
        elif cmd == "exit":
            print("Uscita...")
            break
        else:
            print("Comando non riconosciuto")


def is_mavsdk_running():
    """Controlla se mavsdk_server è già in esecuzione."""
    tasklist_output = os.popen('tasklist').read().lower()
    return "mavsdk_server_win32.exe" in tasklist_output


if __name__ == "__main__":
    asyncio.run(main())
