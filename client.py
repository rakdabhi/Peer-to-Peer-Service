import imp
import threading

from p2pclient import p2pclient
import json
import argparse

if __name__ == "__main__":
    # client_id = None
    # content = None
    # actions = None

    ##############################################################################
    # You need to perform the following tasks:                                   #  
    # 1) Instantiate the client                                                  #
    # 2) Client needs to pick its serveport,bind to it                           #
    # 3) Register with bootstrapper                                              #
    # 4) STart listening on the port picked in step 2                            #
    # 5) Start executing its actions                                             #
    ##############################################################################

    #########################################################################################
    # TODO:  Read the client_id, content and actions from <file>.json, which you can obtain #
    #        from command line arguments. and feed it into the constructor of               #
    #        the p2pclient below                                                            #
    #########################################################################################

    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str, required=True)
    args = parser.parse_args()
    json_file_name = args.file

    file = open(json_file_name)
    client_data = json.load(file)
    file.close()

    client_id = int(client_data['client_id'])
    content = client_data['content']
    actions = client_data['actions']

    client = p2pclient(client_id=client_id, content=content, actions=actions)

    ##############################################################################
    # Now provided you have completed the steps in the p2pclient constructor     #
    # properly, steps                                                            #                  
    # 1, 2 and 3 are completed when you instantiate the client object            #  
    # We are left with steps 4 and 5                                             #
    ##############################################################################

    ##############################################################################
    # TODO: For step 4: call clients.start_listening()                           #
    ##############################################################################

    client_listen_thread = threading.Thread(target=client.start_listening, args=())
    client_listen_thread.start()

    ##############################################################################
    # For step 5: the bootstrapper will call the start() on this client, which  #
    # will make this client start taking its actions.                            #
    ##############################################################################