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
        # punkty
        if not self.player.game_over:
            self.score += time.dt * WORLD_SPEED * 0.1

            self.check_technical_bonus()

            self.score_display.text = f'{int(self.score)} pkt'

        # kamera - śledzenie gracza
        camera.x = lerp(camera.x, self.player.x, time.dt * 10)
        camera.y = lerp(camera.y, self.player.y + 1.5, time.dt * 10)
        camera.z = self.player.z - 10

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