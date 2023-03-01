from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty

from exercise import Exercise
from preset import Preset


class PresetListContainer(GridLayout):
    def __init__(self, **kwargs):
        super(PresetListContainer, self).__init__(**kwargs)
        for item in MainApp.get_running_app().presets:
            self.add_widget(PresetBoxLayout(item.name))
        self.cols = 1
        self.hint_size_y = None
        self. spacing = 10
        self.padding = 10
        self.height = self.minimum_height


class ExerciseListContainer(GridLayout):
    def __init__(self, **kwargs):
        super(ExerciseListContainer, self).__init__(**kwargs)
        app = MainApp.get_running_app()
        if app.current_preset is not None:
            for item in app.current_preset.exercises:
                self.add_widget(PresetBoxLayout(item))
        self.cols = 1
        self.hint_size_y = None
        self. spacing = 10
        self.padding = 10
        self.height = self.minimum_height


class PresetBoxLayout(BoxLayout):
    def __init__(self, *args, **kwargs):
        super(PresetBoxLayout, self).__init__(**kwargs)
        self.add_widget(Label(text=args[0]))
        self.size_hint = (1, None)
        self.height = 130


class ExerciseBoxLayout(BoxLayout):
    def __init__(self, *args, **kwargs):
        super(ExerciseBoxLayout, self).__init__(**kwargs)
        self.exercise = args[0]
        self.add_widget(Label(text=self.exercise.name))

        self.size_hint = (1, None)
        self.height = 130


class StartingScreen(Screen):
    pass


class EditPresetScreen(Screen):
    preset_name = ObjectProperty(None)
    preset_exercises = []

    def __init__(self, *args, **kwargs):
        super(EditPresetScreen, self).__init__(**kwargs)
        app = MainApp.get_running_app()
        if len(args) > 0 and args[0].isinstance(Preset):
            app.current_preset = args[0]
            self.preset_exercises = args[0].exercises
            self.preset_name.text = app.current_preset.name
        else:
            self.preset_name.text = 'new_preset'

    def save(self):
        MainApp.get_running_app().save_preset(Preset(self.preset_name.text, self.preset_exercises))

    def delete(self):
        pass


class EditExerciseScreen(Screen):
    exercise_name = ObjectProperty(None)
    exercise_brk = ObjectProperty(None)
    exercise_reps = ObjectProperty(None)
    exercise_time = ObjectProperty(None)
    toggle_button = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(EditExerciseScreen, self).__init__(**kwargs)
        app = MainApp.get_running_app()
        if app.current_exercise is not None:
            self.exercise_name.text = app.current_exercise.name
            self.exercise_brk.text = f"{app.current_exercise.brk}s"
            if app.current_exercise.time is not None:
                self.exercise_time.text = f"{app.current_exercise.time}s"
                self.exercise_reps.disabled = True
            else:
                self.exercise_reps.text = str(app.current_exercise.reps)
                self.exercise_time.disabled = True
        else:
            self.toggle_button.state = "normal"
            self.toggle_button.text = "exercise duration"
            self.exercise_name.text = "new_exercise"
            self.exercise_brk.text = "15s"
            self.exercise_time.text = "45s"
            self.exercise_reps.disabled = True
            self.exercise_reps.text = "30"
            self.exercise_brk.bind(text=self.format_time)
            self.exercise_brk.bind(text=self.format_time)

    def on_toggle_button_state(self, button):
        if button.state == "normal":
            button.text = "exercise duration"
            self.exercise_time.disabled = False
            self.exercise_reps.disabled = True
        else:
            button.text = "exercise repetitions"
            self.exercise_reps.disabled = False
            self.exercise_time.disabled = True

    def format_time(self, instance, value: str):
        try:
            new_val = self.clear_s(value)
            print(new_val)
            int(new_val)
            instance.text = new_val + "s"
        except:
            instance.text = "s"

    def clear_s(self, string):
        return string.replace("s", "")



class TrainingScreen(Screen):
    pass


class MainApp(App):
    presets = []
    current_preset = None
    current_exercise = None

    def build(self):
        sm = ScreenManager()
        sm.add_widget(StartingScreen(name='start'))
        sm.add_widget(EditPresetScreen(name='edit_preset'))
        sm.add_widget(EditExerciseScreen(name='edit_exercise'))
        sm.add_widget(TrainingScreen(name='training'))

        return sm

    def add_preset(self, name, exercises):
        self.current_preset = Preset(name, exercises)
        self.presets.append(self.current_preset)

    def save_preset(self, new_preset: Preset):
        if self.current_preset is not None:
            self.presets.remove(self.current_preset)
            self.current_preset = None
        self.presets.append(new_preset)


if __name__ == '__main__':
    MainApp().run()
