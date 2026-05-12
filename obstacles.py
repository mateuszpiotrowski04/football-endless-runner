from ursina import Entity, invoke, destroy, time
import random
from settings import LANES, color, WORLD_SPEED


class ObstacleManager:
    def __init__(self, player_ref):
        self.player = player_ref
        self.obstacles = []
        self.spawn_obstacle_loop()

    def spawn_obstacle(self):
        if self.player.game_over: return
        x_pos = random.choice(LANES)
        obs_type = random.choice([0, 1, 2])

        # postać z muru piłkarskiego
        if obs_type == 0:
            obs = Entity(model='cube', color=color.clear, scale=(1, 1, 1), x=x_pos, y=1, z=50, collider='box')

            obs.model3d = base.loader.loadModel('assets/mur_pilkarski.glb')
            obs.model3d.reparentTo(obs)
            obs.model3d.setScale(1.4, 1.0, 1.4)
            obs.model3d.setPos(0, -0.1, 0)
            obs.type = "wall"

        # płotek
        elif obs_type == 1:
            obs = Entity(model='cube', color=color.clear, scale=(1, 1, 1), x=x_pos, y=0.25, z=50, collider='box')

            obs.model3d = base.loader.loadModel('assets/plotek.glb')
            obs.model3d.reparentTo(obs)
            obs.model3d.setScale(0.8, 0.8, 0.8)
            obs.model3d.setPos(0, 0.15, 0)
            obs.type = "up"

        # tyczki
        else:
            obs = Entity(model='cube', color=color.clear, scale=(1, 1, 1), x=x_pos, y=1.25, z=50, collider='box')

            obs.model3d = base.loader.loadModel('assets/tyczki.glb')
            obs.model3d.reparentTo(obs)
            obs.model3d.setScale(1, 0.9, 1.2)
            obs.model3d.setPos(0, -0.45, 0)
            obs.type = "down"

        obs.scored = False
        self.obstacles.append(obs)

    def spawn_obstacle_loop(self):
        if self.player.game_started and not self.player.game_over:
            self.spawn_obstacle()

        invoke(self.spawn_obstacle_loop, delay=0.8)

    def update(self):
        if not self.player.game_started or self.player.game_over: return

        for obs in self.obstacles[:]:
            obs.z -= WORLD_SPEED * time.dt

            # kolizja
            if self.player.intersects(obs).hit:
                self.player.trigger_game_over()

            # usuwanie przeszków
            elif obs.z < -30:
                if hasattr(obs, 'model3d'):
                    obs.model3d.removeNode()

                destroy(obs)
                self.obstacles.remove(obs)