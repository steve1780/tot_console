# tot_console.py
import json
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
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

       def select_file_for_config(self, instance):
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
            select_btn.bind(on_press=lambda x: self.on_file_selected_for_config(filechooser.selection, popup))
            
            popup.open()

       def on_file_selected_for_config(self, selection, popup):
            popup.dismiss()
            if selection:
                self.selected_file = os.path.basename(selection[0])
                print(f"Selected file: {self.selected_file}")
            else:
                print("No file selected")

       def config_dialog(self, button_id):
            item = button_dict.get(button_id)
            if not item:
                return
            
            # Create popup
            content = BoxLayout(orientation='vertical', spacing=10, padding=10)
            popup = Popup(title='Configure Button', content=content, size_hint=(0.8, 0.9))
            
            # Label name
            content.add_widget(Label(text='Button Label:', size_hint_y=None, height=30))
            label_input = TextInput(text=item[3], multiline=False)
            content.add_widget(label_input)
            
            # Output type
            content.add_widget(Label(text='Output Type:', size_hint_y=None, height=30))
            output_box = BoxLayout(size_hint_y=None, height=40)
            output_buttons = []
            output_options = ['3.5" #1', '3.5" #2', 'Amp1', 'Amp2']
            output_map = {'3.5" #1': 'A1', '3.5" #2': 'A2', 'Amp1': 'Amp1', 'Amp2': 'Amp2'}
            current_output = item[8] if len(item) > 8 else 'A1'
            reverse_map = {v: k for k, v in output_map.items()}
            for opt in output_options:
                btn = ToggleButton(text=opt, group='output', size_hint_x=0.25)
                if reverse_map.get(current_output) == opt:
                    btn.state = 'down'
                output_box.add_widget(btn)
                output_buttons.append(btn)
            content.add_widget(output_box)
            
            # File selector
            file_button = Button(text='Select Sound File', size_hint_y=None, height=40)
            file_button.bind(on_press=self.select_file_for_config)
            content.add_widget(file_button)
            self.selected_file = item[6] if item[5] == 'SND' else None
            
            # Effect type
            content.add_widget(Label(text='Effect Type:', size_hint_y=None, height=30))
            effect_box = BoxLayout(size_hint_y=None, height=40)
            effect_buttons = []
            effect_options = ['Sfx', 'MQTT', 'Macro']
            effect_map = {'Sfx': 'SND', 'MQTT': 'MQTT', 'Macro': 'EFF'}
            current_effect = effect_map.get(item[5], 'Sfx')
            reverse_effect_map = {v: k for k, v in effect_map.items()}
            for opt in effect_options:
                btn = ToggleButton(text=opt, group='effect', size_hint_x=0.33)
                if reverse_effect_map.get(item[5]) == opt:
                    btn.state = 'down'
                effect_box.add_widget(btn)
                effect_buttons.append(btn)
            content.add_widget(effect_box)
            
            # MQTT fields
            self.topic_input = TextInput(hint_text='Topic', text=item[6] if item[5] == 'MQTT' else '', size_hint_y=None, height=30)
            self.payload_input = TextInput(hint_text='Payload', text=item[7] if len(item) > 7 and item[5] == 'MQTT' else '', size_hint_y=None, height=30)
            content.add_widget(self.topic_input)
            content.add_widget(self.payload_input)
            
            # Initially hide MQTT fields if not MQTT
            if item[5] != 'MQTT':
                self.topic_input.opacity = 0
                self.payload_input.opacity = 0
            
            # Bind effect buttons to show/hide MQTT fields
            for btn in effect_buttons:
                btn.bind(on_press=self.on_effect_selected)
            
            # OK Cancel
            btn_box = BoxLayout(size_hint_y=None, height=50)
            cancel = Button(text='Cancel')
            ok = Button(text='OK')
            btn_box.add_widget(cancel)
            btn_box.add_widget(ok)
            content.add_widget(btn_box)
            
            cancel.bind(on_press=popup.dismiss)
            ok.bind(on_press=lambda x: self.save_config(popup, button_id, label_input.text, output_buttons, effect_buttons, output_map, effect_map))
            
            popup.open()

       def on_effect_selected(self, instance):
            if instance.text == 'MQTT':
                self.topic_input.opacity = 1
                self.payload_input.opacity = 1
            else:
                self.topic_input.opacity = 0
                self.payload_input.opacity = 0

       def save_config(self, popup, button_id, label, output_buttons, effect_buttons, output_map, effect_map):
            # Get selected output
            global configmode

            selected_output = None
            for btn in output_buttons:
                if btn.state == 'down':
                    selected_output = btn.text
                    break
            output_code = output_map.get(selected_output, 'A1')
            
            # Get selected effect
            selected_effect = None
            for btn in effect_buttons:
                if btn.state == 'down':
                    selected_effect = btn.text
                    break
            effect_code = effect_map.get(selected_effect, 'SND')
            
            # Update button_dict
            item = button_dict[button_id]
            item[3] = label
            if len(item) < 9:
                item.extend([''] * (9 - len(item)))
            item[8] = output_code
            item[5] = effect_code
            if selected_effect == 'Sfx':
                item[6] = self.selected_file or item[6]
                item[7] = ''
            elif selected_effect == 'MQTT':
                item[6] = self.topic_input.text
                item[7] = self.payload_input.text
            elif selected_effect == 'Macro':
                item[6] = 'macro'  # placeholder
                item[7] = ''
            
            # Update button text
            self.buttons[button_id].text = label
            
            # Save to json
            with open('tot_test.json', 'w') as f:
                json.dump(button_dict, f, indent=4)

            configmode = False
            popup.dismiss()
            self.buttons[26].background_color = (0, 0, 0, 1)  # black
       
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
                       size_hint=(0.18, 0.18),
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
                        self.config_dialog(button_id)

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