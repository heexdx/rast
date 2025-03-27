from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
import random

class GuessGame(App):
    def build(self):
        self.number = random.randint(1, 20)
        self.layout = BoxLayout(orientation='vertical')
        
        self.label = Label(text="خمن رقم بين 1 و20", font_size=30)
        self.entry = TextInput(font_size=30, multiline=False)
        self.button = Button(text="تخمين!", font_size=30)
        self.button.bind(on_press=self.check_guess)
        
        self.layout.add_widget(self.label)
        self.layout.add_widget(self.entry)
        self.layout.add_widget(self.button)
        return self.layout

    def check_guess(self, instance):
        try:
            guess = int(self.entry.text)
            if guess == self.number:
                self.show_popup("مبروك!", "لقد فزت! الرقم كان " + str(self.number))
                self.number = random.randint(1, 20)
            elif guess < self.number:
                self.label.text = "الرقم أكبر من ذلك!"
            else:
                self.label.text = "الرقم أصغر من ذلك!"
        except:
            self.show_popup("خطأ", "من فضلك أدخل رقماً صحيحاً")

    def show_popup(self, title, message):
        box = BoxLayout(orientation='vertical')
        box.add_widget(Label(text=message))
        btn = Button(text="حسناً")
        popup = Popup(title=title, content=box)
        btn.bind(on_press=popup.dismiss)
        box.add_widget(btn)
        popup.open()

GuessGame().run()
