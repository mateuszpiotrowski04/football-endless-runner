from ursina import Entity, color, time, scene, destroy, window
from settings import WORLD_SPEED, LANES
from goal import GOAL_DISTANCE


class EnvironmentManager(Entity):
    def __init__(self, player_ref):
        super().__init__()
        self.player = player_ref
        self.finale_goal_ref = None
        self.back_fence = None
        self.needs_post_reset = False

        self.FENCE_LENGTH = 150.0
        self.START_Z = -25.0
        self.END_Z = 130.0
        self.fence_height = 4.0
        self.post_spacing = 5.0

        SKY_COLOR = color.rgb(0.4, 0.75, 0.95)
        window.color = SKY_COLOR

        self.fog_screens = []
        for i in range(10):
            dist = 90 + (i * 5)
            alpha_val = (i + 1) * 0.1

            # mgła końcowa
            screen = Entity(parent=self, model='quad', scale=(400, 200), position=(0, 20, dist), transparent=True,
                            color=color.rgba(0.4, 0.75, 0.95, alpha_val))
            self.fog_screens.append(screen)

        for i in range(5):
            offset_x = 12 + (i * 0.5)
            alpha_val = (i + 1) * 0.2

            for direction in [-1, 1]:
                # mgła boczna
                Entity(parent=self, model='quad', scale=(300, 200), position=(offset_x * direction, 20, 50), rotation=(0, 90, 0),
                       transparent=True, color=color.rgba(0.4, 0.75, 0.95, alpha_val), double_sided=True)

        left_x = LANES[0] - 4.0
        right_x = LANES[-1] + 4.0

        self.tex_scale_z = (self.FENCE_LENGTH / self.post_spacing) * 3.0
        self.tex_scale_y = (self.fence_height / self.post_spacing) * 3.0

        # lewa siatka
        self.left_net = Entity(parent=self, model='cube', scale=(0.02, self.fence_height, self.FENCE_LENGTH),
                               position=(left_x, self.fence_height / 2, self.FENCE_LENGTH / 3), transparent=True,
                               texture='net', texture_scale=(self.tex_scale_z, self.tex_scale_y))

        # prawa siatka
        self.right_net = Entity(parent=self, model='cube', scale=(0.02, self.fence_height, self.FENCE_LENGTH),
                                position=(right_x, self.fence_height / 2, self.FENCE_LENGTH / 3), transparent=True,
                                texture='net', texture_scale=(self.tex_scale_z, self.tex_scale_y))

        self.side_nets = [self.left_net, self.right_net]

        self.all_posts = []

        # słupki boczne
        for z_pos in range(int(self.START_Z), int(self.END_Z), int(self.post_spacing)):
            lp = Entity(parent=self, model='cube', scale=(0.15, self.fence_height, 0.15),
                        position=(left_x, self.fence_height / 2, z_pos), color=color.dark_gray)
            rp = Entity(parent=self, model='cube', scale=(0.15, self.fence_height, 0.15),
                        position=(right_x, self.fence_height / 2, z_pos), color=color.dark_gray)
            self.all_posts.extend([lp, rp])

    def update(self):
        if not self.player.game_started or self.player.game_over:
            self.needs_post_reset = True
            return

        if not self.player.in_finale:
            if self.back_fence:
                destroy(self.back_fence)
                self.back_fence = None
            self.finale_goal_ref = None

            for net in self.side_nets:
                net.scale_z = self.FENCE_LENGTH
                net.z = 50
                net.texture_scale = (self.tex_scale_z, self.tex_scale_y)

            if self.needs_post_reset:
                post_idx = 0
                for z_pos in range(int(self.START_Z), int(self.END_Z), int(self.post_spacing)):
                    self.all_posts[post_idx].z = z_pos
                    self.all_posts[post_idx].enabled = True
                    self.all_posts[post_idx + 1].z = z_pos
                    self.all_posts[post_idx + 1].enabled = True
                    post_idx += 2
                self.needs_post_reset = False

        if self.player.in_finale and not self.back_fence:
            for entity in scene.entities:
                if entity.__class__.__name__ == 'FinaleGoal':
                    self.finale_goal_ref = entity
                    fence_width = (LANES[-1] + 4.0) - (LANES[0] - 4.0)

                    self.back_fence = Entity(parent=self, position=(0, 0, self.finale_goal_ref.z + 8))

                    tex_scale_x_back = (fence_width / self.post_spacing) * 3.0

                    # siatka za bramką
                    Entity(parent=self.back_fence, model='cube', scale=(fence_width, self.fence_height, 0.02),
                           position=(0, self.fence_height / 2, 0), transparent=True,
                           texture='net', texture_scale=(tex_scale_x_back, self.tex_scale_y))

                    # słupki za bramką
                    for post_x in range(int(-fence_width / 2), int(fence_width / 2) + 1, 3):
                        Entity(parent=self.back_fence, model='cube', scale=(0.15, self.fence_height, 0.15),
                               position=(post_x, self.fence_height / 2, 0), color=color.dark_gray)

                    for p in self.all_posts:
                        if p.z > self.back_fence.z:
                            p.enabled = False
                    break

        if self.finale_goal_ref:
            try:
                if (self.finale_goal_ref.z - self.player.z) <= GOAL_DISTANCE:
                    return
            except AttributeError:
                self.finale_goal_ref = None

        tile_length = self.FENCE_LENGTH / self.tex_scale_z
        offset_change = (WORLD_SPEED * time.dt) / tile_length

        for net in self.side_nets:
            nowy_offset_x = (net.texture_offset[0] + offset_change) % 1.0
            net.texture_offset = (nowy_offset_x, 0)

        for p in self.all_posts:
            if not p.enabled:
                continue

            p.z -= WORLD_SPEED * time.dt

            if p.z < self.START_Z:
                if not self.back_fence:
                    p.z += (self.END_Z - self.START_Z)
                else:
                    p.enabled = False

        if self.finale_goal_ref and self.back_fence:
            self.back_fence.z = self.finale_goal_ref.z + 8

            new_length = max(0.1, self.back_fence.z - self.START_Z)
            new_center = self.START_Z + (new_length / 2.0)

            new_tex_scale_z = (new_length / self.post_spacing) * 3.0

            for net in self.side_nets:
                net.scale_z = new_length
                net.z = new_center
                net.texture_scale = (new_tex_scale_z, self.tex_scale_y)