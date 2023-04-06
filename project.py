import os
import re
import paramiko


# constant
basic_config_filename = 'basic_config.txt'
remote_host_config_filename='remote_host_config_filename'
local_file_path='local_file_path'
remote_dir_path='remote_dir_path'

remote_host_param_name ='host'
remote_port_param_name ='port'
remote_username_param_name ='username'
remote_password_param_name ='password'
# end constant







"""
# Define the local file to be uploaded
    local_file_path = '/path/to/local/file.txt'

    # Define the remote destination directory for the file
    remote_dir_path = '/path/to/remote/directory/'
"""
def uploadFile(local_file_path, remote_dir_path, host, port, username, password):
    
    is_upload=True
    try:
        # Create an SSH client instance
        ssh_client = paramiko.SSHClient()

        # Automatically add the remote host's key to the local host's known_hosts file
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the remote host disabled_algorithms={'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']},
        ssh_client.connect(hostname=host, port=port, username=username, password=password, 
                       banner_timeout=60)
        
        # Create an SCP client instance
        scp_client = ssh_client.open_sftp()

        # Upload the local file to the remote host
        scp_client.put(local_file_path, remote_dir_path)


        # Unzip the file on the remote host
        stdin, stdout, stderr = ssh_client.exec_command('unzip '+remote_dir_path+' -d /usr/local/SMS_APP_SERVER_v4Dev/')

        # Print the output of the command
        for line in stdout:
            print(line.strip())

        for line in stdin:
            print(line.strip())



    except Exception as err:
        is_upload = False 
        print(f"Unexpected {err=}, {type(err)=}")
    finally:
        # Close the SCP and SSH client connections
        scp_client.close()
        ssh_client.close()
    return is_upload


def execute_command_by_invoke_shell(ssh_client):
    # start an interactive shell
    shell = ssh_client.invoke_shell()

    # send the unzip command
    shell.send('unzip -o archive.zip\n')

    # wait for the overwrite prompt
    while not shell.recv_ready():
        pass

    # read the prompt and respond with 'A' to overwrite all files
    output = shell.recv(1024).decode('utf-8')
    if 'overwrite' in output.lower():
        shell.send('A\n')

    # wait for the command to complete
    while not shell.exit_status_ready():
        pass

    # close the shell and the connection
    shell.close()


'''
read file where contents are like this:
parameter=value
return value is dictionary like this:
{parameter: value}
'''
def readfile(filename):
    # Open the file for reading
    with open(filename, "r") as file:
        # Read the contents of the file into a variable
        fullcontents = file.read()
        # Close the file
        file.close()
        # start manipulation
        config_dictionary={}
        lines = fullcontents.splitlines();
        for line in lines:
            if(not line.startswith('#')):
                value = line.split('=')
                if(len(value)==2):
                    config_dictionary[value[0]] = value[1]

        # end manipulation    
    return config_dictionary





def getListOfCredentials(host_dict):
    # Sort the dictionary by its keys
    sorted_host_dic = dict(sorted(host_dict.items()))

    ip=[]
    port=[]
    username=[]
    password=[]
    remote_dir=[]

    for key, value in host_dict.items():
        if(key.startswith('host')):
            ip.append(value)

        if(key.startswith('port')):
            port.append(value)

        if(key.startswith('username')):
            username.append(value)
    
        if(key.startswith('password')):
            password.append(value)
        if(key.startswith('remote_dir_path')):
            remote_dir.append(value)
    
            
    return (ip, port, username, password, remote_dir)


def is_valid_ip_address(ip_address):
    ip_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    if re.match(ip_pattern, ip_address):
        return True
    else:
        return False
    


def display(my_dict):
    for key, value in my_dict.items():
        print("\t'{}': '{}'".format(key, value))


def main():
    print("Program version v1.0.0")
    print("paramiko lib version: {}".format(paramiko.__version__))
    
    # load basic configuration
    basicConfig= readfile(filename=basic_config_filename)
    print("# Basic Configuration:")
    display(basicConfig)

    # next target
    '''
        individual remote dir path - done
        feature of append new host interactively.
        prompt password for each host, otherwise store encrypted password 
        check file modification time: upload those files that are modify later

    '''


    # get dictionary of remote host
    host_dic = readfile(filename=basicConfig.get(remote_host_config_filename))
    print("# Host Configuration:")
    display(host_dic)

    # get list of host, port, username, password
    ips, ports, usernames, passwords, remote_dirs = getListOfCredentials(host_dict = host_dic)



    # uploading 
    source_file_path = basicConfig.get(local_file_path)


    for itr in range(len(ips)):
        host = ips[itr]
        port = ports[itr]
        user = usernames[itr]
        password = passwords[itr]
        remote_dir = remote_dirs[itr]
        
        if(is_valid_ip_address(ip_address=host)):
            status = uploadFile(local_file_path=source_file_path, 
                       remote_dir_path=remote_dir,
                       host=host,
                       port=port,
                       username=user,
                       password=password)
            if(status==True):
                print("File uploaded successfully!")
            else:
                print("failed to upload")
    
    # end uploading 




    

if __name__ == '__main__':
    print("start program")
    main()
    print("end program successfully")


