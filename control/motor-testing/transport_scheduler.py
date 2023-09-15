import moteus
from typing import List, Dict
from scheduled_object import ScheduledObject

class TransportScheduler:
    objects: List[ScheduledObject]
    transport: moteus.Fdcanusb
    status: List[Dict]

    def __init__(self) -> None:
        self.transport = moteus.get_singleton_transport()
        self.objects = []
        self.status = []

    def add_object(self, obj: ScheduledObject) -> None:
        self.objects.append(obj)
        self.status.append(dict())

    def update(self) -> None:
        commands_list = [obj.get_scheduled_command() for obj in self.objects]
        self.status = self.transport.cycle(
            commands_list
        )
        for pos, obj in enumerate(self.objects):
            obj.update_state(self.status[pos])
