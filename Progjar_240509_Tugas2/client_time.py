import sys
import socket
import logging



def kirim_data():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logging.warning("membuka socket")

    server_address = ('172.16.16.101', 45000)
    logging.warning(f"opening socket {server_address}")
    sock.connect(server_address)

    try:
        # Send data
        message = 'TIME1310'
        logging.warning(f"{message}")
        sock.sendall(message.encode('utf-8'))

        # Look for the response
        amount_received = 0
        amount_expected = len(message)
        while amount_received < amount_expected:
            data = sock.recv(32)
            amount_received += len(data)
            logging.warning(f"[DITERIMA DARI SERVER] {data}")
        
        # Quit request
        message_quit = 'QUIT1310'
        logging.warning(f"{message_quit}")
        sock.sendall(message_quit.encode('utf-8'))
    finally:
        logging.warning("closing")
        sock.close()
    return


if __name__=='__main__':
    for i in range(1,10):
        kirim_data()