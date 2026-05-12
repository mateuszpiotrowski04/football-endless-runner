from ursina import Entity, invoke, time
import random
from settings import LANES, color, WORLD_SPEED


class ObstacleManager:
    def __init__(self, player_ref):
        self.player = player_ref
        self.active_obstacles = []
        self.pool = []
        self.pre_warm_pool()
        self.spawn_obstacle_loop()

    def pre_warm_pool(self):
        types = ["wall", "up", "down"]
        for target_type in types:
            for _ in range(4):
                self.create_new_obstacles(target_type)

    def create_new_obstacles(self, target_type):
        obs = Entity(model='cube', color=color.clear, scale=(1, 1, 1), collider='box', enabled=False)

        # postać z muru piłkarskiego
        if target_type == "wall":
            obs.model3d = base.loader.loadModel('assets/training wall.glb')
            obs.model3d.reparentTo(obs)
            obs.model3d.setScale(1.4, 1.0, 1.4)
            obs.model3d.setPos(0, -0.1, 0)

        # płotek
        elif target_type == "up":
            obs.model3d = base.loader.loadModel('assets/hurdle up.glb')
            obs.model3d.reparentTo(obs)
            obs.model3d.setScale(0.8, 0.8, 0.8)
            obs.model3d.setPos(0, 0.15, 0)

        # tyczki
        else:
            obs.model3d = base.loader.loadModel('assets/poles down.glb')
            obs.model3d.reparentTo(obs)
            obs.model3d.setScale(1, 0.9, 1.2)
            obs.model3d.setPos(0, -0.45, 0)

        obs.type = target_type
        self.pool.append(obs)
        return obs

    def spawn_obstacle(self):
        if self.player.game_over: return
        x_pos = random.choice(LANES)
        obs_type = random.choice([0, 1, 2])

        if obs_type == 0:
            target_type = "wall"
            y_pos = 1
        elif obs_type == 1:
            target_type = "up"
            y_pos = 0.25
        else:
            target_type = "down"
            y_pos = 1.25

        obs = next((o for o in self.pool if o.type == target_type and not o.enabled), None)

        if not obs:
            obs = self.create_new_obstacles(target_type)

        obs.x = x_pos
        obs.y = y_pos
        obs.z = 50
        obs.scored = False
        obs.enabled = True

        self.active_obstacles.append(obs)

    def spawn_obstacle_loop(self):
        if self.player.game_started and not self.player.game_over:
            self.spawn_obstacle()

        invoke(self.spawn_obstacle_loop, delay=0.8)

    def update(self):
        if not self.player.game_started or self.player.game_over: return

        for obs in self.active_obstacles[:]:
            obs.z -= WORLD_SPEED * time.dt

            # kolizja
            if self.player.intersects(obs).hit:
                self.player.trigger_game_over()

            # ukrywanie przeszków
            elif obs.z < -30:
                obs.enabled = False
                self.active_obstacles.remove(obs)