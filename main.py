from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.clock import Clock

from exercise import Exercise
from preset import Preset

import pickle

class RV(RecycleView):
    list = ObjectProperty(None)


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    pass


class SelectableLabel(RecycleDataViewBehavior, Label):
    """ Add selection support to the Label """
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    obj = None

    def refresh_view_attrs(self, rv, index, data):
        """ Catch and handle the view changes """
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        """ Add selection on touch down """
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """ Respond to the selection of items in the view. """
        self.selected = is_selected
        if self.selected:
            app = MainApp.get_running_app()
            if app.root.current == 'edit_preset':
                self.parent.parent.parent.parent.on_select()
            if app.root.current == 'start' and self.parent is not None:
                self.parent.parent.parent.parent.edit_button.disabled = False
                self.parent.parent.parent.parent.copy_button.disabled = False
                self.parent.parent.parent.parent.remove_button.disabled = False
                self.parent.parent.parent.parent.start_button.disabled = False


# Screens
class StartingScreen(Screen):
    preset_list = ObjectProperty(None)
    edit_button = ObjectProperty(None)
    copy_button = ObjectProperty(None)
    remove_button = ObjectProperty(None)
    start_button = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(StartingScreen, self).__init__(**kwargs)
        self.fill_data()

    def on_enter(self, *args):
        self.fill_data()

    def edit(self):
        MainApp.get_running_app().current_preset = self.preset_list.data[self.preset_list.list.selected_nodes[0]]['obj']

    def copy(self):
        orig = self.preset_list.data[self.preset_list.list.selected_nodes[0]]['obj']
        MainApp.get_running_app().presets.append(Preset(orig.name, orig.exercises))
        self.fill_data()

    def remove(self):
        MainApp.get_running_app().presets.remove(self.preset_list.data[self.preset_list.list.selected_nodes[0]]['obj'])
        self.fill_data()
        if len(self.preset_list.data) == 0:
            self.copy_button.disabled = True
            self.edit_button.disabled = True
            self.remove_button.disabled = True
            self.start_button = True

    def start_training(self):
        MainApp.get_running_app().current_preset = self.preset_list.data[self.preset_list.list.selected_nodes[0]]['obj']

    def fill_data(self):
        self.preset_list.data = [{'text': item.name, 'obj': item} for item in MainApp.get_running_app().presets]


class EditPresetScreen(Screen):
    preset_name = ObjectProperty(None)
    grid = ObjectProperty(None)
    preset_exercises = ObjectProperty(None)
    exercise_name = ObjectProperty(None)
    exercise_brk = ObjectProperty(None)
    exercise_reps = ObjectProperty(None)
    exercise_time = ObjectProperty(None)
    toggle_button = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(EditPresetScreen, self).__init__(**kwargs)
        self.exercise_time.bind(text=self.format_time)
        self.exercise_brk.bind(text=self.format_time)
        self.exercise_reps.bind(text=self.format_int)
        self.toggle_button.state = "down"

    def on_pre_enter(self, *args):
        app = MainApp.get_running_app()
        if app.current_preset is not None:
            self.preset_name.text = app.current_preset.name
            labels = [f"{item.__str__()} with {item.brk}s break" for item in app.current_preset.exercises]
            self.preset_exercises.data = [{'text': text, 'obj': obj}
                                          for text, obj in zip(labels, app.current_preset.exercises)]
        else:
            self.preset_name.text = 'new_preset'
            self.preset_exercises.data = []

    def on_select(self):
        if len(self.preset_exercises.list.selected_nodes) > 0:
            selected_ex = self.preset_exercises.data[self.preset_exercises.list.selected_nodes[0]]
            print(selected_ex)
            self.exercise_name.text = selected_ex['obj'].name
            self.exercise_brk.text = f"{selected_ex['obj'].brk}s"
            if selected_ex['obj'].time is not None:
                self.exercise_time.text = f"{selected_ex['obj'].time}s"
                self.exercise_reps.text = "0"
                self.exercise_reps.disabled = True
                self.toggle_button.state = "normal"
            else:
                self.exercise_reps.text = str(selected_ex['obj'].reps)
                self.exercise_time.text = "0s"
                self.exercise_time.disabled = True
                self.toggle_button.state = "down"

    def on_leave(self, *args):
        app = MainApp.get_running_app()
        app.current_exercise_index = None
        app.current_preset = None
        self.clear_fields()

    def save_exercise(self):
        if len(self.preset_exercises.list.selected_nodes) > 0:
            index = self.preset_exercises.list.selected_nodes[0]
            new_ex = self.build_exercise()
            self.preset_exercises.data[index] = {'text': f"{new_ex.__str__()} with {new_ex.brk}s break", 'obj': new_ex}
        elif self.build_exercise() is not None:
            new_ex = self.build_exercise()
            text = f"{new_ex.__str__()}  with {new_ex.brk}s break"
            self.preset_exercises.data.append({'text': text, 'obj': new_ex})
        self.clear_fields()

    def save(self):
        MainApp.get_running_app().save_preset(Preset(self.preset_name.text, self.get_data()))

    def add(self):
        self.preset_exercises.list.clear_selection()
        self.exercise_name.text = "new_exercise"
        self.exercise_brk.text = "30s"
        self.exercise_time.text = "15s"
        self.toggle_button.state = "down"
        self.exercise_reps.text = "15"

    def clear_fields(self):
        self.preset_exercises.list.clear_selection()
        self.exercise_name.text = ""
        self.exercise_brk.text = ""
        self.exercise_time.text = ""
        self.toggle_button.state = "down"
        self.exercise_reps.text = ""

    def delete(self):
        if len(self.preset_exercises.list.selected_nodes) > 0:
            self.preset_exercises.data.remove(self.preset_exercises.data[self.preset_exercises.list.selected_nodes[0]])
            self.clear_fields()

    def on_toggle_button_state(self, button):
        if button.state == "normal":
            button.text = "exercise duration"
            self.exercise_time.disabled = False
            self.exercise_reps.disabled = True
        else:
            button.text = "exercise repetitions"
            self.exercise_reps.disabled = False
            self.exercise_time.disabled = True

    def get_data(self):
        return [item['obj'] for item in self.preset_exercises.data]

    def format_time(self, instance, value: str):
        """ formatting time fields and allow to spell only numbers """
        instance.text = self.clear_s(value) + "s"

    def format_int(self, instance, value):
        instance.text = self.clear_s(value)

    def clear_s(self, string):
        """ remove all 's' characters in string """
        return ''.join([char for char in string if char.isdigit()])

    def build_exercise(self):
        """ build new exercise object depending on text inputs values """
        try:
            brk = int(self.clear_s(self.exercise_brk.text))
            if self.toggle_button.state == "normal":
                time = int(self.clear_s(self.exercise_time.text))
                reps = None
            else:
                reps = int(self.exercise_reps.text)
                time = None
            return Exercise(name=self.exercise_name.text,
                            brk=brk,
                            time=time,
                            reps=reps
                            )
        except Exception as ex:
            print(ex)
            return None


class TrainingScreen(Screen):
    timer = ObjectProperty(None)
    btn = ObjectProperty(None)
    exercise_name = ObjectProperty(None)
    auto_btn = ObjectProperty(None)
    current_exercise = None
    current_time = None
    is_break = None

    def on_enter(self, *args):
        self.current_exercise = MainApp.get_running_app().current_preset.exercises[0]
        self.is_break = False
        self.check_exercise_type()

    def on_leave(self, *args):
        self.current_exercise = None
        self.current_time = None
        try:
            Clock.unschedule(self.update)
        except Exception as ex:
            print(ex)
        MainApp.get_running_app().current_preset = None
        self.auto_btn.state = "normal"

    def check_exercise_type(self):
        if self.current_exercise is not None:
            self.exercise_name.text = self.current_exercise.name
            if self.current_exercise.reps is None and self.auto_btn.state == "normal":
                self.btn.text = "Start"
                self.timer.text = str(self.current_exercise.time)
            elif self.current_exercise.reps is None and self.auto_btn.state == "down":
                self.btn.text = "Pause"
                self.timer.text = str(self.current_exercise.time)
                self.current_time = self.current_exercise.time
                Clock.schedule_interval(self.update, 1)
            else:
                Clock.unschedule(self.update)
                self.timer.text = str(self.current_exercise.reps)
                self.btn.text = "Next"

    def on_click(self, *args):
        if self.btn.text == "Start":
            self.current_time = self.current_exercise.time
            Clock.schedule_interval(self.update, 1)
            self.btn.text = "Pause"
        elif self.btn.text == "Pause":
            Clock.unschedule(self.update)
            self.btn.text = "Resume"
        elif self.btn.text == "Resume":
            Clock.schedule_interval(self.update, 1)
            self.btn.text = "Pause"
        elif self.btn.text == "Next":
            self.next()
        elif self.btn.text == "Restart":
            self.current_exercise = MainApp.get_running_app().current_preset.exercises[0]
            self.check_exercise_type()

    def update(self, tick):
        if self.current_time is not None and self.current_time > 0:
            self.current_time -= 1
            self.timer.text = str(self.current_time)
        elif self.current_time == 0 and self.is_break:
            Clock.unschedule(self.update)
            self.next()
        elif self.current_time == 0 and not self.is_break:
            self.start_break()

    def start_break(self):
        self.current_time = self.current_exercise.brk
        self.timer.text = str(self.current_time)
        self.exercise_name.text = "Break"
        self.is_break = True

    def next(self):
        try:
            preset = MainApp.get_running_app().current_preset
            self.is_break = False
            self.current_exercise = preset.exercises[preset.exercises.index(self.current_exercise) + 1]
            self.check_exercise_type()
        except:
            self.timer.text = "You completed all exercises.\nCongratulations!"
            Clock.unschedule(self.update)
            self.btn.text = "Restart"



# App
class MainApp(App):
    presets = []
    current_preset = None

    def build(self):
        sm = ScreenManager()
        sm.add_widget(StartingScreen(name='start'))
        sm.add_widget(EditPresetScreen(name='edit_preset'))
        sm.add_widget(TrainingScreen(name='training'))

        return sm

    def save_preset(self, new_preset: Preset):
        if self.current_preset is not None:
            p_id = self.presets.index(self.current_preset)
            self.presets[p_id].excercises = new_preset.exercises
            self.presets[p_id].name = new_preset.name
            self.current_preset = None
        else:
            self.presets.append(new_preset)

    def on_start(self):
        try:
            with open("config.pickle", "rb") as file:
                self.presets = pickle.load(file)
        except Exception as ex:
            print(ex)
            self.presets = []

    def on_stop(self):
        try:
            with open("config.pickle", "wb") as file:
                pickle.dump(self.presets, file)
        except Exception as ex:
            print(ex)


if __name__ == '__main__':
    MainApp().run()
