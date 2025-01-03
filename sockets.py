import socket
import threading
import pickle
import time
import sys

list_of_ids_from_clients = []       # All machine's will end up with the same lists of ids, ips, and ports considering the topology file format.
list_of_ips_from_clients = []
list_of_ports_from_clients = []
list_of_costs_from_clients = []     # Format: [ [client_id, cost], ... ] for the number of machines in the network.
                                        # Ex: [ [2, 7] , [3, 4] , [4, 5] ] for 4 machines. (Self machine (1) is excluded.)                                      
list_of_bool_disabled = []          # All machine's will end up with a list of the same length that corresponds with the other lists.

this_server_id = 0
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
    # print("\nDebug: ENTER read_topology_file_server_lines.\n")
    line = line.split(" ")

    # Server info of the current server being read from the topology file.
    server_id = int(line[0])
    server_ip = line[1]
    server_port = int(line[2])

    # Add to lists.
    list_of_ids_from_clients.append(server_id)
    list_of_ips_from_clients.append(server_ip)
    list_of_ports_from_clients.append(server_port)
    list_of_bool_disabled.append(False)

# Note: Using append because both read topology functions are called on start up. See dv.py file.

# Get the cost between this machine and each neighbor line by line in the topology file.
def read_topology_file_costs(line):
    # print("\nDebug: ENTER read_topology_file_costs.\n")
    line = line.split(" ") # server_id client_id cost

    client_id = int(line[1])
    cost = int(line[2])

    # Cost between this machine and the current other machine. Add to list.
    list_of_costs_from_clients.append([client_id, cost])

    # A client is a neighbor if it is originally read from the topology file.
    neighbors.append(client_id)

# Create an initial routing table with just the link costs the server knows from the topology file.
def create_initial_routing_table(server_id):
    # print("\nDebug: ENTER create_initial_routing_table.\n")

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
    # print("\nDebug: ENTER start_server.\n")

    global this_server_id
    this_server_id = server_id

    # In the list of server connections, find the server_id of this machine for its address and port info. 
    # (Server finds itself and sets up socket with the information.)
    for server_line in top_file_server_lines:

        server_line = server_line.split(" ")

        if (int(server_line[0]) == server_id):
            server_ip = str(server_line[1])
            server_port = int(server_line[2])
            list_of_bool_disabled[server_id - 1] = True     # Disable self.

    # print("Debug: server_ip =", server_ip)
    # print("Debug: server_port =", server_port)

    # Start a thread that the server can listen on
    server_thread = threading.Thread(target=_start_server, args=(server_ip, server_port), daemon=True)
    server_thread.start()

# Start the server on this machine.
def _start_server(server_ip, server_port):
    # print("\nDebug: ENTER _start_server.\n")
    
    # Create UDP socket.
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_sock.bind((server_ip, server_port))

    while True:

        # Receive data whenever a client socket sends it.
        bytes_of_data, client_address = server_sock.recvfrom(1024)
        # Using pickle library to serialize (dumps) and deserialize (loads) the data so that we can use a list format for easy use.
        data_received = pickle.loads(bytes_of_data)
        from_server_id = data_received[0]
        recv_data_updates = data_received[1]
        # Start a thread to process data so this function can continue listening.
        thread_to_process_data = threading.Thread(target=process_data, args=(from_server_id, recv_data_updates, client_address), daemon=True)
        thread_to_process_data.start()

# Process the data taken from another machine. Update this machine's routing table. Update link costs. Update number of packets received.
def process_data(from_server_id, recv_data, client_address):
    # print("\nDebug: ENTER process_data.\n")
    print("RECEIVED DATA FROM SERVER", from_server_id)

    # Increment number of packets received.
    global packets_received
    packets_received += 1

    # debug()

    # Check if data being received is a link cost update. If so, update the link cost to the machine it is received from.
    if isinstance(recv_data, int):
        link_cost = int(recv_data)
        for cost_pair in list_of_costs_from_clients:
            if cost_pair[0] == from_server_id:
                cost_pair[1] = link_cost

        # The link cost from this server to the client data was received from is updated in routing table.
        routing_table[this_server_id - 1][from_server_id - 1] = link_cost

        return
    
    # debug()
    
    # Else, the data being received is a routing table.

    # Immediately update the row of the client the data is received from.
    for i in range(len(routing_table)):
        routing_table[from_server_id - 1][i] = recv_data[from_server_id - 1][i]

    # Using the data, calculate the shortest cost paths from this machine to all others using Bellman-Ford algorithm.
    # --- NOT IMPLEMENTED ---

# Update the link cost between this machine and another.
def update(server_id1, server_id2, link_cost, this_server_id):
    # print("\nDebug: ENTER update.\n")

    server_id1 = int(server_id1)
    server_id2 = int(server_id2)
    if link_cost == "inf":
        link_cost = -1
    link_cost = int(link_cost)
    this_server_id = int(this_server_id)

    # If the server ids are the same.
    if (server_id1 == server_id2):
        print("update", server_id1, server_id2, link_cost, ":: FAIL :: Cannot update a machine's cost to itself.")
        return
    
    # debug()
    
    sending_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # If one of the servers to update is this machine's server, proceed. Acknowledge which id belongs to this machine.
    if (server_id1 == this_server_id):
        for cost_pair in list_of_costs_from_clients:
            if cost_pair[0] == server_id2:
                cost_pair[1] = link_cost

        # Send updated link cost from this machine (server_id1) to the other machine (server_id2).
        data_to_send = pickle.dumps([server_id1, link_cost])
        sending_socket.sendto(data_to_send, (list_of_ips_from_clients[server_id2 - 1], list_of_ports_from_clients[server_id2 - 1]))

        # The link cost from this server to the client data was sent to is updated in routing table.
        routing_table[this_server_id - 1][server_id2 - 1] = link_cost

    elif (server_id2 == this_server_id):
        for cost_pair in list_of_costs_from_clients:
            if cost_pair[0] == server_id1:
                cost_pair[1] = link_cost

        # Send updated link cost from this machine (server_id2) to the other machine (server_id1).
        data_to_send = pickle.dumps([server_id2, link_cost])
        sending_socket.sendto(data_to_send, (list_of_ips_from_clients[server_id1 - 1], list_of_ports_from_clients[server_id1 - 1]))

        # The link cost from this server to the client data was sent to is updated in routing table.
        routing_table[this_server_id - 1][server_id1 - 1] = link_cost

    # If neither server id is this machine's, don't update since only the participating machines should update.
    else:
        print("update", server_id1, server_id2, link_cost, ":: FAIL :: This machine cannot update the link cost between two other machines. This server has id:", this_server_id)
        return

    sending_socket.close()

    print("update", server_id1, server_id2, link_cost,":: SUCCESS")

    # debug()

# A thread is created on this function in dv.py file. It will continuously send out this machine's routing table data at the update interval.
def send_data_on_interval(rout_update_interval, server_id, isNow = False):
    # print("\nDebug: ENTER send_data_on_interval.\n")

    while True:
        time.sleep(rout_update_interval)
        # print("Debug: Interval time elapsed.")

        # For every machine we can communicate with, ...
        for i in range(len(list_of_ids_from_clients)):

            # and isn't disabled, ...
            if not list_of_bool_disabled[i]:

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
            print("step :: SUCCESS")
            break

# Send data immediately.
def send_data_now(server_id):
    send_data_on_interval(0, server_id, True)

# Display the number of packets since the last time this function was called. Reset to 0.
def packets_since_last_call():

    global packets_received
    print("This machine has received", packets_received, "packet(s) since the last check in.")
    packets_received = 0
    print("packets :: SUCCESS")

# Remove connection and stop sending data to the given client.
def disable_connection(client_id):
    # print("\nDebug: ENTER disable_connection.\n")

    client_id = int(client_id)

    # debug()

    # If the machine to disable is not a neighbor.
    if (client_id not in neighbors):
        print("disable", client_id, ":: FAIL :: You can only disable connections between a NEIGHBORING machine.")
        return
    
    # Find the index of the client and disable the connection in the boolean list.
    try:
        index_of_client = list_of_ids_from_clients.index(client_id)

        list_of_bool_disabled[index_of_client] = True

        print("disable", client_id, ":: SUCCESS")

    # If the machine to disable's server id is invalid. (As long as this machine is not sending data to it, it is invalid.)
    except ValueError:
        print("disable", client_id, ":: FAIL :: The server id", client_id, "is not available or already disabled.")

    # debug()

# Simulate server crash by disabling all connections.
def server_crash():
    # print("\nDebug: ENTER server_crash.\n")
    for i in range(len(list_of_bool_disabled)):
        list_of_bool_disabled[i] = True

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

    print("display :: SUCCESS")

def debug():

    x = "List of ids: " + str(list_of_ids_from_clients)
    x += "\nList of ips: " + str(list_of_ips_from_clients)
    x += "\nList of ports: " + str(list_of_ports_from_clients)
    x += "\nList of costs: " + str(list_of_costs_from_clients)
    x += "\nList of bool disabled: " + str(list_of_bool_disabled)

    print(x)
