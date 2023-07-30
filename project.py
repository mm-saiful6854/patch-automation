import os
import re
import paramiko
import datetime,time
import sys
import getpass


'''
Rules:
1. Python method name follows the snake_case convention. 
This convention makes method names easy to read and understand, especially for longer method names.

'''

# constant
system='windows'
basic_config_filename = 'basic_config.txt'
remote_host_config_filename='remote_host_config_filename'
local_file_path_param='local_file_path'
last_check_time_param='last_check_time'
time_string_format='%d-%m-%Y %H:%M:%S'


remote_host_param_name ='host'
remote_port_param_name ='port'
remote_username_param_name ='username'
remote_password_param_name ='password'
remote_dir_path_param_name='remote_dir_path'
# end constant




def detect_system():
    global system
    # sys.platform.startswith('darwin') is required for mac-os. this os is out of support till now.
    if sys.platform.startswith('win'):
        system ='windows'
    elif sys.platform.startswith('linux'):
        system='linux'
    else:
        system='unknown'


"""
# Define the local file to be uploaded
    local_file_path = '/path/to/local/file.txt'

    # Define the remote destination directory for the file
    remote_dir_path = '/path/to/remote/directory/'
"""
def upload_file(local_file_path, remote_dir_path, host, port, username, password, patch_list):
    
    print("Uploading on this host: ")
    print("\t'{}': '{}'".format('local file path', local_file_path))
    print("\t'{}': '{}'".format('host', host))
    print("\t'{}': '{}'".format('port', port))
    print("\t'{}': '{}'".format('username', username))
    print("\t'{}': '{}'".format('password', password))
    print("\t'{}': '{}'".format('remote dir path', remote_dir_path))
    



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

        for filename in patch_list:
            # Upload the local file to the remote host
            scp_client.put(local_file_path+filename, remote_dir_path+filename)

    except Exception as err:
        is_upload = False 
        print(f"Unexpected {err=}, {type(err)=}")
    finally:
        # Close the SCP and SSH client connections
        scp_client.close()
        ssh_client.close()
    return is_upload



'''incompleted'''
def execute_command(ssh_client):
    # Unzip the file on the remote host
    remote_dir_path=""
    stdin, stdout, stderr = ssh_client.exec_command('unzip '+remote_dir_path+' -d /usr/local/SMS_APP_SERVER_v4Dev/')

    # Print the output of the command
    for line in stdout:
        print(line.strip())

    for line in stdin:
        print(line.strip())



'''incompleted'''
def execute_command_by_invoke_shell(ssh_client):
    # start an interactive shell
    shell = ssh_client.invoke_shell()

    # send the unzip command to server
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
{parameter: value} and so on.
'''
def read_file(filename):
    if(filename==None):
        return
    

    mydict={}
    # Open the file for reading
    with open(filename, "r") as file:
        # Read the contents of the file into a variable
        fullcontents = file.read()
        # Close the file
        file.close()
        # start manipulation
        lines = fullcontents.splitlines();
        for line in lines:
            if(not line.startswith('#')):
                value = line.split('=')
                if(len(value)==2):
                    mydict[value[0]] = value[1]

        # end manipulation    
    return mydict





def get_list_of_host_details(host_dict):
    # Sort the dictionary by its keys
    sorted_host_dic = dict(sorted(host_dict.items()))

    ip=[]
    port=[]
    username=[]
    password=[]
    remote_dir=[]

    for key, value in host_dict.items():
        if(key.startswith(remote_host_param_name)):
            ip.append(value)

        if(key.startswith(remote_port_param_name)):
            port.append(value)

        if(key.startswith(remote_username_param_name)):
            username.append(value)
    
        if(key.startswith(remote_password_param_name)):
            password.append(value)
        if(key.startswith(remote_dir_path_param_name)):
            remote_dir.append(value)
    
            
    return (ip, port, username, password, remote_dir)

def convert_time_string_into_unix_time(time_string):
    if(len(time_string)==0):
        return 
    try:
        dt_obj = datetime.datetime.strptime(time_string, time_string_format)
        # multipy by 1000 in order to adding last millisecond
        unix_time = int(dt_obj.timestamp()*1000)
        return unix_time
    except Exception as err:
        print(err)
    return



def get_updated_file_list(source_dir_path, last_check_time_str, current_time_str):
    print("\nchecking for patch: ")
    
    last_check_unix_time = convert_time_string_into_unix_time(last_check_time_str)
    current_unix_time = convert_time_string_into_unix_time(current_time_str)
    print('\tcurrent time: {}'.format(current_unix_time))
    print("\tlast check unix time: {}".format(last_check_unix_time))
    print('')

    patch_file_list=[]
    files = os.listdir(source_dir_path)
    for file in files:
        # Get the full path of the file
        file_path = os.path.join(source_dir_path, file)
        if(os.path.isdir(file_path)):
            get_upload_file_list_in_recursive(file_path, file, patch_file_list, last_check_unix_time, current_unix_time)
            continue
        # Get the file's details
        file_stats = os.stat(file_path)
        # type casting float -> int
        last_modified = int(file_stats.st_mtime*1000)

        # Print the file's details
        print(f'\tFilename: {file}')
        print(f'\tLast modified: {last_modified}')
        if(last_modified>last_check_unix_time and last_modified<=current_unix_time):
            patch_file_list.append(file)
        print('')
    return patch_file_list


def get_upload_file_list_in_recursive(path, dir_name, patch_file_list, last_check_unix_time, current_unix_time):
    files = os.listdir(path)
    for file in files:
        # Get the full path of the file
        file_path = os.path.join(path, file)
        if(os.path.isdir(file_path)):
            get_upload_file_list_in_recursive(file_path,dir_name+'/'+file,patch_file_list, last_check_unix_time, current_unix_time)
            continue
        # Get the file's details
        file_stats = os.stat(file_path)
        # type casting float -> int
        last_modified = int(file_stats.st_mtime*1000)

        # Print the file's details
        print(f'\tFilename: {file}')
        print(f'\tLast modified: {last_modified}')
        if(last_modified>last_check_unix_time and last_modified<=current_unix_time):
            patch_file_list.append(dir_name+'/'+file)
        print('')
    return patch_file_list


'''save current time into basic_config.txt file as last check time'''
def save_last_check_time(filename,mydict):
    # open file in write mode
    with open(filename, 'w') as f:
        # write data to the file
        for key, value in mydict.items():
            f.write(key+'='+ str(value)+'\n')

'''validate ip using regular expression'''
def is_valid_ip_address(ip_address):
    ip_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    if re.match(ip_pattern, ip_address):
        return True
    else:
        return False
    


'''print into console in a decent manner for increasing system readability'''
def display_mydict(my_dict):
    for key, value in my_dict.items():
        if(key.startswith("password")):
            print("\t'{}': '{}'".format(key, '*************'))
        else:
            print("\t'{}': '{}'".format(key, value))


def main():
    print("============================ Program v1.0.0 ==============================")
    current_time_str = datetime.datetime.now().strftime(time_string_format)
    print("Up Time:", current_time_str)

    # detect the running operating system. If operating system is unknown, then exit
    detect_system()
    if(system=='unknown'):
        print("Support unavailable. Sorry")
        return
    
    print("Detected Os: {}".format(system))
    print("paramiko package version: {}".format(paramiko.__version__))
    print('')

    username = getpass.getuser()
    print(f"Hello {username}. Hope everything is fine. I am patch-automation bot.\nHere I am for helping you to push patch from your local computer to your remote servers\n")
    
    
    # next target
    '''
        individual remote dir path - done
        feature of append new host interactively. - pause
        prompt password for each host, otherwise store encrypted password 
        check file modification time: upload those files that are modify later - done
        write current time as last check time into basic_config.txt file - done
        parse directory

    '''


    # load basic configuration
    basicConfig= read_file(filename=basic_config_filename)
    print("# Basic Configuration:")
    display_mydict(basicConfig)

    if(basicConfig == None):
        print("Invalid Basic Configuration. exiting...")
        return


    # get dictionary of remote host configuration
    host_dict = read_file(filename=basicConfig.get(remote_host_config_filename))
    print("# Host Configuration:")
    display_mydict(host_dict)
    if(host_dict == None):
        print("Invalid Host Configuration. exiting...")
        return

    # get list of host, port, username, password
    ips, ports, usernames, passwords, remote_dirs = get_list_of_host_details(host_dict = host_dict)



    # fetching patch files
    source_dir_path = basicConfig.get(local_file_path_param)
    last_check_time_str = basicConfig.get(last_check_time_param)

    patch_file_list = get_updated_file_list(source_dir_path, last_check_time_str, current_time_str)
    print("Patch file List: {}".format(patch_file_list))
    
    if(len(patch_file_list)==0):
        print("No need to push anything.")
    else:
        for itr in range(len(ips)):
            host = ips[itr]
            port = ports[itr]
            user = usernames[itr]
            password = passwords[itr]
            remote_dir = remote_dirs[itr]
        
            if(is_valid_ip_address(ip_address=host)):
                status = upload_file(local_file_path=source_dir_path, remote_dir_path=remote_dir,
                host=host,
                port=port,
                username=user,
                password=password, patch_list=patch_file_list)
                if(status==True):
                    print("File upload done!")
                else:
                    print("failed to upload")
                
        # end uploading 

    print("Store last check time into file")
    basicConfig[last_check_time_param] = current_time_str
    save_last_check_time(basic_config_filename,basicConfig)
    print("Everything goes fine.\nSee you again...")


    

if __name__ == '__main__':
    main()
    print("End")


