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

    #parameter mel wrapping
    num_filter = 32
    freq_low = 300.0

    @staticmethod
    def freq_high(fs):
        return fs / 2

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
        def hamm(N):
            if N < 1:
                return np.array([])
            if N == 1:
                return np.ones(1, float)
            n = np.arange(0, N)
            return 0.54 - 0.46 * np.cos(2.0 * np.pi * n / (N - 1))

        hamm = hamm(self.frame_size)
        windowed = np.zeros((len(framed_signal), self.frame_size))
        for i in xrange(len(framed_signal)):
            windowed[i,:] = framed_signal[i,:] * hamm

        return windowed


    def calc_fft(self, signal):
        fft_signal = np.zeros((signal.shape[0], signal.shape[1]))
        for i in xrange(len(signal)):
            fft_signal[i, :] = np.abs(self.FFT(signal[i, :]))

        return fft_signal

    def DFT(self,x):
        x = np.asarray(x, dtype=float)
        N = x.shape[0]
        n = np.arange(N) # ambil index input sampel 0,1..N-1
        k = n.reshape((N, 1)) # ambil index output sampel 0,1..N-1 dalam bentuk ke bawah, reshape = atur ulang array
        M = np.exp(-2j * np.pi * k * n / N) # rumus DFT
        return np.dot(M, x)

    def FFT(self, signal):
        signal = np.asarray(signal, dtype=float)
        N = signal.shape[0]

        if np.log2(N) % 1 > 0:
            raise ValueError("input harus power of 2")
        elif N <= 32:  # this cutoff should be optimized
            return self.DFT(signal)
        else:
            X_even = self.FFT(signal[::2]) # ambil yang genap
            X_odd = self.FFT(signal[1::2]) # ambil yang ganjil
            factor = np.exp(-2j * np.pi * np.arange(N) / N)
            return np.concatenate([X_even + factor[:N / 2] * X_odd,
                                   X_even + factor[N / 2:] * X_odd])

    def mel(self, fs):
        def calc_mel(freq):
            return 1125 * np.log(1 + (freq / 700)) # rumus mel

        low_high = np.asarray([ self.freq_low, self.freq_high(fs)], dtype=float)
        mel = np.linspace(calc_mel(low_high[0]), calc_mel(low_high[1]), self.num_filter+2) # generate nilai mel dari low and high sejumlah 34 titik filter
        return mel

    def melinhz(self, mel):
        return 700 * (np.exp(mel/1125)-1)

    def calc_fft_bin(self,melinhz, fs):
        return np.floor((self.frame_size+1)*melinhz/fs)

    def fbank(self,fs):
        mel = self.mel(fs)
        melinhz = self.melinhz(mel)
        fft_bin = self.calc_fft_bin(melinhz, fs)

        fbank = np.zeros([self.num_filter, self.frame_size / 2 +1])
        for j in xrange(0, self.num_filter):
            for i in xrange(int(fft_bin[j]), int(fft_bin[j + 1])):
                fbank[j, i] = (i - fft_bin[j]) / (fft_bin[j + 1] - fft_bin[j])
            for i in xrange(int(fft_bin[j + 1]), int(fft_bin[j + 2])):
                fbank[j, i] = (fft_bin[j + 2] - i) / (fft_bin[j + 2] - fft_bin[j + 1])
        return fbank
