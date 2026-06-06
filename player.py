from ursina import Entity, time, curve, lerp, scene, camera
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
        self.ball = Entity(
            parent=scene,
            model='ball',
            scale=1.5,
            position=(0, -0.35, 0.5)
        )
        self.ball_attached = True

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

        self._update_camera()
        self._sync_hitboxes()

        # obrót po zderzeniu
        if self.game_over:
            self._handle_game_over_rotation()
            return

        # powrót z kucania
        if self.is_crouching:
            self._handle_crouch_recovery()

        # powrót ze skoku
        if self.is_jumping:
            self._handle_jump_physics()

        # animacja lotu piłki
        if not self.ball_attached and self.ball_target_pos:
            self.animate_ball_flight()

    def _update_camera(self):
        camera.x = lerp(camera.x, self.x, time.dt * 10)
        camera.y = lerp(camera.y, self.y + 1.5, time.dt * 10)
        camera.z = self.z - 10

    def _sync_hitboxes(self):
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
            self.ball.rotation_x += 500 * time.dt

    def _handle_game_over_rotation(self):
        if not self.in_finale:
            current_angle = self.model3d.getH()
            self.model3d.setH(lerp(current_angle, 0, time.dt * 8))

    def _handle_crouch_recovery(self):
        self.crouch_timer -= time.dt
        if self.crouch_timer <= 0:
            self.is_crouching = False
            self.scale_y = 1.0
            if not self.is_jumping:
                self.y = 0.5
                self.model3d.loop('Run')

    def _handle_jump_physics(self):
        self.y_velocity -= GRAVITY * time.dt
        self.y += self.y_velocity * time.dt
        target_ground = 0.25 if self.is_crouching else 0.5

        if self.y <= target_ground:
            self.y = target_ground
            self.y_velocity = 0
            self.is_jumping = False
            if not self.is_crouching:
                self.model3d.loop('Run')

    def trigger_game_over(self):
        if self.game_over: return
        self.game_over = True
        self.model3d.stop()
        self.model3d.play('Death')

    def reset_player(self):
        self.x = 0
        self.y = 0.5
        self.z = -20
        self.rotation = (0, 0, 0)
        self.model3d.setH(180)
        self.current_lane = 1

        self.is_jumping = False
        self.is_crouching = False
        self.game_over = False
        self.game_started = True
        self.in_finale = False

        self.model3d.stop()
        self.model3d.loop('Run')

        self.ball_attached = True
        self.ball.enabled = True
        self.ball.parent = scene
        self.ball_target_pos = None
        self.ball_flight_timer = 0.0

    def move_to_center(self):
        if self.current_lane != 1:
            self.current_lane = 1
            self.animate_x(LANES[self.current_lane], duration=0.3, curve=curve.in_out_sine)

    def shoot(self, target_pos, shot_outcome):
        self.ball_attached = False
        self.ball.parent = scene
        self.ball_start_pos = self.ball.world_position
        self.ball_target_pos = target_pos
        self.ball_flight_timer = 0.0

        self.shot_outcome = shot_outcome

        self.post_vel_y = 0.0
        self.post_vel_z = 0.0

    def animate_ball_flight(self):
        if self.ball_flight_timer < 1.0:
            self.ball_flight_timer += time.dt / 0.4

            curr_x = lerp(self.ball_start_pos[0], self.ball_target_pos[0], self.ball_flight_timer)
            curr_y = lerp(self.ball_start_pos[1], self.ball_target_pos[1], self.ball_flight_timer)
            curr_z = lerp(self.ball_start_pos[2], self.ball_target_pos[2], self.ball_flight_timer)

            self.ball.position = (curr_x, curr_y, curr_z)
            self.ball.rotation_x -= 500 * time.dt
        else:
            if self.shot_outcome == 'on_target':
                pass

            elif self.shot_outcome == 'goal':
                self.ball.z += self.post_vel_z * time.dt
                goal_net = self.ball_target_pos[2] + 4.0

                if self.ball.z > goal_net:
                    self.ball.z = goal_net
                    if self.post_vel_z > 0:
                        self.ball.rotation_x += self.post_vel_z * 40 * time.dt
                        self.post_vel_z -= 15.0 * time.dt

                if self.ball.y > 0.21:
                    self.post_vel_y -= GRAVITY * time.dt
                    self.ball.y += self.post_vel_y * time.dt

                    if self.ball.z < goal_net:
                        self.ball.rotation_x += 800 * time.dt
                else:
                    self.ball.y = 0.21

            elif self.shot_outcome == 'save':
                if self.ball.y > 0.21:
                    self.post_vel_y -= GRAVITY * time.dt
                    self.ball.y += self.post_vel_y * time.dt
                    self.ball.z += self.post_vel_z * time.dt
                    self.ball.rotation_x += 800 * time.dt
                else:
                    self.ball.y = 0.21
                    if self.post_vel_z < 0:
                        self.ball.z += self.post_vel_z * time.dt
                        self.ball.rotation_x += self.post_vel_z * 40 * time.dt
                        self.post_vel_z += 10.0 * time.dt

            elif self.shot_outcome == 'weak':
                if self.post_vel_z == 0:
                    self.post_vel_z = 5.0

                if self.post_vel_z > 0:
                    self.ball.z += self.post_vel_z * time.dt
                    self.ball.rotation_x += self.post_vel_z * 40 * time.dt
                    self.post_vel_z -= 5.0 * time.dt

            elif self.shot_outcome == 'miss':
                self.post_vel_y -= 0.3 * GRAVITY * time.dt
                self.ball.y += self.post_vel_y * time.dt
                self.ball.rotation_x -= 500 * time.dt
                self.ball.z += 30 * time.dt

                if self.ball.z > self.ball_target_pos[2] + 30:
                    self.ball.enabled = False