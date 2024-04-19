import paramiko
import configparser
import os
from tqdm import tqdm

# import logging

# logging.basicConfig(level=logging.DEBUG) #DELETE BEFORE DEPLOYMENT

def load_ssh_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    return config

def ssh_connect(ssh_config):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ssh_config['hostname'], username=ssh_config['username'], password=ssh_config['password'])
    return client

def list_images(ssh_client, directory):
    stdin, stdout, stderr = ssh_client.exec_command(f'ls {directory}')
    return stdout.read().decode().splitlines()


def download_image(ssh_client, remote_directory, image_name, local_directory):
    local_image_path = os.path.join(local_directory, image_name)
    remote_image_path = os.path.join(remote_directory, image_name)
    ftp_client = ssh_client.open_sftp()
    try:
        print(f"\nDownloading {remote_image_path} to {local_image_path}")
        ftp_client.get(remote_image_path, local_image_path)
        print(f"Download completed. File size: {os.path.getsize(local_image_path)} bytes")
    except Exception as e:
        print(f"Error during download: {e}")
    finally:
        ftp_client.close()
    return local_image_path


def sync_directories(ssh_client, remote_base_directory, local_base_directory):
    from os import makedirs, listdir
    from os.path import exists, join, isdir

    # Ensure the local base directory exists
    if not exists(local_base_directory):
        makedirs(local_base_directory)

    # Get categories from the remote base directory
    remote_categories = list_directories(ssh_client, remote_base_directory)

    for category in remote_categories:
        local_cat_dir = join(local_base_directory, category)
        remote_cat_dir = join(remote_base_directory, category)

        if not exists(local_cat_dir):
            makedirs(local_cat_dir)

        # Sync the current category directory
        sync_category(ssh_client, remote_cat_dir, local_cat_dir)

def list_directories(ssh_client, directory):
    command = f"find {directory} -maxdepth 1 -type d"
    stdin, stdout, stderr = ssh_client.exec_command(command)
    directory_names = stdout.read().decode().strip().split('\n')
    # Remove the parent directory from the list and extract just the names
    directory_names = [name.split('/')[-1] for name in directory_names if name != directory]
    return directory_names

def sync_category(ssh_client, remote_directory, local_directory):
    remote_files = list_images(ssh_client, remote_directory)
    local_files = os.listdir(local_directory)

    missing_files = [file for file in remote_files if file not in local_files]

    # for file in missing_files:
    #     download_image(ssh_client, remote_directory, file, local_directory)
    #     print(f"Downloaded {file} to {local_directory}")

    for file in tqdm(missing_files, desc="Syncing files"):
        download_image(ssh_client, remote_directory, file, local_directory)




def move_file(ssh_client, src_directory, filename, dest_directory):
    src_path = os.path.join(src_directory, filename)
    dest_path = os.path.join(dest_directory, filename)
    ssh_client.exec_command(f'mv {src_path} {dest_path}')
    

def copy_image_to_local(ssh_client, remote_directory, image_name, local_directory):
    download_image(ssh_client, remote_directory, image_name, local_directory)



def verify_file_move(ssh_client, src_path, dest_path):
    # Check if file exists in the destination and not in the source
    stdin, stdout, stderr = ssh_client.exec_command(f"test -f {dest_path} && ! test -f {src_path}")
    if stdout.channel.recv_exit_status() == 0:
        return True  # File moved successfully
    else:
        return False  # File move failed
