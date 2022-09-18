import os
import json
import time
from datetime import date
from dateutil import parser
import argparse
import requests
from configs import settings

class TweetParser:

    def __init__(self, tweetfile = None, imgfolder=None, mode = 'recent'):
        self.bearer_token = settings.bearer_token
        self.keywords = ['malicious', 'spam', 'phish', 'phishing', 'smish', 'scam', 'fraud']
        #self.keywords = ['malicious', 'phish', 'smish', 'phishing', 'scam','fraud']
        archive_url = "https://api.twitter.com/2/tweets/search/all"
        recent_url = "https://api.twitter.com/2/tweets/search/recent"
        self.mode = mode
        if (mode == 'recent'):
            self.search_url = recent_url
        else:
            self.search_url = archive_url
        # waiting time for each query
        self.timeout = 3
        self.tweetfile = tweetfile
        self.imgfolder = imgfolder
        self.media_urls = set()
        self.media_info = {}
        self.tweet_info = {}
        self.user_info = {}

    def bearer_oauth(self, r):
        """
        Method required by bearer token authentication.
        """
        r.headers["Authorization"] = f"Bearer {self.bearer_token}"
        if (self.mode == 'recent'):
            r.headers["User-Agent"] = "v2RecentSearchPython"
        else:
            r.headers["User-Agent"] = "v2FullArchiveSearchPython"
        return r

    def connect_to_endpoint(self,url, params):
        response = requests.request("GET", self.search_url, auth=self.bearer_oauth, params=params)
        # print(response.status_code)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        return response.json()


    def search_tweet(self, start_time, end_time, next_token=None):
        # Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
        # expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
        start_time = parser.parse(start_time).strftime('%Y-%m-%dT%H:00:00.00Z')
        end_time = parser.parse(end_time).strftime('%Y-%m-%dT%H:00:00.00Z')
        query_params = {'query': '('+' OR '.join(self.keywords)+') sms has:images',
                        'next_token': next_token,
                        'start_time': f'{start_time}',
                        'end_time': f'{end_time}',
                        'tweet.fields': 'attachments,author_id,conversation_id,created_at,entities,geo,in_reply_to_user_id,lang,public_metrics,referenced_tweets,source',
                        'user.fields': 'created_at,description,public_metrics,url,verified',
                        'place.fields': 'country,country_code,geo,name,place_type',
                        'media.fields': 'media_key,type,url',
                        'expansions': 'author_id,geo.place_id,attachments.media_keys'}

        json_response = self.connect_to_endpoint(self.search_url, query_params)
        time.sleep(self.timeout)

        return json_response

    def crawl_tweet(self,start_time, end_time):
        cnt = 0
        with open(self.tweetfile, 'w') as f:
            results = self.search_tweet(start_time, end_time)
            f.write(json.dumps(results) + '\n')
            cnt += results['meta']['result_count']
            while ('next_token' in results['meta']):
                results = self.search_tweet(start_time, end_time, results['meta']['next_token'])
                f.write(json.dumps(results) + '\n')
                cnt += results['meta']['result_count']
            print("crawled %d results between %s and %s" % (cnt, start_time, end_time))
        print('done')

    def parse_meida_info(self):
        if (not os.path.exists(self.tweetfile)):
            print("filepath %s not exist, please crawl tweets" % (self.tweetfile))
            exit(-1)

        keys_info = {}
        with open(self.tweetfile) as f:
            for line in f:
                info = json.loads(line.strip())
                if ('includes' in info and 'media' in info['includes']):
                    media = info['includes']['media']
                    for item in media:
                        if ('url' in item):
                            url = item['url']
                            url = url.replace('https', 'http')
                            keys_info[item['media_key']] = url
                if ('data' not in info):
                    continue
                for data in info['data']:
                    if ('attachments' in data):
                        #month = parser.parse(data['created_at']).strftime('%Y-%m')
                        for key in data['attachments']['media_keys']:
                            if (key in keys_info and key not in self.media_info):
                                url = keys_info[key]
                                self.media_info[url] = {'media_url': url, 'created_at': data['created_at'], 'tweet_id': data['id']}

        print("%d image urls extracted from tweets" % (len(keys_info)))

        self.media_urls |= set(self.media_info.keys())

    def parse_tweet_info(self):
        if (not os.path.exists(self.tweetfile)):
            print("filepath %s not exist, please crawl tweets" % (self.tweetfile))
            exit(-1)

        with open(self.tweetfile) as f:
            for line in f:
                info = json.loads(line.strip())
                if ('data' not in info):
                    continue
                for data in info['data']:
                    #month = parser.parse(data['created_at']).strftime('%Y-%m')
                    tweet_id = data['id']
                    tagged_ids = []
                    if ('mentions' in data['entities']):
                        tagged_ids= [t['username'] for t in data['entities']['mentions']]

                    self.tweet_info[tweet_id] = {'tweet_id': tweet_id, 'created_at': data['created_at'], 'author_id': data['author_id'],
                                                 'conversation_id': data['conversation_id'], 'mentions': tagged_ids, 'source': data['source'],
                                                 'lang': data['lang'], 'text': data['text']}

    def parsr_user_info(self):
        if (os.path.exists(self.tweetfile)):
            print("filepath %s not exist, please crawl tweets" % (self.tweetfile))
            exit(-1)

        with open(self.tweetfile) as f:
            for line in f:
                info = json.loads(line.strip())
                if ('includes' in info and 'users' in info['includes']):
                    users = info['includes']['users']
                    for item in users:
                        uid = item['id']
                        if (uid not in self.user_info):
                            self.user_info[uid] = {'id': uid, 'name': item['name'], 'username': item['username'],
                                                   'public_metrics': item['public_metrics']}

    def download_imgs_wget(self):
        if not os.path.exists(self.imgfolder):
            os.mkdir(self.imgfolder)
        for url in self.media_urls:
            os.popen('wget '+url+' -nc -q -P '+ self.imgfolder)

    def download_imgs(self):
        if not os.path.exists(self.imgfolder):
            os.mkdir(self.imgfolder)
        for url in self.media_urls:
            try:
                r = requests.get(url, stream=True)
                if (r.status_code == 200):
                    imgname = url.split('/')[-1]
                    imgpath = os.path.join(self.imgfolder, imgname)
                    with open(imgpath,'wb') as f:
                        for chunk in r:
                            f.write(chunk)
            except:
                print('error when downloading image: '+url)
