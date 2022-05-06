import os
from pydoc import cli
import subprocess
import platform

os_name = platform.system().lower()
zipfile = 'pa2_submission.zip'

client_data_files = [str(i)+'.json' for i in range(1, 21)]
if "windows" in os_name:
    if os.path.exists('./' + zipfile):
        command = ['del', zipfile]
        subprocess.run(command)

    command = ['tar', '-a', '-c', '-f', zipfile]

    for f in client_data_files:
        command.append(f)
    
    command.append('bootstrapper.py')
    command.append('client.py')
    command.append('p2pbootstrapper.py')
    command.append('p2pclient.py')

    subprocess.run(command)
else:
    command = ['rm', '-f', zipfile]
    subprocess.run(command)

    command = ['zip', '-r', zipfile]

    for f in client_data_files:
        command.append(f)
    
    command.append('bootstrapper.py')
    command.append('client.py')
    command.append('p2pbootstrapper.py')
    command.append('p2pclient.py')
    
    subprocess.run(command)
