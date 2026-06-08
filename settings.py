from ursina import color, DirectionalLight, AmbientLight
from panda3d.core import Vec3
import simplepbr

# ustawienia okna
WINDOW_TITLE = "Football Runner"
WINDOW_SIZE = (1600, 900)

# fizyka
LANES = [-2.5, 0, 2.5]
GRAVITY = 35.0
JUMP_FORCE = 10.0
CROUCH_DURATION = 0.85

# oświetlenie
def setup_lighting():
    simplepbr.init()
    light = DirectionalLight()
    light.look_at(Vec3(1, -1, -1))
    AmbientLight(color=color.rgb(0.5, 0.5, 0.5))