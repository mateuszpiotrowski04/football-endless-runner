from ursina import Entity, invoke, destroy, time, color
import random
from settings import *


class ObstacleManager:
    def __init__(self, player_ref):
        self.player = player_ref
        self.obstacles = []
        self.spawn_obstacle_loop()

    def spawn_obstacle(self):
        if self.player.game_over: return
        x_pos = random.choice(LANES)
        obs_type = random.choice([0, 1, 2])

        if obs_type == 0:
            obs = Entity(model='cube', color=color.red, scale=(1, 2, 1), x=x_pos, y=1, z=50, collider='box')
        elif obs_type == 1:
            obs = Entity(model='cube', color=color.orange, scale=(1, 0.5, 1), x=x_pos, y=0.25, z=50, collider='box')
        else:
            obs = Entity(model='cube', color=color.yellow, scale=(1, 0.5, 1), x=x_pos, y=1.25, z=50, collider='box')

        self.obstacles.append(obs)

    def spawn_obstacle_loop(self):
        if not self.player.game_over:
            self.spawn_obstacle()
            invoke(self.spawn_obstacle_loop, delay=0.8)

    def update(self):
        if self.player.game_over: return

        for obs in self.obstacles[:]:
            obs.z -= WORLD_SPEED * time.dt

            if self.player.intersects(obs).hit:
                self.player.trigger_game_over()
            elif obs.z < -30:
                destroy(obs)
                self.obstacles.remove(obs)