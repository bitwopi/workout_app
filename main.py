from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, BooleanProperty

from exercise import Exercise
from preset import Preset


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    pass


class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    obj = None

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if self.selected:
            MainApp.get_running_app().current_exercise = self.index



# Screens
class StartingScreen(Screen):
    pass


class EditPresetScreen(Screen):
    preset_name = ObjectProperty(None)
    sv = ObjectProperty(None)
    grid = ObjectProperty(None)
    preset_exercises = ObjectProperty(None)
    exercise_name = ObjectProperty(None)
    exercise_brk = ObjectProperty(None)
    exercise_reps = ObjectProperty(None)
    exercise_time = ObjectProperty(None)
    toggle_button = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(EditPresetScreen, self).__init__(**kwargs)
        self.exercise_brk.bind(text=self.format_time)
        self.exercise_brk.bind(text=self.format_time)

    def on_pre_enter(self, *args):
        app = MainApp.get_running_app()
        if app.current_preset is not None:
            self.preset_name.text = app.current_preset.name
            labels = []
            for item in app.current_preset.exercises:
                if item.reps is not None:
                    labels.append(f"{item.name}({item.reps} reps) with {item.brk}s break")
                else:
                    labels.append(f"{item.name}({item.time}s) with {item.brk}s break")
            self.preset_exercises.data = [{'text': text, 'obj': obj}
                                          for text, obj in zip(labels, app.current_preset.exercises)]
        else:
            self.preset_name.text = 'new_preset'
            self.preset_exercises.data = []

    def on_touch_down(self, touch):
        if len(self.preset_exercises.selected) > 0:
            app = MainApp.get_running_app()
            selected_ex = self.preset_exercises.selected[0]
            if selected_ex.index != app.current_exercise_index:
                self.exercise_name.text = selected_ex.obj.name
                self.exercise_brk.text = f"{selected_ex.obj.brk}s"
                if selected_ex.obj.time is not None:
                    self.exercise_time.text = f"{selected_ex.obj.time}s"
                    self.exercise_reps.text = "0"
                    self.exercise_reps.disabled = True
                    self.toggle_button.state = "normal"
                else:
                    self.exercise_time.text = str(selected_ex.obj.reps)
                    self.exercise_time.text = "0s"
                    self.exercise_time.disabled = True
                    self.toggle_button.state = "down"

    def on_leave(self, *args):
        app = MainApp.get_running_app()
        app.current_exercise_index = None
        app.current_preset = None

    def save_exercise(self):
        if len(self.preset_exercises.selected) > 0:
            selected_ex = self.preset_exercises.selected[0]
            selected_ex.obj = self.build_exercise()
            if selected_ex.obj.time is None:
                selected_ex.text = f"{selected_ex.obj.name}({selected_ex.obj.time}s)  with {selected_ex.obj.brk}s break)"
            else:
                selected_ex.text = f"{selected_ex.obj.name}({selected_ex.obj.time} reps)  with {selected_ex.obj.brk}s " \
                                   f"break)"
        else:
            new_ex = self.build_exercise()
            if new_ex.time is None:
                text = f"{new_ex.name}({new_ex.time}s)  with {new_ex.brk}s break)"
            else:
                text = f"{new_ex.name}({new_ex.reps} reps)  with {new_ex.brk}s break)"
            self.preset_exercises.data.append({'text': text, 'obj': new_ex})
        self.preset_exercises.clear_selection()
        MainApp.get_running_app().current_exercise_index = None

    def save(self):
        MainApp.get_running_app().save_preset(Preset(self.preset_name.text, self.get_data()))

    def add(self):
        self.preset_exercises.clear_selection()
        MainApp.get_running_app().current_exercise_index = None
        self.exercise_name.text = "new_exercise"
        self.exercise_brk.text = "30s"
        self.exercise_time.text = "15s"
        self.toggle_button.state = "down"
        self.exercise_reps.text = "15"
        self.exercise_time.disabled = True

    def delete(self):
        if len(self.preset_exercises.selected) > 0:
            self.preset_exercises.data.remove(self.preset_exercises.selected[0])
            self.preset_exercises.clear_selection()
            MainApp.get_running_app().current_exercise_index = None

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
        return [item.obj for item in self.preset_exercises.data]

    def format_time(self, instance, value: str):
        """ formatting time fields and allow to spell only numbers """
        try:
            new_val = self.clear_s(value)
            print(new_val)
            int(new_val)
            instance.text = new_val + "s"
        except:
            instance.text = "s"

    def clear_s(self, string):
        """ remove all 's' characters in string """
        return string.replace("s", "")

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
        except:
            return None



class TrainingScreen(Screen):
    pass


# App
class MainApp(App):
    presets = []
    current_preset = None
    current_exercise_index = None

    def build(self):
        sm = ScreenManager()
        sm.add_widget(StartingScreen(name='start'))
        sm.add_widget(EditPresetScreen(name='edit_preset'))
        sm.add_widget(TrainingScreen(name='training'))

        return sm

    def add_preset(self, name, exercises):
        self.current_preset = Preset(name, exercises)
        self.presets.append(self.current_preset)

    def save_preset(self, new_preset: Preset):
        if self.current_preset is not None:
            p_id = self.presets.index(self.current_preset)
            self.current_preset = None
            self.presets[p_id] = new_preset
            self.temp_preset = None
        else:
            self.presets.append(new_preset)


if __name__ == '__main__':
    MainApp().run()
