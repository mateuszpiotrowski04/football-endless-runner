from ursina import Ursina, mouse, time, camera
from settings import WINDOW_TITLE, WINDOW_SIZE, setup_lighting
from player import FootballPlayer
from obstacles import ObstacleManager
from game_loop import GameLoop
from pitch import Pitch
from ui import UIManager
from environment import EnvironmentManager

# okno gry
app = Ursina(title=WINDOW_TITLE, size=WINDOW_SIZE)
mouse.visible = False
time.dt = min(time.dt, 0.1)

# oświetlenie
setup_lighting()

# gra
player = FootballPlayer()
obstacle_manager = ObstacleManager(player)
main_loop = GameLoop(player, obstacle_manager)

# boisko
camera.rotation_x = 5
pitch = Pitch(player)
environment = EnvironmentManager(player)

# ui
ui = UIManager(
    start_callback=main_loop.start_game,
    restart_callback=main_loop.restart_game,
    menu_callback=main_loop.reset_to_menu
)
player.ui_ref = ui

app.run()