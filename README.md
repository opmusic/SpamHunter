# SpamHunter
  This is our repo for the paper CCS'2022 -- Clues in Tweets: Twitter-Guided Discovery and Analysis of SMS Spam.
  
  ## How to install
  You should install allennlp, nltk, tesseract manually to use the specified NLP models and OCR tool. The default python version is Python3.7.10.
  * allennlp: https://github.com/allenai/allennlp
  * nltk: https://www.nltk.org/install.html
  * tesseract: https://tesseract-ocr.github.io/tessdoc/Installation.html
  
  ## How to run
  <pre> python spam_hunter.py</pre>
  
  ## Settings
  specify the following parameters in config/settings.py
   * bearer_token : Twitter API token
   * twitterfolder: folder to store the original crawled tweet informaion
   * imgfolder: folder to store all images downloaded from tweet attachments
   * resfile: store the detection results
   * start_time: default 1 day before the current time (UTC time)
   * end_time: current time (UTC time)
  
  ## Modules
   * class SpamHunter -- main class
   * class SMSDetector -- SMS image detector
   * class TweetDetector -- Spam-reporting tweet classifier
   * extract_sms_text.py -- OCR
