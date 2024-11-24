import socket
import threading
import pickle
import time
import sys

list_of_ids_from_clients = []                   # All machine's will end up with the same lists of ids, ips, and ports considering the topology file format.
list_of_ips_from_clients = []
list_of_ports_from_clients = []
list_of_costs_from_clients = []                 # Format: [ [client_id, cost], ... ] for the number of machines in the network.
                                                # Ex: [ [2, 7] , [3, 4] , [4, 5] ] for 4 machines. (Self machine (1) is excluded.)
list_of_missed_interval_counts = [0, 0, 0, 0]

packets_received = 0
neighbors = []

# Routing table
#    1 2 3 4
# 1 [ , , , ]
# 2 [ , , , ]
# 3 [ , , , ]
# 4 [ , , , ]
routing_table = [[-1, -1, -1, -1], [-1, -1, -1, -1], [-1, -1, -1, -1], [-1, -1, -1, -1]] # -1 represents infinity.

# Get id, ip, and port of each machine line by line in the topology file.
def read_topology_file_server_lines(line):
    print("\nDebug: ENTER read_topology_file_server_lines.\n")
    line = line.split(" ")

    # Server info of the current server being read from the topology file.
    server_id = int(line[0])
    server_ip = line[1]
    server_port = int(line[2])

    print("server_id in read and establish =", server_id)
    print("server_ip in read and establish =", server_ip)
    print("server_port in read and establish =", server_port)

    # Add to lists.
    list_of_ids_from_clients.append(server_id)
    list_of_ips_from_clients.append(server_ip)
    list_of_ports_from_clients.append(server_port)

# Note: Using append because both read topology functions are called on start up. See dv.py file.

# Get the cost between this machine and each neighbor line by line in the topology file.
def read_topology_file_costs(line):
    print("\nDebug: ENTER read_topology_file_costs.\n")
    line = line.split(" ") # server_id client_id cost

    server_id = int(line[0])
    client_id = int(line[1])
    cost = int(line[2])

    # Cost between this machine and the current other machine. Add to list.
    list_of_costs_from_clients.append([client_id, cost])

    # A client is a neighbor if it is originally read from the topology file.
    neighbors.append([client_id])


def create_initial_routing_table(server_id):
    print("\nDebug: ENTER create_initial_routing_table.\n")

    for j in range(len(list_of_costs_from_clients)):

        # server_id - 1 will be the row of the routing table we are initializing.
        # list_of_costs_from_clients[j][0] - 1 is the column of the routing table we are initializing. 
        # ^ This value is taken from the first index in the pair [client_id, cost].
        # The value being assigned is taken from the second index of that pair.
        routing_table[server_id - 1][list_of_costs_from_clients[j][0] - 1] = list_of_costs_from_clients[j][1]

    # Set cost to self to 0.
    routing_table[server_id - 1][server_id - 1] = 0

# Get server's information then start a thread.
def start_server(server_id, top_file_server_lines):
    print("\nDebug: ENTER start_server.\n")

    # In the list of server connections, find the server_id of this machine for its address and port info. 
    # (Server finds itself and sets up socket with the information.)
    for server_line in top_file_server_lines:

        server_line = server_line.split(" ")

        if (int(server_line[0]) == server_id):
            server_ip = str(server_line[1])
            server_port = int(server_line[2])


    print("Debug: server_ip =", server_ip)
    print("Debug: server_port =", server_port)

    # Start a thread that the server can listen on
    server_thread = threading.Thread(target=_start_server, args=(server_ip, server_port), daemon=True)
    server_thread.start()

# Start the server on this machine.
def _start_server(server_ip, server_port):
    print("\nDebug: ENTER _start_server.\n")
    
    # Create UDP socket.
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_sock.bind((server_ip, server_port))

    # server_sock.listen(5)

    while True:

        print("Debug: Server waiting for data...")

        # Receive data whenever a client socket sends it.
        bytes_of_data, client_address = server_sock.recvfrom(1024)
        # Using pickle library to serialize (dumps) and deserialize (loads) the data so that we can use a list format for easy use.
        data_received = pickle.loads(bytes_of_data)
        from_server_id = data_received[0]
        recv_routing_table = data_received[1]
        # Start a thread to process data so this function can continue listening.
        thread_to_process_data = threading.Thread(target=process_data, args=(from_server_id, recv_routing_table, client_address), daemon=True)
        thread_to_process_data.start()

    server_socket.close()

# Process the data taken from another machine. Update this machine's routing table. Update number of packets received.
def process_data(from_server_id, recv_routing_table, client_address):
    print("\nDebug: ENTER process_data.\n")
    print("RECEIVED DATA FROM SERVER", from_server_id)

    # Increment number of packets received.
    global packets_received
    packets_received += 1

    

# Display the number of packets since the last time this function was called. Reset to 0.
def packets_since_last_call():

    global packets_received
    print("This machine has received", packets_received, "packet(s) since the last check in.")
    packets_received = 0

# A thread is created on this function in dv.py file. It will continuously send out this machine's routing table data at the update interval.
def send_updates_on_interval(rout_update_interval, server_id, isNow = False):
    print("\nDebug: ENTER send_updates_on_interval.\n")

    while True:
        time.sleep(rout_update_interval)
        print("Debug: Interval time elapsed.")

        # For every machine we can communicate with, ...
        for i in range(len(list_of_ids_from_clients)):

            # serialize the server id and routing table data, ...
            data_to_send = pickle.dumps([server_id, routing_table])

            # create a UDP socket, ...
            sending_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # and send the data to them. Don't need to send it to self.
            if i != server_id - 1:
                sending_socket.sendto(data_to_send, (list_of_ips_from_clients[i], list_of_ports_from_clients[i]))

            # Close sending socket.
            sending_socket.close()
        
        # If data was sent with send_data_now function, don't stay in the loop.
        if isNow:
            break

# Send data immediately.
def send_data_now(server_id):
    send_updates_on_interval(0, server_id, True)

# Remove connection and stop sending data to the given client.
def disable_connection(client_id):

    # If the machine to disable is not a neighbor.
    if (client_id not in neighbors):
        print("You can only disable connections between a NEIGHBORING machine.")
        return
    
    # Find the index of the client and remove it from this machine's lists of connections and costs.
    try:
        index_of_client = list_of_ids_from_clients.index(client_id)
        del list_of_ids_from_clients[index_of_client]
        del list_of_ips_from_clients[index_of_client]
        del list_of_ports_from_clients[index_of_client]

        for cost_pair in list_of_costs_from_clients:
            if client_id == cost_pair[0]:
                del list_of_costs_from_clients[cost_pair]

    # If the machine to disable's server id is invalid. (As long as this machine is not sending data to it, it is invalid.)
    except ValueError:
        print("The server id", client_id, "is not available or already disabled.")

# Simulate server crash by removing all connections and costs.
def server_crash():
    list_of_ids_from_clients.clear()
    list_of_ips_from_clients.clear()
    list_of_ports_from_clients.clear()
    list_of_costs_from_clients.clear()

# Display this machine's current routing table.
def print_routing_table():

    x = "-- Cost from server (left) to destination server (top) --\n"
    x += "     1  2  3  4\n"

    for i in range(len(routing_table)):
        x += str(i + 1) + " ["
        for j in range(len(routing_table[i])):
            if routing_table[i][j] != -1:
                x += "  " + str(routing_table[i][j])
            else:
                x += " " + str(routing_table[i][j])
        x += "]\n"

    print(x)
