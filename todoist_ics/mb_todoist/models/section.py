from ..exceptions import InvalidInputDict

class Section:
    required_keys = [
                "id", "name", "project_id", "section_order", "collapsed",
                "sync_id", "is_deleted", "is_archived", "archived_at",
                "added_at"
            ]

    def __init__(self, section: dict):
        # Check if all required_keys all present
        if not all(key in section.keys() for key in self.required_keys):
            raise InvalidInputDict

        # Save all values to object
        self.id = section['id']
        self.name = section['name']
        self.project_id = section['project_id']
        self.section_order = section['section_order']
        self.collapsed = section['collapsed']
        self.sync_id = section['sync_id'] if section['sync_id'] != "null" else None
        self.is_deleted = section['is_deleted']
        self.is_archived = section['is_archived'] if section['is_archived'] != "null" else None
        self.added_at = section['added_at']

    def __repr__(self):
        return f"Section(id={self.id}, name={self.name})"

    def __eq__(self, other):
        if isinstance(other, Section):
            if self.id == other.id:
                return True

        return False
