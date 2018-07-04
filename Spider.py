import urllib.request
import re
import itertools
import urllib.parse
import time
import json
import os

def download(url,user_agent='lucas',num_retries=2):
    print('Download:',url)
    headers={'User-agent':user_agent}
    request=urllib.request.Request(url,headers=headers)
    try:
        html=urllib.request.urlopen(request).read()
    except urllib.request.URLError as e:
        print('Download error:',e.reason)
        html=None
        if num_retries>0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                return download(url,user_agent, num_retries - 1)
    return html


def crawl_sitemap(url):
    sitemap=download(url)
    sitemap = sitemap.decode('utf-8')

    # TypeError:cannot use a string pattern on a bytes-like object
    # Solution: sitemap=sitemap.decode('utf-8')
    links=re.findall('<loc>(.*?)</loc>',sitemap)
    for link in links:
        html=download(link)


def iterator_crawler(url1):
    max_errors=5
    num_errors=0
    for page in itertools.count(1):
        url='{}{}'.format(url1,page)
        html=download(url)
        if html is None:
            num_errors+=1
            if num_errors==max_errors:
                break
            else:
                num_errors=0


def get_links(html):
    webpage_regex=re.compile('<a[^>]+href=["\'](.*?)["\']',re.IGNORECASE)
    return webpage_regex.findall(html)


def link_crawler(seed_url,link_regex):
    crawl_queue=[seed_url]
    seen=set(crawl_queue)
    while crawl_queue:
        url=crawl_queue.pop()
        html=download(url)
        for link in get_links(html):
            if re.match(link_regex,link):
                link=urllib.parse.urljoin(seed_url,link)
                if link not in seen:
                    seen.add(link)
                    crawl_queue.append(link)

class spider:
    def __init__(self,artists):
        self.artists=artists

    def download(SELF,url, user_agent='lucas', num_retries=2):
        start=time.time()
        print('Download:', url)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
                   'Referer': 'https://music.163.com/',
                   'Accept-Language':'zh-CN, zh;q=0.8',
                   'Content-Type':'application/x-www-form-urlencoded'
                   }
        request = urllib.request.Request(url, headers=headers)
        try:
            html = urllib.request.urlopen(request).read()
        except urllib.request.URLError as e:
            print('Download error:', e.reason)
            html = None
            if num_retries > 0:
                if hasattr(e, 'code') and 500 <= e.code < 600:
                    return download(url, user_agent, num_retries - 1)
        print('         Time Used:{:.2}'.format(time.time()-start))
        return html

    def get_url(self,id):
        # Get URL
        print('Get URL of Song ID:{}!'.format(id))
        lyric_url = 'http://music.163.com/api/song/media?id={}'.format(id)
        song_url = 'http://music.163.com/song/media/outer/url?id={}.mp3'.format(id)
        return lyric_url,song_url

    def get_singer_img(self,name,url):
        file=open('G:\\Spring_Semester_2018\\J2EE实训\数据\\音乐数据库\\image\\singer\\{}.jpg'.format(name),'wb')
        img=self.download(url)
        file.write(img)
        file.close()
        print('Singer:{} Got Img Successfully!'.format(name))

    def get_album_img(self,singer_name,album_name,url):
        try:
            os.mkdir('G:\\Spring_Semester_2018\\J2EE实训\数据\\音乐数据库\\image\\album\\{}'.format(singer_name))
        except OSError:
            pass
        file=open('G:\\Spring_Semester_2018\\J2EE实训\数据\\音乐数据库\\image\\album\\{}\\{}.jpg'.format(singer_name,album_name),'wb')
        album_img=self.download(url)
        file.write(album_img)
        file.close()
        print('Singer:{} Album:{} Got Img Successfully!'.format(singer_name,album_name))

    def crawler(self):
        for artist in list(self.artists):
            SQL_file = open('G:\\Spring_Semester_2018\\J2EE实训\\数据\\音乐数据库\\data\\insert_{}.sql'.format(artist), 'w')
            localtime = time.asctime(time.localtime(time.time()))
            SQL_file.write('# {}'.format(localtime))
            SQL_file.write('\n')
            print('Begin Singer:{}'.format(artist))
            Command = 'INSERT INTO artist (name, gender, birthplace, occupation, birthday, representative, region, initial, play_count, image, intro, country)' \
                      'VALUES ("{NAME}",{GENDER},"{BIRTHPLACE}","{OCCUPATION}","{BIRTHADY}","{REPRESENTATIVE}",{REGION},"{INITIAL}",0,"{IMAGE}","{INTRO}","{COUNTRY}");'.format(
                NAME=artist,
                GENDER=self.artists[artist]['Information']['gender'],
                BIRTHPLACE=self.artists[artist]['Information']['birthplace'],
                BIRTHADY=self.artists[artist]['Information']['birthday'],
                REPRESENTATIVE=self.artists[artist]['Information']['representative'],
                REGION=self.artists[artist]['Information']['region'],
                INITIAL=self.artists[artist]['Information']['initial'],
                IMAGE='/image/singer/{}.jpg'.format(artist),
                INTRO=self.artists[artist]['Information']['intro'],
                COUNTRY=self.artists[artist]['Information']['country'],
                OCCUPATION=self.artists[artist]['Information']['occupation']
            )
            SQL_file.write(Command)
            SQL_file.write('\n')
            self.get_singer_img(artist,self.artists[artist]['Information']['image'])

            for albums in list(self.artists[artist]['专辑']):
                print('     Begin Album:{}'.format(albums))
                Command ='INSERT INTO album (name, release_date, region, style, intro, image, play_count, artist_id)' \
                         ' VALUES ("{NAME}","{RELEASE_DATE}",{REGION},{STYLE},"{INTRO}","{IMAGE}",0,{ARTIST_ID});'.format(
                    NAME=albums,
                    RELEASE_DATE=self.artists[artist]['专辑'][albums]['release_date'],
                    INTRO=self.artists[artist]['专辑'][albums]['intro'],
                    REGION=self.artists[artist]['专辑'][albums]['region'],
                    STYLE=self.artists[artist]['专辑'][albums]['style'],
                    IMAGE='/image/album/{}/{}.jpg'.format(artist,albums),
                    ARTIST_ID='(SELECT id from artist where name="{}")'.format(artist)
                )
                SQL_file.write(Command)
                SQL_file.write('\n')
                self.get_album_img(artist,albums,self.artists[artist]['专辑'][albums]['image'])

                for song in list(self.artists[artist]['专辑'][albums]['歌曲']):
                    print(          'Begin Song:{}'.format(song))
                    song_name=song
                    song_id = self.artists[artist]['专辑'][albums]['歌曲'][song]['id']
                    lyrics_path='/lyrics/{}/{}/{}.lrc'.format(artist,albums,song)
                    file_path='/music/{}/{}/{}.mp3'.format(artist,albums,song)
                    Command='INSERT INTO song (name, artist_id, album_id, language, style, release_date, lyrics_path, image, play_count, file_path, region) ' \
                            'VALUES ("{NAME}",{ARTIST_ID},{ALBUM_ID},"{LANGUAGE}",{STYLE},"{RELEASE_DATE}","{LYRICS_PATH}",NULL ,0,"{FILE_PATH}",{REGION});'.format(
                        NAME=song,
                        ARTIST_ID='(SELECT id from artist WHERE name="{}")'.format(artist),
                        ALBUM_ID='(SELECT id from album WHERE name="{}" and album.artist_id=(SELECT id from artist WHERE name="{}"))'.format(albums,artist),
                        LANGUAGE=self.artists[artist]['专辑'][albums]['歌曲'][song]['language'],
                        STYLE=self.artists[artist]['专辑'][albums]['style'],
                        RELEASE_DATE=self.artists[artist]['专辑'][albums]['release_date'],
                        LYRICS_PATH=lyrics_path,
                        FILE_PATH=file_path,
                        REGION=self.artists[artist]['专辑'][albums]['region']
                    )
                    SQL_file.write(Command)
                    SQL_file.write('\n')
                    lyric_url,song_url=self.get_url(song_id)

                    # Get Lrics
                    time.sleep(2)
                    lyrics_html = self.download(lyric_url).decode('utf-8')
                    lyrics = re.split('":"|","', lyrics_html)[1]
                    lyrics = lyrics.strip('\'')
                    lyrics = lyrics.replace('\\n', '\n')
                    try:
                        os.mkdir(
                            'G:\\Spring_Semester_2018\\J2EE实训\\数据\\音乐数据库\\lyrics\\{ARTIST_NAME}'.format(
                                ARTIST_NAME=artist))
                    except OSError:
                        pass
                    try:
                       os.mkdir(
                           'G:\\Spring_Semester_2018\\J2EE实训\\数据\\音乐数据库\\lyrics\\{ARTIST_NAME}\\{ALBUM_NAME}\\'.format(
                               ARTIST_NAME=artist, ALBUM_NAME=albums))
                    except OSError:
                       pass
                    lyrics_file = open(
                        'G:\\Spring_Semester_2018\\J2EE实训\\数据\\音乐数据库\\lyrics\\{ARTIST_NAME}\\{ALBUM_NAME}\\{SONG_NAME}.lrc'.format(
                            ARTIST_NAME=artist, ALBUM_NAME=albums, SONG_NAME=song_name), 'w')
                    lyrics_file.write(lyrics)
                    lyrics_file.close()
                    print('Lyric File:{} Saved'.format(song_name).center(16))

                    # Get File
                    time.sleep(1)
                    song_html=self.download(song_url)
                    try:
                        os.mkdir(
                            'G:\\Spring_Semester_2018\\J2EE实训\\数据\\音乐数据库\\music\\{ARTIST_NAME}'.format(
                                ARTIST_NAME=artist))
                    except OSError:
                        pass
                    try:
                        os.mkdir(
                        'G:\\Spring_Semester_2018\\J2EE实训\\数据\\音乐数据库\\music\\{ARTIST_NAME}\\{ALBUM_NAME}\\'.format(
                            ARTIST_NAME=artist, ALBUM_NAME=albums))
                    except OSError:
                        pass
                    song_file = open(
                        'G:\\Spring_Semester_2018\\J2EE实训\\数据\\音乐数据库\\music\\{ARTIST_NAME}\\{ALBUM_NAME}\\{SONG_NAME}.mp3'.format(
                            ARTIST_NAME=artist, ALBUM_NAME=albums, SONG_NAME=song_name), 'wb')
                    song_file.write(song_html)
                    song_file.close()
                    print('Song File:{} Saved'.format(song_name).center(16))
            filew = open('G:\\Spring_Semester_2018\\J2EE实训\\数据\\音乐数据库\\data\\{}.json'.format(artist), 'w', encoding='utf-8')
            json.dump(self.artists, filew)
            filew.close()
            SQL_file.close()


if __name__ == '__main__':
    artists = {
        'Michael Jackson': {
            'Information': {
                'name': 'Michael Jackson',
                'gender': 1,
                'birthplace': '美国',
                'occupation': '歌手',
                'birthday': '1958-8-29',
                'representative': 'We are the world',
                'region': 3,
                'initial': 'M',
                'image': 'http://p3.music.126.net/WoMhaqFqAU1oLIb17VOE3g==/109951163025141447.jpg?param=640y300',
                'intro': '迈克尔·杰克逊（Michael Jackson，1958.8.29－2009.6.25）全名迈克尔·约瑟夫·杰克逊，简称MJ。是一名在世界各地影响力和知名度最大的音乐家、舞蹈家、艺术家、表演家、慈善家、被誉为流行音乐之王。',
                'country': '美国'
            },
            '专辑': {
                'Scream': {
                    'intro': '两度入列摇滚名人殿堂 流行界唯一天王 首张舞曲概念精选专辑.',
                    'image': 'http://p4.music.126.net/JZpY3RvA3AVjru77UFz9YA==/18361844184647224.jpg?param=177y177',
                    'release_date': '2017-09-29',
                    'region': 3,
                    'style': 1,
                    '歌曲': {
                        'This Place Hotel (a.k.a. Heartbreak Hotel)': {
                            'id': 509512556,
                            'language': '英语',
                        },
                        'Thriller': {
                            'id': 509512565,
                            'language': '英语',
                        },
                        'Blood on the Dance Floor': {
                            'id': 509512559,
                            'language': '英语',
                        },
                        'Torture': {
                            'id': 509512560,
                            'language': '英语',
                        },
                        'Scream': {
                            'id': 509512566,
                            'language': '英语',
                        },
                        'Dangerous': {
                            'id': 509512569,
                            'language': '英语',
                        },
                        'Unbreakable': {
                            'id': 509512563,
                            'language': '英语',
                        },
                        'Ghosts': {
                            'id': 509512562,
                            'language': '英语',
                        },
                    }
                },
                'Michael': {
                    'intro': '已逝的流行音乐之王Michael Jackson的全新录音室专辑将于12月14日在全美发行，新专辑的名字叫做《Michael》。',
                    'image': 'http://p3.music.126.net/dOJEBAYUDBWUhYSuySrkmg==/6639950721056545.jpg?param=177y177',
                    'release_date': '2010-12-13',
                    'region': 3,
                    'style': 1,
                    '歌曲': {
                        'Hollywood Tonight': {
                            'id': 21177807,
                            'language': '英语',
                        },
                        'Keep Your Head Up': {
                            'id': 21177809,
                            'language': '英语',
                        },
                        'Best Of Joy': {
                            'id': 21177813,
                            'language': '英语',
                        },
                        'Breaking News': {
                            'id': 21177815,
                            'language': '英语',
                        },
                        'Behind The Mask': {
                            'id': 21177819,
                            'language': '英语',
                        },
                        'Much Too Soon': {
                            'id': 21177822,
                            'language': '英语',
                        },

                    }
                },

            }
        }
    }

    spy=spider(artists)
    spy.crawler()

