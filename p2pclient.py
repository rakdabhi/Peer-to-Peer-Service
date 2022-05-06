"""
Follow the instructions in each method and complete the tasks. We have given most of the house-keeping variables
that you might require, feel free to add more if needed. Hints are provided in some places about what data types 
can be used, others are left to students' discretion, make sure that what you are returning from one method gets correctly
interpreted on the other end. Most functions ask you to create a log, this is important
as this is what the auto-grader will be looking for.
Follow the logging instructions carefully.
"""

"""
Appending to log: every time you have to add a log entry, create a new dictionary and append it to self.log. The dictionary formats for diff. cases are given below
Registraion: (R)
{
    "time": <time>,
    "text": "Client ID <client_id> registered"
}
Unregister: (U)
{
    "time": <time>,
    "text": "Unregistered"
}
Fetch content: (Q)
{
    "time": <time>,
    "text": "Obtained <content_id> from <IP>#<Port>
}
Purge: (P)
{
    "time": <time>,
    "text": "Removed <content_id>"
}
Obtain list of clients known to a client: (O)
{
    "time": <time>,
    "text": "Client <client_id>: <<client_id>, <IP>, <Port>>, <<client_id>, <IP>, <Port>>, ..., <<client_id>, <IP>, <Port>>"
}
Obtain list of content with a client: (M)
{
    "time": <time>,
    "text": "Client <client_id>: <content_id>, <content_id>, ..., <content_id>"
}
Obtain list of clients from Bootstrapper: (L)
{
    "time": <time>,
    "text": "Bootstrapper: <<client_id>, <IP>, <Port>>, <<client_id>, <IP>, <Port>>, ..., <<client_id>, <IP>, <Port>>"
}
"""
import random
import threading
import socket
import time
import json
from enum import Enum


class State(Enum):
    REGISTERED = 1
    UNREGISTERED = 2


def send_message(message, ip='127.0.0.1', port=8888, receive_data=False):
    socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_connection.connect((ip, port))
    socket_connection.send(message.encode())
    returned_data = None
    if receive_data:
        returned_data = socket_connection.recv(1048).decode()
        print(f"send_message() returned_data: {returned_data}")
    socket_connection.close()
    return returned_data


class p2pclient:
    def __init__(self, client_id, content, actions):
        ##############################################################################
        # TODO: Initialize the class variables with the arguments coming             #
        #       into the constructor                                                 #
        ##############################################################################

        self.client_id = client_id
        self.content = content
        self.actions = actions  # this list of actions that the client needs to execute

        self.content_originator_list = {}  # None for now, it will be built eventually

        ##################################################################################
        # TODO:  You know that in a P2P architecture, each client acts as a client       #
        #        and the server. Now we need to setup the server socket of this client   #
        #        Initialize the the self.socket object on a random port, bind to the port#
        #        Refer to                                                                #
        #        https://docs.python.org/3/howto/sockets.html on how to do this.         #
        ##################################################################################

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip_address = "127.0.0.1"
        random.seed(client_id)
        self.port_number = random.randint(9000, 9999)
        self.socket.bind((self.ip_address, self.port_number))

        self.bootstrapper_ip = '127.0.0.1'
        self.bootstrapper_port = 8888

        # 'log' variable is used to record the series of events that happen on the client
        # Empty list for now, update as we take actions
        # See instructions above on how to append to log
        self.log = []

        # Timing variables:
        ###############################################################################################
        # TODO:  Ensure that you're doing actions according to time. B.S dictates time. Update this   #
        #        variable when BS sends a time increment signal                                       #
        ###############################################################################################
        self.time = 0
        self.num_of_actions_completed = 0
        self.max_time = 0
        if len(self.actions) > 0:
            self.max_time = self.actions[-1]["time"]
        self.finished_tasks = False

        ##############################################################################
        # TODO:  Register with the bootstrapper by calling the 'register' function   #
        #        Make sure you communicate to the B.S the serverport that this client#
        #        is running on to the bootstrapper.                                  #
        ##############################################################################
        self.register()

        ##############################################################################
        # TODO:  You can set status variable based on the status of the client:      #
        #        Registered: if registered to bootstrapper                           #
        #        Unregistered: unregistred from bootstrapper                         #
        #        Feel free to add more states if you need to                         #
        #        HINT: You may find enum datatype useful                             #
        ##############################################################################
        self.status = State.REGISTERED

        # file_name = f"client_{self.client_id}.json"
        # out = open(file_name, "w")
        # json.dump(self.log, out)
        # out.close()

    def start_listening(self):
        ##############################################################################
        # TODO:  This function will make the client start listening on the randomly  #
        #        chosen server port. Refer to                                        #
        #        https://docs.python.org/3/howto/sockets.html on how to do this.     #
        #        You will need to link each connecting client to a new thread (using #
        #        client_thread function below) to handle the requested action.       #
        ##############################################################################
        self.socket.listen()
        while True:
            if self.finished_tasks:
                self.socket.close()
                break
            else:
                try:
                    connecting_client, address = self.socket.accept()
                    thread = threading.Thread(target=self.client_thread, args=(connecting_client, address))
                    thread.start()
                except:
                    break
        exit()

    def client_thread(self, connecting_client, address):
        ##############################################################################
        # TODO:  This function should handle the incoming connection requests from   #
        #        other clients.You are free to add more arguments to this function   #
        #        based your need                                                     #
        #        HINT: After reading the input from the buffer, you can decide what  #
        #        action needs to be done. For example, if the client is requesting   #
        #        list of known clients, you can return the output of self.return_list_of_known_clients #
        ##############################################################################
        while True:
            data = connecting_client.recv(1024).decode().split()
            if data:
                request = data[0]
                message = None
                if "START" in request:
                    self.perform_action(new_time=1)
                elif "INCREMENT" in request:
                    new_time = int(data[1])
                    print(f"Received INCREMENT message from bootstrapper, new_time = {new_time}")
                    self.perform_action(new_time)
                elif "CLOSE" in data:
                    if self.time >= self.max_time:
                        print(f"Received CLOSE message from bootstrapper")
                        file_name = f"client_{self.client_id}.json"
                        out = open(file_name, "w")
                        json.dump(self.log, out)
                        out.close()
                    self.finished_tasks = True
                    self.socket.close()
                    print("Socket closed")
                    break
                elif "List" in request:
                    which_list, client_ip, client_port = data[1], data[2], int(data[3])
                    if "clients" in which_list:
                        message = json.dumps(self.return_list_of_known_clients())
                        print(f"Sending {message} to Client {client_ip} {client_port} (list of known clients)")
                    elif "hashes" in which_list:
                        message = json.dumps(self.return_content_list())
                        print(f"Sending {message} to Client {client_ip} {client_port} (list of object hashes)")
                    connecting_client.send(message.encode())
                elif "request_content" in request:
                    content_id = data[1]
                    message = self.find_content_or_hint(content_id)
                    connecting_client.send(message.encode())
        print("exit")
        exit()
    def find_content_or_hint(self, content_id):
        message = "sorry"
        if content_id in self.content:
            message = "found"
        elif content_id in self.content_originator_list:
            content = self.content_originator_list[content_id]
            client_id, client_ip, client_port = int(content[0]), content[1], int(content[2])
            if client_id != self.client_id:
                message = f"hint {client_id} {client_ip} {client_port}"
        return message

    def register(self, ip='127.0.0.1', port=8888):
        ##############################################################################
        # TODO:  Register with the bootstrapper. Make sure you communicate the server#
        #        port that this client is running on to the bootstrapper.            #
        #        Append an entry to self.log that registration is successful         #
        ##############################################################################
        message = f"register {self.client_id} {self.ip_address} {self.port_number} {self.max_time}"
        send_message(message)
        register_dict = {"time": self.time,
                         "text": f"Client ID {self.client_id} registered"}
        self.log.append(register_dict)
        print(f"Registered {self.client_id} {self.ip_address} {self.port_number} {self.max_time}")

    def deregister(self, ip='127.0.0.1', port=8888):
        ##############################################################################
        # TODO:  Deregister/re-register with the bootstrapper                        #
        #        Append an entry to self.log that deregistration is successful       #
        ##############################################################################
        message = f"deregister {self.client_id} {self.ip_address} {self.port_number}"
        send_message(message)
        if self.time > 0:
            deregister_dict = {"time": self.time,
                               "text": "Unregistered"}
            self.log.append(deregister_dict)
        print(f"Unregistered {self.client_id} {self.ip_address} {self.port_number} from Bootstrapper")

    def start(self):
        ##############################################################################
        # TODO:  When the Bootstrapper sends a start signal, the client starts       #
        #        executing its actions. Once this is called, you have to             #
        #        start reading the items in self.actions and start performing them   #
        #        sequentially, at the time they have been scheduled for, and as timed#
        #        by B.S. Once you complete an action, let the B.S know and wait for  #
        #        B.S's signal before continuing to next action                       #
        ##############################################################################

        ##############################################################################
        # TODO:  ***IMPORTANT***                                                     #
        # At the end of your actions, “export” self.log to a file: client_x.json,    #
        # this is what the autograder is looking for. Python’s json package should   #
        # come handy.                                                                #
        ##############################################################################
        self.perform_action(new_time=1)

    def perform_action(self, new_time):
        if self.time + 1 != new_time:
            print(f"self.time = {self.time}, new_time = {new_time}")
            pass
        else:
            self.time = new_time
            for action_dict in self.actions:
                if action_dict["time"] == self.time:
                    code = action_dict["code"]
                    if code == "R":
                        self.register()
                    elif code == "U":
                        self.deregister()
                    elif code == "L":
                        self.query_bootstrapper_all_clients()
                    elif code == "Q":
                        self.request_content(action_dict["content_id"])
                    elif code == "P":
                        self.purge_content(action_dict["content_id"])
                    elif code == "O":
                        self.query_client_for_known_client(int(action_dict["client_id"]))
                    elif code == "M":
                        self.query_client_for_content_list(int(action_dict["client_id"]))
                    break

            message = f"action_complete {self.client_id} {self.ip_address} {self.port_number}"
            send_message(message)

            print(f"Client {self.client_id} sent action_complete message to Bootstrapper")

            file_name = f"client_{self.client_id}.json"
            out = open(file_name, "w")
            json.dump(self.log, out)
            out.close()

            if self.time == self.max_time:
                file_name = f"client_{self.client_id}.json"
                out = open(file_name, "w")
                json.dump(self.log, out)
                out.close()

    # TODO: clarify on logging
    def query_bootstrapper_all_clients(self, logging=True):
        ##############################################################################
        # TODO:  Use the connection to ask the bootstrapper for the list of clients  #
        #        registered clients.                                                 #
        #        Append an entry to self.log                                         #
        ##############################################################################
        message = f"query {self.client_id} {self.ip_address} {self.port_number}"
        returned_data = send_message(message, receive_data=True)
        if logging:
            log_data = returned_data.replace("(", "<") \
                .replace(")", ">") \
                .replace("[", "") \
                .replace("]", "") \
                .replace("'", "") \
                .replace("\"", "")
            query_bootstrapper_dict = {"time": self.time,
                                       "text": f"Bootstrapper: {log_data}"}
            self.log.append(query_bootstrapper_dict)
        clients_list = json.loads(returned_data)
        return clients_list

    # TODO: clarify on logging
    def query_client_for_known_client(self, client_id, client_ip=None, client_port=None, logging=True):
        client_list = None
        ##############################################################################
        # TODO:  Connect to the client and get the list of clients it knows          #
        #        Append an entry to self.log                                         #
        ##############################################################################
        if client_ip is None and client_port is None:
            bootstrapper_clients_list = self.query_bootstrapper_all_clients(logging=False)
            client = None
            for client_info in bootstrapper_clients_list:
                if int(client_info[0]) == client_id:
                    client = client_info
                    break
            client_ip = client[1]
            client_port = int(client[2])
        message = f"List clients {self.ip_address} {self.port_number}"
        returned_data = send_message(message=message, ip=client_ip, port=client_port, receive_data=True)
        if logging:
            log_data = returned_data.replace("[", "<").replace("]", ">").replace("\"", "")
            query_client_dict = {"time": self.time,
                                 "text": f"Client {client_id}: {log_data}"}
            self.log.append(query_client_dict)
        client_list = json.loads(returned_data)
        return client_list

    def return_list_of_known_clients(self):
        ##############################################################################
        # TODO:  Return the list of clients known to you                             #
        #        HINT: You can make a set of <client_id, IP, Port> from self.content_originator_list #
        #        and return it.                                                      #
        ##############################################################################
        # known_clients_set = set()
        # for content in self.content_originator_list:
        #     client = self.content_originator_list[content]
        #     client_id, client_ip, client_port = int(client[0]), client[1], int(client[2])
        #     if self.client_id != client_id:
        #         known_clients_set.add((client_id, client_ip, client_port))
        known_clients_list = []
        for content in self.content_originator_list:
            client = self.content_originator_list[content]
            client_id, client_ip, client_port = int(client[0]), client[1], int(client[2])
            if (client not in known_clients_list) and (self.client_id != client_id):
                known_clients_list.append((client_id, client_ip, client_port))
        known_clients_list.sort(key=lambda x: x[0])
        return known_clients_list

    def query_client_for_content_list(self, client_id, client_ip=None, client_port=None):
        content_list = None
        ##############################################################################
        # TODO:  Connect to the client and get the list of content it has            #
        #        Append an entry to self.log                                         #
        ##############################################################################
        if client_ip is None and client_port is None:
            bootstrapper_clients_list = self.query_bootstrapper_all_clients(logging=False)
            client = None
            for client_info in bootstrapper_clients_list:
                if int(client_info[0]) == client_id:
                    client = client_info
                    break
            client_ip = client[1]
            client_port = int(client[2])

        message = f"List hashes {self.ip_address} {self.port_number}"
        print(f"Asked client {client_id}: {message}")
        returned_data = send_message(message=message, ip=client_ip, port=client_port, receive_data=True)
        print(f"From Client {client_id}, got this content list: {returned_data}")
        log_data = returned_data.replace("[", "").replace("]", "").replace("\"", "")

        query_client_contact_list = {"time": self.time,
                                     "text": f"Client {client_id}: {log_data}"}
        self.log.append(query_client_contact_list)

        content_list = json.loads(returned_data)
        return content_list

    def return_content_list(self):
        ##############################################################################
        # TODO:  Return the content list that you have (self.content)                #
        ##############################################################################
        return self.content

    def request_content(self, content_id):
        #####################################################################################################
        # TODO:  Your task is to obtain the content and append it to the                                    #
        #        self.content list.  To do this:                                                            #
        #        Get the content as per the instructions in the pdf. You can use the above query_*          #
        #        methods to help you in fetching the content.                                               #
        #        Make sure that when you are querying different clients for the content you want, you record#
        #        their responses(hints, if present) appropriately in the self.content_originator_list       #
        #        Append an entry to self.log that content is obtained                                       #
        #####################################################################################################
        found_client_ip = "-1.1.1.1"
        found_client_port = -1
        content_found = False

        print(f"Content Originator List: {self.content_originator_list}")

        if content_id in self.content:
            self.content_originator_list[content_id] = self.client_id, self.ip_address, self.port_number
            content_found = True
            found_client_ip = self.ip_address
            found_client_port = self.port_number

        if not content_found and content_id in self.content_originator_list:
            client = self.content_originator_list[content_id]
            client_id, client_ip, client_port = int(client[0]), client[1], int(client[2])
            message = f"request_content {content_id}"
            print(f"Phase 1: requesting content {content_id} from Client {client_id}")
            returned_message = send_message(message=message, ip=client_ip, port=client_port, receive_data=True)
            if "found" in returned_message:
                content_found = True
                self.content.append(content_id)
                found_client_ip = client_ip
                found_client_port = client_port

        if not content_found:
            message = f"query {self.client_id} {self.ip_address} {self.port_number}"
            bootstrapper_returned_data = send_message(message, receive_data=True)
            registered_clients_list = json.loads(bootstrapper_returned_data)
            for client in registered_clients_list:
                client_id, client_ip, client_port = int(client[0]), client[1], int(client[2])
                for i in range(3):
                    message = f"request_content {content_id}"
                    print(f"Phase 2: requesting content {content_id} from Client {client_id}")
                    returned_message = send_message(message=message, ip=client_ip, port=client_port,
                                                    receive_data=True).split()
                    if "sorry" in returned_message[0]:
                        break
                    elif "found" in returned_message[0]:
                        content_found = True
                        self.content.append(content_id)
                        self.content_originator_list[content_id] = (client_id, client_ip, client_port)
                        found_client_ip = client_ip
                        found_client_port = client_port
                        break
                    elif "hint" in returned_message[0]:
                        client_id, client_ip, client_port = int(returned_message[1]), returned_message[2], int(
                            returned_message[3])
                if content_found:
                    break

            if not content_found:
                for client in registered_clients_list:
                    client_id, client_ip, client_port = int(client[0]), client[1], int(client[2])
                    known_clients_list = self.query_client_for_known_client(client_id=client_id, client_ip=client_ip,
                                                                            client_port=client_port, logging=False)
                    for known_client in known_clients_list:
                        known_client_id, known_client_ip, known_client_port = int(known_client[0]), known_client[
                            1], int(known_client[2])
                        message = f"request_content {content_id}"
                        print(f"Phase 3: requesting content {content_id} from Client {known_client_id}")
                        returned_message = send_message(message=message, ip=known_client_ip, port=known_client_port,
                                                        receive_data=True)
                        if "found" in returned_message:
                            content_found = True
                            self.content.append(content_id)
                            self.content_originator_list[content_id] = (
                                known_client_id, known_client_ip, known_client_port)
                            found_client_ip = known_client_ip
                            found_client_port = known_client_port
                            break
                        # for i in range(3):
                        #     message = f"request_content {content_id}"
                        #     print(f"Phase 3: requesting content {content_id} from Client {known_client_id}")
                        #     returned_message = send_message(message=message, ip=known_client_ip, port=known_client_port,
                        #                                     receive_data=True).split()
                        #     if "sorry" in returned_message[0]:
                        #         break
                        #     elif "found" in returned_message[0]:
                        #         content_found = True
                        #         self.content.append(content_id)
                        #         self.content_originator_list[content_id] = (
                        #             known_client_id, known_client_ip, known_client_port)
                        #         found_client_ip = known_client_ip
                        #         found_client_port = known_client_port
                        #         break
                        #     elif "hint" in returned_message[0]:
                        #         known_client_id, known_client_ip, known_client_port = int(returned_message[
                        #                                                                       1]), returned_message[2], int(returned_message[3])
                    if content_found:
                        break

        request_content_dict = {"time": self.time,
                                "text": f"Obtained {content_id} from {found_client_ip}#{found_client_port}"}
        self.log.append(request_content_dict)

    def purge_content(self, content_id):
        #####################################################################################################
        # TODO:  Delete the content from your content list                                                  #
        #        Append an entry to self.log that content is purged                                         #
        #####################################################################################################
        # if content_id in self.content:
        #     self.content.remove(content_id)
        self.content.remove(content_id)
        purged_content_dict = {"time": self.time,
                               "text": f"Removed {content_id}"}
        self.log.append(purged_content_dict)
