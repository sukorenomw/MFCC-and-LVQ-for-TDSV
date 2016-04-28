import sys

from scikits import audiolab

class FileReader():

    @staticmethod
    def read_audio(audio):
        [signal, fs, codec] = audiolab.wavread(audio)
        return [signal, fs]

    @staticmethod
    def add_temp(file):
        return file[0:len(file)-4]+"-silenced.wav"
        # return file


