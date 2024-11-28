# CS 4470 - Main driver for distance vector routing protocol implementation.
# In the network, this machine is referred as the server, while other machines in the network are referred to as clients.
import sys
import threading

from sockets import read_topology_file_server_lines, read_topology_file_costs, start_server, create_initial_routing_table
from sockets import update, send_data_on_interval, send_data_now, packets_since_last_call, disable_connection, server_crash
from sockets import print_routing_table

# [0] = dv.py | [1] = topology.txt | [2] = interval
if len(sys.argv) != 3: 
    print("Two arguments required: <topology-file-name> <routing-update-interval>")
    sys.exit(1)

# Open file to read, 'with' will close the file when done.
with open(sys.argv[1], "r") as top_file:
    top_file_all_lines = [line.rstrip("\n") for line in top_file.readlines()] # Use rstrip to remove new line character (\n) from lines.

rout_update_interval = float(sys.argv[2])

# Getting all info from topology file. ------------------------------------------------------------
server_id = int(sys.argv[1].split(".")[0][15]) # Take the number in the server's topology text file name. Format: 'topology_server#.txt'.
# print("Debug: server_id =", server_id)

num_of_servers = top_file_all_lines[0]
num_of_neighbors = top_file_all_lines[1]

# print("Debug: num_of_servers =", num_of_servers)
# print("Debug: num_of_neighbors =", num_of_neighbors)

# Read the server information line by line in the topology file.
for i in range(2,6):
    read_topology_file_server_lines(top_file_all_lines[i])

# Read the costs to each neighbor line by line in the topology file.
for i in range(6,len(top_file_all_lines)):
    read_topology_file_costs(top_file_all_lines[i])

# Done getting all info from topology file. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

# Start the server on this machine, pass the connection lines from the topology file.
start_server(server_id, top_file_all_lines[2:6])

# Initialize this machine's routing table.
create_initial_routing_table(server_id)

# Start sending out distance vector data over the given interval.
interval_thread = threading.Thread(target=send_data_on_interval,args=(rout_update_interval, server_id), daemon=True)
interval_thread.start()

# Loop on the main thread for user commands.
inUserLoop = True

while inUserLoop:
    print("Execute a user command by typing.")

    # Taking input from the user. Commands are either 1, 2, or 4 values.
    next = input().split(" ", 3)

    # If the command is a single string. (i.e. step, packets, display, and crash)
    if len(next) == 1:
        match next[0]:
            case "step":
                send_data_now(server_id)
            case "packets":
                packets_since_last_call()
            case "display":
                print_routing_table()
            case "crash":
                server_crash()
            case "exit":
                print("All threads terminating. Program closing.")
                inUserLoop = False
            case _:
                print("Command not recognized.")
            
    # If the command is two values. (i.e. disable <server-id>)
    elif len(next) == 2:
        match next[0]:
            case "disable":
                try:
                    # Pass the id of client to disable.
                    disable_connection(next[1])
                except ValueError:
                    print("disable", next[1], ":: FAIL :: Server id must be an integer.")
            case _:
                print("Command not recognized.")

    # If the command is four values. (i.e. update <server-id1> <server-id2> <link cost>)
    elif len(next) == 4:
        match next[0]:
            case "update":
                try:
                    update(next[1], next[2], next[3], server_id)
                except ValueError:
                    print("update", next[1], next[2], next[3], ":: FAIL :: Server ids must be integers and link cost must be an integer or 'inf'.")
            case _:
                print("Command not recognized.")

    else:
        print("Command not recognized.")

    