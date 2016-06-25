import timeit
from controller.filereader import FileReader
from controller.mfcc import MFCC
import numpy as np
import matplotlib.pyplot as pl

def wrapper(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)

    return wrapped

def timetest(func, *args):
    return timeit.timeit(wrapper(func, *args), number=1)

def allfunc():
    mfcc=MFCC()
    signal, fs = FileReader.read_audio('1.wav')
    silenced_signal, fs = mfcc.remove_silence('1.wav')
    frame, framed = mfcc.frame_blocking(silenced_signal)
    windowed = mfcc.hamm_window(framed)
    fft = mfcc.calc_fft(windowed)
    energy, fbank = mfcc.fbank(fft,fs)
    features = mfcc.features(energy)

    return mfcc, signal, silenced_signal,fs, frame, framed, windowed, fft, energy, fbank, features