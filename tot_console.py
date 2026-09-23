# tot_console.py
import json
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.widget import Widget
#from kivy.uix.button import Button
from kivy.properties import DictProperty

# Set the window size
Window.size = (800, 600)

class ToTScreen(Widget):
    button_dict = DictProperty({})


    def __init__(self, button_dict, **kwargs):
        super().__init__(**kwargs)
        self.button_dict = button_dict
        # self.button_dict = {
    # 1: ["sound0",  "LABEL", "Green", "SND", "atatin.wav", "",  "A1"],
    # 2: ["sound1",  "LABEL", "Green", "SND", "whogoes.wav", "",  "A1"],
    # 3: ["sound2",  "LABEL", "Green", "SND", "trouble.wav", "",  "A1"],
    # 4: ["sound3",  "LABEL", "Green", "SND", "mangy.wav", "",  "A1"],
    # 5: ["sound4",  "LABEL", "Green", "SND", "havecandy.wav", "", "A1"],
    # 6: ["sound5",  "LABEL", "Green", "SND", "orders.wav", "",  "A1"],
    # 7: ["sound6",  "LABEL", "Green", "SND", "words.wav", "",  "A1"],
    # 8: ["sound7",  "LABEL", "Green", "SND", "honor.wav", "",  "A1"],
    # 9: ["sound8",  "LABEL", "Green", "SND", "learn.wav", "",  "A1"],
    # 10: ["sound9", "LABEL", "Green", "SND", "candy.wav", "",  "A1"],
    # 11: ["sound10", "LABEL", "Green","SND", "ayee.wav", "",  "A1"],
    # 12: ["sound11", "LABEL", "Green","SND", "am_captain.wav", "", "A1"],
    # 13: ["sound12", "LABEL", "Green","SND", "treats.wav", "", "A1"],
    # 14: ["sound13", "LABEL", "Green","SND", "little_ones.wav", "", "A1"],
    # 15: ["sound14", "LABEL", "Green","SND", "candy.wav", "", "A1"],
    # 16: ["sound15", "LABEL", "Green","SND", "treats.wav", "", "A1"],
    # 17: ["sound16", "LABEL", "Green","SND", "areyoupirates.wav", "", "A1"],
    # 18: ["sound17", "LABEL", "Green","SND", "candy.wav", "", "A1"],
    # 19: ["sound18", "LABEL", "Green","SND", "ayee.wav", "", "A1"],
    # 20: ["sound19", "LABEL", "Green","SND", "am_captain.wav", "", "A1"],
    # 21: ["sound20", "LABEL", "Green","SND", "treats.wav", "", "A1"],
    # 22: ["sound21", "LABEL", "Green","SND", "little_ones.wav", "", "A1"],
    # 23: ["sound22", "LABEL", "Green","SND", "candy.wav", "",  "A1"],
    # 24: ["sound23", "LABEL", "Green","SND", "treats.wav", "", "A1"],
    # 25: ["sound24", "LABEL", "Green","SND", "treats.wav", "", "A1"]
# }
        print("Button dictionary loaded:", self.button_dict)



    def butt_pressed(self, id):
         print(f"Button '{id}' pressed!")



class TotConsole(App):
    button_dict = DictProperty({})
    def build(self):
        # pass the button dictionary to the root widget
        self.root = ToTScreen(button_dict=self.button_dict)
        return self.root




if __name__ == '__main__':

    with open('config.json') as fptr:
        config = json.load(fptr)

    SERVER = config["server"]
    SSID = config["ssid"]
    PWD = config["password"]
    pflag = config["printflag"]

    with open('totconsole.json') as fptr:
           button_dict = json.load(fptr)

        # swap the json string key index for int that we need in the kv file
    button_dict = {k: v for k, v in button_dict.items() }
    print(button_dict)

    TotConsole(button_dict=button_dict).run()
    