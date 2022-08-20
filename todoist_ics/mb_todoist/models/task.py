from ..exceptions import InvalidInputDict

class Task:
    required_keys = [
                "id", "user_id", "project_id", "content", "description",
                "due", "priority", "parent_id", "child_order", "section_id",
                "collapsed", "labels", "added_by_uid",
                "assigned_by_uid", "responsible_uid", "checked", "is_deleted",
                "sync_id", "completed_at", "added_at"
            ]

    def __init__(self, task: dict):
        # Check if all required_keys all present
        if not all(key in task.keys() for key in self.required_keys):
            raise InvalidInputDict

        # Save all values to object
        self.id = task['id']
        self.user_id = task['user_id']
        self.project_id = task['project_id']
        self.content = task['content']
        self.description = task['description']
        self.due = task['due']
        self.priority = task['priority']
        self.parent_id = task['parent_id'] if task['parent_id'] != "null" else None
        self.child_order = task['child_order']
        self.section_id = task['section_id'] if task['section_id'] != "null" else None
        self.day_order = task.get('day_order', None)
        self.collapsed = task['collapsed']
        self.labels = task['labels']
        self.added_by_uid = task['added_by_uid']
        self.assigned_by_uid = task['assigned_by_uid']
        self.responsible_uid = task['responsible_uid']
        self.checked = task['checked']
        self.is_deleted = task['is_deleted']
        self.sync_id = task['sync_id'] if task['sync_id'] != "null" else None
        self.completed_at = task['completed_at'] if task['completed_at'] != "null" else None
        self.added_at = task['added_at']

    def __repr__(self):
        return f"Task(id={self.id}, name={self.content}, checked={self.checked})"

    def __eq__(self, other):
        if isinstance(other, Task):
            if self.id == other.id:
                return True

        return False
