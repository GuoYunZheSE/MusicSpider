import threading
import os
import requests
import time
import re
import urllib
def view_bar(num, total):  #显示进度条
    rate = num/total
    rate_num = int(rate * 100)
    number=int(50*rate)
    r = '\r[%s%s]%d%%' % ("#"*number, " "*(50-number), rate_num, )
    print("\r {}".format(r),end=" ")   #\r回到行的开头
class Getfile():  #下载文件
    def __init__(self,url):
        self.url=url
        #self.filename=filename
        self.re=requests.head(url,allow_redirects=True)  #运行head方法时重定向
    def getsize(self):
        try:
            self.file_total=int(self.re.headers['Content-Length']) #获取下载文件大小
            return self.file_total
        except:
            print('无法获取下载文件大小')
            exit()
    def getfilename(self):  #获取默认下载文件名
        filename=''
        if 'Content-Disposition' in self.re.headers:
            n=self.re.headers.get('Content-Disposition').split('name=')[1]
            filename=urllib.parse.unquote(n,encoding='utf8')
        elif os.path.splitext(self.re.url)[1]!='':
            filename=os.path.basename(self.re.url)
        return filename
    def downfile(self,filename):  #下载文件
        self.r = requests.get(self.url,stream=True)
        with open(filename, "wb") as code:
            for chunk in self.r.iter_content(chunk_size=1024): #边下载边存硬盘
                if chunk:
                    code.write(chunk)
        time.sleep(1)
        #print ("\n下载完成")
    def downprogress(self,filename):
        self.filename=filename
        self.file_size=0
        self.file_total=self.getsize()
        while self.file_size<self.file_total:  #获取当前下载进度
            time.sleep(1)
            if os.path.exists(self.filename):
                self.down_rate=(os.path.getsize(self.filename)-self.file_size)/1024/1024
                self.down_time=(self.file_total-self.file_size)/1024/1024/self.down_rate
                print (" "+str('%.2f' %self.down_rate+"MB/s"),end="")
                self.file_size=os.path.getsize(self.filename)
            print (" "+str(int(self.down_time))+"s",end="")
            print (" "+str('%.2f' %(self.file_size/1024/1024))+"MB",end="")
            view_bar(self.file_size, self.file_total)