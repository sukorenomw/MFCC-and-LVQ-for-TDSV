import os
import math
import numpy as np

from filereader import FileReader
from subprocess import call

DEBUG=True

class MFCC():

    # parameters for silence removal
    above_period = '1'
    below_period = '-1'
    duration = '0.05'
    threshold = '0.3%'

    #parameter for fame blocking
    frame_size = 256
    overlap = 128

    def remove_silence(self, audio):
        call(['sox', audio, FileReader.add_temp(audio), 'silence', self.above_period, self.duration, self.threshold, self.below_period, self.duration, self.threshold])
        silenced_signal, silenced_fs = FileReader.read_audio(FileReader.add_temp(audio))
        os.remove(FileReader.add_temp(audio))
        return [silenced_signal, silenced_fs]

    def frame_blocking(self, audio_signal):
        num_frame = int(math.floor((len(audio_signal) - self.frame_size)/self.overlap)) +1
        frames = np.zeros((num_frame,self.frame_size))
        for i in xrange(num_frame):
            frames[i,:] = audio_signal[i*self.overlap:i*self.overlap+self.frame_size]

        print "Jumlah Frame: "+str(num_frame) if DEBUG else ''
        print "signal(0): " + str(audio_signal[0]) if DEBUG else ''
        print "signal(last): " + str(audio_signal[len(audio_signal)-1]) if DEBUG else ''
        print "Frames[first]: " + str(frames[0, 0]) if DEBUG else ''
        print "Frames[last]: " + str(frames[num_frame-1,self.frame_size-1]) if DEBUG else ''

        return [num_frame, frames]

    def hamm_window(self, frame_size, framed_signal, num_frame):
        hamm = self.hamm(frame_size)
        windowed = np.zeros((num_frame, frame_size))
        for i in xrange(num_frame):
            windowed[i,:] = framed_signal[i,:] * hamm

        return windowed


    def hamm(self,N):
        if N < 1:
            return np.array([])
        if N == 1:
            return np.ones(1, float)
        n = np.arange(0, N)
        return 0.54 - 0.46 * np.cos(2.0 * np.pi * n / (N - 1))
