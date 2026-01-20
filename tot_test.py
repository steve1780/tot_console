# tot_console.py
import json
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
import ast

class TotFloatLayout(App):

       def build(self):
                 self.title = 'Tot Console Test'
                 Window.size = (800, 600)
                 self.layout = FloatLayout()

                 for i in range(1, 26):
                    item = button_dict.get(i)
                    if item:
                        btn = Button(text=str(item[3]), 
                            background_color = ast.literal_eval(item[4]), 
                            size_hint=(0.19, 0.19),
                             pos_hint={'x': float(item[1]), 'y': float(item[2])})
                        btn.bind(on_press=lambda instance, item=item: self.butt_pressed(item))                  
                        self.layout.add_widget(btn)
                        
                 return self.layout

       def butt_pressed(self, item):
              #rint(f"Button with data '{item[0]}' pressed!")       
              if item[5] == "SND":
                  sound_file = item[6]
                  print(f"Playing sound: {sound_file}")
              if item[5] == "EFF":
                  effect_name = item[6]
                  print(f"Triggering effect: {effect_name}")
              if item[5] == "MQTT":
                  light_pattern = item[6]
                  print(f"Activating light pattern: {light_pattern}")
                  Window.size = (1200,1000)
              if item[0] == "sound11" :
                   Window.size = (800,600)




if __name__ == '__main__':

    # with open('config.json') as fptr:
    #     config = json.load(fptr)

    # SERVER = config["server"]
    # SSID = config["ssid"]
    # PWD = config["password"]
    # pflag = config["printflag"]

    with open('tot_test.json') as fptr:
        button_dict = json.load(fptr)

    # swap the json string key index for int that we need in the kv file
    button_dict = {int(k): v for k, v in button_dict.items() }
    

    TotFloatLayout().run()