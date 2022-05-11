import cv2
import pytesseract

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
        # if (overlap_area/text_area > 0.75):
        #    return True

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
            if is_overlap(box, (x,y,w,h)):
                if (d['text'][i].strip()):
                    text += d['text'][i].strip()
                    text += ' '
        all_text.append(text)
    return all_text

#imgpath = 'data/images/2022-05/FSUKKe6WYAEQlBH.jpg'
#print(ocr(imgpath, [179, 36, 865, 197]))