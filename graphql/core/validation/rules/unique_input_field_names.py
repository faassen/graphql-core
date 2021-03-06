from ...error import GraphQLError
from .base import ValidationRule


class UniqueInputFieldNames(ValidationRule):
    def __init__(self, context):
        super(UniqueInputFieldNames, self).__init__(context)
        self.known_names = {}

    def enter_ObjectValue(self, node, key, parent, path, ancestors):
        self.known_names = {}

    def enter_ObjectField(self, node, key, parent, path, ancestors):
        field_name = node.name.value
        if field_name in self.known_names:
            return GraphQLError(
                self.duplicate_input_field_message(field_name),
                [self.known_names[field_name], node.name]
            )

        self.known_names[field_name] = node.name

    @staticmethod
    def duplicate_input_field_message(field_name):
        return 'There can only be one input field named "{}".'.format(field_name)
