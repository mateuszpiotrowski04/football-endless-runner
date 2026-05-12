from ursina import Entity, camera, color, Text, Button, Vec3, time, invoke, application
import math


class UIManager(Entity):
    def __init__(self, start_callback, restart_callback):
        super().__init__(parent=camera.ui)
        self.start_callback = start_callback
        self.restart_callback = restart_callback

        # paleta kolorów
        self.c_bg = color.rgba(0, 0, 0, 0.8)
        self.c_text_main = color.rgba(0.9, 0.9, 0.9, 1.0)
        self.c_text_sub = color.rgba(0.5, 0.5, 0.5, 1.0)
        self.c_btn_primary = color.rgba(0.3, 0.3, 0.3, 1.0)
        self.c_btn_danger = color.rgba(0.5, 0.2, 0.2, 1.0)
        self.c_btn_flash = color.rgba(0.5, 0.5, 0.5, 1.0)

        # flagi stanu ui
        self.active_menu = 'start'
        self.is_clicking = False
        self.end_menu_index = 0

        # tło
        self.bg_panel = Entity(parent=self, model='quad', scale=(3, 3), color=self.c_bg, enabled=True, z=1)

        # ekran startowy
        self.start_menu = Entity(parent=self, enabled=True)
        self.title = Text(parent=self.start_menu, text='FOOTBALL RUNNER', scale=4, y=0.2, origin=(0, 0),
                          color=self.c_text_main)
        self.instructions = Text(parent=self.start_menu, text='DEMO 2.0', scale=1.5,
                                 y=0.12, origin=(0, 0), color=self.c_text_sub)

        self.start_button = Button(parent=self.start_menu, text='START', color=self.c_btn_primary, scale=(0.3, 0.08),
                                   y=-0.1, collider=None)
        self.start_button.text_entity.color = self.c_text_main
        self.start_button.base_scale = Vec3(0.3, 0.08, 1)

        # ekran końcowy
        self.end_menu = Entity(parent=self, enabled=False)
        self.game_over_text = Text(parent=self.end_menu, text='KONIEC TRENINGU', scale=3.5, y=0.2, origin=(0, 0),
                                   color=self.c_text_main)
        self.final_score_text = Text(parent=self.end_menu, text='Wynik: 0 pkt', scale=2, y=0.05, origin=(0, 0),
                                    color=self.c_text_sub)

        self.restart_button = Button(parent=self.end_menu, text='ZAGRAJ PONOWNIE', color=self.c_btn_primary, scale=(0.3, 0.08),
                                     x=-0.18, y=-0.1, collider=None)
        self.restart_button.text_entity.color = self.c_text_main
        self.restart_button.base_scale = Vec3(0.3, 0.08, 1)

        self.exit_button = Button(parent=self.end_menu, text='KONIEC GRY', color=self.c_btn_danger, scale=(0.3, 0.08),
                                  x=0.18, y=-0.1, collider=None)
        self.exit_button.text_entity.color = self.c_text_main
        self.exit_button.base_scale = Vec3(0.3, 0.08, 1)

    def update(self):
        if self.is_clicking: return

        # animacja wyboru
        pulse_value = math.sin(time.time() * 4) * 0.006

        if self.active_menu == 'start':
            self.start_button.scale = self.start_button.base_scale + Vec3(pulse_value, pulse_value, 0)

        elif self.active_menu == 'end':
            self.restart_button.scale = self.restart_button.base_scale
            self.exit_button.scale = self.exit_button.base_scale

            if self.end_menu_index == 0:
                self.restart_button.scale = self.restart_button.base_scale + Vec3(pulse_value, pulse_value, 0)
            else:
                self.exit_button.scale = self.exit_button.base_scale + Vec3(pulse_value, pulse_value, 0)

    def input(self, key):
        if self.active_menu is None or self.is_clicking: return

        if self.active_menu == 'end':
            if key == 'left arrow' or key == 'right arrow':
                self.end_menu_index = 1 - self.end_menu_index

        if key == 'enter' or key == 'space':
            self.is_clicking = True

            if self.active_menu == 'start':
                active_btn = self.start_button
            elif self.active_menu == 'end':
                active_btn = self.restart_button if self.end_menu_index == 0 else self.exit_button

            # animacja kliknięcia
            active_btn.animate_scale(active_btn.base_scale * 0.9, duration=0.1)
            active_btn.animate_color(self.c_btn_flash, duration=0.1)

            if self.active_menu == 'start':
                invoke(self.start_game, delay=0.15)
            elif self.active_menu == 'end':
                if self.end_menu_index == 0:
                    invoke(self.trigger_restart, delay=0.15)
                else:
                    invoke(application.quit, delay=0.15)

    def start_game(self):
        self.is_clicking = False
        self.active_menu = None
        self.start_menu.enabled = False
        self.bg_panel.enabled = False
        self.start_button.color = self.c_btn_primary
        self.start_callback()

    def show_game_over(self, score):
        self.active_menu = 'end'
        self.end_menu_index = 0
        self.bg_panel.enabled = True
        self.end_menu.enabled = True
        self.final_score_text.text = f'Wynik: {int(score)} pkt'
        self.restart_button.color = self.c_btn_primary
        self.exit_button.color = self.c_btn_danger

    def trigger_restart(self):
        self.is_clicking = False
        self.active_menu = None
        self.restart_button.color = self.c_btn_primary
        if self.restart_callback:
            self.restart_callback()