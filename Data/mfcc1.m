#{
Perform MFCC on helloworld wav file.
http://dsp.stackexchange.com/questions/26083/verifying-mfcc-final-result
#}
#fres=floor((frameSize/fs) * (700 * (exp((lh_mel(1)+(((0:size(mel,2)-1)*(lh_mel(2)-lh_mel(1)))/Nofilters+1))/1125)-1)));
#{
Perform MFCC on helloworld wav file.
http://dsp.stackexchange.com/questions/26083/verifying-mfcc-final-result
#}


#clear all;
close all;
#{Step 0: Reading the File & initializing the Time and Freq.
#}
    [x,fs,nbits]=wavread('buka-silenced.wav');
    #x=x(x <= -0.00021 | x >= 0.00021);
    ts=1/fs;
    N=length(x);
    Tmax=(N-1)*ts;
    fsu=fs/(N-1);
    t=(0:ts:Tmax);
    f=(-fs/2:fsu:fs/2);
    figure, subplot(411),plot(t,x),xlabel('Time'),title('Original Speech');
    subplot(412),plot(f,fftshift(abs(fft(x)))),xlabel('Freq (Hz)'),title('Frequency Spectrum');

#{
Step 1: Pre-Emphasis

#}

    a=[1];
    b=[1 -0.95];
    y=filter(b,a,x);
    subplot(413),plot(t,y),xlabel('Time'),title('Signal After High Pass Filter - Time Domain');
    subplot(414),plot(f,fftshift(abs(fft(y)))),xlabel('Freq (Hz)'),title('Signal After High Pass Filter - Frequency Spectrum');

#{
Step 2: Frame Blocking

#}
    frameSize=256;
    frameOverlap=128;
    frames=enframe(x,frameSize,frameOverlap);
    NumFrames=size(frames,1);

#{
Step 3: Hamming Windowing

#}
    hamm=hamming(256)';
    for i=1:NumFrames
    windowed(i,:)=frames(i,:).*hamm;
    end



#{
Step 4: FFT 
Taking only the positive values in the FFT that is the first half of the frame after being computed. 
#}

    for i=1:NumFrames
    ft(i,:)=abs(fft(windowed(i,:))(1:frameSize/2));     
    end


#{
Step 5: Mel Filterbanks
Lower Frequency = 300Hz
Upper Frequency = fs/2
With a total of 22 points we can create 20 filters.
#}
    Nofilters=32;
    lowhigh=[300 fs/2];
    %Here logarithm is of base 'e'
    lh_mel=1125*(log(1+lowhigh/700));
    mel=linspace(lh_mel(1),lh_mel(2),Nofilters+2);
    melinhz=700*(exp(mel/1125)-1);
    %Converting to frequency resolution
    fres=floor(((frameSize)+1)*melinhz/fs); 
    %Creating the filters
    for m =2:length(mel)-1
        for k=1:frameSize/2
          if k<fres(m-1)
              H(m-1,k) = 0;
          elseif (k>=fres(m-1)&&k<=fres(m))
              H(m-1,k)= (k-fres(m-1))/(fres(m)-fres(m-1));
          elseif (k>=fres(m)&&k<=fres(m+1))
             H(m-1,k)= (fres(m+1)-k)/(fres(m+1)-fres(m));
          elseif k>fres(m+1)
              H(m-1,k) = 0;    
          endif
        end
    end
    %H contains the 20 filterbanks, we now apply it to the
    %processed signal.
    for i=1:NumFrames
    for j=1:Nofilters
        bankans(i,j)=sum(ft(i,:).*H(j,:));
    end
    end


#{
Step 6: Nautral Log and DCT
#}
    pkg load signal
    pkg load image
    %Here logarithm is of base '10'
    logged=log(bankans)/log(10);
    vec=[];
    for i=1:NumFrames
        lnd(i,:)=dct2(logged(i,:));
        vec=[vec,lnd(i,1:13)];
    end
    vec=padarray(vec,[0 1222-size(vec,2)], 0, 'post');
%plotting the MFCC

    figure 
    hold on
    for i=1:NumFrames
        plot(lnd(i,:)),xlabel('Number of Coefficients'),ylabel('MFCC value');
    end
    hold off
    
%playing the data
%    player2 = audioplayer(y, fs, nbits);
%    play(player2);