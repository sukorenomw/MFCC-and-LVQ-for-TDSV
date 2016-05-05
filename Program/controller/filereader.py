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

    @staticmethod
    def get_output_class(file):
        return file[file[:file.rfind('/')].rfind('/')+1:file.rfind('/')]+"-"+file[file.rfind('/') + 1:len(file)-5].capitalize()

