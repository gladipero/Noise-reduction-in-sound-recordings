
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.switch import Switch
from kivy.uix.textinput import TextInput
from jnius import autoclass
from jnius import JavaException



Builder.load_string('''
<AudioTool>
	orientation: 'vertical'
	Label:
		id: display_label
		text: '00:00'
	BoxLayout:
		size_hint: 1, .2
		TextInput:
			id: user_input
			text: '1'
			disabled: duration_switch.active == False
		Switch:
			id: duration_switch
	BoxLayout:
		Button:
			id: start_button
			text: 'Start Recording'
			on_release: root.startRecording_clock()
		Button:
			id: stop_button
			text: 'Stop Recording'
			on_release: root.stopRecording_clock()
			disabled: True

''')

class AudioApp(App):
	def build(self):
		return AudioTool()

class MyRecorder():
	def __init__(self):
		'''Recorder object To access Android Hardware'''
    	self.MediaRecorder = autoclass('android.media.MediaRecorder')
        self.AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
    	self.OutputFormat = autoclass('android.media.MediaRecorder$OutputFormat')
        self.AudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder')
 
        # create out recorder
        self.mRecorder = self.MediaRecorder()
        self.mRecorder.setAudioSource(self.AudioSource.MIC)
        self.mRecorder.setOutputFormat(self.OutputFormat.THREE_GPP)
        self.mRecorder.setOutputFile('/sdcard/MYAUDIO.3gp')
        self.mRecorder.setAudioEncoder(self.AudioEncoder.AMR_NB)
        self.mRecorder.prepare()









class AudioTool(BoxLayout):
	def __init__(self, **kwargs):
		super(AudioTool,self).__init__(**kwargs)

		self.start_button = self.ids['start_button']
		self.stop_button = self.ids['stop_button']
		self.display_label = self.ids['display_label']
		self.switch = self.ids['duration_switch']
		
		self.user_input = self.ids['user_input']
		self.counter = ''


	def startRecording(self, dt):
		self.r = MyRecorder()
		self.r.mRecorder.start()

	def stopRecording(self):
		Clock.unschedule(self.UpdateDisplay)
		Clock.unschedule(self.startRecording)
		self.display_label.text = 'Finished Recording'
		self.start_button.disabled = False
		self.stop_button.disabled = True
		self.switch.disabled = False

	def startRecording_clock(self):
		self.mins = 0
		self.zero = 1 #Reset if the function is called
		Clock.schedule_interval(self.UpdateDisplay, 1)
		self.duration = int(self.user_input.text)
		self.start_button.disabled = True	#prevents the user from clicking start
		self.stop_button.disabled = False
		self.switch.disabled = True
		Clock.schedule_once(self.startRecording)

	def stopRecording_clock(self):

		Clock.unschedule(self.UpdateDisplay)
		Clock.unschedule(self.startRecording)
		self.display_label.text = 'Finished Recording'
		self.start_button.disabled = False
		self.stop_button.disabled = True
		self.switch.disabled = False

	def UpdateDisplay(self,dt):
		'''
		Called Every second when start is pressed
		'''
		if self.switch.active == False:
			if self.zero < 60 and len(str(self.mins)) == 1:
				self.display_label.text = '0' + str(self.mins) + ':0' + str(self.zero)
				self.zero += 1

			elif self.zero < 60 and len(str(self.zero)) == 2:
				self.display_label.text = '0' + str(self.mins) + ':' + str(self.zero)
				self.zero += 1

			elif self.zero == 60:
				self.mins += 1
				self.display_label.text = '0' + str(self.mins) + ':00'	
				self.zero = 1 # Reset seconds again

		elif self.switch.active == True:
			if self.duration == 0:
				self.display_label.text = 'Recording Finished'
				self.stopRecording()

			elif self.duration > 0 and len(str(self.duration)) == 1:
				self.display_label.text = '00' + ':0' + str(self.duration)
				self.duration -= 1

			elif self.duration > 0 and self.duration < 60 and len(str(self.duration)) == 2:
				self.display_label.text = '00' + ':0' + str(self.duration)
				self.duration -= 1

			elif self.duration >= 60 and len(str(self.duration % 60)) == 1:
				self.mins = self.duration / 60
				self.display_label.text = '0' + str(self.mins) + ':0' + str(self.duration % 60)
				self.duration -= 1

			elif self.duration >= 60 and len(str(self.duration % 60)) == 2:
				self.mins = self.duration / 60
				self.display_label.text = '0' + str(self.mins) + ':' + str(self.duration % 60)
				self.duration -= 1





if __name__ == '__main__':
	AudioApp().run()

