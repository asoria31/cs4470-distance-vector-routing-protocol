import socket


# Establish a connection with each machine in the topology file.
def read_topology_file_and_establish_connections(line):
    print("\nDebug: ENTER read_topology_file_and_establish_connections.\n")
    line = line.split(" ")

    # Server info of the current server being read from the topology file.
    server_id = line[0]
    server_ip = line[1]
    server_port = line[2]

    print("server_id in read and establish =", server_id)
    print("server_ip in read and establish =", server_ip)
    print("server_port in read and establish =", server_port)


# Start the server on this machine.
def start_server(server_id, top_file_server_lines):
    print("\nDebug: ENTER start_server.\n")
    # In the list of server connections, find the server_id of this machine for its address and port info.
    for server_line in top_file_server_lines:

        server_line= server_line.split(" ")

        if (server_line[0] == server_id):
            server_ip = str(server_line[1])
            server_port = int(server_line[2])


    print("Debug: server_ip =", server_ip)
    print("Debug: server_port =", server_port)


    # Create UDP socket.
    # server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # server_sock.bind(server_ip, server_port)






# REMEMBER TO CLOSE THE SOCKETS IN THE DISCONNECTION FUNCTIONS