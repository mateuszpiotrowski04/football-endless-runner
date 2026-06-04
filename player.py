from ursina import Entity, time, curve, lerp, scene
from direct.actor.Actor import Actor
from settings import LANES, JUMP_FORCE, CROUCH_DURATION, GRAVITY


class FootballPlayer(Entity):
    def __init__(self):
        super().__init__(y=0.5, z=-20, collider='box')

        # ustwienia startowe
        self.current_lane = 1
        self.x = LANES[self.current_lane]
        self.y_velocity = 0.0

        self.is_jumping = False
        self.is_crouching = False
        self.crouch_timer = 0.0

        self.game_started = False
        self.game_over = False
        self.in_finale = False

        # piłkarz
        self.model3d = Actor('assets/character.gltf')
        self.model3d.setScale(0.4, 0.4, 0.4)
        self.model3d.reparent_to(scene)
        self.model3d.setH(180)
        self.model3d.loop('Run')

        # piłka
        self.ball = Actor('assets/ball.gltf')
        self.ball.setScale(0.2)
        self.ball.reparent_to(scene)
        self.ball_attached = True

    def trigger_game_over(self):
        if self.game_over: return
        self.game_over = True
        self.model3d.stop()
        self.model3d.play('Death')

    # sterowanie
    def input(self, key):
        if not self.game_started or self.game_over or self.in_finale: return

        if (key == 'left arrow') and self.current_lane > 0:
            self.current_lane -= 1
            self.animate_x(LANES[self.current_lane], duration=0.15, curve=curve.out_sine)

        elif (key == 'right arrow') and self.current_lane < len(LANES) - 1:
            self.current_lane += 1
            self.animate_x(LANES[self.current_lane], duration=0.15, curve=curve.out_sine)

        if (key == 'up arrow') and not self.is_jumping and not self.is_crouching:
            self.y_velocity = JUMP_FORCE
            self.is_jumping = True
            self.model3d.play('Jump')

        if (key == 'down arrow') and not self.is_crouching:
            self.is_crouching = True
            self.crouch_timer = CROUCH_DURATION
            self.scale_y = 0.5
            self.model3d.loop('Roll')
            if self.is_jumping:
                self.y_velocity = -JUMP_FORCE * 1.5
            else:
                self.y = 0.25

    def update(self):
        if not self.game_started: return

        # obrót po zderzeniu
        if self.game_over:
            if not self.in_finale:
                current_angle = self.model3d.getH()
                self.model3d.setH(lerp(current_angle, 0, time.dt * 8))
            return

        # synchronizacja z hitboxem piłkarza
        self.model3d.setX(self.x)
        self.model3d.setZ(self.z)
        self.model3d.setY(self.y - (self.scale_y * 0.5))

        # synchronizacja z hitboxem piłki
        if self.ball_attached:
            self.ball.setX(self.x)
            self.ball.setZ(self.z + 0.5)
            self.ball.setY(self.y - (self.scale_y * 0.5) + 0.18)

        # rotacja piłki
        self.ball.setP(self.ball.getP() - 500 * time.dt)

        # powrót z kucania
        if self.is_crouching:
            self.crouch_timer -= time.dt
            if self.crouch_timer <= 0:
                self.is_crouching = False
                self.scale_y = 1.0
                if not self.is_jumping:
                    self.y = 0.5
                    self.model3d.loop('Run')

        # powrót ze skoku
        if self.is_jumping:
            self.y_velocity -= GRAVITY * time.dt
            self.y += self.y_velocity * time.dt
            target_ground = 0.25 if self.is_crouching else 0.5

            if self.y <= target_ground:
                self.y = target_ground
                self.y_velocity = 0
                self.is_jumping = False
                if not self.is_crouching:
                    self.model3d.loop('Run')

    def move_to_center(self):
        if self.current_lane != 1:
            self.current_lane = 1
            self.animate_x(LANES[self.current_lane], duration=0.3, curve=curve.in_out_sine)