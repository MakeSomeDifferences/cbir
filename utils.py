# -*- coding: utf-8 -*-

import os
import json
from collections import namedtuple
import matplotlib.pyplot as plt
import cv2
import numpy as np


HParams = namedtuple('HParams',
                     'batch_size, hash_bits, '
                     'learning_rate, image_size, image_chanel, mode, class_num, use_gpu')


class Config:
    def __init__(self, config_dir, config_name):
        self.__config_dir = config_dir
        self.__config_name = config_name
        self.__data = None
        self.__init()

    def __init(self):
        self.__config_path_name = os.path.join(self.__config_dir, self.__config_name)
        if not os.path.exists(self.__config_dir):
            os.makedirs(self.__config_dir)
        self.load()

    def save(self, config):
        with open(self.__config_path_name, "w") as f:
            json.dump(config, f)

    def load(self):
        with open(self.__config_path_name) as f:
            self.__data = json.load(f)

    def get_image_retrieval_method(self):
        return self.__data["ImageRetrievalMethod"]

    def set_image_retrieval_method(self, image_retrieval_method):
        self.__data["ImageRetrievalMethod"] = image_retrieval_method

    def get_min_sim(self, image_retrieval_method):
        return self.__data["SearchMethod"][image_retrieval_method]["MinSim"]

    def set_min_sim(self, image_retrieval_method, min_sim):
        self.__data["SearchMethod"][image_retrieval_method]["MinSim"] = min_sim

    def get_max_return_num(self, image_retrieval_method):
        return self.__data["SearchMethod"][image_retrieval_method]["MaxReturnNum"]

    def set_max_return_num(self, image_retrieval_method, max_return_num):
        self.__data["SearchMethod"][image_retrieval_method]["MaxReturnNum"] = max_return_num

    def get_feature_dir(self, image_retrieval_method):
        return self.__data["SearchMethod"][image_retrieval_method]["FeatureDir"]

    def get_data_base_root(self):
        return self.__data["DataBaseRoot"]

    def get_data_base(self, image_retrieval_method):
        return self.__data["SearchMethod"][image_retrieval_method]["DataBase"]

    def get_feature_base_root(self):
        return self.__data["FeatureBaseRoot"]

    def get_all_image_retrieval_methods(self):
        return [x for x in self.__data["SearchMethod"].keys()]


def LBP(image):
    W, H = image.shape
    xx = [-1,  0,  1, 1, 1, 0, -1, -1]
    yy = [-1, -1, -1, 0, 1, 1,  1,  0]
    res = np.zeros((W - 2, H - 2), dtype="uint8")
    for i in range(1, W - 2):
        for j in range(1, H - 2):
            temp = ""
            for m in range(8):
                Xtemp = xx[m] + i
                Ytemp = yy[m] + j    #分别获得对应坐标点
                if image[Xtemp, Ytemp] > image[i, j]: #像素比较
                    temp = temp + '1'
                else:
                    temp = temp + '0'
            res[i - 1][j - 1] = int(temp, 2)   #写入结果中
    return res


def get_hist(image_path_name, size):
    try:
        image = cv2.imread(image_path_name, cv2.IMREAD_GRAYSCALE)
        image = cv2.resize(image, (128, 128))
        lbp = LBP(image)
        # lbp = local_binary_pattern(image, n_points, radius)
        n, bins, patches = plt.hist(lbp.flatten() * 1.0, bins=size, normed=False, edgecolor='None', facecolor='red')
        bins = [int(pin.get_height()) for pin in patches]
        plt.close()
        return bins
    except Exception as e:
        print(e, image_path_name)
    return None


def transform(hash_code):
    code = ""
    for b in hash_code:
        code += str(b)
    return code


def r_transform(hash_code):
    code = [int(b) for b in hash_code]
    return code


def normalization(code):
    max_num, min_num = max(code), min(code)
    return [(x - min_num) / (max_num - min_num) for x in code]

