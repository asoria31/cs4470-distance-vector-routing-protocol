# CS 4470 - Main driver for distance vector routing protocol implementation.
# In the network, this machine is referred as the server, while other machines in the network are referred to as clients.
import sys
import threading

from sockets import read_topology_file_server_lines, read_topology_file_costs, start_server, send_updates_on_interval, create_initial_routing_table, debug_print_list
from sockets import print_routing_table

# [0] = dv.py | [1] = topology.txt | [2] = interval
if len(sys.argv) != 3: 
    print("Two arguments required: <topology-file-name> <routing-update-interval>")
    sys.exit(1)

# Open file to read, 'with' will close the file when done.
with open(sys.argv[1], "r") as top_file:
    top_file_all_lines = [line.rstrip("\n") for line in top_file.readlines()] # Use rstrip to remove new line character (\n) from lines.

rout_update_interval = float(sys.argv[2])



print(top_file_all_lines)



# Getting all info from topology file. ------------------------------------------------------------
server_id = int(sys.argv[1].split(".")[0][15]) # Take the number in the server's topology text file name. Format: 'topology_server#.txt'.
print("Debug: server_id =", server_id)

num_of_servers = top_file_all_lines[0]
num_of_neighbors = top_file_all_lines[1]

print("Debug: num_of_servers =", num_of_servers)
print("Debug: num_of_neighbors =", num_of_neighbors)



print(top_file_all_lines[2:6])



# Start the server on this machine, pass the connection lines from the topology file.
start_server(server_id, top_file_all_lines[2:6])

# Read the server information line by line in the topology file.
for i in range(2,6):
    read_topology_file_server_lines(top_file_all_lines[i])

# Read the costs to each neighbor line by line in the topology file.
for i in range(6,len(top_file_all_lines)):
    read_topology_file_costs(top_file_all_lines[i])

# Done getting all info from topology file. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

# Initialize this machine's routing table.
create_initial_routing_table(server_id)


interval_thread = threading.Thread(target=send_updates_on_interval,args=(rout_update_interval, server_id))
interval_thread.start()

# debug_print_list()
print_routing_table()