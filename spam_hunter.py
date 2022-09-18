from query_tweet import TweetParser
from detect_sms_img import SMSDetector
from detect_tweet_text import TweetDetector
from extract_sms_text import *
from google_api import google_translate
from datetime import datetime, timezone, timedelta

from configs import settings
import os,json

class SpamHunter:

    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time
        self.twitterfile = os.path.join(settings.twitterfolder, 'tweet_'+end_time+'.json')

        #load settings
        self.twitter_mode = settings.twitter_mode
        self.imgfolder = settings.imgfolder
        self.resfile = settings.resfile

        self.enable_tweet_detect = settings.enable_tweet_detect
        self.enable_google_api = settings.enable_google_api

        self.tweetParser : TweetParser = TweetParser(self.twitterfile, self.imgfolder, mode = self.twitter_mode)
        self.smsDetector: SMSDetector = SMSDetector()
        if (self.enable_tweet_detect):
            self.tweetDetector: TweetDetector = TweetDetector()
        self.tweet_info = {}
        self.image_info = {}

    def detect(self):
        print('---------------crawl tweets---------------')
        self.tweetParser.crawl_tweet(self.start_time, self.end_time)
        self.tweetParser.parse_meida_info()
        self.tweetParser.parse_tweet_info()
        print('---------------download images---------------')
        self.tweetParser.download_imgs()

        self.tweet_info = self.tweetParser.tweet_info
        self.media_info = self.tweetParser.media_info

        print('---------------detect sms images---------------')
        detected_info = {}
        if (os.path.exists(self.resfile)):
            with open(self.resfile) as f:
                for line in f:
                    info = json.loads(line.strip())
                    key = info['image_name']
                    detected_info[key] = info
        with open(self.resfile,'a') as f:
            for url, info in self.media_info.items():
                imgname = url.split('/')[-1]
                imgpath = os.path.join(self.imgfolder, imgname)
                if (os.path.exists(imgpath) and imgname not in detected_info):
                    sms_boxes = self.smsDetector.detect_sms(imgpath, None)
                    tweet_label = True
                    if (sms_boxes):
                        # enable tweet_detect
                        if (self.enable_tweet_detect):
                            tweet_text = self.tweet_info[info['tweet_id']]['text']
                            tweet_lang = self.tweet_info[info['tweet_id']]['lang']

                            # translate tweet text
                            if (tweet_lang != 'en' and self.enable_google_api):
                                tweet_text = google_translate(tweet_text)

                            tweet_label = self.tweetDetector.detect_tweet_text(tweet_text)

                    if (sms_boxes and tweet_label > 0.5):
                        #extract urls & sender
                        all_text = extract_all_text(imgpath)
                        urls = extract_url_from_text(all_text)
                        sender = extract_sender_from_text(all_text)

                        #extract sms text
                        if (self.enable_google_api):
                            sms_text = extract_sms_text_google(imgpath, sms_boxes)
                        else:
                            sms_text = extract_sms_text(imgpath, sms_boxes)

                        #extract tagged ids
                        tid = info['tweet_id']
                        tagged_ids = self.tweet_info[tid]['mentions']

                        info = {'image_name': imgname, 'image_path': imgpath, 'created_at': info['created_at'], 'sms_label': len(sms_boxes) != 0, 'sms_text': sms_text, 'urls': urls, 'sender': sender, 'mentions': tagged_ids, 'tweet_label': tweet_label}
                    else:
                        info = {'image_name': imgname, 'image_path': imgpath, 'created_at': info['created_at'], 'sms_label': len(sms_boxes) != 0, 'tweet_label': tweet_label}
                    f.write(json.dumps(info) + '\n')

if __name__ == '__main__':
    #load end_time and start_time
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=1)

    start_time = start_time.strftime('%Y-%m-%dT%HZ')
    end_time = end_time.strftime('%Y-%m-%dT%HZ')

    if (settings.end_time):
        end_time = settings.end_time
    if (settings.start_time):
        start_time = settings.start_time
    spamhunter =SpamHunter(start_time, end_time)
    spamhunter.detect()