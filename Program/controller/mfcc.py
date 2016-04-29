import os
import math
import numpy as np
import cmath

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

    def hamm_window(self, framed_signal):
        hamm = self.hamm(self.frame_size)
        windowed = np.zeros((len(framed_signal), self.frame_size))
        for i in xrange(len(framed_signal)):
            windowed[i,:] = framed_signal[i,:] * hamm

        return windowed

    def calc_fft(self, signal):
        fft_signal = np.zeros((signal.shape[0], signal.shape[1]))
        for i in xrange(len(signal)):
            fft_signal[i, :] = np.abs(self.FFT(signal[i, :]))

        return fft_signal

    def DFT(self, x):
        x = np.asarray(x, dtype=float)
        N = x.shape[0]
        n = np.arange(N)  # ambil index input sampel 0,1..N-1
        k = n.reshape((N, 1))  # ambil index output sampel 0,1..N-1 dalam bentuk ke bawah, reshape = atur ulang array
        M = np.exp(-2j * np.pi * k * n / N)  # hitung exponensial bilangan complex
        return np.dot(M, x)

    def FFT(self, signal):
        signal = np.asarray(signal, dtype=float)
        N = signal.shape[0]

        # print "nilai x FFT: " + str(x) if DEBUG else ''
        # print "nilai N FFT: " + str(N) if DEBUG else ''

        if np.log2(N) % 1 > 0:
            raise ValueError("input harus power of 2")
        elif N <= 32: #kondisi berhenti rekursif
            return self.DFT(signal)
        else:
            X_even = self.FFT(signal[::2]) # ambil yang genap
            X_odd = self.FFT(signal[1::2]) # ambil yang ganjil
            factor = np.exp(-2j * np.pi * np.arange(N) / N)
            return np.concatenate([X_even + factor[:N / 2] * X_odd,
                                   X_even - factor[N / 2:] * X_odd])

    def hamm(self,N):
        if N < 1:
            return np.array([])
        if N == 1:
            return np.ones(1, float)
        n = np.arange(0, N)
        return 0.54 - 0.46 * np.cos(2.0 * np.pi * n / (N - 1))
