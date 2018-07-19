import urllib.request
import re
import urllib.parse
import bs4
import progressbar
import requests
import os
import time
import json
import random

def check(name):
    if '/' in name:
        name=name.replace('/', '_')
    if '\\' in name:
        name =name.replace('\\', '_')
    if ':' in name:
        name =name.replace(':', '_')
    if '?' in name:
        name =name.replace('?', '_')
    if '|' in name:
        name = name.replace('|', '_')
    if '<' in name:
        name =name.replace('<', '_')
    if '>' in name:
        name =name.replace('>', '_')
    if '\'' in name:
        name =name.replace('\'', '_')
    if '\"' in name:
        name =name.replace('\"', '_')

    if '*' in name:
            name = name.replace('*', '_')
    return name

def get_ip_list(obj):
    ip_text = obj.findAll('tr', {'class': 'odd'})   # 获取带有IP地址的表格的所有行
    ip_list = []
    for i in range(len(ip_text)):
        ip_tag = ip_text[i].findAll('td')
        ip_port = ip_tag[1].get_text() + ':' + ip_tag[2].get_text() # 提取出IP地址和端口号
        ip_list.append(ip_port)
    print("共收集到了{}个代理IP".format(len(ip_list)))
    print(ip_list)
    return ip_list
def Updat_Image():
    artists=[['Taylor Swift',44266],['薛之谦',5781],['五月天',13193],['林俊杰',3684],['林宥嘉',3685],['周杰伦',6452],
        ['张杰',6472],['Maroon5',96266],['EXO',759509],['田馥甄',9548],['陈奕迅',2116],['A-Lin',7063],
        ['KARD',12214083],['WINNER',976163],['The Piano Guys',99093],['张震岳',6453],['G.E.M.邓紫棋',7763],
        ['Michael Jackson',38853],['玉置浩二',15558],['大塚 愛',17477],['KOKIA',16686],['张信哲',6454],["The Beatles",101988],['梁静茹',8325],
        ['赵雷',6731],['王菲',9621],['Justin Timberlake',35331],['Wolfgang Amadeus Mozart',804174],['Alan Walker',1045123],
        ['Two Steps From Hell',102714],['萧敬腾',5768],['萧亚轩',9945],['徐良',5929],
        ['汪苏泷',5538],['许嵩',5771]]
    for artist in artists:
        artist_para = {
            'name': artist[0],
            'gender': 2,
            'birthplace': '法国',
            'birthday': '1972-05-03',
            'representative': 'Green Days',
            'region': 4,
            'initial': 'C',
            'country': '日本',
            'occupation': '歌手',
            'style': 1,
            'language': '英法日',
            'limit': 90,
            'offset': 0,
            'id': artist[1]
         }
        Spy=NetEaseSpider(artist_para)
        Spy.parse_ip_web()
        Spy.parse_artist_html()
        album_num = Spy.artist.albums.__len__()
        Spy.download_singer_img()
        album_count = 0
        for album in Spy.artist.albums:
            print('Album:{}/{}'.format(album_count, album_num))
            album_count += 1
            Spy.download_album_img(album)


class Artist:
    def __init__(self,artist_id,artist_name,img,info):
        self.id=artist_id
        self.albums=[]
        self.name=artist_name
        self.img=img
        self.info=info

    def add_album(self,album):
        self.albums.append(album)

class Album:
    def __init__(self,name,a_id,img):
        self.name=name
        self.id=a_id
        self.img=img
        self.url='https://music.163.com/album?id={}'.format(self.id)
        self.info=''
        self.songs=[]
        self.release_date=''

    def add_song(self,song):
        self.songs.append(song)

    def set_info(self,info):
        self.info=info

    def set_release_date(self,rd):
        self.release_date=rd

class Song:
    def __init__(self,name,s_id):
        self.name=name
        self.id=s_id
        self.lyric_url = 'http://music.163.com/api/song/media?id={}'.format(s_id)
        self.song_url = 'http://music.163.com/song/media/outer/url?id={}.mp3'.format(s_id)


class NetEaseSpider:
    def __init__(self,para):
        self.para=para
        self.main_url='https://music.163.com/'
        self.artist_url='https://music.163.com/artist/album?id={}&limit={}&offset={}'.format(para['id'],para['limit'],para['offset'])
        self.artist_info='https://music.163.com/artist/desc?id={}'.format(para['id'])
        self.artist_id=para['id']
        self.ip_list=[]
        # driver = webdriver.PhantomJS(executable_path='D:\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe')
        #         # driver.implicitly_wait(1)
        # self.cookie=driver.get_cookies()

    def download(self,url, num_retries=2):
        print('Download:', url)
        headers = {
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
                   'Referer': 'https://music.163.com/',
                   'Connection':'keep-alive',
                   'Accept-Language':'zh-CN, zh;q=0.8',
                   'Pragma':'no - cache',
                   'Cache - Control': 'no - cache',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                   'Content-Type':'application/x-www-form-urlencoded'
                   }
        # # Cookie Added
        # cookie_support=urllib.request.HTTPCookieProcessor(cookiejar=http.cookiejar.CookieJar())
        # opener=urllib.request.build_opener(cookie_support)
        # urllib.request.install_opener(opener)

        proxy=self.get_random_ip()
        httpproxy_handler=urllib.request.ProxyHandler(proxy)
        opener=urllib.request.build_opener(httpproxy_handler)
        request = urllib.request.Request(url, headers=headers)
        try:
            html = opener.open(request).read()
        except urllib.request.URLError as e:
            print('Download error:', e.reason)
            html = None
            if num_retries > 0:
                if hasattr(e, 'code') and 500 <= e.code < 600:
                    return self.download(url, num_retries - 1)
        return html

    def get_bs(self,url):
        html=self.download(url).decode('utf-8')
        self.bs=bs4.BeautifulSoup(html,'lxml')

    def parse_ip_web(self):
        url = 'http://www.xicidaili.com/'
        headers = {
            'User-Agent': 'User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'}
        request = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(request)
        bsObj = bs4.BeautifulSoup(response, 'lxml')  # 解析获取到的html
        self.ip_list=get_ip_list(bsObj)

    def parse_artist_html(self):
        self.get_bs(self.artist_url)
        artist_img=self.bs.select('div.n-artist img')[0]['src']
        artist_img=artist_img.replace('640y300','400y400')
        artist_name=self.bs.select('h2')[0].text

        imgs=self.bs.select('ul#m-song-module li div img')
        a_ids=self.bs.select('ul#m-song-module li div a.msk')
        names=self.bs.select('ul#m-song-module li div')

        self.get_bs(self.artist_info)
        artist_info=self.bs.select('div.n-artdesc p')[0]
        artist_info=artist_info.text
        if artist_info.__len__()>=340:
            artist_info=artist_info[0:340]
        self.artist=Artist(self.artist_id, artist_name, artist_img,artist_info)

        for i in range(0,imgs.__len__()):
            img=imgs[i]['src']
            img=img.replace('120y120','400y400')
            a_id=int(a_ids[i]['href'].split('id=')[1])
            name=names[i]['title']
            self.artist.albums.append(Album(check(name), a_id, img))

    def parse_album_html(self,album):
        self.get_bs(album.url)
        try:
            release_date = self.bs.select('div div div div div div div div  p')[1].text.split('：')[1]
        except IndexError:
            release_date='2018-1-1'
        album.set_release_date(release_date)

        info=self.bs.select('div.f-brk p')
        album_info=''
        for i in range(0,info.__len__()):
            album_info+=info[i].text
        if album_info.__len__()>=340:
            album_info=album_info[0:340]
        album.set_info(album_info)

        songs=self.bs.select('ul.f-hide li a')
        for song in songs:
            song_name=song.text
            if song_name.__len__()>=50:
                song_name=song_name[0:50]
            song_id=int(song['href'].split('id=')[1])
            album.add_song(Song(check(song_name),song_id))

    def download_file(self,url,file_path,method):
        print('\tDownload:', url)
        headers = {
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
                   'Referer': 'https://music.163.com/',
                   'Connection':'keep-alive',
                   'Accept-Language':'zh-CN, zh;q=0.8',
                   'Pragma':'no - cache',
                   'Cache - Control': 'no - cache',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                   'Content-Type':'application/x-www-form-urlencoded'
                   }
        response=requests.request('GET',url,stream=True,data=None,headers=headers, proxies=self.get_random_ip())
        try:
            total_length = int(response.headers.get('Content-Length'))
            with open(file_path, method)as f:
                widgets = ['\t\tProgress: ', progressbar.Percentage(), ' ',
                           progressbar.Bar(marker='#', left='[', right=']'),
                           ' ', progressbar.ETA(), ' ', progressbar.FileTransferSpeed()]
                pbar = progressbar.ProgressBar(widgets=widgets, maxval=total_length).start()
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        f.flush()
                    pbar.update(len(chunk) + 1)
                pbar.finish()
        except TypeError:
            print('File Not Exits!')
            file=open(file_path,method)
            file.close()
        except FileNotFoundError:
            print('File Not Found!')
            pass

    def download_singer_img(self):
        print('Downloading:{}\'s Image'.format(self.artist.name))
        file_path='G:\\Spring_Semester_2018\\J2EE实训\数据\\音乐数据库\\image\\singer\\{}.jpg'.format(self.artist.name)
        self.download_file(self.artist.img,file_path,'wb')

    def download_album_img(self,album):
        print('Downloading:{}\'s Image'.format(album.name))
        try:
            os.mkdir('G:\\Spring_Semester_2018\\J2EE实训\数据\\音乐数据库\\image\\album\\{}'.format(self.artist.name))
        except OSError:
            pass
        file='G:\\Spring_Semester_2018\\J2EE实训\数据\\音乐数据库\\image\\album\\{}\\{}.jpg'.format(self.artist.name,album.name)
        self.download_file(album.img,file,'wb')

    def get_random_ip(self):
        random_ip = 'http://' + random.choice(self.ip_list)
        proxy_ip = {'http:': random_ip}
        print('\tUsing Proxy:{}'.format(random_ip))
        return proxy_ip

    def download_song(self,album):
        song_num=album.songs.__len__()
        song_count=0
        for song in album.songs:
            song_count+=1
            print('Song:{}/{}'.format(song_count,song_num))
            try:
                lyrics_html = self.download(song.lyric_url).decode('utf-8')
                lyrics = re.split('":"|","', lyrics_html)[1]
                lyrics = lyrics.strip('\'')
                lyrics = lyrics.replace('\\n', '\n')
            except IndexError:
                lyrics='暂无歌词'
            try:
                os.mkdir(
                    'G:\\Spring_Semester_2018\\J2EE实训\\数据\\音乐数据库\\lyrics\\{ARTIST_NAME}'.format(
                        ARTIST_NAME=self.artist.name))
            except OSError:
                pass

            try:
                os.mkdir(
                    'G:\\Spring_Semester_2018\\J2EE实训\\数据\\音乐数据库\\lyrics\\{ARTIST_NAME}\\{ALBUM_NAME}\\'.format(
                        ARTIST_NAME=self.artist.name, ALBUM_NAME=album.name))
            except OSError:
                pass

            try:
                lyrics_file = open(
                    'G:\\Spring_Semester_2018\\J2EE实训\\数据\\音乐数据库\\lyrics\\{ARTIST_NAME}\\{ALBUM_NAME}\\{SONG_NAME}.lrc'.format(
                        ARTIST_NAME=self.artist.name, ALBUM_NAME=album.name, SONG_NAME=song.name), 'w',
                    encoding='utf-8')
            except FileNotFoundError:
                try:
                    lyrics_file = open(
                        'G:\\Spring_Semester_2018\\J2EE实训\\数据\\音乐数据库\\lyrics\\{ARTIST_NAME}\\{ALBUM_NAME}\\{SONG_NAME}.lrc'.format(
                            ARTIST_NAME=self.artist.name, ALBUM_NAME=album.name, SONG_NAME='InvalidFileName'), 'w',
                        encoding='utf-8')
                except FileNotFoundError:
                    os.mkdir(
                        'G:\\Spring_Semester_2018\\J2EE实训\\数据\\音乐数据库\\lyrics\\{ARTIST_NAME}\\{ALBUM_NAME}\\'.format(
                            ARTIST_NAME=self.artist.name, ALBUM_NAME='InvalidAlbumName'))
                    lyrics_file = open(
                        'G:\\Spring_Semester_2018\\J2EE实训\\数据\\音乐数据库\\lyrics\\{ARTIST_NAME}\\{ALBUM_NAME}\\{SONG_NAME}.lrc'.format(
                            ARTIST_NAME=self.artist.name, ALBUM_NAME='InvalidAlbumName', SONG_NAME='InvalidFileName'), 'w',
                        encoding='utf-8')
            except OSError:
                os.mkdir(
                    'G:\\Spring_Semester_2018\\J2EE实训\\数据\\音乐数据库\\lyrics\\{ARTIST_NAME}\\{ALBUM_NAME}\\'.format(
                        ARTIST_NAME=self.artist.name, ALBUM_NAME='InvalidAlbumName'))
                lyrics_file = open(
                    'G:\\Spring_Semester_2018\\J2EE实训\\数据\\音乐数据库\\lyrics\\{ARTIST_NAME}\\{ALBUM_NAME}\\{SONG_NAME}.lrc'.format(
                        ARTIST_NAME=self.artist.name, ALBUM_NAME='InvalidAlbumName', SONG_NAME='InvalidFileName'), 'w',
                    encoding='utf-8')
            lyrics_file.write(lyrics)
            lyrics_file.close()
            print('\t\tLyric File:{} Saved'.format(song.name))

            # Get File
            time.sleep(1)
            try:
                os.mkdir(
                    'G:\\Spring_Semester_2018\\J2EE实训\\数据\\音乐数据库\\music\\{ARTIST_NAME}'.format(
                        ARTIST_NAME=self.artist.name))
            except OSError:
                pass
            try:
                os.mkdir(
                    'G:\\Spring_Semester_2018\\J2EE实训\\数据\\音乐数据库\\music\\{ARTIST_NAME}\\{ALBUM_NAME}\\'.format(
                        ARTIST_NAME=self.artist.name, ALBUM_NAME=album.name))
            except OSError:
                pass


            try:
                song_file = open(
                    'G:\\Spring_Semester_2018\\J2EE实训\\数据\\音乐数据库\\music\\{ARTIST_NAME}\\{ALBUM_NAME}\\{SONG_NAME}.mp3'.format(
                        ARTIST_NAME=self.artist.name, ALBUM_NAME=album.name, SONG_NAME=song.name), 'w',
                    encoding='utf-8')
                song_file.close()
                song_file='G:\\Spring_Semester_2018\\J2EE实训\\数据\\音乐数据库\\music\\{ARTIST_NAME}\\{ALBUM_NAME}\\{SONG_NAME}.mp3'.format(
                        ARTIST_NAME=self.artist.name, ALBUM_NAME=album.name, SONG_NAME=song.name)
            except FileNotFoundError:
                song_file='G:\\Spring_Semester_2018\\J2EE实训\\数据\\音乐数据库\\music\\{ARTIST_NAME}\\{ALBUM_NAME}\\{SONG_NAME}.mp3'.format(
                        ARTIST_NAME=self.artist.name, ALBUM_NAME=album.name, SONG_NAME="InvalidFilename")

            self.download_file(song.song_url,song_file,'wb')
            print('\t\tSong File:{} Saved'.format(song.name))

    def SQL_artist(self):
        Command = "INSERT INTO artist (name, gender, birthplace, occupation, birthday, representative, region, initial, play_count, image, intro, country)" \
                  "VALUES ('{NAME}',{GENDER},'{BIRTHPLACE}','{OCCUPATION}','{BIRTHADY}','{REPRESENTATIVE}',{REGION},'{INITIAL}',0,'{IMAGE}','{INTRO}','{COUNTRY}');".format(
            NAME=self.artist.name,
            GENDER=self.para['gender'],
            BIRTHPLACE=self.para['birthplace'],
            BIRTHADY=self.para['birthday'],
            REPRESENTATIVE=self.para['representative'],
            REGION=self.para['region'],
            INITIAL=self.para['initial'],
            IMAGE='/image/singer/{}.jpg'.format(self.artist.name),
            INTRO=self.artist.info,
            COUNTRY=self.para['country'],
            OCCUPATION=self.para['occupation']
        )
        return Command

    def SQL_album(self,album):
        Command = "INSERT INTO album (name, release_date, region, style, intro, image, play_count, artist_id)" \
                  " VALUES ('{NAME}','{RELEASE_DATE}',{REGION},{STYLE},'{INTRO}','{IMAGE}',0,{ARTIST_ID});".format(
            NAME=album.name,
            RELEASE_DATE=album.release_date,
            INTRO=album.info,
            REGION=self.para['region'],
            STYLE=self.para['style'],
            IMAGE='/image/album/{}/{}.jpg'.format(self.artist.name, album.name),
            ARTIST_ID="(SELECT id from artist where name='{}')".format(self.artist.name)
        )
        return Command

    def SQL_song(self,album,song):
        Command = "INSERT INTO song (name, artist_id, album_id, language, style, release_date, lyrics_path, image, play_count, file_path, region) " \
                  "VALUES ('{NAME}',{ARTIST_ID},{ALBUM_ID},'{LANGUAGE}',{STYLE},'{RELEASE_DATE}','{LYRICS_PATH}',NULL ,0,'{FILE_PATH}',{REGION});".format(
            NAME=song.name,
            ARTIST_ID="(SELECT id from artist WHERE name='{}')".format(self.artist.name),
            ALBUM_ID="(SELECT id from album WHERE name='{}' and album.artist_id=(SELECT id from artist WHERE name='{}'))".format(
                album.name, self.artist.name),
            LANGUAGE=self.para['language'],
            STYLE=self.para['style'],
            RELEASE_DATE=album.release_date,
            LYRICS_PATH='/lyrics/{}/{}/{}.lrc'.format(self.artist.name,album.name,song.name),
            FILE_PATH='/music/{}/{}/{}.mp3'.format(self.artist.name,album.name,song.name),
            REGION=self.para['region']
        )
        return Command



if __name__ == '__main__':
    # artist_para={
    #     'name':'Clémentine',
    #     'gender':2,
    #     'birthplace':'法国',
    #     'birthday':'1972-05-03',
    #     'representative':'Green Days',
    #     'region':4,
    #     'initial':'C',
    #     'country':'日本',
    #     'occupation':'歌手',
    #     'style':1,
    #     'language':'英法日',
    #     'limit':7,
    #     'offset':8,
    #     'id':159271
    # }
    # Spy = NetEaseSpider(para=artist_para)
    # Spy.parse_ip_web()
    #
    #
    # filew = open('G:\\Spring_Semester_2018\\J2EE实训\\数据\\音乐数据库\\data\\{}.json'.format(artist_para['name']), 'w', encoding='utf-8')
    # json.dump(artist_para, filew)
    # filew.close()
    #
    #
    # Spy.parse_artist_html()
    # album_num=Spy.artist.albums.__len__()
    # SQL_file = open('G:\\Spring_Semester_2018\\J2EE实训\\数据\\音乐数据库\\data\\insert_{}.sql'.format(Spy.artist.name), 'w',encoding='utf-8')
    # localtime = time.asctime(time.localtime(time.time()))
    # SQL_file.write('# {}'.format(localtime))
    # SQL_file.write('\n')
    #
    #
    # SQL_file.write(Spy.SQL_artist())
    # SQL_file.write('\n')
    # Spy.download_singer_img()
    # album_count=0
    # for album in Spy.artist.albums:
    #     album_count+=1
    #     Spy.download_album_img(album)
    #     Spy.parse_album_html(album)
    #     SQL_file.write(Spy.SQL_album(album))
    #     SQL_file.write('\n')
    #     print('Album:{}/{}'.format(album_count,album_num))
    #     for song in album.songs:
    #         SQL_file.write(Spy.SQL_song(album,song))
    #         SQL_file.write('\n')
    #     Spy.download_song(album)
    Updat_Image()
