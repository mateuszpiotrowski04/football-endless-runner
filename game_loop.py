from ursina import Entity, camera, time, Text, color, invoke
from settings import WORLD_SPEED
from goal import FinaleGoal, GOAL_DISTANCE

class GameLoop(Entity):
    def __init__(self, player_ref, obstacle_manager_ref):
        super().__init__()
        self.player = player_ref
        self.obstacle_manager = obstacle_manager_ref

        self.score = 0.0
        self.WIN_SCORE = 10

        self.preparing_finale = False
        self.is_finale = False
        self.goal_entity = None
        self.power = 0.0
        self.shot_fired = False

        self.goal_entity = FinaleGoal(self.player, self.trigger_win)

        self.score_display = Text(
            text='0 pkt',
            parent=camera.ui,
            position=(-0.55, 0.45),
            scale=1.7,
            color=color.black,
            origin=(0, 0)
        )

    def update(self):
        if self._handle_game_over_state(): return
        if not self.player.game_started: return

        self._handle_normal_run_logic()

        if self.is_finale or self.preparing_finale:
            self._handle_finale_logic()

        self.obstacle_manager.update()

    def _handle_game_over_state(self):
        if self.player.game_over:
            if not self.player.ui_ref.end_menu.enabled:
                self.player.ui_ref.show_game_over(self.score)
                self.score_display.enabled = False
                self.player.ui_ref.hide_power_bar()
            return True
        return False

    def _handle_normal_run_logic(self):
        if not self.is_finale or (self.goal_entity.z - self.player.z) > GOAL_DISTANCE:
            self.score += time.dt * WORLD_SPEED * 0.1
            self.score_display.text = f'{int(self.score)} pkt'
            self.check_technical_bonus()

        if self.score >= self.WIN_SCORE and not self.preparing_finale:
            self.preparing_finale = True
            self.obstacle_manager.can_spawn = False

    def _handle_finale_logic(self):
        if self.preparing_finale and not self.is_finale:
            if len(self.obstacle_manager.active_obstacles) == 0:
                self.trigger_finale()

        if self.is_finale and not self.shot_fired and self.goal_entity:
            distance_to_goal = self.goal_entity.z - self.player.z

            if distance_to_goal <= GOAL_DISTANCE:
                if self.power == 0:
                    self.player.model3d.stop()

                self.power += time.dt * 0.65

                if self.power > 1.01:
                    self.power = 1.01

                self.player.ui_ref.update_power_bar(self.power)

    def check_technical_bonus(self):
        for obs in self.obstacle_manager.active_obstacles:
            if obs.z < self.player.z and not obs.scored:
                if abs(obs.x - self.player.x) < 0.5:
                    if (obs.type == 'up' and self.player.is_jumping) or (obs.type == 'down' and self.player.is_crouching):
                        self.player.ui_ref.show_bonus_popup()
                        invoke(self.add_bonus_points, delay=1.3)
                obs.scored = True

    def add_bonus_points(self):
        self.score += 10

    def input(self, key):
        if self.is_finale and not self.shot_fired and not self.player.game_over:
            if self.goal_entity and (self.goal_entity.z - self.player.z) <= GOAL_DISTANCE:
                if key == 'left arrow':
                    self.execute_shot('left')
                elif key == 'up arrow':
                    self.execute_shot('center')
                elif key == 'right arrow':
                    self.execute_shot('right')

    def trigger_finale(self):
        self.is_finale = True
        self.preparing_finale = False
        self.shot_fired = False
        self.power = 0.0
        self.player.in_finale = True
        self.player.move_to_center()
        self.goal_entity.reset_goal()

    def execute_shot(self, direction):
        self.shot_fired = True
        self.player.ui_ref.hide_power_bar()

        self.player.model3d.stop()

        if direction == 'left': target_x = -2
        elif direction == 'right': target_x = 2
        else: target_x = 0

        if self.power >= 1.0:
            target_y = 5.0
            target_z = self.goal_entity.z + 10
            base_outcome = 'miss'

        elif self.power <= 0.33:
            target_y = 0.2
            target_z = self.goal_entity.z - 15
            base_outcome = 'weak'

        else:
            target_y = 2.0 if self.power > 0.66 else 0.2
            target_z = self.goal_entity.z - 3.2
            base_outcome = 'on_target'

        self.player.ball_attached = False

        self.player.shoot((target_x, target_y, target_z), base_outcome)
        invoke(self.verify_shot, target_x, base_outcome, delay=0.4)

    def verify_shot(self, target_x, base_outcome):
        if base_outcome == 'miss' or base_outcome == 'weak':
            self.player.model3d.loop('Defeat')
            invoke(self.show_end_screen, delay=2)
            return

        if target_x == self.goal_entity.goalkeeper.x:
            self.player.shot_outcome = 'save'
            self.player.post_vel_y = 2.0 if self.player.ball.y > 1.0 else 3.5
            self.player.post_vel_z = -8.0

            self.player.model3d.loop('Defeat')
            invoke(self.show_end_screen, delay=2)
        else:
            self.player.shot_outcome = 'goal'
            self.player.post_vel_z = 15.0

            self.player.model3d.loop('PickUp')
            invoke(self.trigger_win, delay=2)

    def start_game(self):
        self.player.game_started = True
        self.player.model3d.loop('Run')

    def restart_game(self):
        self.player.reset_player()

        # czyszczenie przeszkód
        for obs in self.obstacle_manager.active_obstacles:
            obs.enabled = False
        self.obstacle_manager.active_obstacles.clear()

        self.obstacle_manager.enabled = True
        self.obstacle_manager.can_spawn = True

        # reset punktów
        self.score = 0
        self.score_display.text = '0 pkt'
        self.score_display.enabled = True

        # przejecie kontroli
        self.player.ui_ref.end_menu.enabled = False
        self.player.ui_ref.bg_panel.enabled = False

        self.is_finale = False
        self.preparing_finale = False
        self.shot_fired = False

        self.goal_entity.reset_goal()
        self.goal_entity.enabled = False

    def reset_to_menu(self):
        self.restart_game()

        self.player.game_started = False
        self.player.model3d.stop()

        self.player.ui_ref.show_start_menu()

    def trigger_win(self):
        self.player.game_started = False
        self.player.ui_ref.show_win_screen(self.score)
        self.score_display.enabled = False

    def show_end_screen(self):
        self.player.game_over = True
        self.player.ui_ref.show_game_over(self.score)
        self.score_display.enabled = False