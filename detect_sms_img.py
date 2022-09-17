import os
import json
import cv2
import shutil
import numpy as np

class SMSDetector:
    def __init__(self):
        self.config = "models/twitter_train_yolo.cfg"
        self.weights = "models/twitter_train_yolo_final.weights"
        self.names = "models/labels.txt"

        with open(self.names, "r") as f:
            self.classes = [line.strip() for line in f.readlines()]

        self.net, self.output_layers = self.load_model()

    def load_model(self):
        # Load the network
        net = cv2.dnn.readNetFromDarknet(self.config, self.weights)
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

        # Get the output layer from YOLO
        layers = net.getLayerNames()
        #for Ubuntu
        output_layers = [layers[i - 1] for i in net.getUnconnectedOutLayers()]
        #for Mac
        #output_layers = [layers[i[0] - 1] for i in net.getUnconnectedOutLayers()]

        return net, output_layers

    def detect_sms(self, imgpath, outpath = None):
        CONF_THRESH, NMS_THRESH = 0, 0

        # Read and convert the image to blob and perform forward pass to get the bounding boxes with their confidence scores
        img = cv2.imread(imgpath)
        height, width = img.shape[:2]

        blob = cv2.dnn.blobFromImage(img, 1 / 255.0, (416, 416), swapRB=False, crop=False)
        self.net.setInput(blob)
        layer_outputs =self.net.forward(self.output_layers)

        top_classes, confidences, b_boxes = [], [], []
        for output in layer_outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > CONF_THRESH:
                    center_x, center_y, w, h = (detection[0:4] * np.array([width, height, width, height])).astype('int')

                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    b_boxes.append([x, y, int(w), int(h)])
                    confidences.append(float(confidence))
                    top_classes.append(self.classes[int(class_id)])

        # Perform non maximum suppression for the bounding boxes to filter overlapping and low confident bounding boxes
        res = cv2.dnn.NMSBoxes(b_boxes, confidences, CONF_THRESH, NMS_THRESH)
        # print(res)
        if (len(res) > 0):
            indices = res.flatten().tolist()

            # Draw the filtered bounding boxes with their class to the image
            # self.draw_bounding_box(img, top_classes, b_boxes, outpath)

            return [b_boxes[index] for index in indices]
            #return [{'bound': b_boxes[index], 'conf': confidences[index]} for index in indices]
            # return [b_boxes[index] for index in indices]

        return []

    def draw_bounding_box(self, img, classes, b_boxes, outpath):
        colors = np.random.uniform(0, 255, size=(20, 3))

        for index in range(len(classes)):
            x, y, w, h = b_boxes[index]
            cv2.rectangle(img, (x, y), (x + w, y + h), colors[index], 2)
            cv2.putText(img, classes[index], (x + 5, y + 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, colors[index], 2)

        cv2.imwrite(outpath, img)

    def detect_sms_img(self, imgfolder, resfile, month = None):
        cnt = 0
        with open(resfile, 'w') as f:
            for path in os.listdir(imgfolder):
                if (path.endswith('.jpg') or path.endswith('.png')):
                    imgpath = os.path.join(imgfolder, path)
                    pred = self.detect_sms(imgpath, None)
                    if (pred):
                        info = {'image_name': path, 'month': month, 'is_sms': True, 'bound_boxes': pred}
                        cnt += 1
                    else:
                        info = {'image_name': path, 'month': month, 'is_sms': False, 'bound_boxes': []}
                    f.write(json.dumps(info) + '\n')
        print("detect sms images from %s : %d" % (imgfolder, cnt))