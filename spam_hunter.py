from query_tweet import TweetParser
from detect_sms_img import SMSDetector
from detect_tweet_text import TweetDetector
from extract_sms_text import extract_sms_text
from datetime import datetime, timezone, timedelta

import os,json

class SpamHunter:

    def __init__(self, start_time, end_time, resfile):
        self.start_time = start_time
        self.end_time = end_time
        self.twitterfile = 'data/tweet_'+end_time+'.json'
        self.imgfolder = 'data/images/2022-05'
        self.resfile = resfile

        self.tweetParser : TweetParser = TweetParser(self.twitterfile, self.imgfolder, mode = 'recent')
        self.smsDetector: SMSDetector = SMSDetector()
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
                    tweet_text = self.tweet_info[info['tweet_id']]['text']
                    tweet_label = self.tweetDetector.detect_tweet_text(tweet_text)
                    month = info['month']
                    if (sms_boxes):
                        sms_text = extract_sms_text(imgpath, sms_boxes)
                        info = {'image_name': imgname, 'image_path': imgpath, 'month': month, 'sms_label': True, 'sms_text': sms_text, 'tweet_label': tweet_label}
                    else:
                        info = {'image_name': imgname, 'image_path': imgpath, 'month': month, 'sms_label': False, 'tweet_label': tweet_label}
                    f.write(json.dumps(info) + '\n')

if __name__ == '__main__':
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days = 1)
    spamhunter =SpamHunter(start_time.strftime('%Y-%m-%dT%HZ'), end_time.strftime('%Y-%m-%dT%HZ'), 'data/detect_results.json')
    spamhunter.detect()
