from ursina import Entity, invoke, time, duplicate
import random
from settings import LANES, color


class ObstacleManager:
    def __init__(self, player_ref):
        self.player = player_ref
        self.main_loop = None
        self.active_obstacles = []
        self.pool = []
        self.can_spawn = True

        self.base_wall = Entity(model='training wall', scale=(1.4, 1.0, 1.4), y=-0.1, enabled=False)
        self.base_up = Entity(model='hurdle up', scale=(0.8, 0.8, 0.8), y=0.15, enabled=False)
        self.base_down = Entity(model='poles down', scale=(1, 0.9, 1.2), y=-0.45, enabled=False)

        self.pre_warm_pool()
        self.spawn_obstacle_loop()

    def pre_warm_pool(self):
        types = ["wall", "up", "down"]
        for target_type in types:
            for _ in range(8):
                self.create_new_obstacles(target_type)

    def create_new_obstacles(self, target_type):
        obs = Entity(model='cube', color=color.clear, scale=(1, 1, 1), collider='box', enabled=False)
        obs.visual = Entity(parent=obs)

        # postać z muru piłkarskiego
        if target_type == "wall":
            obs.model3d = duplicate(self.base_wall)
        # płotek
        elif target_type == "up":
            obs.model3d = duplicate(self.base_up)
        # tyczki
        else:
            obs.model3d = duplicate(self.base_down)

        obs.model3d.parent = obs.visual
        obs.model3d.enabled = True

        obs.type = target_type
        self.pool.append(obs)
        return obs

    def spawn_single_obstacle(self, lane_index, target_type):
        if target_type == "wall":
            y_pos = 1.0
        elif target_type == "up":
            y_pos = 0.25
        else:
            y_pos = 1.25

        obs = next((o for o in self.pool if o.type == target_type and not o.enabled), None)

        if not obs:
            obs = self.create_new_obstacles(target_type)

        obs.x = LANES[lane_index]
        obs.y = y_pos
        obs.z = 120
        obs.scored = False
        obs.enabled = True

        self.active_obstacles.append(obs)

    def spawn_formation(self):
        level = self.main_loop.current_level
        types = ["wall", "up", "down"]

        rand_val = random.random()

        # pojedyncze przeszkody
        if level == 1:
            self.spawn_single_obstacle(random.randint(0, 2), random.choice(types))

        # pojedyncze lub podwójne ten sam typ
        elif level == 2:
            if rand_val < 0.3:
                empty_lane = random.randint(0, 2)
                obs_type = random.choice(types)
                for i in range(3):
                    if i != empty_lane:
                        self.spawn_single_obstacle(i, obs_type)
            else:
                self.spawn_single_obstacle(random.randint(0, 2), random.choice(types))

        # pojedyncze, podwójne lub mieszane
        else:
            if rand_val < 0.4:
                self.spawn_single_obstacle(random.randint(0, 2), random.choice(types))

            elif rand_val < 0.8:
                empty_lane = random.randint(0, 2)
                obs_type = random.choice(types)
                for i in range(3):
                    if i != empty_lane:
                        self.spawn_single_obstacle(i, obs_type)
            else:
                empty_lane = random.randint(0, 2)
                type1 = random.choice(types)
                type2 = random.choice([t for t in types if t != type1])
                lanes_to_fill = [i for i in range(3) if i != empty_lane]

                self.spawn_single_obstacle(lanes_to_fill[0], type1)
                self.spawn_single_obstacle(lanes_to_fill[1], type2)

    def spawn_obstacle_loop(self):
        if not self.main_loop:
            invoke(self.spawn_obstacle_loop, delay=0.1)
            return

        delay = self.main_loop.spawn_rate

        if self.player.game_started and not self.player.game_over and self.can_spawn:
            self.spawn_formation()

        invoke(self.spawn_obstacle_loop, delay=delay)

    def update(self):
        if not self.player.game_started or self.player.game_over: return

        for obs in self.active_obstacles[:]:
            obs.z -= self.main_loop.current_speed * time.dt

            # kolizja
            if self.player.intersects(obs).hit:
                self.player.trigger_game_over()

            # ukrywanie przeszków
            elif obs.z < -30:
                obs.enabled = False
                self.active_obstacles.remove(obs)