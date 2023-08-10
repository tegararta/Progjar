import socket
import threading
import os


def download(sock, fileinfo):
    try:
        file_size, file_name = fileinfo.split(
            ':', 3)
        file_size = int(file_size)

        if not os.path.exists("recived"):
            os.makedirs("recived")

        file_path = os.path.join("recived", file_name)
        with open(file_path, 'wb') as file:
            remaining_bytes = file_size
            while remaining_bytes > 0:
                data = sock.recv(1024)
                file.write(data)
                remaining_bytes -= len(data)

        print(f"File '{file_name}' berhasil diterima folder recived.")
    except Exception as e:
        print(f"Terjadi kesalahan saat menerima file: {e}")


def upload(sock):
    try:
        metod = input("1. unicast\n2. multicast\npilih:")
        if metod == "1":
            recipient = input("penerima: ")
            file_path = input("path file: ")
            if not os.path.exists(file_path):
                print("File tidak ditemukan.")
                return

            with open(file_path, 'rb') as file:
                file_data = file.read()
                file_size = len(file_data)

            # Check if the recipient is 'broadcast' or 'multicast'
        elif metod == '2':
            file_path = input("path file: ")
            with open(file_path, 'rb') as file:
                file_data = file.read()
                file_size = len(file_data)
            fileinfo = f"{file_size}:{os.path.basename(file_path)}:.:multicast"
            sock.sendall(bytes(f"file:{fileinfo}", encoding='utf-8'))
            sock.sendall(file_data)
            print("File dikirim secara multicast.")
            return

        # Send the file to the specified recipient
        fileinfo = f"{file_size}:{os.path.basename(file_path)}:./:{recipient}"
        sock.sendall(bytes(f"file:{fileinfo}", encoding='utf-8'))
        sock.sendall(file_data)
        print(f"File berhasil dikirim ke {recipient}.")
    except Exception as e:
        print(f"Terjadi kesalahan saat mengirim file: {e}")


def receive_message(sock):
    while True:
        try:
            message = sock.recv(1024).decode('utf-8')
            if message.startswith("file:"):
                download(sock, message[5:])
            else:
                print(message)
        except Exception as e:
            print(f"Terjadi kesalahan pada koneksi dengan server: {e}")
            sock.close()
            break


def chat(sock):
    while True:
        try:
            message = input()
            if message == "2":
                upload(sock)
            elif message == '1':
                metod = input("1. Unicast\n2. Multicast\npilih:")
                if metod == "1":
                    penerima = input("Nama Klien : ")
                    pesan = input("Pesan:")
                    message = f"unicast:{penerima}:{pesan}"
                    sock.send(bytes(message, encoding='utf-8'))
                else:
                    pesan = input("Pesan :")
                    sock.send(bytes(pesan, encoding='utf-8'))
            else:
                print("Pilihan tidak tersedia.")
        except Exception as e:
            print(f"Terjadi kesalahan saat mengirim pesan: {e}")
            sock.close()
            break


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Ganti dengan alamat IP mesin server
    server_address = ('192.168.1.6', 5000)
    sock.connect(server_address)
    username = input("Masukkan nama Anda: ")
    sock.send(bytes(username, encoding='utf-8'))
    print("1. Kirim pesan\n2. Kirim file\npilih:")

    receive_thread = threading.Thread(
        target=receive_message, args=(sock,))
    send_thread = threading.Thread(target=chat, args=(sock,))
    receive_thread.start()
    send_thread.start()


main()
