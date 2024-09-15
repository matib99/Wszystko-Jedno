import paramiko
import os
import time
import atexit

# SSH connection details
HOST = 'entropy_j'
USERNAME = 'juliajoanna'
KEY_FILENAME = '~/.ssh/id_ed25519_1'

REMOTE_DIR_SHORT = '~/YourPersonalGod/elektrownia/short_videos'
REMOTE_DIR_LONG = '~/YourPersonalGod/elektrownia/long_videos'
LOCAL_DIR_SHORT = './short_videos'
LOCAL_DIR_LONG = './long_videos'

TIME_INTERVAL = 10  # Check every 10 seconds

ssh_agent = None

def get_file_list(ssh_client, directory):
    """Get the list of files from the remote directory"""
    stdin, stdout, stderr = ssh_client.exec_command(f'ls {directory}')
    files = stdout.read().decode().splitlines()
    return files

def download_file(ssh_client, remote_file_path, local_file_path):
    """Download a file from the remote server"""
    sftp = ssh_client.open_sftp()
    sftp.get(remote_file_path, local_file_path)
    sftp.close()
    print(f'Downloaded: {remote_file_path} to {local_file_path}')

def check_and_download_new_file():
    # Create SSH client and connect to the server
    global ssh_agent
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(HOST, username=USERNAME, key_filename=KEY_FILENAME)

    # Initial list of files
    previous_files_short = get_file_list(ssh_client, REMOTE_DIR_SHORT)
    previous_files_long = get_file_list(ssh_client, REMOTE_DIR_LONG)

    while True:
        # Check the current list of files
        current_files_short = get_file_list(ssh_client, REMOTE_DIR_SHORT)
        current_files_long = get_file_list(ssh_client, REMOTE_DIR_LONG)
        
        # Check if any new file appeared
        new_files_short = set(current_files_short) - set(previous_files_short)
        new_files_long = set(current_files_long) - set(previous_files_long)
        
        if new_files_short:
            for new_file in new_files_short:
                remote_file_path = os.path.join(REMOTE_DIR_SHORT, new_file)
                local_file_path = os.path.join(LOCAL_DIR_SHORT, new_file)
                download_file(ssh_client, remote_file_path, local_file_path)
        
        if new_files_long:
            for new_file in new_files_long:
                remote_file_path = os.path.join(REMOTE_DIR_LONG, new_file)
                local_file_path = os.path.join(LOCAL_DIR_LONG, new_file)
                # Download the new file
                download_file(ssh_client, remote_file_path, local_file_path)

        # Update the list of previous files
        previous_files_short = current_files_short
        previous_files_long = current_files_long

        # Sleep for a while before checking again
        time.sleep(TIME_INTERVAL)  # Check every 10 seconds

def on_close():
    # Close the SSH connection
    ssh_agent.close()

atexit.register(on_close)


if __name__ == "__main__":
    check_and_download_new_file()