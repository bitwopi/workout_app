from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.slider import Slider


# Declare both screens
class StartingScreen(Screen):
    def __init__(self, **kwargs):
        super(StartingScreen, self).__init__(**kwargs)
        sv = ScrollView(always_overscroll=True)
        bl = BoxLayout()
        bl.add_widget(PresetListContainer())
        bl.size_hint_y = None
        bl.height = bl.minimum_height
        sv.add_widget(bl)
        self.add_widget(sv)
        print(MainApp().get_running_app().root)


class PresetListContainer(GridLayout):
    def __init__(self, **kwargs):
        super(PresetListContainer, self).__init__(**kwargs)
        for i in range(20):
            self.add_widget(PresetBoxLayout(str(i)))
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
        bl = BoxLayout()
        bl.spacing = 10
        start_btn = Button(text='start training')
        # start_btn.bind(on_press=self.start_btn_pressed)
        edit_btn = Button(text='edit preset')
        # edit_btn.bind(on_press=self.edit_btn_pressed())
        rm_btn = Button(text='remove preset')
        bl.add_widget(start_btn)
        bl.add_widget(edit_btn)
        bl.add_widget(rm_btn)
        self.add_widget(bl)

    # def start_btn_pressed(*args):
    #     sm.transition.direction = 'left'
    #     sm.current = 'training'
    #
    # def edit_btn_pressed(*args):
    #     sm.transition.direction = 'right'
    #     sm.current = 'edit_preset'


class EditPresetScreen(Screen):
    pass


class EditExerciseScreen(Screen):
    pass


class TrainingScreen(Screen):
    pass


class MainApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(StartingScreen(name='start'))
        sm.add_widget(EditPresetScreen(name='edit_preset'))
        sm.add_widget(EditExerciseScreen(name='edit_exercise'))
        sm.add_widget(TrainingScreen(name='training'))

        return sm


if __name__ == '__main__':
    MainApp().run()
