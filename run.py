import os
from pathlib import Path
import requests
from dotenv import load_dotenv
import sys

load_dotenv()

pterodactyl_url = os.getenv('PTERODACTYL_URL')
pterodactyl_token = os.getenv('PTERODACTYL_AUTH_TOKEN')

ptero_headers = {
    "Authorization": f'Bearer {pterodactyl_token}',
    "Content-Type": "application/json",
}

# From filesystem, we can only be able to get the backup_uuid which is their respective file names.
# Backups are stored in ptero: 01f3e8d9-1d9c-427d-b7ed-f128f3f173a5.tar.gz
# Intented to be used on one of the Node(s).
def get_all_filesystem_backups():
    filesystem_backups_dir = "/var/lib/pterodactyl/backups/"
    files_in_backup = os.listdir(filesystem_backups_dir)
    backup_files = [
        Path(Path(f).stem).stem for f in files_in_backup if f.endswith('.tar.gz')]
    return backup_files


def backups_not_in_ptero():
    ptero_backups = get_all_backups_from_ptero()
    local_backups = get_all_filesystem_backups()
    # Getting all the uuids of local backups not in ptero
    backups_not_in_ptero_list = []
    for each_local_backup in local_backups:
        if not each_local_backup in ptero_backups.keys():
            backups_not_in_ptero_list.append(each_local_backup)
    return backups_not_in_ptero_list


###
# WARNING
# - This will always report a list of backups if there are multiple nodes configured in Pterodactyl
# Due to backups from servers on other nodes not being in the filesystem of this node.
###
def backups_not_in_filesystem():
    ptero_backups = get_all_backups_from_ptero()
    local_backups = get_all_filesystem_backups()
    # Getting all the uuids of the ptero backups not on filesystem
    backups_not_in_filesystem_list = []
    for each_ptero_backup in ptero_backups.keys():
        if not each_ptero_backup in local_backups:
            backups_not_in_filesystem_list.append(each_ptero_backup)
    return backups_not_in_filesystem_list


def get_all_backups_from_ptero():
    all_backups_from_ptero = {}
    backups_response = requests.get(f'{pterodactyl_url}/ultra-admin/backup/list', headers=ptero_headers)
    if backups_response.status_code != 200:
        sys.exit(f"Error when connecting with pterodactyl with status code: {backups_response.status_code}")
    all_ptero_backups = backups_response.json()['data']
    for each_ptero_backup in all_ptero_backups:
        all_backups_from_ptero[each_ptero_backup['uuid']] = {
            'id': each_ptero_backup['id'],
            'server_id': each_ptero_backup['server_id'],
            'name': each_ptero_backup['name'],
            'created_at': each_ptero_backup['created_at']
        }
    return all_backups_from_ptero

if __name__ == "__main__":
    # not_filesystem_backups = backups_not_in_filesystem()
    # print(not_filesystem_backups)
    not_ptero_backups = backups_not_in_ptero()
    print(not_ptero_backups)