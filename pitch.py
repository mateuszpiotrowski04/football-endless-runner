from ursina import Entity, color, time, scene, destroy
from settings import WORLD_SPEED, LANES
from goal import GOAL_DISTANCE


class Pitch(Entity):
    def __init__(self, player_ref):
        super().__init__()
        self.player = player_ref
        self.finale_goal_ref = None
        self.goal_line = None
        self.goal_searched = False

        self.PITCH_LENGTH = 150.0
        self.START_Z = -25.0
        self.CENTER_Z = self.START_Z + (self.PITCH_LENGTH / 2.0)

        self.LINES_START_Z = -100.0
        self.LINES_LENGTH = 300.0
        self.LINES_CENTER_Z = self.LINES_START_Z + (self.LINES_LENGTH / 2.0)

        self.tex_scale_z = 20
        self.lane_width = 2.2
        self.goal_line_offset = -1.5

        self.light_grass = color.rgba(0.0, 1.0, 0.0, 1.0)
        self.dark_grass = color.rgba(0.0, 0.5, 0.0, 1.0)

        # środkowy pas trawy
        self.base_pitch = Entity(parent=self, model='plane', scale=(15, 1, self.PITCH_LENGTH), position=(0, 0, self.CENTER_Z),
                                 color=self.light_grass, texture='grass', texture_scale=(5.0, self.tex_scale_z))

        # boczne pasy trawy
        self.left_strip = Entity(parent=self, model='plane', scale=(self.lane_width, 1, self.PITCH_LENGTH),
                                 position=(LANES[0], 0.01, self.CENTER_Z), color=self.dark_grass, texture='grass',
                                 texture_scale=(self.lane_width / 3.0, self.tex_scale_z))

        self.right_strip = Entity(parent=self, model='plane', scale=(self.lane_width, 1, self.PITCH_LENGTH),
                                  position=(LANES[-1], 0.01, self.CENTER_Z), color=self.dark_grass, texture='grass',
                                  texture_scale=(self.lane_width / 3.0, self.tex_scale_z))

        self.strips_to_shorten = [self.left_strip, self.right_strip]

        self.side_segment_width = 5.0
        self.extra_segments = []

        positions_x = [-10.0, -15.0, 10.0, 15.0]
        for pos_x in positions_x:
            # trawa poza boiskiem
            segment = Entity(parent=self, model='plane', scale=(self.side_segment_width, 1, self.PITCH_LENGTH),
                             position=(pos_x, 0, self.CENTER_Z), color=self.light_grass, texture='grass',
                             texture_scale=(self.side_segment_width / 3.0, self.tex_scale_z))
            self.extra_segments.append(segment)

        self.ground_elements = [self.base_pitch, *self.strips_to_shorten, *self.extra_segments]

        play_area_left = LANES[0] - (self.lane_width / 2.0)
        play_area_right = LANES[-1] + (self.lane_width / 2.0)
        self.line_margin = 1.5

        # linie boczne
        self.side_lines = [
            Entity(parent=self, model='plane', scale=(0.1, 1, self.LINES_LENGTH), color=color.white,
                   position=(play_area_left - self.line_margin, 0.02, self.LINES_CENTER_Z)),
            Entity(parent=self, model='plane', scale=(0.1, 1, self.LINES_LENGTH), color=color.white,
                   position=(play_area_right + self.line_margin, 0.02, self.LINES_CENTER_Z))
        ]

    def update(self):
        if not self.player.in_finale:
            if self.goal_line:
                destroy(self.goal_line)
                self.goal_line = None

            self.finale_goal_ref = None
            self.goal_searched = False

            for line in self.side_lines:
                line.scale_z = self.LINES_LENGTH
                line.z = self.LINES_CENTER_Z

            for strip in self.strips_to_shorten:
                strip.scale_z = self.PITCH_LENGTH
                strip.z = self.CENTER_Z
                strip.texture_scale = (self.lane_width / 3.0, self.tex_scale_z)

        if not self.player.game_started or self.player.game_over:
            return

        if self.player.in_finale and not self.goal_searched:
            for entity in scene.entities:
                if entity.__class__.__name__ == 'FinaleGoal':
                    self.finale_goal_ref = entity
                    self.goal_searched = True

                    play_area_left = LANES[0] - (self.lane_width / 2.0)
                    play_area_right = LANES[-1] + (self.lane_width / 2.0)

                    # linia końcowa
                    self.goal_line = Entity(parent=self, model='plane', scale=(play_area_right - play_area_left + (self.line_margin * 2.0), 1, 0.1),
                                            color=color.white, position=(0, 0.02, self.finale_goal_ref.z + self.goal_line_offset))
                    break
            if not self.finale_goal_ref:
                self.goal_searched = True

        if self.finale_goal_ref:
            try:
                if (self.finale_goal_ref.z - self.player.z) <= GOAL_DISTANCE:
                    return
            except AttributeError:
                self.finale_goal_ref = None

        length = self.PITCH_LENGTH / self.tex_scale_z
        offset_change = (WORLD_SPEED * time.dt) / length
        new_offset_y = (self.base_pitch.texture_offset[1] + offset_change) % 1.0

        for element in self.ground_elements:
            element.texture_offset = (0, new_offset_y)

        if self.finale_goal_ref and self.goal_line:
            self.goal_line.z = self.finale_goal_ref.z + self.goal_line_offset

            new_length_lines = self.goal_line.z - self.LINES_START_Z
            for line in self.side_lines:
                line.scale_z = new_length_lines
                line.z = self.LINES_START_Z + (new_length_lines / 2.0)

            new_length_grass = max(0.1, self.goal_line.z - self.START_Z)
            new_center_grass = self.START_Z + (new_length_grass / 2.0)

            new_tex_scale_z = self.tex_scale_z * (new_length_grass / self.PITCH_LENGTH)

            for strip in self.strips_to_shorten:
                strip.scale_z = new_length_grass
                strip.z = new_center_grass
                strip.texture_scale = (self.lane_width / 3.0, new_tex_scale_z)