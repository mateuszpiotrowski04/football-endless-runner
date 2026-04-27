from ursina import Entity, camera, time, lerp

class GameLoop(Entity):
    def __init__(self, player_ref, obstacle_manager_ref):
        super().__init__()
        self.player = player_ref
        self.obstacle_manager = obstacle_manager_ref

    def update(self):
        # kamera - śledzenie gracza
        camera.x = lerp(camera.x, self.player.x, time.dt * 10)
        camera.y = lerp(camera.y, self.player.y + 1.5, time.dt * 10)
        camera.z = self.player.z - 10

        self.obstacle_manager.update()