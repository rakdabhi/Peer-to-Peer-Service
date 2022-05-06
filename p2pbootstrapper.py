"""
Follow the instructions in each method and complete the tasks. We have given most of the house-keeping variables
that you might require, feel free to add more if needed. Hints are provided in some places about what data types 
can be used, others are left to user discretion, make sure that what you are returning from one method gets correctly
interpreted on the other end. 
At end of each timestep, after all clients have completed their actions, log the registered clients in the format below
{
    "time": <time>,
    "text": "Clients registered: <<client_id>, <IP>, <Port>>, <<client_id>, <IP>, <Port>>, ..., <<client_id>, <IP>, <Port>>"
}
"""
import json
import socket
import threading


class p2pbootstrapper:
    def __init__(self, ip='127.0.0.1', port=8888):
        ##############################################################################
        # TODO:  Initialize the socket object and bind it to the IP and port, refer  #
        #        https://docs.python.org/3/howto/sockets.html on how to do this.     #
        ##############################################################################

        self.boots_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.boots_socket.bind((ip, port))

        self.clients = []  # None for now, will get updates as clients register
        self.clients_dict = {}
        self.remove_clients_list = []

        # Append the log to this variable.
        self.log = []

        # Timing variables:
        ###############################################################################################
        # TODO:  To track the time for all clients, self.time starts at 0, when all clients register  #
        #        self.MAX_CLIENTS is the number of clients we will be spinnign up. You can use this   #
        #        to keep track of how many 'complete' messages to get before incrementing time.       #
        #        CHange this when testing locally                                                     #
        ###############################################################################################
        self.time = 0
        self.MAX_CLIENTS = 20

        self.max_time = 0
        self.num_clients_completed_action = 0
        self.finished_tasks = False

    def start_listening(self):
        ##############################################################################
        # TODO:  This function will make the BS start listening on the port 8888     #
        #        Refer to                                                            #
        #        https://docs.python.org/3/howto/sockets.html on how to do this.     #
        #        You will need to link each connecting client to a new thread (using #
        #        client_thread function below) to handle the requested action.       #
        ##############################################################################
        self.boots_socket.listen()
        while True:
            if self.finished_tasks:
                self.boots_socket.close()
                break
            else:
                try:
                    connecting_client, address = self.boots_socket.accept()
                    thread = threading.Thread(target=self.client_thread, args=(connecting_client, address))
                    thread.start()
                except:
                    break
        exit()

    def client_thread(self, connecting_client, address):
        ##############################################################################
        # TODO:  This function should handle the incoming connection requests from   #
        #        clients. You are free to add more arguments to this function based  #
        #        on your need                                                        #
        #        HINT: After reading the input from the buffer, you can decide what  #
        #        action needs to be done. For example, if the client wants to        #
        #        deregister, call self.deregister_client                             #
        ##############################################################################
        while True:
            if self.finished_tasks:
                break
            else:
                data = connecting_client.recv(1024).decode().split()
                if len(data) > 0:
                    request, client_id, client_ip, client_port = data[0], int(data[1]), data[2], int(data[3])
                    if request == "register":
                        self.register_client(client_id, client_ip, client_port)
                        if self.max_time < int(data[4]):
                            self.max_time = int(data[4])
                    elif request == "deregister":
                        self.deregister_client(client_id, client_ip, client_port)
                    elif request == "query":
                        registered_clients_list = self.return_clients()
                        message = json.dumps(registered_clients_list)
                        connecting_client.send(message.encode())
                    elif request == "action_complete":
                        print(f"Received action_complete from Client {client_id} at time {self.time}")
                        self.num_clients_completed_action += 1
                        self.process_action_complete(request, client_id, client_ip, client_port)
        exit()

    def register_client(self, client_id, ip, port):
        ########################################################################################
        # TODO:  Add client to self.clients, if already present, update status to 'registered  #
        ########################################################################################
        self.clients_dict[(client_id, ip, port)] = True
        # if (client_id, ip, port) not in self.clients:
        #     self.clients.append((client_id, ip, port))
        self.clients.append((client_id, ip, port))
        self.clients.sort(key=lambda x: x[0])
        print(f"Client {client_id} registered to Bootstrapper")

    def deregister_client(self, client_id, ip, port):
        ##############################################################################
        # TODO:  Update status of client to 'deregisterd'                            #
        ##############################################################################
        if (client_id, ip, port) in self.clients:
            # self.clients.remove((client_id, ip, port))
            # self.clients_dict[(client_id, ip, port)] = False
            self.remove_clients_list.append((client_id, ip, port))
            print(f"Client {client_id} unregistered from Bootstrapper")

    def return_clients(self):
        ##############################################################################
        # TODO:  Return self.clients                                                 #
        ##############################################################################
        self.clients.sort(key=lambda x: x[0])
        return self.clients

    def start(self):
        ##############################################################################
        # TODO:  Start timer for all clients so clients can start performing their   #
        #        actions                                                             #
        ##############################################################################

        registered_clients_log = f"{self.return_clients()}"
        registered_clients_log = registered_clients_log.replace("(", "<") \
            .replace(")", ">") \
            .replace("[", "") \
            .replace("]", "") \
            .replace("'", "")
        log_dict = {"time": 0,
                    "text": f"Clients registered: {registered_clients_log}"}
        self.log.append(log_dict)

        out_file = open("bootstrapper.json", "w")
        json.dump(self.log, out_file)
        out_file.close()

        print("Bootstrapper sent out START to all clients!!!")
        message = "START"
        self.send_message_to_clients(message)
        self.time = 1

    def process_action_complete(self, msg, client_id, client_ip, client_port):
        ##############################################################################
        # TODO:  Process the 'action complete' message from a client,update time if  #
        #        all clients are done, inform all clients about time increment       #
        ##############################################################################
        print(f"Num_clients_completed_action: {self.num_clients_completed_action}")

        if self.num_clients_completed_action == len(self.clients_dict):
            self.num_clients_completed_action = 0

            for (client_id, ip, port) in self.remove_clients_list:
                if (client_id, ip, port) in self.clients:
                    self.clients.remove((client_id, ip, port))
                    self.clients_dict[(client_id, ip, port)] = False
            self.remove_clients_list = []

            registered_clients_log = f"{self.return_clients()}"
            registered_clients_log = registered_clients_log.replace("(", "<") \
                .replace(")", ">") \
                .replace("[", "") \
                .replace("]", "") \
                .replace("'", "")
            log_dict = {"time": self.time,
                        "text": f"Clients registered: {registered_clients_log}"}
            self.log.append(log_dict)

            out_file = open("bootstrapper.json", "w")
            json.dump(self.log, out_file)
            out_file.close()

            if self.time == self.max_time:
                # self.boots_socket.close()
                message = "CLOSE"
                print("Sent CLOSE message to all clients")
                self.send_message_to_clients(message)
                out_file = open("bootstrapper.json", "w")
                json.dump(self.log, out_file)
                out_file.close()
                self.finished_tasks = True
                self.boots_socket.close()
                print("Socket closed")
                print("exited")
                exit()
            else:
                self.time += 1
                message = f"INCREMENT: {self.time}"
                self.send_message_to_clients(message)

    def send_message_to_clients(self, message):
        for client in self.clients_dict:
            (client_id, client_ip, client_port) = client
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((client_ip, client_port))
            client_socket.send(message.encode())
            client_socket.close()
