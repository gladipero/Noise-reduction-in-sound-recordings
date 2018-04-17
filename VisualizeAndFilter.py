from __future__ import print_function, division, unicode_literals
import wave
import numpy as np
import matplotlib.pyplot as plt

# compatibility with Python 3

def plot_graph(file,figno,title):
	#Extract Raw Audio from Wav File
	signal = file.readframes(-1)
	signal = np.fromstring(signal, 'Int16')
	fs = file.getframerate()
	Time=np.linspace(0, len(signal)/fs, num=len(signal))
	plt.figure(figno)
	plt.title(title)
	plt.plot(Time,signal)
	plt.show()


wr = wave.open('Voice0001.wav', 'r')

plot_graph(wr,1,'input')	

wr = wave.open('Voice0001.wav', 'r')
par = list(wr.getparams()) # Get the parameters from the input.
# This file is stereo, 2 bytes/sample, 44.1 kHz.
par[3] = 0 # The number of samples will be set by writeframes.

# Open the output file
ww = wave.open('filtered.wav', 'w')
ww.setparams(tuple(par)) # Use the same parameters as the input file.

lowpass = 2000 # Remove lower frequencies.
highpass = 4000 # Remove higher frequencies.

sz = wr.getframerate() # Read and process 1 second at a time.
c = int(wr.getnframes()/sz) # whole file
for num in range(c):
    print('Processing {}/{} s'.format(num+1, c))
    da = np.fromstring(wr.readframes(sz), dtype=np.int16)
    left, right = da[0::2], da[1::2] # left and right channel
    lf, rf = np.fft.rfft(left),np.fft.rfft(right)
    lf[:lowpass], rf[:lowpass] = 0, 0 # low pass filter
    #lf[55:66], rf[55:66] = 0, 0 # line noise in sample from site
    lf[highpass:], rf[highpass:] = 0,0 # high pass filter
    nl, nr = np.fft.irfft(lf), np.fft.irfft(rf)
    ns = np.column_stack((nl,nr)).ravel().astype(np.int16)
    ww.writeframes(ns.tostring())
# Close the files.
wr.close()
ww.close()

spf = wave.open("filtered.wav", 'r')

plot_graph(spf,2,'output')
