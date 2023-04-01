import os
import requests
import datetime
import logging
from dotenv import load_dotenv
from termcolor import colored

# Configure logging
logging.basicConfig(filename='gitlab_cleanup.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration from .env file
load_dotenv()
gitlab_api = os.getenv('GITLAB_API')
project_id = os.getenv('GITLAB_PROJECT_ID')
access_token = os.getenv('GITLAB_ACCESS_TOKEN')

# Configuration
dry_run = True  # Set to False to perform actual deletions

# Define the repository name and the number of tags to keep per repository
important_repositories = {
    'cache': 500,
    'development': 50,
}

# Define the repositories to ignore
ignored_repositories = [
    'main',
]
get_size_of_ignored_repositories = True  # Set to True to get the size of ignored repositories

older_than_days = 30 # Delete tags older than this number of days
tags_per_page = 100  # Set the number of tags to fetch per page (max 100)
delete_empty_repositories = True  # Set to True to delete empty repositories (with 0 tags)

# Functions
def get_all_repositories():
    log_and_print(colored("Fetching all repositories...", "cyan"))
    url = f'{gitlab_api}/projects/{project_id}/registry/repositories'
    headers = {'Private-Token': access_token}
    response = requests.get(url, headers=headers)
    return response.json()

def get_all_tags(repository_id):
    log_and_print(colored(f"Fetching all tags for repository ID: {repository_id}...", "cyan"))
    all_tags = []
    page = 1

    while True:
        url = f'{gitlab_api}/projects/{project_id}/registry/repositories/{repository_id}/tags'
        headers = {'Private-Token': access_token}
        params = {'per_page': tags_per_page, 'page': page}
        response = requests.get(url, headers=headers, params=params)
        tags = response.json()

        log_and_print(colored(f"Found {len(tags)} tags on page {page}...", "cyan"))

        if not tags:
            break

        all_tags.extend(tags)
        page += 1

    return all_tags

def delete_repository(repository_id):
    log_and_print(colored(f"Deleting repository ID: {repository_id}...", "red"))
    url = f'{gitlab_api}/projects/{project_id}/registry/repositories/{repository_id}'
    headers = {'Private-Token': access_token}
    response = requests.delete(url, headers=headers)
    return response.status_code

def get_tag_details(repository_id, tag_name):
    log_and_print(colored(f"Fetching details for tag: {tag_name} in repository ID: {repository_id}...", "cyan"))
    url = f'{gitlab_api}/projects/{project_id}/registry/repositories/{repository_id}/tags/{tag_name}'
    headers = {'Private-Token': access_token}
    response = requests.get(url, headers=headers)
    return response.json()

def delete_tag(repository_id, tag_name):
    log_and_print(colored(f"Deleting tag: {tag_name} from repository ID: {repository_id}...", "red"))
    url = f'{gitlab_api}/projects/{project_id}/registry/repositories/{repository_id}/tags/{tag_name}'
    headers = {'Private-Token': access_token}
    response = requests.delete(url, headers=headers)
    return response.status_code

def log_and_print(message):
    logging.info(message)
    print(message)

# Main
repositories = get_all_repositories()
log_and_print(colored(f"Found {len(repositories)} repositories...", "cyan"))
log_and_print(colored(f"Repositories: {[repository['name'] for repository in repositories]}", "cyan"))

now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

for repository in repositories:
    repository_id = repository['id']
    repository_name = repository['name']

    if repository_name in ignored_repositories and not get_size_of_ignored_repositories:
        log_and_print(colored(f"Repository: {repository_name} is ignored, skipping...", "yellow"))
        continue

    log_and_print(colored(f"Processing repository: {repository_name}...", "yellow"))

    tags = get_all_tags(repository_id)

    if delete_empty_repositories and len(tags) == 0:
        log_and_print(colored(f"Repository: {repository_name} is empty, deleting...", "red"))
        if not dry_run:
            delete_status = delete_repository(repository_id)
            # TODO: This error code is not correct, need to debug
            print(delete_status)
            if delete_status == 200:
                log_and_print(colored(f'Deleted repository: {repository_name}', "green"))
            else:
                log_and_print(colored(f'Failed to delete repository: {repository_name}', "red"))
        else:
            log_and_print(colored(f'Dry run, not deleting repository: {repository_name}', "yellow"))
        continue

    detailed_tags = []

    log_and_print(colored(f"Found {len(tags)} tags for repository: {repository_name}...", "cyan"))

    if repository_name in ignored_repositories:
        continue

    for tag in tags:
        tag_name = tag['name']
        tag_details = get_tag_details(repository_id, tag_name)
        detailed_tags.append(tag_details)

        log_and_print(colored(f"Found tag: {tag_name} with created_at: {tag_details['created_at']}", "cyan"))

    if repository_name in important_repositories:
        log_and_print(colored(f"Repository: {repository_name} is important, keeping {important_repositories[repository_name]} tags...", "yellow"))
        num_tags_to_keep = important_repositories[repository_name]
        sorted_tags = sorted(detailed_tags, key=lambda t: t['created_at'], reverse=True)
        tags_to_delete = sorted_tags[num_tags_to_keep:]
        log_and_print(colored(f"Keeping {num_tags_to_keep} tags for repository: {repository_name}...", "yellow"))
        log_and_print(colored(f"Deleting {len(tags_to_delete)} tags for repository: {repository_name}...", "yellow"))
        log_and_print(colored(f"Tags to delete: {[tag['name'] for tag in tags_to_delete]}", "yellow"))
        log_and_print(colored(f"Tags to keep: {[tag['name'] for tag in sorted_tags[:num_tags_to_keep]]}", "yellow"))
    else:
        log_and_print(colored(f"Repository: {repository_name} is not important, deleting all tags older than {older_than_days} days...", "magenta"))
        tags_to_delete = [tag for tag in detailed_tags if (now - datetime.datetime.fromisoformat(tag['created_at'].replace('Z', '+00:00'))).days > older_than_days]
        log_and_print(colored(f"Keeping {len(detailed_tags) - len(tags_to_delete)} tags for repository: {repository_name}...", "magenta"))
        log_and_print(colored(f"Deleting {len(tags_to_delete)} tags for repository: {repository_name}...", "magenta"))
        log_and_print(colored(f"Tags to delete: {[tag['name'] for tag in tags_to_delete]}", "magenta"))
        log_and_print(colored(f"Tags to keep: {[tag['name'] for tag in detailed_tags if tag not in tags_to_delete]}", "magenta"))

    for tag in tags_to_delete:
        tag_name = tag['name']
        if dry_run:
            log_and_print(colored(f'[Dry Run] Would delete tag: {tag_name} from repository: {repository_name}', "green"))
        else:
            delete_status = delete_tag(repository_id, tag_name)
            if delete_status == 200:
                log_and_print(colored(f'Deleted tag: {tag_name} from repository: {repository_name}', "green"))
            else:
                log_and_print(colored(f'Failed to delete tag: {tag_name} from repository: {repository_name}', "red"))

