from ursina import Entity, color, time, curve
import random

GOAL_DISTANCE = 35

class FinaleGoal(Entity):
    def __init__(self, player_ref, main_loop_ref, win_callback):
        super().__init__()
        self.player = player_ref
        self.main_loop = main_loop_ref
        self.win_callback = win_callback
        self.enabled = False
        self.z = 120

        # bramka
        self.goal = Entity(
            parent=self,
            model='goal',
            scale=(1.1, 1.3, 1.1),
            y=-0.2
        )

        # bramkarz
        self.goalkeeper = Entity(
            parent=self,
            model='training wall',
            scale=(1.5, 1.2, 1.5),
            y=1.05,
            z=-2.0,
            color=color.red,
            collider='box'
        )

        self.lanes = [-2, 0, 2]
        self.current_lane_index = 1
        self.goalkeeper.x = self.lanes[self.current_lane_index]
        self.move_timer = self.main_loop.gk_interval

    def update(self):
        if not self.player.game_started or self.player.game_over: return

        distance = self.z - self.player.z

        if distance > GOAL_DISTANCE:
            self.z -= self.main_loop.current_speed * time.dt

        self.move_timer -= time.dt
        if self.move_timer <= 0:
            decision = random.choice([-1, 0, 1])
            self.current_lane_index += decision
            self.current_lane_index = max(0, min(2, self.current_lane_index))

            target_x = self.lanes[self.current_lane_index]

            anim_duration = self.main_loop.gk_interval * 0.5
            self.goalkeeper.animate_x(target_x, duration=anim_duration, curve=curve.out_sine)

            self.move_timer = self.main_loop.gk_interval

    def reset_goal(self):
        self.z = 120
        self.current_lane_index = 1
        self.goalkeeper.x = self.lanes[self.current_lane_index]
        self.move_timer = self.main_loop.gk_interval
        self.enabled = True