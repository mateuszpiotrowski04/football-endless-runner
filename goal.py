from ursina import Entity, color, time, curve
import random
from settings import WORLD_SPEED

GOAL_DISTANCE = 35

class FinaleGoal(Entity):
    def __init__(self, player_ref, win_callback):
        super().__init__()
        self.player = player_ref
        self.win_callback = win_callback

        self.z = 60

        # bramka
        Entity(parent=self, model='cube', scale=(0.2, 3, 0.2), x=-3, y=1.5, color=color.white)
        Entity(parent=self, model='cube', scale=(0.2, 3, 0.2), x=3, y=1.5, color=color.white)
        Entity(parent=self, model='cube', scale=(6.2, 0.2, 0.2), y=3, color=color.white)
        Entity(parent=self, model='quad', scale=(6, 3), z=2, y=1.5, color=color.rgba(100, 150, 255, 100))

        # bramkarz
        self.dummy = Entity(parent=self, model='cube', scale=(2, 2, 0.5), y=1, color=color.red, collider='box')

        self.lanes = [-2, 0, 2]
        self.current_lane_index = 1
        self.dummy.x = self.lanes[self.current_lane_index]
        self.move_timer = 0.5

    def update(self):
        if not self.player.game_started or self.player.game_over: return

        distance = self.z - self.player.z

        if distance > GOAL_DISTANCE:
            self.z -= WORLD_SPEED * time.dt

        self.move_timer -= time.dt
        if self.move_timer <= 0:
            decision = random.choice([-1, 0, 1])
            self.current_lane_index += decision
            self.current_lane_index = max(0, min(2, self.current_lane_index))

            target_x = self.lanes[self.current_lane_index]
            self.dummy.animate_x(target_x, duration=0.25, curve=curve.out_sine)

            self.move_timer = 0.5