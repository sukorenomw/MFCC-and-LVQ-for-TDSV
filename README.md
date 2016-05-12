# Implementasi Penerapan MFCC dan LVQ untuk pengenalan pembicara

## Installation

### Dependancy

1. Python 2.7.10 or greater, can be downloaded [here](https://www.python.org/downloads/release/python-2710/)
2. Scipy and Numpy for python, can be downloaded [here](http://www.scipy.org/scipylib/download.html#)
3. SoX - Sound eXchange audio library, can be downloaded [here](http://sox.sourceforge.net/)

for windows user you can install [WinPython](https://sourceforge.net/projects/winpython/) bundle (included scipy and numpy pack)

## Program Explanation

### Training
![](https://github.com/sukorenomw/MFCC-and-LVQ-for-TDSV/blob/master/train.PNG)

Keterangan:

1. Menu untuk mengganti ke tampilan training, testing atau batch features extraction.
2. Menu untuk menampilkan option help.
3. Tombol untuk memilih satu audio file.
4. Tombol untuk play audio.
5. Tombol untuk pause audio.
6.	Tombol untuk stop audio.
7.	Kontrol volume audio.
8.	Input field kelas keluaran.
9.	Tombol untuk mengekstraksi fitur dan menyimpannya ke dalam database.
10.	Table hasil ekstraksi fitur.
11.	Informasi nama audio file.
12.	Informasi jumlah sampel pada audio file.
13.	Informasi Frequency Sampling pada audio file.
14.	Double spinbox untuk mengganti nilai parameter Learning Rate.
15.	Double spinbox untuk mengganti nilai parameter pengurangan Learning Rate.
16.	Input field untuk mengganti nilai parameter jumlah iterasi.
17.	Tombol untuk mengeksekusi pelatihan data.
18.	Tombol untuk reload daftar database yang baru ditambahkan.
19.	Combo box untuk memilih database yang ingin digunakan.
20.	Tabel hasil bobot akhir pelatihan data.

### Batch features extraction

![](https://github.com/sukorenomw/MFCC-and-LVQ-for-TDSV/blob/master/batch.PNG)

Keterangan:

1.	Tombol untuk memilih file-file audio.
2.	Tombol untuk mengekstraksi fitur dari semua audio file yang dipilih dan menyimpannya ke dalam database.
3.	Tombol untuk memilih satu audio file.
4.	Tabel untuk menampilkan file-file audio yang dipilih.

### Testing File

![](https://github.com/sukorenomw/MFCC-and-LVQ-for-TDSV/blob/master/teset.PNG)

Keterangan:

1.  Menu untuk mengganti ke tampilan training atau testing.
2.	Menu untuk menampilkan option help.
3.	Tombol untuk memilih satu audio file.
4.	Tombol untuk play audio.
5.	Tombol untuk pause audio.
6.	Tombol untuk stop audio.
7.	Kontrol volume audio.
8.	Input field kelas keluaran.
9.	Tombol untuk mengekstraksi fitur.
10.	Informasi nama audio file.
11.	Informasi jumlah sampel pada audio file.
12.	Informasi Frequency Sampling pada audio file.
13.	Combo box untuk memilih database yang ingin digunakan.
20.	Tombol untuk mengidentifikasi pembicara.
21.	Informasi nama pembicara yang teridentifikasi.
22.	Informasi kata yang teridentifikasi.





