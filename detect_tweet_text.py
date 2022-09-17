#install allennlp
from allennlp.predictors.predictor import Predictor
from models.my_text_classifier import *

import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import TweetTokenizer
from nltk.tag import pos_tag
import re, string, os
import emoji

class TweetDetector:
    def __init__(self):
        self.model_path = 'models/model.tar.gz'
        self.predictor = Predictor.from_path(self.model_path, predictor_name = "sentence_classifier")
        self.input_path = ''
        self.output_path = ''

    def remove_noise(self, tweet_tokens, stop_words=()):
        cleaned_tokens = []

        for token, tag in pos_tag(tweet_tokens):
            if tag.startswith("NN"):
                pos = 'n'
            elif tag.startswith('VB'):
                pos = 'v'
            else:
                pos = 'a'

            lemmatizer = WordNetLemmatizer()
            token = lemmatizer.lemmatize(token.lower(), pos)

            # if len(token) > 0 and token not in string.punctuation and token not in stop_words:
            if len(token) > 0 and token not in stop_words:
                cleaned_tokens.append(emoji.demojize(token))
        return cleaned_tokens

    def tokenize(self, text):
        text = re.sub('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', 'EMAIL', text)
        # text = re.sub('@\w+','@USER', text)
        # r = url_regex.UrlRegex(text)
        # for t in r.links:
        #    text = text.replace(t.full,'HTTPURL')
        text = re.sub('\n', ' ', text)

        tweet_tokenizer = TweetTokenizer()

        tokens = tweet_tokenizer.tokenize(text)
        clean_tokens = self.remove_noise(tokens, stop_words=set())

        tokens_tag = [word for word in clean_tokens]

        return " ".join(tokens_tag)

    def detect_tweet_text(self, tweet_text):
        # remove tweet url
        tweet_text = re.sub(r'http[s]?://t\.co/[0-9a-zA-z]+', '', tweet_text)

        # remove noise
        clean_tweet_text = self.tokenize(tweet_text)
        # classify
        results = self.predictor.predict(sentence = clean_tweet_text)

        return results['probs'][0]