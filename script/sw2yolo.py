# -*- coding:utf-8 -*-
# @Time     : 2021/7/13 17:10
# @Author   : Richardo Mu
# @FILE     : sw2yolo.py
# @Software : PyCharm
'''
python view_data.py t
to see annotations xmls' labels 
{'other_clothes': 2275, 'hat': 2060, 'reflective_clothes': 948, 'person': 491}
'''

import os
import os.path
import sys
import torch
import torch.utils.data as data
import cv2
import numpy as np

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
label_keys = {'other_clothes': "0", 'hat': "1", 'reflective_clothes': "2", 'person': "3"}

def parsexml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    filename = root.find('filename').text
    boxes = []
    classnames = []
    for obj in root.findall('object'):
        name = obj.find('name').text
        bndbox = obj.find('bndbox')
        xmin = bndbox.find('xmin').text
        ymin = bndbox.find('ymin').text
        xmax = bndbox.find('xmax').text
        ymax = bndbox.find('ymax').text
        if int(xmin) >= int(xmax) or int(ymin) >= int(ymax):
            continue
        boxes.append([int(xmin), int(ymin), int(xmax), int(ymax)])
        classnames.append(name)
    return classnames, boxes


save_path = '/home/data/tbw_data/face-dataset/yolodata/reflective-clothes/save_data'
root = "/home/data/tbw_data/face-dataset/yolodata/reflective-clothes/"
train_img_root = root + "JPEGImages"

print(os.path.dirname(train_img_root))
imgs_path = os.listdir(train_img_root)
imgs_path = [os.path.join(train_img_root, i) for i in imgs_path]

for i in range(len(imgs_path)):
    print(i, imgs_path[i])
    img = cv2.imread(imgs_path[i])
    base_img = os.path.basename(imgs_path[i])
    base_txt = os.path.basename(imgs_path[i])[:-4] + ".txt"
    save_img_path = os.path.join(save_path, base_img)
    save_txt_path = os.path.join(save_path, base_txt)
    with open(save_txt_path, "w") as f:
        height, width, _ = img.shape
        xml_path = imgs_path[i].replace("JPEGImages", "Annotations")[:-4] + ".xml"
        classnames, labels = parsexml(xml_path)
        # annotations = np.zeros((0, 14))
        if len(labels) == 0:
            continue
        for idx, label in enumerate(labels):
            annotation = np.zeros((1, 4))
            # bbox
            label[0] = max(0, label[0])
            label[1] = max(0, label[1])
            label[2] = min(width - 1, label[2])
            label[3] = min(height - 1, label[3])
            annotation[0, 0] = (label[0] + (label[2] -label[0]) / 2) / width  # cx
            annotation[0, 1] = (label[1] + (label[3]-label[1]) / 2) / height  # cy
            annotation[0, 2] = (label[2] -label[0]) / width  # w
            annotation[0, 3] = (label[2] -label[0]) / height  # h
            # str_label = "0" if classnames[idx] == "head" else "1"
            str_label = label_keys[classnames[idx]]
            for i in range(len(annotation[0])):
                str_label = str_label + " " + str(annotation[0][i])
            str_label = str_label.replace('[', '').replace(']', '')
            str_label = str_label.replace(',', '') + '\n'
            f.write(str_label)
    cv2.imwrite(save_img_path, img)
