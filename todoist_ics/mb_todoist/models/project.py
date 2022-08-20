from ..exceptions import InvalidInputDict

class Project:
    required_keys = [
                "id", "name", "color", "parent_id", "child_order", "collapsed",
                "shared", "is_deleted", "is_archived", "sync_id", "view_style"
            ]

    def __init__(self, project: dict):
        # Check if all required_keys all present
        if not all(key in project.keys() for key in self.required_keys):
            raise InvalidInputDict

        # Save all values to object
        self.id = project["id"]
        self.name = project["name"]
        self.color = project["color"]
        self.parent_id = project["parent_id"] if project["parent_id"] != "null" else None
        self.child_order = project["child_order"]
        self.collapsed = project["collapsed"]
        self.shared = project["shared"]
        self.is_deleted = project["is_deleted"]
        self.is_archived = project["is_archived"]
        self.sync_id = project["sync_id"] if project["sync_id"] != "null" else None
        self.view_style = project["view_style"]
        self.inbox_project = project.get("inbox_project", False)
        self.team_inbox = project.get("team_inbox", False)  

    def __repr__(self):
        return f"Project(id={self.id}, name={self.name})"

    def __eq__(self, other):
        if isinstance(other, Project):
            if self.id == other.id:
                return True

        return False
