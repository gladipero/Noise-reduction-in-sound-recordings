from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.label import Label 
from kivy.uix.button import Button 
from kivy.lang import Builder
from kivy.app import App 
from kivy.clock import Clock 
from kivy.uix.textinput import TextInput
from kivy.uix.switch import Switch
import soundfile as sf
import sounddevice as sd
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.factory import Factory
import os
from scipy.signal import butter,lfilter
import numpy as np
import time

Builder.load_string('''
<AudioTool>
    orientation: 'vertical'
    Label:
        id: display_label
        text: 'Welcome to Reducto'
        bold: True
        color: [0,.5,0,1]
        font_size : 25
    BoxLayout:
        size_hint: 1, .5
        TextInput:
            id: user_input
            text: '5'
            background_color: [1,1,1,1]
            font_size: 20
            padding_x:[400,300]
            padding_y:[35,30] 
            on_text: root.enforce_numeric()
              
        
                        
    BoxLayout:
        Button:
            id: start_button
            text: 'Start Recording'
            font_size: 20
            font_name:
            on_release: root.startRecording_clock()

    BoxLayout:
        Button:
            id: load_button
            text: 'Load Sound'
            font_size: 20
            on_release: root.show_load()
            
<RecordDialog>:
    BoxLayout:
        size: root.size
        pos: root.pos
        orientation: "vertical"
        Label:
            id: recorder_text
            text: "Playing Processed Audio"
            bold: True
            color: [1,0,0,1]
            font_size : 20
        Button:
            id: stop_playback
            text: 'Stop Processed Audio and save it'
            on_press: root.stop_playback_button()
        Button:
            id: btnExit
            text: "Exit"
            on_press: app.stop()

<LoadDialog>:
    BoxLayout:
        size: root.size
        pos: root.pos
        orientation: "vertical"
        FileChooserListView:
            id: filechooser
            rootpath: '/Users/Aashi/Desktop'
            filters: ["*.wav"]

        BoxLayout:
            size_hint_y: None
            height: 30
            Button:
                text: "Cancel"
                on_release: root.discard_button()

            Button:
                text: "Load"
                on_release: root.load(filechooser.path, filechooser.selection)
''')



class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    discard_button = ObjectProperty(None)

class RecordDialog(FloatLayout):
    stop_playback = ObjectProperty(None)
    discard = ObjectProperty(None)
    stop_playback_button = ObjectProperty(None)
    discard_button = ObjectProperty(None)
    def stop_playback_button(self):
        sd.stop()
        sd.wait()
        filename = AudioTool.file_path[:-4]+'filtered.wav'
        sf.write(filename,AudioTool.data,AudioTool.fs)
        self.dismiss_popup

    def discard_button(self):
        sd.stop()
        self.dismiss_popup()

    def dismiss_popup(self):
        self._popup.dismiss


Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('RecordDialog', cls=RecordDialog)


class AudioApp(App):
    def build(self):
        return AudioTool()

class Filter(ObjectProperty):
    def butter_bandpass(self,lowcut, highcut, fs, order=1):
        #print(order)
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return b, a


    def butter_bandpass_filter(self,data, lowcut, highcut, fs, order=1):
        #print (order)
        b, a = self.butter_bandpass(lowcut, highcut, fs, order=order)
        y = lfilter(b, a, data)
        return y

    def apply_filter(self,file_path):
        data,fs = sf.read(file_path, dtype='float64')
        lowcut = 4000.0
        highcut = 2000.0
        data = self.butter_bandpass_filter(data ,lowcut ,highcut,fs,order=1)
        return data,fs
        #print(file_path[:-3]) 


class AudioTool(BoxLayout):
    def __init__(self, **kwargs):
        super(AudioTool, self).__init__(**kwargs)
        self.start_button = self.ids['start_button']
        #self.stop_button = self.ids['stop_button']
        self.display_label = self.ids['display_label']
        #self.switch = self.ids['duration_switch'] # Tutorial 3
        self.user_input = self.ids['user_input']

    loadfile = ObjectProperty(None)
    text_input = ObjectProperty(None)
    file_path = ''
    data,fs = [],44000
    
    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    '''def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()
'''
    def load(self, path, filename):
        print(path)
        with open(os.path.join(path, filename[0])) as stream:
            #print(os.path.join(path, filename[0]))
            self.file_path = os.path.join(path, filename[0])
            self.data,self.fs = Filter().apply_filter(self.file_path)
            content = RecordDialog(stop_playback=self.stop_playback,discard=self.discard)
            self._popup = Popup(title = "Processed Audio", content = content, size_hint=(0.9,0.9))
            sd.play(self.data,self.fs)
            self._popup.open()
        #self.dismiss_popup()

    def discard(self):
        sd.stop()
        #self.dismiss_popup()

    def stop_playback(self):
        sd.stop()
        sd.wait()
        filename = self.file_path[:-4]+'filtered.wav'
        sf.write(filename,self.data,self.fs)
    
    

    def save(self, path, filename):
        with open(os.path.join(path, filename), 'w') as stream:
            stream.write(self.text_input.text)

        self.dismiss_popup()

    def enforce_numeric(self): 
        '''Make sure the textinput only accepts numbers'''
        if self.user_input.text.isdigit() == False: 
            digit_list = [num for num in self.user_input.text if num.isdigit()]
            self.user_input.text = "".join(digit_list)

    def startRecording_clock(self):
        
        #self.mins = 0 #Reset the minutes
        #self.zero = 1 # Reset if the function gets called more than once
        self.duration = int(self.user_input.text) #Take the input from the user and convert to a number
        print(self.duration)
        self.start_button.disabled = True 
        #self.stop_button.disabled = False
        #self.switch.disabled = True 
        #duration = 10  # seconds
        fs=44100
        self.user_input.text="started"
        self.record(self.duration,fs)
        #Clock.schedule_interval(self.updateDisplay, 1)

 #TO BE UPDATED       
    def record(self,duration,fs):
        myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
        sd.wait()
        timestr = time.strftime("%Y%m%d-%H%M%S")+ '.wav'
        sf.write(timestr,myrecording,samplerate = 44100)
        
    '''def stopRecording(self):
    
        #Clock.unschedule(self.updateDisplay)
        self.display_label.text = 'Finished Recording!'
        self.start_button.disabled = False
        self.stop_button.disabled = True #TUT 3
        #self.switch.disabled = False #TUT 3 re enable the switch
        #data, samplerate = sf.read('abc.wav')
        #sd.play(data, samplerate)
       '''  
    '''def updateDisplay(self,dt):   
        if self.switch.active == False:
            if self.zero < 60 and len(str(self.zero)) == 1:
                self.display_label.text = '0' + str(self.mins) + ':0' + str(self.zero)
                self.zero += 1
                
            elif self.zero < 60 and len(str(self.zero)) == 2:
                    self.display_label.text = '0' + str(self.mins) + ':' + str(self.zero)
                    self.zero += 1
            
            elif self.zero == 60:
                self.mins +=1
                self.display_label.text = '0' + str(self.mins) + ':00'
                self.zero = 1
        
        elif self.switch.active == True:
            if self.duration == 0: # 0
                self.display_label.text = 'Recording Finished!'
                self.start_button.disabled = False # Re enable start
                self.stop_button.disabled = True # Re disable stop
                Clock.unschedule(self.updateDisplay)
                self.switch.disabled = False # Re enable the switch
                
            elif self.duration > 0 and len(str(self.duration)) == 1: # 0-9
                self.display_label.text = '00' + ':0' + str(self.duration)
                self.duration -= 1

            elif self.duration > 0 and self.duration < 60 and len(str(self.duration)) == 2: # 0-59
                self.display_label.text = '00' + ':' + str(self.duration)
                self.duration -= 1

            elif self.duration >= 60 and len(str(self.duration % 60)) == 1: # EG 01:07
                self.mins = self.duration / 60
                self.display_label.text = '0' + str(self.mins) + ':0' + str(self.duration % 60)
                self.duration -= 1

            elif self.duration >= 60 and len(str(self.duration % 60)) == 2: # EG 01:17
                self.mins = self.duration / 60
                self.display_label.text = '0' + str(self.mins) + ':' + str(self.duration % 60)
                self.duration -= 1
    '''
    def loadSound(self):
        fl.Editor().run()
        

if __name__ == '__main__':
    AudioApp().run()
