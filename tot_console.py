# tot_console.py
import json
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.properties import DictProperty

# Set the window size
Window.size = (800, 600)

class ToTScreen(Widget):
    button_dict = DictProperty({})
    
    def butt_pressed(self, id):
         print(f"Button '{id}' pressed!")
    


class TotConsole(App):
    def build(self):
        #return Builder.load_file('totconsole.kv')
        #Window.show()
        with open('totconsole.json') as fptr:
            button_dict = json.load(fptr)
    
        # swap the json string key index for int that we need in the kv file
        button_dict = {int(k): v for k, v in button_dict.items() }
        print(button_dict)
        return ToTScreen()


    
if __name__ == '__main__':

    with open('config.json') as fptr:
        config = json.load(fptr)
        
    SERVER = config["server"]
    SSID = config["ssid"]
    PWD = config["password"]
    pflag = config["printflag"]


    TotConsole().run()