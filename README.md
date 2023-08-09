# SpamHunter
  This is our repo for the paper CCS'2022 -- Clues in Tweets: Twitter-Guided Discovery and Analysis of SMS Spam. Here is our dataset repository: https://github.com/opmusic/SpamHunter_dataset.
  
  ## How to install
  You should install allennlp, nltk, tesseract manually to use the specified NLP models and OCR tool. The default python version is Python3.7.10. To use the allennlp models, the version of protobuf must be 3.20.x. Note you need to install git lfs to download our models. In case you have problems when downloading the weights of our Yolo model, we also provide a backup link: https://drive.google.com/file/d/1AkC5ZDsFq38alDxy7OdKUBZ3AMsdw8NU/view?usp=sharing
  * allennlp: https://github.com/allenai/allennlp
  * nltk: https://www.nltk.org/install.html
  * tesseract: https://tesseract-ocr.github.io/tessdoc/Installation.html
  
  ## How to run
  <pre> python spam_hunter.py</pre>
  
  ## Settings
  specify the following parameters in config/settings.py
   * enable_tweet_detect: if enable the tweet detection model
   * bearer_token: Twitter API token
   * twitter_mode: recent or archive (https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference)
   * twitterfolder: folder to store the original crawled tweet informaion
   * imgfolder: folder to store all images downloaded from tweet attachments
   * resfile: store the detection results
   * enable_google_api: if enable google API
   * google_service_account_file: path to google service account file
   * start_time: start time of tweets created
   * end_time: end time of tweets created
  
  ## Modules
   * class SpamHunter -- main class
   * class SMSDetector -- SMS image detector
   * class TweetDetector -- Spam-reporting tweet classifier
   * extract_sms_text.py -- OCR
   * google_api.py -- Google cloud service API
