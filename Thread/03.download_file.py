#import os, request, threading, urllib.request, urllib.error, urllib.parse dan time
import os
import requests
import threading
import urllib.request, urllib.error, urllib.parse
import time

#Inisialisasi url
url = "https://apod.nasa.gov/apod/image/1901/LOmbradellaTerraFinazzi.jpg"

#membuat rentang nilai untuk split
def buildRange(value, numsplits):
    lst = []
    for i in range(numsplits):
        if i == 0:
            lst.append('%s-%s' % (i, int(round(1 + i * value/(numsplits*1.0) + value/(numsplits*1.0)-1, 0))))
        else:
            lst.append('%s-%s' % (int(round(1 + i * value/(numsplits*1.0),0)), int(round(1 + i * value/(numsplits*1.0) + value/(numsplits*1.0)-1, 0))))
    return lst

class SplitBufferThreads(threading.Thread):
    """ Splits the buffer to ny number of threads
        thereby, concurrently downloading through
        ny number of threads.
    """

    #Constructor untuk class
    #dilakukan inisiasi pada setiap atribut yang ada
    def __init__(self, url, byteRange):
        super(SplitBufferThreads, self).__init__()
        self.__url = url
        self.__byteRange = byteRange
        self.req = None

    #melakukan request terhadap url berdasarkan byte range
    def run(self):
        self.req = urllib.request.Request(self.__url,  headers={'Range': 'bytes=%s' % self.__byteRange})

    #mendapat file data berdasarkan url yang ada
    def getFileData(self):
        return urllib.request.urlopen(self.req).read()

#Program utama
def main(url=None, splitBy=3):
    #inisialisasi start_time dengan memanggil fungsi time() dari library
    start_time = time.time()

    #Pemeriksaan jika url tidak tersedia
    #Mengakhiri program dan return kosong
    if not url:
        print("Please Enter some url to begin download.")
        return

    #variabel filename diisi dengan hasil split berdasarkan '/' dari url 
    fileName = url.split('/')[-1]

    #request head dari header yang didapat dari panjang konten
    sizeInBytes = requests.head(url, headers={'Accept-Encoding': 'identity'}).headers.get('content-length', None)
    
    #menampilkan jumlah byte untuk di unduh
    print("%s bytes to download." % sizeInBytes)
    
    #pemeriksaan jika sizeInBytes null
    #Mengakhiri program dan return kosong
    if not sizeInBytes:
        print("Size cannot be determined.")
        return

    #Memasukkan file data sebanyak jumlah split
    dataLst = []
    for idx in range(splitBy):
        #Pemanggilan fungsi buildRange dengan parameter sizeInBytes dan splitBy
        byteRange = buildRange(int(sizeInBytes), splitBy)[idx]

        #Split buffer thread dengan parameter url dan byterange
        bufTh = SplitBufferThreads(url, byteRange)
        
        #Memulai dan menggabungkan hasil
        bufTh.start()
        bufTh.join()

        #memasukkan hasil kedalam array dataLst
        dataLst.append(bufTh.getFileData())

    #mengisi content dengan menggabungkan b'' dengan list dataLst
    content = b''.join(dataLst)

    #pemerikssaan jika dataLst tidak null
    if dataLst:
        #pemeriksaan jika terdapat path untuk fileName 
        if os.path.exists(fileName):
            #penghapusan fileName
            os.remove(fileName)
        #Print time yang diperlukan saat running
        #Mengurangi time saat ini dengan start_time
        print("--- %s seconds ---" % str(time.time() - start_time))
        #Penulisan isi content pada file
        with open(fileName, 'wb') as fh:
            fh.write(content)
        print("Finished Writing file %s" % fileName)

#Jalankan program utama
if __name__ == '__main__':
    main(url)