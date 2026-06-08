from ursina import Entity, camera, color, Text, Button, Vec3, time, invoke, application, curve, destroy
import math
import random

class Palette:
    BG_OVERLAY = color.rgba(0, 0, 0, 0.8)

    TEXT_PRIMARY = color.rgba(0.9, 0.9, 0.9, 1.0)
    TEXT_SECONDARY = color.rgba(0.5, 0.5, 0.5, 1.0)
    TEXT_DISABLED = color.rgba(0.5, 0.5, 0.5, 0.8)
    TEXT_DANGER = color.rgba(0.5, 0.2, 0.2, 1.0)
    TEXT_GOLD = color.rgba(1.0, 0.9, 0, 1.0)
    TEXT_BONUS = color.black

    BTN_PRIMARY = color.rgba(0.3, 0.3, 0.3, 1.0)
    BTN_SECONDARY = color.gray
    BTN_DANGER = color.rgba(0.5, 0.2, 0.2, 1.0)
    BTN_DISABLED = color.rgba(0.2, 0.2, 0.2, 0.8)
    BTN_FLASH = color.rgba(0.5, 0.5, 0.5, 1.0)

    BAR_BORDER = color.rgba(0.3, 0.3, 0.3, 1.0)
    BAR_BG = color.black
    POWER_WEAK = color.gray
    POWER_GOOD = color.green
    POWER_PERFECT = color.orange
    POWER_TOO_STRONG = color.red


class MenuButton(Button):
    def __init__(self, text, parent, x=0, y=0, btn_color=Palette.BTN_PRIMARY):
        super().__init__(
            parent=parent,
            text=text,
            color=btn_color,
            scale=(0.3, 0.08),
            position=(x, y),
            collider=None
        )
        self.text_entity.color = Palette.TEXT_PRIMARY
        self.base_scale = Vec3(0.3, 0.08, 1)
        self.original_color = btn_color
        self.is_disabled = False

    def set_disabled(self, disabled):
        self.is_disabled = disabled
        if disabled:
            self.color = Palette.BTN_DISABLED
            self.text_entity.color = Palette.TEXT_DISABLED
        else:
            self.color = self.original_color
            self.text_entity.color = Palette.TEXT_PRIMARY

class UIManager(Entity):
    def __init__(self, start_callback, restart_callback, menu_callback, next_callback):
        super().__init__(parent=camera.ui)
        self.start_callback = start_callback
        self.restart_callback = restart_callback
        self.menu_callback = menu_callback
        self.next_callback = next_callback

        self.max_unlocked_level = 1

        # flagi stanu ui
        self.active_menu = 'main'
        self.is_clicking = False
        self.menu_index = 0

        # tło
        self.bg_panel = Entity(parent=self, model='quad', scale=(3, 3), color=Palette.BG_OVERLAY, enabled=True, z=1)

        # menu główne
        self.main_menu = Entity(parent=self, enabled=True)
        Text(parent=self.main_menu, text='FOOTBALL RUNNER', scale=5, y=0.25, origin=(0, 0), color=Palette.TEXT_PRIMARY)

        self.btn_main_play = MenuButton('WYBIERZ POZIOM', parent=self.main_menu, y=0.05)
        self.btn_main_help = MenuButton('JAK GRAĆ', parent=self.main_menu, y=-0.07)
        self.btn_main_exit = MenuButton('KONIEC TRENINGU', parent=self.main_menu, y=-0.19, btn_color=Palette.BTN_DANGER)

        self.main_buttons = [self.btn_main_play, self.btn_main_help, self.btn_main_exit]

        # menu wyboru poziomu
        self.level_menu = Entity(parent=self, enabled=False)
        Text(parent=self.level_menu, text='WYBIERZ POZIOM', scale=3.5, y=0.3, origin=(0, 0), color=Palette.TEXT_PRIMARY)

        self.btn_lvl_1 = MenuButton('POZIOM 1', parent=self.level_menu, y=0.12)
        self.btn_lvl_2 = MenuButton('POZIOM 2', parent=self.level_menu, y=0.02)
        self.btn_lvl_3 = MenuButton('POZIOM 3', parent=self.level_menu, y=-0.08)
        self.btn_lvl_4 = MenuButton('ENDLESS RUN', parent=self.level_menu, y=-0.18)
        self.btn_lvl_back = MenuButton('WRÓĆ', parent=self.level_menu, y=-0.32, btn_color=Palette.BTN_SECONDARY)

        self.level_buttons = [self.btn_lvl_1, self.btn_lvl_2, self.btn_lvl_3, self.btn_lvl_4, self.btn_lvl_back]

        # instrukcja
        self.instr_menu = Entity(parent=self, enabled=False)
        Text(parent=self.instr_menu, text='INSTRUKCJA', scale=3.5, y=0.35, origin=(0, 0), color=Palette.TEXT_PRIMARY)

        instrukcja = (
            "STEROWANIE:\n"
            "strzałka w lewo/prawo   -   ruch w lewo/prawo\n"
            "strzałka w dół   -   przewrót\n"
            "strzałka w górę   -   skok\n"
            "\nSIŁA STRZAŁU:\n"
            "kolor szary   -   strzał za słaby\n"
            "kolor zielony   -   strzał po ziemi\n"
            "kolor pomarańczowy   -   strzał górą\n"
            "kolor czerwony   -   strzał za mocny\n"
            "\nKIERUNEK STRZAŁU:\n"
            "strzałka w lewo/prawo   -   strzał w lewo/prawo\n"
            "strzałka w górę   -   strzał w środek\n"
        )

        Text(parent=self.instr_menu, text=instrukcja, scale=1.4, x=-0.35, y=0.25, origin=(-0.5, 0.5), color=Palette.TEXT_PRIMARY)

        self.btn_instr_back = MenuButton('WRÓĆ', parent=self.instr_menu, y=-0.35, btn_color=Palette.BTN_SECONDARY)

        self.instr_buttons = [self.btn_instr_back]

        # ekran przegranej
        self.end_menu = Entity(parent=self, enabled=False)
        Text(parent=self.end_menu, text='KONIEC TRENINGU', scale=4, y=0.2, origin=(0, 0), color=Palette.TEXT_DANGER)
        self.final_score_text = Text(parent=self.end_menu, text='Wynik: 0 pkt', scale=2, y=0.05, origin=(0, 0))

        self.btn_end_restart = MenuButton('ZAGRAJ PONOWNIE', parent=self.end_menu, x=-0.2, y=-0.1, btn_color=Palette.BTN_SECONDARY)
        self.btn_end_menu = MenuButton('MENU GŁÓWNE', parent=self.end_menu, x=0.2, y=-0.1)

        self.end_buttons = [self.btn_end_restart, self.btn_end_menu]

        # ekran wygranej
        self.win_menu = Entity(parent=self, enabled=False)
        Text(parent=self.win_menu, text='GOL! Nowy POZIOM', scale=4, y=0.2, origin=(0, 0), color=Palette.TEXT_GOLD)
        self.win_score_text = Text(parent=self.win_menu, text='Wynik: 0 pkt', scale=2, y=0.05, origin=(0, 0))

        self.btn_win_next = MenuButton('NASTĘPNY POZIOM', parent=self.win_menu, x=-0.2, y=-0.1, btn_color=Palette.BTN_SECONDARY)
        self.btn_win_menu = MenuButton('MENU GŁÓWNE', parent=self.win_menu, x=0.2, y=-0.1)

        self.win_buttons = [self.btn_win_next, self.btn_win_menu]

        # pasek siły strzału
        self.base_bar_x = 0
        self.base_bar_y = -0.3

        self.power_bar_bg = Button(parent=camera.ui, scale=(0.5, 0.04), position=(self.base_bar_x, self.base_bar_y),
                                   color=Palette.BAR_BORDER, collider=None, enabled=False)

        self.power_bar_inner = Entity(parent=self.power_bar_bg, model='quad', scale=(0.98, 0.8),
                                      color=Palette.BAR_BG, z=-0.01)

        self.power_bar_fill = Entity(parent=self.power_bar_bg, model='quad', scale=(0, 0.8), x=-0.49, origin=(-0.5, 0),
                                     color=Palette.POWER_WEAK, z=-0.02)

        Entity(parent=self.power_bar_inner, model='quad', color=Palette.BAR_BORDER, scale=(0.005, 1), x=-0.165, z=-0.03)
        Entity(parent=self.power_bar_inner, model='quad', color=Palette.BAR_BORDER, scale=(0.005, 1), x=0.165, z=-0.03)

    def get_current_buttons(self):
        if self.active_menu == 'main': return self.main_buttons
        if self.active_menu == 'levels': return self.level_buttons
        if self.active_menu == 'instr': return self.instr_buttons
        if self.active_menu == 'end': return self.end_buttons
        if self.active_menu == 'win': return self.win_buttons
        return []

    def update(self):
        if self.is_clicking: return

        pulse_value = math.sin(time.time() * 4) * 0.006
        buttons = self.get_current_buttons()

        for i, btn in enumerate(buttons):
            if i == self.menu_index:
                btn.scale = btn.base_scale + Vec3(pulse_value, pulse_value, 0)
            else:
                btn.scale = btn.base_scale

    def input(self, key):
        if self.active_menu is None or self.is_clicking: return

        buttons = self.get_current_buttons()
        if not buttons: return

        # ruch po menu
        if key == 'up arrow' or (key == 'left arrow' and self.active_menu in ['end', 'win']):
            self.move_selection(-1, buttons)
        elif key == 'down arrow' or (key == 'right arrow' and self.active_menu in ['end', 'win']):
            self.move_selection(1, buttons)

        if key == 'enter' or key == 'space':
            selected_btn = buttons[self.menu_index]
            if not selected_btn.is_disabled:
                self.execute_click(selected_btn)

    def move_selection(self, direction, buttons):
        if not buttons: return

        self.menu_index = (self.menu_index + direction) % len(buttons)

        while buttons[self.menu_index].is_disabled:
            self.menu_index = (self.menu_index + direction) % len(buttons)

    def execute_click(self, btn):
        self.is_clicking = True
        btn.animate_scale(btn.base_scale * 0.9, duration=0.1)
        btn.animate_color(Palette.BTN_FLASH, duration=0.1)
        invoke(self.handle_button_action, btn, delay=0.15)

    def handle_button_action(self, btn):
        self.is_clicking = False
        btn.color = btn.original_color
        btn.scale = btn.base_scale

        # menu główne
        if btn == self.btn_main_play:
            self.show_level_menu()
        elif btn == self.btn_main_help:
            self.show_instructions()
        elif btn == self.btn_main_exit:
            application.quit()

        # poziomy
        elif btn == self.btn_lvl_1:
            self.start_game(1)
        elif btn == self.btn_lvl_2:
            self.start_game(2)
        elif btn == self.btn_lvl_3:
            self.start_game(3)
        elif btn == self.btn_lvl_4:
            self.start_game(4)
        elif btn == self.btn_lvl_back:
            self.show_main_menu()

        # instrukcja
        elif btn == self.btn_instr_back:
            self.show_main_menu()

        # koniec gry
        elif btn == self.btn_end_restart:
            self.trigger_restart()
        elif btn == self.btn_end_menu:
            self.trigger_menu()
        elif btn == self.btn_win_next:
            self.trigger_next()
        elif btn == self.btn_win_menu:
            self.trigger_menu()

    def hide_all(self):
        self.main_menu.enabled = False
        self.level_menu.enabled = False
        self.instr_menu.enabled = False
        self.end_menu.enabled = False
        self.win_menu.enabled = False
        self.bg_panel.enabled = False

    def refresh_unlocks(self):
        self.btn_lvl_2.set_disabled(self.max_unlocked_level < 2)
        self.btn_lvl_3.set_disabled(self.max_unlocked_level < 3)
        self.btn_lvl_4.set_disabled(self.max_unlocked_level < 4)

    def show_main_menu(self):
        self.hide_all()
        self.active_menu = 'main'
        self.menu_index = 0
        self.bg_panel.enabled = True
        self.main_menu.enabled = True

    def show_level_menu(self):
        self.hide_all()
        self.refresh_unlocks()
        self.active_menu = 'levels'
        self.menu_index = 0
        self.bg_panel.enabled = True
        self.level_menu.enabled = True

    def show_instructions(self):
        self.hide_all()
        self.active_menu = 'instr'
        self.menu_index = 0
        self.bg_panel.enabled = True
        self.instr_menu.enabled = True

    def show_game_over(self, score):
        self.hide_all()
        self.active_menu = 'end'
        self.menu_index = 0
        self.bg_panel.enabled = True
        self.end_menu.enabled = True
        self.final_score_text.text = f'Wynik: {int(score)} pkt'

    def show_win_screen(self, score, current_level=1):
        self.hide_all()
        self.active_menu = 'win'
        self.menu_index = 0
        self.bg_panel.enabled = True
        self.win_menu.enabled = True
        self.win_score_text.text = f'Wynik: {int(score)} pkt'

    def start_game(self, level):
        self.active_menu = None
        self.bg_panel.enabled = False
        self.hide_all()
        self.start_callback(level)

    def trigger_restart(self):
        self.active_menu = None
        self.bg_panel.enabled = False
        self.hide_all()
        self.restart_callback()

    def trigger_next(self):
        self.active_menu = None
        self.bg_panel.enabled = False
        self.hide_all()
        self.next_callback()

    def trigger_menu(self):
        if self.menu_callback:
            self.menu_callback()

    def show_bonus_popup(self):
        bonus_popup = Text(text='+10 pkt', parent=camera.ui, position=(-0.8, 0.4), scale=1.5, color=Palette.TEXT_BONUS, origin=(-0.5, 0.5))
        bonus_popup.animate_scale(1.5, duration=0.2, curve=curve.out_back)

        invoke(bonus_popup.animate_position, (-0.8, 0.45), duration=0.3, curve=curve.in_sine, delay=1.0)
        invoke(bonus_popup.animate_color, color.clear, duration=0.3, delay=1.0)
        invoke(destroy, bonus_popup, delay=1.3)

    def update_power_bar(self, power):
        self.power_bar_bg.enabled = True
        clamped_power = min(power, 1.0)
        self.power_bar_fill.scale_x = clamped_power * 0.98
        self.power_bar_bg.position = (self.base_bar_x, self.base_bar_y)

        if power <= 0.33: self.power_bar_fill.color = Palette.POWER_WEAK
        elif power <= 0.66: self.power_bar_fill.color = Palette.POWER_GOOD
        elif power <= 1.0: self.power_bar_fill.color = Palette.POWER_PERFECT
        else:
            self.power_bar_fill.color = Palette.POWER_TOO_STRONG

            # animacja trzęsienia
            shake_intensity = 0.008
            shake_x = self.base_bar_x + random.uniform(-shake_intensity, shake_intensity)
            shake_y = self.base_bar_y + random.uniform(-shake_intensity, shake_intensity)
            self.power_bar_bg.position = (shake_x, shake_y)

    def hide_power_bar(self):
        self.power_bar_bg.enabled = False
        self.power_bar_bg.position = (self.base_bar_x, self.base_bar_y)