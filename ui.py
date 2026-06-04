from ursina import Entity, camera, color, Text, Button, Vec3, time, invoke, application
import math


class UIManager(Entity):
    def __init__(self, start_callback, restart_callback, menu_callback = None):
        super().__init__(parent=camera.ui)
        self.start_callback = start_callback
        self.restart_callback = restart_callback
        self.menu_callback = menu_callback

        # paleta kolorów
        self.c_bg = color.rgba(0, 0, 0, 0.8)
        self.c_text_main = color.rgba(0.9, 0.9, 0.9, 1.0)
        self.c_text_sub = color.rgba(0.5, 0.5, 0.5, 1.0)
        self.c_btn_primary = color.rgba(0.3, 0.3, 0.3, 1.0)
        self.c_btn_danger = color.rgba(0.5, 0.2, 0.2, 1.0)
        self.c_btn_flash = color.rgba(0.5, 0.5, 0.5, 1.0)
        self.c_gold = color.rgba(1.0, 0.9, 0, 1.0)

        # flagi stanu ui
        self.active_menu = 'start'
        self.is_clicking = False
        self.menu_index = 0

        # tło
        self.bg_panel = Entity(parent=self, model='quad', scale=(3, 3), color=self.c_bg, enabled=True, z=1)

        # ekran startowy
        self.start_menu = Entity(parent=self, enabled=True)
        self.title = Text(parent=self.start_menu, text='FOOTBALL RUNNER', scale=4, y=0.2, origin=(0, 0),
                          color=self.c_text_main)
        self.instructions = Text(parent=self.start_menu, text='DEMO 2.0', scale=1.5,
                                 y=0.12, origin=(0, 0), color=self.c_text_sub)

        # ekran przegranej
        self.end_menu = Entity(parent=self, enabled=False)
        self.game_over_text = Text(parent=self.end_menu, text='KONIEC TRENINGU', scale=3.5, y=0.2, origin=(0, 0),
                                   color=self.c_text_main)
        self.final_score_text = Text(parent=self.end_menu, text='Wynik: 0 pkt', scale=2, y=0.05, origin=(0, 0),
                                    color=self.c_text_sub)

        # przycisk start
        self.start_button = Button(parent=self.start_menu, text='START', color=self.c_btn_primary, scale=(0.3, 0.08),
                                   y=-0.1, collider=None)
        self.start_button.text_entity.color = self.c_text_main
        self.start_button.base_scale = Vec3(0.3, 0.08, 1)

        # ekran przegranej
        self.end_menu = Entity(parent=self, enabled=False)
        self.game_over_text = Text(parent=self.end_menu, text='KONIEC TRENINGU', scale=3.5, y=0.2, origin=(0, 0),
                                   color=self.c_text_main)
        self.final_score_text = Text(parent=self.end_menu, text='Wynik: 0 pkt', scale=2, y=0.05, origin=(0, 0),
                                    color=self.c_text_sub)

        # przycisk zagraj ponownie
        self.restart_button = Button(parent=self.end_menu, text='ZAGRAJ PONOWNIE', color=self.c_btn_primary, scale=(0.3, 0.08),
                                     x=-0.18, y=-0.1, collider=None)
        self.restart_button.text_entity.color = self.c_text_main
        self.restart_button.base_scale = Vec3(0.3, 0.08, 1)

        # przycisk koniec gry
        self.exit_button = Button(parent=self.end_menu, text='KONIEC GRY', color=self.c_btn_danger, scale=(0.3, 0.08),
                                  x=0.18, y=-0.1, collider=None)
        self.exit_button.text_entity.color = self.c_text_main
        self.exit_button.base_scale = Vec3(0.3, 0.08, 1)

        # ekran wygranej
        self.win_menu = Entity(parent=self, enabled=False)
        self.win_text = Text(parent=self.win_menu, text='GOL!', scale=5, y=0.2, origin=(0, 0),
                             color=self.c_gold)
        self.win_score_text = Text(parent=self.win_menu, text='Wynik: 0 pkt', scale=2, y=0.05, origin=(0, 0),
                                   color=self.c_text_main)

        # przycisk menu główne
        self.menu_button = Button(parent=self.win_menu, text='MENU GŁÓWNE', color=self.c_btn_primary, scale=(0.3, 0.08),
                                  x=-0.18, y=-0.1, collider=None)
        self.menu_button.text_entity.color = self.c_text_main
        self.menu_button.base_scale = Vec3(0.3, 0.08, 1)

        # przycisk koniec gry
        self.win_exit_button = Button(parent=self.win_menu, text='KONIEC GRY', color=self.c_btn_danger, scale=(0.3, 0.08),
                                      x=0.18, y=-0.1, collider=None)
        self.win_exit_button.text_entity.color = self.c_text_main
        self.win_exit_button.base_scale = Vec3(0.3, 0.08, 1)

        # pasek siły strzału
        self.power_bar_bg = Entity(parent=camera.ui, model='quad', scale=(0.5, 0.04), y=-0.3,
                                   color=color.rgba(0, 0, 0, 150), enabled=False)
        self.power_bar_fill = Entity(parent=self.power_bar_bg, model='quad', scale=(0, 1), x=-0.5, origin=(-0.5, 0),
                                     color=color.yellow)

    def update(self):
        if self.is_clicking: return

        # animacja wyboru
        pulse_value = math.sin(time.time() * 4) * 0.006

        if self.active_menu == 'start':
            self.start_button.scale = self.start_button.base_scale + Vec3(pulse_value, pulse_value, 0)

        elif self.active_menu == 'end':
            self.restart_button.scale = self.restart_button.base_scale
            self.exit_button.scale = self.exit_button.base_scale

            if self.menu_index == 0:
                self.restart_button.scale = self.restart_button.base_scale + Vec3(pulse_value, pulse_value, 0)
            else:
                self.exit_button.scale = self.exit_button.base_scale + Vec3(pulse_value, pulse_value, 0)

        elif self.active_menu == 'win':
            self.menu_button.scale = self.menu_button.base_scale
            self.win_exit_button.scale = self.win_exit_button.base_scale

            if self.menu_index == 0:
                self.menu_button.scale = self.menu_button.base_scale + Vec3(pulse_value, pulse_value, 0)
            else:
                self.win_exit_button.scale = self.win_exit_button.base_scale + Vec3(pulse_value, pulse_value, 0)

    def input(self, key):
        if self.active_menu is None or self.is_clicking: return

        if self.active_menu == 'end' or self.active_menu == 'win':
            if key == 'left arrow' or key == 'right arrow':
                self.menu_index = 1 - self.menu_index

        if key == 'enter' or key == 'space':
            self.is_clicking = True

            if self.active_menu == 'start':
                active_btn = self.start_button
            elif self.active_menu == 'end':
                active_btn = self.restart_button if self.menu_index == 0 else self.exit_button
            elif self.active_menu == 'win':
                active_btn = self.menu_button if self.menu_index == 0 else self.win_exit_button

            # animacja kliknięcia
            active_btn.animate_scale(active_btn.base_scale * 0.9, duration=0.1)
            active_btn.animate_color(self.c_btn_flash, duration=0.1)

            if self.active_menu == 'start':
                invoke(self.start_game, delay=0.15)
            elif self.active_menu == 'end':
                if self.menu_index == 0:
                    invoke(self.trigger_restart, delay=0.15)
                else:
                    invoke(application.quit, delay=0.15)
            elif self.active_menu == 'win':
                if self.menu_index == 0:
                    if self.menu_callback:
                        invoke(self.menu_callback, delay=0.15)
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
        self.menu_index = 0
        self.bg_panel.enabled = True
        self.end_menu.enabled = True
        self.final_score_text.text = f'Wynik: {int(score)} pkt'
        self.restart_button.color = self.c_btn_primary
        self.exit_button.color = self.c_btn_danger

    def show_win_screen(self, score):
        self.active_menu = 'win'
        self.menu_index = 0
        self.bg_panel.enabled = True
        self.win_menu.enabled = True
        self.end_menu.enabled = False
        self.win_score_text.text = f'Wynik: {int(score)} pkt'

    def show_start_menu(self):
        self.active_menu = 'start'
        self.is_clicking = False
        self.menu_index = 0
        self.bg_panel.enabled = True
        self.start_menu.enabled = True
        self.end_menu.enabled = False
        self.win_menu.enabled = False
        self.start_button.color = self.c_btn_primary

    def trigger_restart(self):
        self.is_clicking = False
        self.active_menu = None
        self.bg_panel.enabled = False
        self.end_menu.enabled = False
        self.restart_button.color = self.c_btn_primary
        if self.restart_callback:
            self.restart_callback()

    def update_power_bar(self, power):
        self.power_bar_bg.enabled = True

        clamped_power = min(power, 1.0)
        self.power_bar_fill.scale_x = clamped_power

        if power <= 0.33:
            self.power_bar_fill.color = color.yellow
        elif power <= 0.66:
            self.power_bar_fill.color = color.orange
        elif power <= 1.0:
            self.power_bar_fill.color = color.red
        else:
            self.power_bar_fill.color = color.black

    def hide_power_bar(self):
        self.power_bar_bg.enabled = False