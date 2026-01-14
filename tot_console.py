# main.py
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.properties import DictProperty

# Set the window size
Window.size = (800, 600)

class ToTScreen(Widget):
    dict = DictProperty({20:"Hanted Sound", 21: "BOOO", 22:"HISS", 23:"SCARE",
                        5:"Hoot", 6: "BOO", 7:"Hoot", 8: "BOO", 9: "YA",
                        10:"Hoot", 11: "BOO", 12:"Hoot", 13: "BOO", 14: "YA",
                        15:"Hoot", 16: "BOO", 17:"Hoot", 18: "BOO", 19: "YA",
                        1:"Hoot", 2: "BOO", 3:"Hoot", 4: "BOO", 5: "YA"                                                
                        })
    
    def butt_pressed(self, id):
         print(f"Button '{id}' pressed!")
    


class TotConsole(App):
    def build(self):
        #return Builder.load_file('totconsole.kv')
        #Window.show()
        return ToTScreen()
        
        


if __name__ == '__main__':
    TotConsole().run()
