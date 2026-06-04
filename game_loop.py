from ursina import Entity, camera, time, lerp, Text, color, curve, destroy, invoke
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

        self.ball_start_pos = None
        self.ball_target_pos = None
        self.ball_flight_timer = 0.0

        self.score_display = Text(
            text='0 pkt',
            parent=camera.ui,
            position=(-0.55, 0.45),
            scale=1.7,
            color=color.black,
            origin=(0, 0)
        )

    def update(self):
        # kamera - śledzenie gracza
        camera.x = lerp(camera.x, self.player.x, time.dt * 10)
        camera.y = lerp(camera.y, self.player.y + 1.5, time.dt * 10)
        camera.z = self.player.z - 10

        if self.handle_game_over_state(): return

        if not self.player.game_started: return

        if self.is_finale or self.preparing_finale:
            self.handle_finale_logic()
        else:
            self.handle_normal_run_logic()

        # animacja lotu piłki
        if not self.player.ball_attached and self.ball_target_pos:
            self.ball_flight_timer += time.dt / 0.4
            if self.ball_flight_timer > 1.0:
                self.ball_flight_timer = 1.0

            curr_x = lerp(self.ball_start_pos[0], self.ball_target_pos[0], self.ball_flight_timer)
            curr_y = lerp(self.ball_start_pos[1], self.ball_target_pos[1], self.ball_flight_timer)
            curr_z = lerp(self.ball_start_pos[2], self.ball_target_pos[2], self.ball_flight_timer)

            self.player.ball.setPos(curr_x, curr_y, curr_z)

        self.obstacle_manager.update()

    def handle_game_over_state(self):
        if self.player.game_over:
            if not self.player.ui_ref.end_menu.enabled:
                self.player.ui_ref.show_game_over(self.score)
                self.score_display.enabled = False
                self.player.ui_ref.hide_power_bar()
            return True
        return False

    def handle_normal_run_logic(self):
        self.score += time.dt * WORLD_SPEED * 0.1
        self.check_technical_bonus()
        self.score_display.text = f'{int(self.score)} pkt'

        if self.score >= self.WIN_SCORE and not self.preparing_finale:
            self.preparing_finale = True
            self.obstacle_manager.can_spawn = False

    def handle_finale_logic(self):
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
                    if (obs.type == 'up' and self.player.is_jumping) or \
                            (obs.type == 'down' and self.player.is_crouching):
                        self.trigger_bonus_ui()
                        obs.scored = True
                obs.scored = True

    def input(self, key):
        if self.is_finale and not self.shot_fired and not self.player.game_over:
            if self.goal_entity and (self.goal_entity.z - self.player.z) <= 35.1:
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
        self.goal_entity = FinaleGoal(self.player, self.trigger_win)

    def execute_shot(self, direction):
        self.shot_fired = True
        self.player.ui_ref.hide_power_bar()

        self.player.model3d.stop()

        target_x = -2 if direction == 'left' else (2 if direction == 'right' else 0)

        if self.power >= 1.0:
            target_y = 5.0
            target_z = self.goal_entity.z + 10
            is_goal_possible = False

        elif self.power <= 0.33:
            target_y = 0.2
            target_z = self.goal_entity.z - 15
            is_goal_possible = False

        elif self.power <= 0.66:
            target_y = 0.2
            target_z = self.goal_entity.z + 2
            is_goal_possible = True

        else:
            target_y = 2.0
            target_z = self.goal_entity.z + 2
            is_goal_possible = True

        self.player.ball_attached = False

        self.ball_start_pos = (self.player.ball.getX(), self.player.ball.getY(), self.player.ball.getZ())
        self.ball_target_pos = (target_x, target_y, target_z)
        self.ball_flight_timer = 0.0

        invoke(self.verify_shot, target_x, is_goal_possible, delay=0.4)

    def verify_shot(self, target_x, is_goal_possible):
        murek_x = self.goal_entity.dummy.x

        if not is_goal_possible or target_x == murek_x:
            self.player.model3d.loop('Defeat')
            invoke(self.show_end_screen, delay=2)
        else:
            self.player.model3d.loop('PickUp')
            invoke(self.trigger_win, delay=2)

    def trigger_bonus_ui(self):
        bonus_popup = Text(
            text='+10 pkt',
            parent=camera.ui,
            position=(-0.55, 0.4),
            scale=1.7,
            color=color.black,
            origin=(0, 0)
        )

        bonus_popup.animate_scale(1.2, duration=0.2, curve=curve.out_back)

        invoke(self.animate_bonus_away, bonus_popup, delay=1.0)

    def animate_bonus_away(self, popup):
        popup.animate_position((-0.55, 0.45), duration=0.3, curve=curve.in_sine)

        popup.animate_color(color.clear, duration=0.3)

        invoke(self.add_bonus_points, delay=0.3)
        invoke(destroy, popup, delay=0.3)

    def add_bonus_points(self):
        self.score += 10

    def start_game(self):
        self.player.game_started = True
        self.player.model3d.loop('Run')

    def restart_game(self):
        # restart gracza
        self.player.x = 0
        self.player.y = 0.5
        self.player.z = -20
        self.player.rotation = (0, 0, 0)
        self.player.model3d.setH(180)
        self.player.current_lane = 1

        self.player.is_jumping = False
        self.player.is_crouching = False
        self.player.game_over = False
        self.player.game_started = True
        self.player.in_finale = False

        self.player.ball_attached = True

        self.player.model3d.stop()
        self.player.model3d.loop('Run')

        # czyszczenie przeszkód
        for obs in self.obstacle_manager.active_obstacles:
            obs.enabled = False
        self.obstacle_manager.active_obstacles.clear()

        self.obstacle_manager.enabled = True
        self.obstacle_manager.can_spawn = True
        self.obstacle_manager.spawn_timer = 0

        # reset punktów
        self.score = 0
        self.score_display.text = '0 pkt'
        self.score_display.enabled = True

        # przejecie kontroli
        self.player.ui_ref.end_menu.enabled = False
        self.player.ui_ref.bg_panel.enabled = False

        # Resetowanie Finału
        self.is_finale = False
        self.preparing_finale = False
        self.shot_fired = False

        if self.goal_entity:
            destroy(self.goal_entity)
            self.goal_entity = None

        time.dt = 0

    def reset_to_menu(self):
        self.restart_game()

        self.player.game_started = False
        self.player.model3d.stop()

        self.player.ui_ref.show_start_menu()

    def delayed_game_over(self):
        self.player.trigger_game_over()

    def trigger_win(self):
        self.player.game_started = False
        self.player.ui_ref.show_win_screen(self.score)
        self.score_display.enabled = False

    def show_end_screen(self):
        self.player.game_over = True
        self.player.ui_ref.show_game_over(self.score)
        self.score_display.enabled = False