import sys

from scikits import audiolab

class FileReader():

    @staticmethod
    def read_audio(audio):
        [signal, fs, codec] = audiolab.wavread(audio)
        return [signal, fs]


