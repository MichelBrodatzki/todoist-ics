from ..exceptions import InvalidInputDict

class Label:
    required_keys = [
                "id", "name", "color", "item_order", "is_deleted", "is_favorite"
            ]

    def __init__(self, label: dict):
        # Check if all required_keys all present
        if not all(key in label.keys() for key in self.required_keys):
            raise InvalidInputDict

        # Save all values to object
        self.id = label['id']
        self.name = label['name']
        self.color = label['color']
        self.item_order = label['item_order']
        self.is_deleted = label['is_deleted']
        self.is_favorite = label['is_favorite']

    def __repr__(self):
        return f"Label(id={self.id}, name={self.name})"

    def __eq__(self, other):
        if isinstance(other, Label):
            if self.id == other.id:
                return True

        return False
