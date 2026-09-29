# tot_console.py
from fileinput import filename
import json
from kivy.config import Config
# Set desired window size via Config before other Kivy imports
Config.set('graphics', 'width', '1920')
Config.set('graphics', 'height', '1080')
Config.set('graphics', 'resizable', '1')

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
from kivy.uix.slider import Slider
from kivy.metrics import sp
import ast
import logging
#import serial
import paho.mqtt.client as mqtt
import os
from time import sleep


os.environ["KIVY_NO_CONSOLELOG"] = "1"  # Hides logs printed to the console

broker_address = "gamma"
port = 1883

configmode = False
colord = {
    "BLACK": "(0,0,0,1)",
    "YELLOW": "(1,1,0,1)",
    "GREEN": "(0,1,0,1)",
    "BLUE": "(0,0,1,1)",
    "RED": "(1,0,0,1)",
    "ORANGE": "(1,0.5,0,1)",
    "PURPLE": "(0.5,0,0.5,1)",
    "PINK": "(1,0.75,0.8,1)",
    "CYAN": "(0,1,1,1)" 
    }

class TotFloatLayout(App):
       global configmode
       global colord
       # Font scale multiplier (1.0 = 100%). Increase by 60% => 1.6
       FONT_SCALE = 1.6

       def sp_scaled(self, value):
            return sp(value * self.FONT_SCALE)

       def sp_config(self, value):
          """Scale fonts for config dialog: previously 30% larger, now reduced by 15%."""
          # original factor = FONT_SCALE * 1.3; reduce the config dialog fonts by 15% -> *0.85
          config_factor = self.FONT_SCALE * 1.3 * 0.85
          return sp(value * config_factor)

       
       def select_file(self):
            # Create a box layout for the file chooser and buttons
            box = BoxLayout(orientation='vertical')
            filechooser = FileChooserListView(path='sfx')  # Start in sfx directory
            box.add_widget(filechooser)
            
            # Add buttons
            btn_layout = BoxLayout(size_hint_y=None, height=50)
            cancel_btn = Button(text='Cancel', font_size=self.sp_scaled(14))
            select_btn = Button(text='Select', font_size=self.sp_scaled(14))
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
                with open('tot_console.json', 'w') as f:
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
            cancel_btn = Button(text='Cancel', font_size=self.sp_scaled(14))
            select_btn = Button(text='Select', font_size=self.sp_scaled(14))
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
                self.statline.text = f"Selected file: {self.selected_file}"
                if hasattr(self, 'file_button'):
                    self.file_button.text = 'Current Sound File: ' + self.selected_file
                print(f"Selected file: {self.selected_file}")
            else:
                print("No file selected")

       def config_dialog(self, button_id):
            item = button_dict.get(button_id)
            if not item:
                return
            
            # Create popup
            content = BoxLayout(orientation='vertical', spacing=10, padding=10)
            # Make popup slightly taller (approx +15%) so MQTT fields are more usable
            popup = Popup(title='Configure Button', title_size=self.sp_config(18), content=content, size_hint=(0.48, 0.63))
            
            # Label name
            content.add_widget(Label(text='Button Label:', size_hint_y=None, height=30, font_size=self.sp_config(14)))
            label_input = TextInput(text=item[3], multiline=False, font_size=self.sp_config(14))
            content.add_widget(label_input)
            
            # Output type
            content.add_widget(Label(text='Output Type:', size_hint_y=None, height=30, font_size=self.sp_config(14)))
            output_box = BoxLayout(size_hint_y=None, height=40)
            output_buttons = []
            output_options = ['3.5" #1', '3.5" #2', 'Amp1', 'Amp2']
            output_map = {'3.5" #1': 'A1', '3.5" #2': 'A2', 'Amp1': 'Amp1', 'Amp2': 'Amp2'}
            current_output = item[8] if len(item) > 8 else 'A1'
            reverse_map = {v: k for k, v in output_map.items()}
            for opt in output_options:
                btn = ToggleButton(text=opt, group='output', size_hint_x=0.25, font_size=self.sp_config(14))
                if reverse_map.get(current_output) == opt:
                    btn.state = 'down'
                # Make background_color take effect
                btn.background_normal = ''
                btn.background_down = ''
                output_box.add_widget(btn)
                output_buttons.append(btn)
            # Initialize visuals and bind handlers so state updates before handler runs
            for btn in output_buttons:
                btn.background_color = (0.1, 0.6, 0.1, 1) if btn.state == 'down' else (0.3, 0.3, 0.3, 1)
                btn.bind(on_release=lambda inst, obs=output_buttons: self.on_output_selected(inst, obs))
            content.add_widget(output_box)
            
            # File selector
            filename = item[6] 
            self.file_button = Button(text='Current Sound File: '+ filename, size_hint_y=None, height=40, font_size=self.sp_config(14))
            self.file_button.bind(on_release=self.select_file_for_config)
            content.add_widget(self.file_button)
            self.selected_file = item[6] if item[5] == 'SND' else None
            

            # Effect type
            content.add_widget(Label(text='Effect Type:', size_hint_y=None, height=30, font_size=self.sp_config(14)))
            effect_box = BoxLayout(size_hint_y=None, height=40)
            effect_buttons = []
            effect_options = ['Sfx', 'MQTT', 'Macro']
            effect_map = {'Sfx': 'SND', 'MQTT': 'MQTT', 'Macro': 'EFF'}
            current_effect = effect_map.get(item[5], 'Sfx')
            reverse_effect_map = {v: k for k, v in effect_map.items()}
            for opt in effect_options:
                btn = ToggleButton(text=opt, group='effect', size_hint_x=0.33, font_size=self.sp_config(14))
                if reverse_effect_map.get(item[5]) == opt:
                    btn.state = 'down'
                btn.background_normal = ''
                btn.background_down = ''
                effect_box.add_widget(btn)
                effect_buttons.append(btn)
            # Initialize visuals and bind handlers
            for btn in effect_buttons:
                btn.background_color = (0.1, 0.6, 0.1, 1) if btn.state == 'down' else (0.3, 0.3, 0.3, 1)
                btn.bind(on_release=lambda inst, ebs=effect_buttons: (self.on_effect_selected(inst), self.update_effect_visuals(ebs)))
            content.add_widget(effect_box)
            
            # MQTT fields (increase height for readability on touchscreens)
            self.topic_input = TextInput(hint_text='Topic', text=item[6] if item[5] == 'MQTT' else '', size_hint_y=None, height=38, font_size=self.sp_config(14))
            self.payload_input = TextInput(hint_text='Payload', text=item[7] if len(item) > 7 and item[5] == 'MQTT' else '', size_hint_y=None, height=38, font_size=self.sp_config(14))
            content.add_widget(self.topic_input)
            content.add_widget(self.payload_input)

            # Initially hide MQTT fields if not MQTT (collapse height to avoid empty space)
            if item[5] != 'MQTT':
                self.topic_input.opacity = 0
                self.payload_input.opacity = 0
                self.topic_input.height = 0
                self.payload_input.height = 0
            
            # Bind effect buttons to show/hide MQTT fields (use on_release so ToggleButton state is updated first)
            for btn in effect_buttons:
                btn.bind(on_release=self.on_effect_selected)
            
            # OK Cancel
            btn_box = BoxLayout(size_hint_y=None, height=50)
            cancel = Button(text='Cancel', font_size=self.sp_config(14))
            ok = Button(text='OK', font_size=self.sp_config(14))
            btn_box.add_widget(cancel)
            btn_box.add_widget(ok)
            content.add_widget(btn_box)
            
            cancel.bind(on_press=popup.dismiss)
            ok.bind(on_press=lambda x: self.save_config(popup, button_id, label_input.text, output_buttons, effect_buttons, output_map, effect_map))
            
            popup.open()
            
       def on_effect_selected(self, instance):
            if instance.text == 'MQTT':
             # Reveal and size MQTT fields
             self.topic_input.opacity = 1
             self.payload_input.opacity = 1
             self.topic_input.height = 38
             self.payload_input.height = 38
            else:
             # Hide and collapse MQTT fields
             self.topic_input.opacity = 0
             self.payload_input.opacity = 0
             self.topic_input.height = 0
             self.payload_input.height = 0

       def on_output_selected(self, instance, output_buttons):
          # Update visuals for output toggle buttons so the 'down' state is obvious
          for btn in output_buttons:
             btn.background_color = (0.1, 0.6, 0.1, 1) if btn.state == 'down' else (0.3, 0.3, 0.3, 1)

       def update_effect_visuals(self, effect_buttons):
          for btn in effect_buttons:
             btn.background_color = (0.1, 0.6, 0.1, 1) if btn.state == 'down' else (0.3, 0.3, 0.3, 1)

       def get_color_for_output(self, output_type):
            """Get button color based on output type (A1, A2, Amp1, Amp2)"""
            color_map = {
                'A1': 'GREEN',      # 3.5 #1
                'A2': 'BLUE',       # 3.5 #2
                'Amp1': 'RED',
                'Amp2': 'ORANGE'
            }
            return color_map.get(output_type, 'GREEN')

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
            
            # Update button color based on output type
            color_name = self.get_color_for_output(output_code)
            item[4] = color_name
            
            # Update button text and color
            self.buttons[button_id].text = label
            self.buttons[button_id].background_color = ast.literal_eval(colord[color_name])
            
            # Save to json
            with open('tot_test.json', 'w') as f:
                json.dump(button_dict, f, indent=4)

            popup.dismiss()
       
       def toggle_config_mode(self, instance=None):
            global configmode
            # Simple toggle: flip the configmode flag and update visuals
            configmode = not configmode
            try:
                if configmode:
                    self.config_button.background_color = (0.9, 0.3, 0.3, 1)
                    self.statline.text = 'Config mode: ON'
                else:
                    self.config_button.background_color = (0.3, 0.3, 0.3, 1)
                    self.statline.text = 'Status: Ready'
            except Exception:
                pass

       def on_key_down(self, window, key, scancode=None, codepoint=None, modifiers=None):
            # F1 keycode on many systems is 282; toggle config on F1
            try:
                if key == 282:
                    self.toggle_config_mode()
                    return True
            except Exception:
                pass
            return False

       def apply_volume(self, value):
            pct = max(0, min(100, int(value)))
            self.volume_label.text = f'Volume: {pct}%'
            if hasattr(self, 'volume_slider'):
                self.volume_slider.value = pct
            try:
                os.system(f'amixer set "Master" {pct}% unmute >/dev/null 2>&1 || amixer set "PCM" {pct}% unmute >/dev/null 2>&1')
            except Exception:
                pass

       def set_volume(self, instance, value):
            self.apply_volume(value)

       def build(self):
            self.title = 'Trick Or Treat Console'
            # Window size is configured via Config at import time.
            # Keep Window.size in sync in case runtime change is needed.
            Window.size = (1920, 1080)
            self.layout = FloatLayout()
            self.current_button = None
            self.buttons = {}

            self.layout.canvas.before.clear()
            with self.layout.canvas.before:
                from kivy.graphics import Color, Rectangle
                Color(0.08, 0.08, 0.08, 1)
                Rectangle(pos=self.layout.pos, size=self.layout.size)

            top_bar = BoxLayout(size_hint=(1, 0.08), pos_hint={'x': 0, 'y': 0.92}, padding=(12, 6), spacing=4)
            with top_bar.canvas.before:
                from kivy.graphics import Color, Rectangle
                Color(0.18, 0.18, 0.18, 1)
                Rectangle(pos=top_bar.pos, size=top_bar.size)

            # Config button will be placed at the bottom-left (created later)

            self.volume_label = Label(
                text='Volume: 80%',
                color=(0.95, 0.92, 0.70, 1),
                bold=True,
                size_hint=(None, None),
                size=(120, 44),
                font_size=self.sp_scaled(14),
            )
            self.volume_slider = Slider(
                min=0,
                max=100,
                value=80,
                step=1,
                size_hint=(None, None),
                size=(220, 44),
                cursor_size=(24, 24),
                value_track=True,
                value_track_color=(0.95, 0.65, 0.15, 1),
            )
            self.volume_slider.bind(value=self.set_volume)

            # Add CONFIG Button to the top bar (use regular Button)
            self.config_button = Button(text='CONFIG', bold=True, background_normal='', background_down='', background_color=(0.3, 0.3, 0.3, 1), color=(0.95, 0.92, 0.70, 1), font_size=self.sp_scaled(16), size_hint_x=None, width=110)
            # Bind only on_release so mouse clicks work reliably
            self.config_button.bind(on_release=self.toggle_config_mode)
            top_bar.add_widget(self.config_button)
            self.layout.add_widget(top_bar)

            volume_box = BoxLayout(
                orientation='horizontal',
                spacing=8,
                padding=(4, 4),
                size_hint=(None, None),
                size=(360, 64),
                pos_hint={'right': 1, 'top': 1},
            )
            volume_box.add_widget(self.volume_label)
            volume_box.add_widget(self.volume_slider)
            # Bind keyboard F1 to toggle config
            Window.bind(on_key_down=self.on_key_down)

            button_layer = FloatLayout(size_hint=(1, 0.90), pos_hint={'x':0, 'y':0})
            self.layout.add_widget(button_layer)

            self.statline = Label(text='Status: Ready', size_hint=(1, 0.08), pos_hint={'x':0, 'y':0}, color=(0.95, 0.95, 0.95, 1), bold=True, font_size=self.sp_scaled(14))
            self.layout.add_widget(self.statline)

            self.apply_volume(self.volume_slider.value)

            

            for i in range(1, 31):
                item = button_dict.get(i)
                if not item:
                    continue
                if item[5] == 'MENU':
                    continue

                btn = Button(text=str(item[3]),
                             background_color=ast.literal_eval(colord[item[4]]),
                             size_hint=(0.19, 0.19),
                             pos_hint={'x': float(item[1]), 'y': float(item[2])},
                             font_size=self.sp_scaled(14))
                # Use on_release so both touch and mouse click trigger reliably
                btn.bind(on_release=lambda instance, i=i: self.butt_pressed(i))
                button_layer.add_widget(btn)
                self.buttons[i] = btn

            # Add this last so the control remains above the button layer.
            self.layout.add_widget(volume_box)

            title_label = Label(
                text='Trick Or Treat Console',
                color=(0.95, 0.92, 0.70, 1),
                bold=True,
                halign='center',
                valign='middle',
                size_hint=(None, None),
                size=(600, 64),
                pos_hint={'center_x': 0.5, 'top': 1},
                font_size=self.sp_scaled(18),
            )
            title_label.text_size = title_label.size
            self.layout.add_widget(title_label)
                        
            return self.layout

       def butt_pressed(self, button_id):
              #rint(f"Button with data '{item[0]}' pressed!")
              global configmode
              global sfxpath
              

              item = button_dict.get(button_id)
              if not item:
                  return

              # If we're in config mode, allow configuration for SND, MQTT, and EFF buttons
              if configmode:
                  if item[5] in ("SND", "MQTT", "EFF"):
                      try:
                          self.statline.text = f"Config mode: ON {item[3]}"
                      except Exception:
                          self.statline.text = "Config mode: ON"
                      self.config_dialog(button_id)
                      return

              # Normal (non-config) behavior
              if item[5] == "SND":
                  sound_file = item[6]
                  if not configmode:
                        self.statline.text = f"Playing sound: {sound_file}"
                        client.publish("RP1", sound_file)
                        # need an exception here if file not found
                        try:
                            os.system('aplay --buffer-size=800000 ' + sfxpath + sound_file + '&')
                        except FileNotFoundError:
                            self.statline.text = f"Error playing sound, file not found"
                        else:
                            self.statline.text = f"Playing sound: {sound_file}"

              if item[5] == "EFF":
                sound_file = item[6]  # Assuming the sound file is stored in the 7th position
                effect_name = item[6]
                self.statline.text = f"Triggering effect please wait ..."
                     
                client.publish("effect", "on")

                # #GPIO.output(relayDB[6], ROn)  # initiate light effects
                # client.publish("lights/circuit1", "off")
                # client.publish("lights/circuit2", "off")
                
                # sleep(1)
                # # Trigger the strobe 
                # client.publish("lights/circuit3", "on")
                # #GPIO.output(relayDB[6], ROff) # turn off strobe trigger      

                # #play the thunder sound on the console 
                os.system('aplay --buffer-size=800000 ' + sfxpath + sound_file + '&')
                

                # # Play the thunder on the soundbar only
                client.publish("RP1", sound_file)

                # # wait tiny bit before strobe off
                # sleep(4)
                # client.publish("lights/circuit3", "off")

                # #wait some more time before turning the lights back on
                # sleep(4)
                # client.publish("lights/circuit1", "on")
                # client.publish("lights/circuit2", "on")

              
              if item[5] == "MQTT":
                  mtopic = item[6]
                  mpayload = item[7]
                  self.statline.text = f"MQTT command: {mtopic}, {mpayload}"
                  client.publish(mtopic, mpayload)
                  os.system('aplay --buffer-size=800000 ' + sfxpath + mpayload + '&')

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
                   Window.size = (1920,1080)

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

    with open('config.json') as fptr:
        config = json.load(fptr)

    SERVER = config["server"]
    SSID = config["ssid"]
    PWD = config["password"]
    pflag = config["printflag"]
    sfxpath = config["sfxpath"]
    print(sfxpath)

    # initialize mqtt broker for comms to tot3 board
    broker_address="gamma"
    port = 1883
    logging.basicConfig(level=logging.INFO)

    print("Creating new mqtt client instance")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1) 
    #client = mqtt.Client('P0') #create new instance 
    # All client_on callbacks go first

    client.on_log = on_log
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    print("Connecting to broker")
    client.connect(broker_address, port) #connect to broker
    client.loop_start()

    client.publish("lights","on")
    client.publish("strobe","off")
    print('Initial topics published')

    with open('tot_test.json') as fptr:
        button_dict = json.load(fptr)

    # swap the json string key index for int that we need in the kv file
    button_dict = {int(k): v for k, v in button_dict.items() }
    

    TotFloatLayout().run()