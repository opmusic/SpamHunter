import io
import logging

from configs import settings
if settings.enable_google_api:
    from google.oauth2 import service_account
    from google.cloud import vision
    from google.cloud import translate_v2

    breaks = vision.TextAnnotation.DetectedBreak.BreakType

def detect_sms_para(path):
    credentials = service_account.Credentials.from_service_account_file(settings.google_service_account_file)

    client = vision.ImageAnnotatorClient(credentials=credentials)

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.document_text_detection(image=image)
    texts = response.full_text_annotation

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    if (not texts):
        logging.info("no text detected in image: " + path)
        return [], []

    res = []
    for page in texts.pages:
        for block in page.blocks:
            for para in block.paragraphs:
                bound_x = [b.x for b in para.bounding_box.vertices]
                bound_y = [b.y for b in para.bounding_box.vertices]
                para_box = (min(bound_x), min(bound_y), max(bound_x), max(bound_y))

                box_text = ''
                for word in para.words:
                    for symbol in word.symbols:
                        box_text += symbol.text
                        if symbol.property.detected_break.type_ != breaks.UNKNOWN:
                            box_text += ' '

                res.append({'box': para_box, 'text': box_text.strip()})

    return res

def google_translate(text, target="en"):
    credentials = service_account.Credentials.from_service_account_file(settings.google_service_account_file)
    client = translate_v2.Client(credentials=credentials)

    translation = client.translate(text, target_language=target)

    res = translation["translatedText"]

    return res