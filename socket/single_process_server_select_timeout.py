# coding: utf-8
import select
import socket
import queue


def main():
    # Create a TCP/IP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(False)

    # Bind the socket to the port
    server_address = ('localhost', 10000)
    print('starting up on {} port {}'.format(*server_address))
    server.bind(server_address)

    # Listen for incoming connections
    server.listen(5)
    # Sockets from which we expect to read
    inputs = [server]

    # Sockets to which we expect to write
    outputs = []

    # Outgoing message queues (socket:Queue)
    message_queues = {}

    # select timeout
    timeout = 1

    while inputs:
        # Wait for at least one of the sockets to be ready for processing
        print('waiting for the next event')
        readable, writable, exceptional = select.select(inputs,
                                                        outputs,
                                                        inputs,
                                                        timeout)

        if not (readable or writable or exceptional):
            print('timed out, do some other work here')
            continue

        # Handle inputs
        for s in readable:
            if s is server:
                # A "readable" socket is ready to accept a connection
                connection, client_address = s.accept()
                print('connection from {}'.format(client_address))
                connection.setblocking(0)
                inputs.append(connection)

                # Give the connection a queue for data
                # we want to send
                message_queues[connection] = queue.Queue()
            else:
                data = s.recv(1024)
                if data:
                    # A readable client socket has data
                    print('received {} from {}'.format(data, s.getpeername()))
                    message_queues[s].put(data)
                    # Add output channel for response
                    if s not in outputs:
                        outputs.append(s)
                else:
                    # Interpret empty result as closed connection
                    print('closing {}'.format(client_address))
                    # Stop listening for input on the connection
                    if s in outputs:
                        outputs.remove(s)
                    inputs.remove(s)
                    s.close()

                    # Remove message queue
                    del message_queues[s]

        # Handle outputs
        for s in writable:
            try:
                next_msg = message_queues[s].get_nowait()
            except queue.Empty:
                # No messages waiting so stop checking
                # for writability.
                print('{} queue empty'.format(s.getpeername()))
                outputs.remove(s)
            else:
                print('sending {} to {}'.format(next_msg, s.getpeername()))
                s.send(next_msg)

        # Handle "exceptional conditions"
        for s in exceptional:
            print('exception condition on {}'.format(s.getpeername()))
            # Stop listening for input on the connection
            inputs.remove(s)
            if s in outputs:
                outputs.remove(s)
            s.close()

            # Remove message queue
            del message_queues[s]


if __name__ == '__main__':
    main()
