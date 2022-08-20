import threading
import os
import time
import bottle
import isodate
import json
from pytz import timezone
from ics import Calendar, Event
from dotenv import load_dotenv
from . import mb_todoist

todoist_apis = {}
sync_active = {}

@bottle.route('/ics/<ics_token>.ics')
def return_ics(ics_token):
    global todoist_apis
    global sync_active

    while sync_active[ics_token]:
        time.sleep(0.5)

    todoist_api = todoist_apis.get(ics_token.lower())

    ics = Calendar()

    if todoist_api is None:
        return u'{}'.format(ics.serialize())

    sections = {section.id: (section.name, section.project_id) for section in todoist_api.get_sections()}
    projects = {project.id: (project.name, project.parent_id) for project in todoist_api.get_projects()}
    tasks = [task for task in todoist_api.get_tasks() if task.due is not None]

    for task in tasks:
        location_array = []
        if task.section_id is not None:
            section_name, section_project = sections[task.section_id]
            location_array.append(section_name)
            next_project_id = section_project
            while next_project_id is not None:
                project_name, project_parent = projects[next_project_id]
                location_array.append(project_name)
                next_project_id = project_parent
        elif task.project_id is not None:
            next_project_id = task.project_id
            while next_project_id is not None:
                project_name, project_parent = projects[next_project_id]
                location_array.append(project_name)
                next_project_id = project_parent

        if "T" in task.due['date']:
            datetime = isodate.parse_datetime(task.due['date'])
            datetime = datetime.replace(tzinfo=timezone(os.environ.get("ICS_TIMEZONE", "UTC")))

            duration = None
            try:
                duration = isodate.parse_duration(os.environ.get("ICS_DEFAULT_DURATION", "PT1H"))
            except Exception:
                duration = isodate.parse_duration("PT1H")

            for label in task.labels:
                try:
                    duration = isodate.parse_duration(label)
                except Exception:
                    pass

            task_event = Event()
            task_event.uid = f"{task.id}@{ics_token}"
            task_event.name = ("☒" if task.checked else "☐") + " " + task.content
            task_event.begin = datetime
            task_event.duration = duration
            task_event.description = f"{task.description}"
            if len(location_array) > 0:
                task_event.location = " / ".join(location_array[::-1])

            ics.events.add(task_event)
        else:
            date = isodate.parse_date(task.due['date'])
            task_event = Event()
            task_event.uid = f"{task.id}@{ics_token}"
            task_event.name = ("☒" if task.checked else "☐") + " " + task.content
            task_event.begin = date
            task_event.make_all_day()
            task_event.description = f"{task.description}"
            if len(location_array) > 0:
                task_event.location = " / ".join(location_array[::-1])

            ics.events.add(task_event)

    return u'{}'.format(ics.serialize())

def sync_everything():
    global todoist_apis
    global sync_active
    while True:
        for ics_token, todoist_api in todoist_apis.items():
            sync_active[ics_token.lower()] = True
            todoist_api.sync()
            sync_active[ics_token.lower()] = False
        time.sleep(15)

def run():
    load_dotenv()
    
    todoist_tokens = json.loads(os.environ.get("TODOIST_TOKENS", "{}"))
    print ("Todoist API tokens loaded: {}".format(len(todoist_tokens)))

    webserver_host = os.environ.get("WEBSERVER_HOST", "127.0.0.1")
    webserver_port = int(os.environ.get("WEBSERVER_PORT", 8080))

    global todoist_apis
    global sync_active

    for ics_token, api_token in todoist_tokens.items():
        try:
            todoist_apis[ics_token.lower()] = mb_todoist.TodoistAPI(api_token)
            sync_active[ics_token.lower()] = True
        except Exception as error:
            print (f"ERROR! Wrong TODOIST_TOKEN for {ics_token}! Removing it ...")
            todoist_apis.pop(ics_token.lower())

    sync_thread = threading.Thread(target=sync_everything)
    sync_thread.start()
    print ("Running Todoist-ICS on {}:{} with {} tokens ...".format(webserver_host, webserver_port, len(todoist_apis)))
    bottle.run(host=webserver_host, port=webserver_port, quiet=True)
    
