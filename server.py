import socket
import threading
from datetime import datetime
import os
import sys

def sender_file(sender_connection, data, clients):
    try:
        prep, file_name, relative_folder, recep = data.split(':', 4)[1:]
        file_size = int(prep)

        if recep.lower() == 'multicast':
            recipient_conns = [
                conn for conn in clients if conn != sender_connection]
        else:
            recipient_conns = [conn for conn, username in clients.items(
            ) if username == recep]

        if not recipient_conns:
            print(
                f"{recep} is not connected.")
            return

        prep = f"{file_size}:{file_name}:{relative_folder}"
        for recipient_conn in recipient_conns:
            recipient_conn.sendall(
                bytes(f'file:{prep}:{recep}', encoding='utf-8'))

        received_bytes = 0
        while received_bytes < file_size:
            file_data = sender_connection.recv(4096)
            if not file_data:
                break

            for recipient_conn in recipient_conns:
                recipient_conn.sendall(file_data)

            received_bytes += len(file_data)
            loading_percentage = min(
                100, int(received_bytes / file_size * 100))
            sys.stdout.write(
                f"\rSeending to {recep}: {loading_percentage}%")
            sys.stdout.flush()
        print(f"\nFile {file_name} terkirimkan ke {recep}")
    except Exception as e:
        print(f" Error saat meneruskan file: {str(e)}")
    finally:
        return


def unicast(sender, recipient, message, clients):
    for conn, username in clients.items():
        if username == recipient:
            data = f'(unicast): {clients[sender]} : {message}'
            conn.sendall(bytes(data, encoding='utf-8'))
            return


def broadcast(message, user, clients):
    for conn in clients:
        if conn != user:
            data = f' {clients[user]}: {message}'
            conn.sendall(bytes(data, encoding='utf-8'))


def handle_client(conn, clients, lastmes):
    try:
        client_name = conn.recv(64).decode('utf-8')
        clients[conn] = client_name
        lastmes[conn] = False
        addr = conn.getpeername()
        print(f'Nama : {client_name} Connected in [{addr[1]}]  ')

        while True:
            data = conn.recv(1024).decode('utf-8')
            if data != '':
                if data.startswith(b'unicast'):
                    name, recipient, message = data.split(':', 2)
                    unicast(
                        conn, recipient, message, clients)
                    print(f' {client_name}:{message}')
                elif data.startswith(b'file:'):
                    sender_file(conn, data, clients)
                else:
                    broadcast(data, user=conn, clients=clients)
            else:
                return
    except:
        if conn in clients:
            print(f'Nama : {client_name} Disconnected in [{addr[1]}] .')
            del clients[conn]
            lastmes.pop(conn)
            conn.close()

def main():
    clients = {}
    lastmes = {}
    
    socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('192.168.1.6', 5000)    
    socket_server.bind(server_address)
    socket_server.listen(10)
    print('Server [AKTIF] {} port {}'.format(*server_address))
    print("Terkoneksi :")

    while True:
        conn, name = socket_server.accept()
        threading.Thread(target=handle_client, args=(conn, clients, lastmes)).start()


main()
