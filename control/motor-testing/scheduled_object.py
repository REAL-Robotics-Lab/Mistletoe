import moteus
from typing import List, Dict
import traceback

class ScheduledObject:
    current_command: moteus.Command

    def update_state(state: Dict) -> None:
        """Update the state of the object after the command has run.
        """
        print("Override me!")
        pass

    def get_scheduled_command(self):
        return self.current_command
    
    def schedule(self, command: moteus.Command) -> None:
        self.current_command = command