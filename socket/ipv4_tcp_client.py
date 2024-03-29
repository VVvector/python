# coding=utf-8
import socket

def main():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = ('8.8.8.8', 60)
    print('connecting to {} port {}'.format(*server_address))

    sock.bind(('192.168.60.1', 70))

    sock.connect(server_address)

    try:
        # Send data
        message = b'This is the message.  It will be repeated.'
        print('sending: {}'.format(message))
        sock.sendall(message)

        # Look for the response
        amount_received = 0
        amount_expected = len(message)

        while amount_received < amount_expected:
            data = sock.recv(16)
            amount_received += len(data)
            print('received: {}'.format(data.decode()))

    finally:
        print('closing socket')
        sock.close()

if __name__ == '__main__':
    main()
