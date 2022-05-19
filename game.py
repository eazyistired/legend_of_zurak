from overworld import Overworld
from level import Level


class Game:
    def __init__(self, surface):
        self.max_level = 0
        self.display_surface = surface
        self.overworld = Overworld(0, self.max_level, self.display_surface, self.create_level)
        self.status = 'overworld'

    def create_level(self, current_level):
        self.status = 'level'
        self.level = Level(current_level, self.display_surface, self.create_overworld)

    def create_overworld(self, current_level, new_max_level):
        self.status = 'overworld'
        if new_max_level > self.max_level:
            self.max_level = new_max_level
        self.overworld = Overworld(current_level, self.max_level, self.display_surface, self.create_level)

    def run(self):
        if self.status == 'overworld':
            self.overworld.run()
        else:
            self.level.run()
