# tot_console.py
import json
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
import ast

class TotFloatLayout(App):

       def build(self):
            self.title = 'Tot Console Test'
            Window.size = (800, 600)
            self.layout = FloatLayout()

            self.statline = Label(text='Status: Ready', size_hint=(1, 0.1), pos_hint={'x':0, 'y':0})
            self.layout.add_widget(self.statline)

            for i in range(1, 31):
                item = button_dict.get(i)
                if item:
                    btn = Button(text=str(item[3]),
                       background_color = ast.literal_eval(item[4]),
                       size_hint=(0.22, 0.22),
                       pos_hint={'x': float(item[1]), 'y': float(item[2])})
                    btn.bind(on_press=lambda instance, item=item: self.butt_pressed(item))                  
                    self.layout.add_widget(btn)

            # item = button_dict.get(26)
            # btn = Button(text=str(item[3]), 
            #     background_color = ast.literal_eval(item[4]), 
            #     size_hint=(0.15, 0.15),
            #     pos_hint={'x': float(item[1]), 'y': float(item[2])}
            #     )
            # self.layout.add_widget(btn)
            # btn.bind(on_press=lambda instance, item=item: self.butt_pressed(item))                  
                        
            return self.layout

       def butt_pressed(self, item):
              #rint(f"Button with data '{item[0]}' pressed!")       
              if item[5] == "SND":
                  sound_file = item[6]
                  self.statline.text = f"Playing sound: {sound_file}"
              
              if item[5] == "EFF":
                  effect_name = item[6]
                  self.statline.text = f"Triggering effect: {effect_name}"
              
              if item[5] == "MQTT":
                  light_pattern = item[6]
                  print(f"Activating light pattern: {light_pattern}")
                  self.statline.text = f"Activating light pattern: {light_pattern}"

              if item[5] == "MENU":
                  menu_name = item[6]
                  print(f"Opening menu: {menu_name}")
                  self.statline.text = f"Configuring button, click button to change"

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