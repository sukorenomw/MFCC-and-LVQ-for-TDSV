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
    signal, fs = FileReader.read_audio('buka-silenced.wav')
    frame, framed = mfcc.frame_blocking(signal)
    windowed = mfcc.hamm_window(framed)
    fft = mfcc.calc_fft(windowed)
    energy, fbank = mfcc.fbank(fft,fs)

    return mfcc, signal, fs, frame, framed, windowed, fft, energy, fbank