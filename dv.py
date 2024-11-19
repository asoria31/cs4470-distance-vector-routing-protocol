# CS 4470 - Main driver for distance vector routing protocol implementation.
import sys

from sockets import read_topology_file_and_establish_connections, start_server

# [0] = dv.py | [1] = topology.txt | [2] = interval
if len(sys.argv) != 3: 
    print("Two arguments required: <topology-file-name> <routing-update-interval>")
    sys.exit(1)

# Open file to read, 'with' will close the file when done.
with open(sys.argv[1], "r") as top_file:
    # top_file_all_lines = top_file.readlines()
    top_file_all_lines = [line.rstrip("\n") for line in top_file.readlines()] # Use rstrip to remove new line character (\n) from lines.

rout_update_interval = sys.argv[1] # ----------------------------- should this be an int or a float



print(top_file_all_lines)



# Get all info from topology file. ----------------------------------------------------------------
server_id = sys.argv[1].split(".")[0][15] # Take the number in the server's topology text file name. Format: 'topology_server#.txt'.
print("Debug: server_id =", server_id)

num_of_servers = top_file_all_lines[0]
num_of_neighbors = top_file_all_lines[1]

print("Debug: num_of_servers =", num_of_servers)
print("Debug: num_of_neighbors =", num_of_neighbors)



print(top_file_all_lines[2:6])



# Start the server on this machine, pass the connection lines from the topology file.
start_server(server_id, top_file_all_lines[2:6])

# Create connections. See sockets.py file.
for i in range(2,6):
    # Establish a UDP socket connection for each server in the topology file.
    read_topology_file_and_establish_connections(top_file_all_lines[i])




# Get all info from topology file. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^