import uuid
from Components import Component


class Entity:

    def __init__(self):
        self.__id = uuid.uuid4()
        self.__components = {}

    def add_component(self, component: Component):
        self.__components[component.__class__] = component

    def get_component(self, component) -> Component:
        return self.__components.get(component)

    def remove_component(self, component_name: str):
        if component_name in self.__components.keys():
            del self.__components[component_name]
