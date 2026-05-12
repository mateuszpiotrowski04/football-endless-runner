from ursina import Ursina, mouse, window, time, camera
from settings import WINDOW_TITLE, WINDOW_SIZE, color, setup_lighting
from player import FootballPlayer
from obstacles import ObstacleManager
from game_loop import GameLoop
from pitch import Pitch
from ui import UIManager

# okno gry
app = Ursina(title=WINDOW_TITLE, size=WINDOW_SIZE)
mouse.visible = False
window.color = color.light_gray
time.dt = min(time.dt, 0.1)

# oświetlenie
setup_lighting()

# ziemia
camera.rotation_x = 5
pitch = Pitch()

# gra
player = FootballPlayer()
obstacle_manager = ObstacleManager(player)
main_loop = GameLoop(player, obstacle_manager)

# ui
ui = UIManager(start_callback=main_loop.start_game, restart_callback=main_loop.restart_game)
player.ui_ref = ui

app.run()