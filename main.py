import os
import shutil
from asana import AsanaClient
import requests_cache
import argparse

# Cache
requests_cache.install_cache('tasks_cache', expire_after=3600)  # Cache expires after an hour
requests_cache.core.remove_expired_responses()

# Client token
token = os.environ['ASANA_TOKEN']
assert token != '', 'Environment variable ASANA_TOKEN not set'

# Terminal Arguments
parser = argparse.ArgumentParser()
parser.add_argument('-n', '--notes', help='Show Task Notes', action='store_true')
parser.add_argument('-s', '--subtasks', help='Show Subtasks', action='store_true')
args = parser.parse_args()

wrap_size = shutil.get_terminal_size((80, 20))
client = AsanaClient(token, wrap_size=wrap_size, show_details=args.notes, show_subtasks=args.subtasks)

# Hello Message
print('Hello, ' + client.me['name'])
print('=' * wrap_size[0])
print('Your current tasks are: ')
print('=' * wrap_size[0])

# Tasks
tasks = client.get_tasks_tree()
for t in tasks:
    print(t)
    print("_" * wrap_size[0])
