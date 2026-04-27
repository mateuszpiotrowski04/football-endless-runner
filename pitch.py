from ursina import Entity, color

class Pitch:
    def __init__(self):
        self.ground = Entity(
            model='plane',
            scale=(7, 1, 100),
            color=color.green
        )