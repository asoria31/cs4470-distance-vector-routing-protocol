import socket
import threading
import pickle
import time

list_of_ids_from_clients = []                   # All machine's will end up with the same lists of ids, ips, and ports considering the topology file format.
list_of_ips_from_clients = []
list_of_ports_from_clients = []
list_of_costs_from_clients = []                 # Format: [ [client_id, cost], ... ] for the number of machines in the network.
                                                # Ex: [ [2, 7] , [3, 4] , [4, 5] ] for 4 machines. (Self machine (1) is excluded.)
list_of_missed_interval_counts = [0, 0, 0, 0]


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
    server_thread = threading.Thread(target=_start_server, args=(server_ip, server_port))
    server_thread.start()

# Start the server on this machine.
def _start_server(server_ip, server_port):
    print("\nDebug: ENTER _start_server.\n")
    
    # Create UDP socket.
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_sock.bind((server_ip, server_port))

    # server_sock.listen(5)

    while True:

        print("Debug: Server is open...")

        # Receive data whenever a client socket sends it.
        bytes_of_data, client_address = server_sock.recvfrom(1024)
        # Using pickle library to serialize (dumps) and deserialize (loads) the data so that we can use a list format for easy use.
        recv_routing_table = pickle.loads(bytes_of_data)
        # Start a thread to process data so this function can continue listening.
        thread_to_process_data = threading.Thread(target=process_data, args=(recv_routing_table, client_address))
        thread_to_process_data.start()



def process_data(recv_routing_table, client_address):
    print("\nDebug: ENTER process_data.\n")

    print(recv_routing_table[1])

    



# A thread is created on this function in dv.py file. It will continuously send out this machine's routing table data at the update interval.
def send_updates_on_interval(rout_update_interval, server_id):
    print("\nDebug: ENTER send_updates_on_interval.\n")

    while True:
        time.sleep(rout_update_interval)
        print("Debug: Interval time elapsed.")

        # For every machine we can communicate with, ...
        for i in range(len(list_of_ids_from_clients)):
            print(i)

            # serialize the routing table data, ...
            data_to_send = pickle.dumps(routing_table)

            # create a UDP socket, ...
            sending_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # and send the data to them. Don't need to send it to self.
            if i != server_id - 1:
                sending_socket.sendto(data_to_send, (list_of_ips_from_clients[i], list_of_ports_from_clients[i]))

            # Close sending socket.
            sending_socket.close()


def debug_print_list(): # dfhgksrtvehhhhhhhhhhhgnyegiuo54hvon o ui6yuyuhy6  5rjhkrthgi4ugh  jggjktghjg 4ughthtjg

    for i in range(0, 3):
        print("++++++++++++++++++++++++++++++++++++++++++++++++++")
        print(list_of_ids_from_clients[i])
        print(list_of_ips_from_clients[i])
        print(list_of_ports_from_clients[i])
        print(list_of_costs_from_clients[i])
        print(list_of_missed_interval_counts[i])

def print_routing_table():

    x = "     1  2  3  4\n"

    for i in range(len(routing_table)):
        x += str(i + 1) + " ["
        for j in range(len(routing_table[i])):
            if routing_table[i][j] != -1:
                x += "  " + str(routing_table[i][j])
            else:
                x += " " + str(routing_table[i][j])
        x += "]\n"

    print(x)




# REMEMBER TO CLOSE THE SOCKETS IN THE DISCONNECTION FUNCTIONS