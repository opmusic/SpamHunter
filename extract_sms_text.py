import cv2
import pytesseract
import re
from urlextract import URLExtract

from google_api import detect_sms_para

def is_overlap(box1, box2):
    x1, y1, w1, h1 = box1
    p1, q1, w2, h2 = box2

    x_tag = y_tag = False
    if (p1 <= x1 and x1 <= p1+w2) or (x1 <= p1 and p1 <= x1+w1):
        x_tag = True
    if (q1 <= y1 and y1 <= q1+h2) or (y1 <= q1 and q1 <= y1+h1):
        y_tag = True

    if (x_tag & y_tag):
        text_area = w1 * h1
        box_area = w2 * h2
        overlap_area = (min(x1+w1, p1+w2) - max(x1, p1)) * (min(y1+h1, q1+h2) - max(y1, q1))
        # print(overlap_area/text_area)
        if (overlap_area/text_area > 0.75):
            return True

    return (x_tag & y_tag)

def extract_sms_text(imgpath, boxes):
    img = cv2.imread(imgpath)

    d = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    n_boxes = len(d['level'])
    all_text = []
    for box in boxes:
        text = ''
        for i in range(n_boxes):
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            if is_overlap((x,y,w,h), box):
                if (len(d['text'][i].strip().split()) > 0):
                    text += d['text'][i]
        all_text.append(text)
    return all_text

def extract_sms_text_google(imgpath, boxes):
    para_boxes = detect_sms_para(imgpath)

    all_text = []
    for box in boxes:
        text = ''
        for info in para_boxes:
            if is_overlap(info['box'], box):
                if (len(info['text'].strip().split()) > 6):
                    text += info['text']
        all_text.append(text)
    return all_text

def extract_all_text(imgpath):
    img = cv2.imread(imgpath)

    config = r'-l eng+osd+snum --psm 6'
    txt = pytesseract.image_to_string(img, config=config)

    return txt

def extract_url_from_text(text):
    text = re.sub('([-/?&])\n',lambda x: x.group(1), text)
    text = re.sub('\n([-/.?&])', lambda x: x.group(1), text)

    extractor = URLExtract()
    urls = extractor.find_urls(text)

    return list(set(urls))

def extract_sender_from_text(text):
        tel_pattern1 = "^(\+\d{1,2}\s?)?1?\-?\.?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}"
        tel_pattern2 = "[A-Z]{2}-[A-Z]{6}"
        tel_pattern3 = "^([\d\-A-Za-z]*?)[>]"

        #select first 6 lines
        lines = text.split('\n')[:6]

        for str in lines:
            str = str.replace(' ','')
            r1 = re.search(tel_pattern1, str)
            if (r1):
                tel = r1.group(0)
                if (str.index(tel) < 5):
                    return tel
            r2 = re.search(tel_pattern2, str)
            if (r2):
                tel = r2.group(0)
                if (str.index(tel) < 5):
                    return tel

            r3 = re.search(tel_pattern3, str)
            if (r3):
                tel = r3.group(1)
                if (str.index(tel) < 5 and len(tel) > 5 and len(tel) < 11):
                    return tel

        return ''
