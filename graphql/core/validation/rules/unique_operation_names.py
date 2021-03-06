from ...error import GraphQLError
from .base import ValidationRule


class UniqueOperationNames(ValidationRule):
    def __init__(self, context):
        super(UniqueOperationNames, self).__init__(context)
        self.known_operation_names = {}

    def enter_OperationDefinition(self, node, key, parent, path, ancestors):
        operation_name = node.name
        if not operation_name:
            return

        if operation_name.value in self.known_operation_names:
            return GraphQLError(
                self.duplicate_operation_name_message(operation_name.value),
                [self.known_operation_names[operation_name.value], operation_name]
            )

        self.known_operation_names[operation_name.value] = operation_name

    @staticmethod
    def duplicate_operation_name_message(operation_name):
        return 'There can only be one operation named "{}".'.format(operation_name)
