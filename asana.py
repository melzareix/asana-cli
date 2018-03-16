import requests
import humanize
from datetime import datetime
from asciitree import LeftAligned
from terminalcolors import TerminalColor


class AsanaClient:
    def __init__(self, token, wrap_size, show_subtasks=False, show_details=False):
        self.token = token
        self.headers = {'Authorization': 'Bearer ' + self.token}
        self.base_api = 'https://app.asana.com/api/1.0/'
        self.show_subtasks = show_subtasks
        self.show_details = show_details
        self.wrap_size = wrap_size[0]
        self.api_urls = {
            'me': 'users/me',
            'workspaces': 'workspaces',
            'task_details': 'tasks/',
            'assigned_tasks': 'tasks?opt_fields=assignee&assignee=me&limit=100&completed_since=now&workspace=',
        }
        self.me = self.get_me()
        self.workspaces = self.get_workspaces()

    def get_me(self):
        """
        Get details about current user.
        """
        r = requests.get(self.base_api + self.api_urls['me'], headers=self.headers)
        return r.json()['data']

    def get_workspaces(self):
        """
        Get current user workspaces.
        """
        return [str(workspace['id']) for workspace in self.me['workspaces']]

    def get_tasks_tree(self):
        tasks = self.get_my_tasks()
        tasks_trees = []
        for task in tasks:
            task['title'] = TerminalColor.BOLD + '## ' + task['title'] + TerminalColor.END
            tree = {
                task['title']: {
                    'Due date: ' + TerminalColor.BOLD + TerminalColor.RED + task['due_date'] + TerminalColor.END: {}
                }
            }
            # Show notes or not
            if self.show_details:
                tree[task['title']]['Notes:' + task['notes']] = {}

            if self.show_subtasks and len(task['subtasks']) > 0:
                tree[task['title']]['subtasks'] = {}
                for subtask in task['subtasks']:
                    tree[task['title']]['subtasks'][subtask] = {}

            tasks_trees.append(LeftAligned()(tree))
        return tasks_trees[:3]

    def get_my_tasks(self):
        """
        Get all tasks assigned to current user.
        """
        tasks = []
        for workspace_id in self.workspaces:
            for task in self.get_workspace_tasks(workspace_id):
                tasks.append(task)
        return tasks

    def get_workspace_tasks(self, workspace):
        """
        Get tasks assigned to current user in workspace.
        """
        r = requests.get(self.base_api + self.api_urls['assigned_tasks'] + workspace, headers=self.headers)
        tasks = r.json()['data']
        tasks_details = []
        for task in tasks:
            task_id = str(task['id'])
            tasks_details.append(self.get_task_details(task_id))
        return tasks_details

    def get_task_details(self, task_id):
        """
        Get details of a certain task or subtask.
        """
        r = requests.get(self.base_api + self.api_urls['task_details'] + task_id, headers=self.headers)
        task_details = r.json()['data']
        subtasks = self.get_subtasks(task_id)
        return {
            'title': task_details['name'],
            'notes': task_details['notes'],
            'due_date': AsanaClient.readable_date(task_details['due_on']),
            'subtasks': subtasks
        }

    def get_subtasks(self, task_id):
        r = requests.get(self.base_api + self.api_urls['task_details'] + task_id + '/subtasks', headers=self.headers)
        subtasks = r.json()['data']
        return [subtask['name'] for subtask in subtasks]

    @staticmethod
    def readable_date(date):
        if date is None:
            return 'No due date'
        return humanize.naturalday(datetime.strptime(date, '%Y-%m-%d'))
