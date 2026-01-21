# tot_console.py
import json
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.boxlayout import BoxLayout
import ast
import logging
#import serial
#import RPi.GPIO as GPIO
import os
from time import sleep
#import paho.mqtt.client as mqtt

configmode = False

class TotFloatLayout(App):
       global configmode
       
       def select_file(self):
            # Create a box layout for the file chooser and buttons
            box = BoxLayout(orientation='vertical')
            filechooser = FileChooserListView(path='sfx')  # Start in sfx directory
            box.add_widget(filechooser)
            
            # Add buttons
            btn_layout = BoxLayout(size_hint_y=None, height=50)
            cancel_btn = Button(text='Cancel')
            select_btn = Button(text='Select')
            btn_layout.add_widget(cancel_btn)
            btn_layout.add_widget(select_btn)
            box.add_widget(btn_layout)
            
            # Create popup
            popup = Popup(title='Pick a sound file...', content=box, size_hint=(0.9, 0.9))
            
            # Bind buttons
            cancel_btn.bind(on_press=popup.dismiss)
            select_btn.bind(on_press=lambda x: self.on_file_selected(filechooser.selection, popup))
            
            popup.open()

       def on_file_selected(self, selection, popup):
            popup.dismiss()
            if selection and self.current_button:
                selected_file = os.path.basename(selection[0])
                button_dict[self.current_button][6] = selected_file
                print(f"Updated button {self.current_button} to {selected_file}")
                # Save to json
                with open('tot_test.json', 'w') as f:
                    json.dump(button_dict, f, indent=4)
                self.statline.text = f"Button {self.current_button} updated to {selected_file}"
            else:
                print("No file selected")
            self.current_button = None

       
       def build(self):
            self.title = 'Tot Console Test'
            Window.size = (800, 600)
            self.layout = FloatLayout()
            self.current_button = None
            self.buttons = {}

            self.statline = Label(text='Status: Ready', size_hint=(1, 0.1), pos_hint={'x':0, 'y':0})
            self.layout.add_widget(self.statline)

            for i in range(1, 31):
                item = button_dict.get(i)
                if item:
                    btn = Button(text=str(item[3]),
                       background_color = ast.literal_eval(item[4]),
                       size_hint=(0.22, 0.22),
                       pos_hint={'x': float(item[1]), 'y': float(item[2])})
                    btn.bind(on_press=lambda instance, i=i: self.butt_pressed(i))                  
                    self.layout.add_widget(btn)
                    self.buttons[i] = btn              
                        
            return self.layout

       def butt_pressed(self, button_id):
              #rint(f"Button with data '{item[0]}' pressed!")
              global configmode
              

              item = button_dict.get(button_id)
              if not item:
                  return       
              if item[5] == "SND":
                  sound_file = item[6]
                  if configmode == False:
                       
                        self.statline.text = f"Playing sound: {sound_file}"
                        ### need have an exeption here if file not found
                        try:
                            os.system('aplay --buffer-size=800000 sfx/' + sound_file + '&')
                            
                            # omx not working properly in fedora test environment. Pi only
                            #os.system('omxplayer --audio_fifo 15 sfx/' + sound_file + '&')

                        except FileNotFoundError:
                            self.statline.text = f"Error playing sound, file not found: {e}"
                        else:
                            self.statline.text = f"Playing sound: {sound_file}"
                  else:
                        self.statline.text = f"Config mode: ON {sound_file}"
                        self.current_button = button_id
                        self.select_file()
                        self.buttons[26].background_color = (0, 0, 0, 1)  # black
                        configmode = False

              if item[5] == "EFF":
                  effect_name = item[6]
                  self.statline.text = f"Triggering effect: {effect_name}"
              
              if item[5] == "MQTT":
                  mtopic = item[6]
                  mpayload = item[7]
                  self.statline.text = f"MQTT command: {mtopic}, {mpayload}"

              if item[5] == "MENU":
                  menu_name = item[6]
                  configmode = not configmode
                  if configmode:
                      self.buttons[button_id].background_color = (1, 0, 0, 1)  # red
                      self.statline.text = f"Configuring button, click button to change"
                  else:
                      self.buttons[button_id].background_color = (0, 0, 0, 1)  # black
                      self.statline.text = "Status: Ready"

              if item[0] == "sound11" :
                   Window.size = (800,600)

# functions ===========================================================
def on_log(client, userdata, level, buf):
      logging.info(buf)

def on_connect(client, userdata, flags, rc):
      if rc==0 :
         client_connected_flag = True
         logging.info("Connected ok")
      else :
          logging.info("Bad connection returned code " + str(rc))
          logging.info("Client loop stopped")
          client.loop_stop()

def on_disconnect(client, userdata, rc):
      logging.info("Disconnect ok " + str(rc))

def on_publish(client, userdata, mid):
      logging.info("In on_publish callback, data = " + str(mid))



if __name__ == '__main__':
    configmode = False

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