from ursina import *
from settings import *
from player import FootballPlayer
from obstacles import ObstacleManager
from game_loop import GameLoop
from pitch import Pitch

# okno gry
app = Ursina(title=WINDOW_TITLE, size=WINDOW_SIZE)
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

app.run()