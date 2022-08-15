import os
import bottle
import todoist
import isodate
import json
from pytz import timezone
from ics import Calendar, Event
from dotenv import load_dotenv

todoist_apis = {}

@bottle.route('/ics/<ics_token>.ics')
def return_ics(ics_token):
    global todoist_apis
    todoist_api = todoist_apis.get(ics_token.lower())

    ics = Calendar()

    if todoist_api is None:
        return u'{}'.format(ics.serialize())

    todoist_api.sync()

    labels = {label['id']: label['name'] for label in todoist_api.state['labels']}
    tasks = [item for item in todoist_api.state['items'] if item['due'] is not None]

    for task in tasks:
        if 'T' in task['due']['date']:
            datetime = isodate.parse_datetime(task['due']['date'])
            datetime = datetime.replace(tzinfo=timezone(os.environ.get("ICS_TIMEZONE", "UTC")))
            date = isodate.parse_date(task['due']['date'])

            duration = None
            try:
                duration = isodate.parse_duration(os.environ.get("ICS_DEFAULT_DURATION", "PT1H"))
            except Exception:
                duration = isodate.parse_duration("PT1H")

            for label_id in task['labels']:
                try:
                    duration = isodate.parse_duration(labels[label_id])
                except Exception:
                    pass

            task_event = Event()
            task_event.name = ("☒" if task['checked'] else "☐") + " " + task['content']
            task_event.begin = datetime
            task_event.duration = duration
            task_event.description = task['description']
            ics.events.add(task_event)
        else:
            date = isodate.parse_date(task['due']['date'])
            task_event = Event()
            task_event.name = task['content']
            task_event.begin = date
            task_event.make_all_day()
            task_event.description = task['description']
            ics.events.add(task_event)

    return u'{}'.format(ics.serialize())

def run():
    load_dotenv()
    
    todoist_tokens = json.loads(os.environ.get("TODOIST_TOKENS", "{}"))
    print ("Todoist API tokens loaded: {}".format(len(todoist_tokens)))

    webserver_host = os.environ.get("WEBSERVER_HOST", "127.0.0.1")
    webserver_port = int(os.environ.get("WEBSERVER_PORT", 8080))

    global todoist_apis

    for ics_token, api_token in todoist_tokens.items():
        todoist_apis[ics_token.lower()] = todoist.TodoistAPI(api_token)
        todoist_apis[ics_token.lower()].sync()

        if todoist_apis[ics_token.lower()].state['user'] == {}:
            print ("ERROR! Wrong TODOIST_TOKEN!")
            exit(2)

    print ("Running Todoist-ICS on {}:{} ...".format(webserver_host, webserver_port))
    bottle.run(host=webserver_host, port=webserver_port, quiet=True)
    
