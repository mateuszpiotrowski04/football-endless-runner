from ursina import Entity, camera, time, lerp, Text, color, curve, destroy, invoke
from settings import WORLD_SPEED

class GameLoop(Entity):
    def __init__(self, player_ref, obstacle_manager_ref):
        super().__init__()
        self.player = player_ref
        self.obstacle_manager = obstacle_manager_ref

        self.score = 0.0

        self.score_display = Text(
            text='0 pkt',
            parent=camera.ui,
            position=(-0.55, 0.45),
            scale=1.7,
            color=color.black,
            origin=(0, 0)
        )

    def update(self):
        if self.player.game_over:
            if hasattr(self.player, 'ui_ref') and not self.player.ui_ref.end_menu.enabled:
                self.player.ui_ref.show_game_over(self.score)
                self.score_display.enabled = False
            return

        # kamera - śledzenie gracza
        camera.x = lerp(camera.x, self.player.x, time.dt * 10)
        camera.y = lerp(camera.y, self.player.y + 1.5, time.dt * 10)
        camera.z = self.player.z - 10

        if not self.player.game_started: return

        # punkty
        self.score += time.dt * WORLD_SPEED * 0.1

        self.check_technical_bonus()

        self.score_display.text = f'{int(self.score)} pkt'

        self.obstacle_manager.update()

    def check_technical_bonus(self):
        for obs in self.obstacle_manager.obstacles:
            if obs.z < self.player.z and not obs.scored:
                if abs(obs.x - self.player.x) < 0.5:
                    if (obs.type == 'up' and self.player.is_jumping) or \
                            (obs.type == 'down' and self.player.is_crouching):
                        self.trigger_bonus_ui()
                        obs.scored = True
                obs.scored = True

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

        self.player.model3d.stop()
        self.player.model3d.loop('Run')

        # czyszczenie przeszkód
        for obs in self.obstacle_manager.obstacles:
            destroy(obs)
        self.obstacle_manager.obstacles.clear()

        # reset punktów
        self.score = 0
        self.score_display.text = '0 pkt'
        self.score_display.enabled = True

        # przejecie kontroli
        self.player.ui_ref.end_menu.enabled = False
        self.player.ui_ref.bg_panel.enabled = False

        time.dt = 0