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
        print "Frames[0,0]: " + str(frames[0,0]) if DEBUG else ''

        return [num_frame, frames]
