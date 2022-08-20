from .exceptions import ApiTokenMissingError, ApiTokenWrongError, InvalidInputDict
from .models.project import Project
from .models.section import Section
from .models.task import Task
from .models.label import Label

from typing import Tuple, Optional
import requests
import json
import pprint

class TodoistAPI:
    api_base_url = "https://api.todoist.com/sync/v9"
    api_token = None

    sync_token = "*"
    state = {}

    def __init__(self, api_token=None) -> None:
        if api_token is None:
            raise ApiTokenMissingError

        self.api_token = api_token

    def sync(self, resource_types=["all"], sync_completed=True) -> None:
        headers, data = self._get_required_request_data()
        data['resource_types'] = json.dumps(resource_types)

        r = requests.post(
                    url=self._get_url(endpoint="/sync"),
                    headers=headers,
                    data=data
                   )
        
        response = r.json()

        if r.status_code != 200:
            pprint.pprint(response)
            if response['error_tag']:
                if response['error_tag'] == "AUTH_INVALID_TOKEN":
                    raise ApiTokenWrongError
                elif response['error_tag'] == "UNKNOWN_ERROR":
                    print("Unknown error ocurred! Resetting state ...")
                    self.sync_token = "*"
                    self.state = {}
                    self.sync()

        else:
            self.sync_token = response['sync_token'] if response['sync_token'] else "*"
            self._parse_sync_response(response)
            if sync_completed:
                self._sync_completed_items(response['completed_info'])

    def get_projects(self) -> list:
        return self.state['projects']

    def get_sections(self) -> list:
        return self.state['sections']

    def get_tasks(self) -> list:
        return self.state['tasks']

    def get_labels(self) -> list:
        return self.state['labels']

    def _sync_completed_items(
                self,
                completed_info: list=[]
            ) -> None:
        completed_tasks = []
        
        for info in completed_info:
            items = []
            if "completed_items" not in info:
                continue

            if "project_id" in info:
                items = self._get_archived_items(project_id=info['project_id'])['items']
                pass

            if "section_id" in info:
                items = self._get_archived_items(section_id=info['section_id'])['items']
                pass
            
            if "item_id" in info:
                items = self._get_archived_items(item_id=info['item_id'])['items']
                pass

            for item in items:
                if not item in completed_tasks:
                    completed_tasks.append(item)
                    pass
        self._parse_tasks(sync_tasks=completed_tasks)

    def _get_archived_items(
                self,
                project_id: Optional[str]=None,
                section_id: Optional[str]=None,
                item_id: Optional[str]=None,
                limit: int=20
            ) -> dict:
        headers, data = self._get_required_request_data()
        data.pop("sync_token")
        data['limit'] = min(limit, 100)
        endpoint = None
        if project_id is not None:
            endpoint = f"/archive/items?project_id={project_id}"
        elif section_id is not None:
            endpoint = f"/archive/items?section_id={section_id}"
        elif item_id is not None:
            endpoint = f"/archive/items?parent_id={item_id}"
        else:
            # TODO: custom exception
            raise Exception

        r = requests.post(
                    url=self._get_url(endpoint=endpoint),
                    headers=headers,
                    data=data
                )

        return r.json()
    
    def _get_required_request_data(self) -> Tuple[dict, dict]:
        headers = {"Authorization": f"Bearer {self.api_token}"}
        data = {"sync_token": self.sync_token}
        return (headers, data)
    
    def _get_url(self, endpoint="/") -> str:
        if self.api_base_url.endswith("/"):
            self.api_base_url = self.api_base_url[:-1]

        if endpoint.startswith("/"):
            endpoint = endpoint[1:]

        url = f"{self.api_base_url}/{endpoint}"
        return url

    def _parse_sync_response(self, sync_response: dict={}) -> None:
        self._parse_projects(sync_response.get("projects", []))
        self._parse_sections(sync_response.get("sections", []))
        self._parse_tasks(sync_response.get("items", []))
        self._parse_labels(sync_response.get("labels", []))

    def _parse_projects(self, sync_projects: list=[]) -> None:
        if "projects" not in self.state:
            self.state['projects'] = []

        for project in sync_projects:
            try:
                new_project = Project(project)
                if new_project not in self.state['projects']:
                    self.state['projects'].append(new_project)
                else:
                    project_index = self.state['projects'].index(new_project)
                    self.state['projects'][project_index] = new_project

            except InvalidInputDict:
                print(f"InvalidInputDict: {project.keys()}")

    def _parse_sections(self, sync_sections: list=[]) -> None:
        if "sections" not in self.state:
            self.state['sections'] = []

        for section in sync_sections:
            try:
                new_section = Section(section)
                if new_section not in self.state['sections']:
                    self.state['sections'].append(new_section)
                else:
                    section_index = self.state['sections'].index(new_section)
                    self.state['sections'][section_index] = new_section

            except InvalidInputDict:
                print(f"InvalidInputDict: {section.keys()}")

    def _parse_tasks(self, sync_tasks: list=[]) -> None:
        if "tasks" not in self.state:
            self.state['tasks'] = []

        for task in sync_tasks:
            try:
                new_task = Task(task)
                if new_task not in self.state['tasks']:
                    self.state['tasks'].append(new_task)
                else:
                    task_index = self.state['tasks'].index(new_task)
                    self.state['tasks'][task_index] = new_task

            except InvalidInputDict:
                print(f"InvalidInputDict: {task.keys()}")

    def _parse_labels(self, sync_labels: list=[]) -> None:
        if "labels" not in self.state:
            self.state['labels'] = []

        for label in sync_labels:
            try:
                new_label = Label(label)
                if new_label not in self.state['labels']:
                    self.state['labels'].append(new_label)
                else:
                    label_index = self.state['labels'].index(new_label)
                    self.state['labels'][label_index] = new_label

            except InvalidInputDict:
                print(f"InvalidInputDict: {label.keys()}")

