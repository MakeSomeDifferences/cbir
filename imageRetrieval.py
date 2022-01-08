# -*- coding: utf-8 -*-

import itertools
import math
import os
import json
import imagehash
from PIL import Image

from log import LOG
from utils import normalization, get_hist, transform, r_transform


class ImageRetrievalBase:

    def __init__(self):
        self.image_database = dict()

    def character_image(self, image_path):
        pass

    def character_directory(self, image_dir):
        pass

    def search(self, image_path):
        pass


class ImageHashRetrievalRetrieval(ImageRetrievalBase):

    def __init__(self, config):
        super().__init__()
        self.config = config

    def search(self, image_path):
        hash_code, hist_code = self.character_image(image_path)
        retrieval_result = []
        for key in self.image_database.keys():
            basic_sim = self.calc_sim(r_transform(key), hash_code)
            for item in self.image_database[key]:
                sim = self.calc_corr(item["hist_code"], hist_code)
                sim = 0.6 * basic_sim + 0.4 * sim
                one = {"image_path": item["image_path_name"], "sim": sim}
                retrieval_result.append(one)
        return sorted(retrieval_result, key=lambda x: x["sim"], reverse=True)

    @staticmethod
    def calc_sim(code_l, code_r):
        similarity = sum([1 if x == y else 0 for x, y in zip(code_l, code_r)])
        similarity = similarity / len(code_l)
        return similarity

    @staticmethod
    def calc_corr(a, b):
        a_avg = sum(a) / len(a)
        b_avg = sum(b) / len(b)
        cov_ab = sum([(x - a_avg) * (y - b_avg) for x, y in zip(a, b)])
        sq = math.sqrt(sum([(x - a_avg) ** 2 for x in a]) * sum([(x - b_avg) ** 2 for x in b]))
        corr_factor = cov_ab / sq
        return corr_factor

    @staticmethod
    def calc_sim2(a, b):
        sim = 0.0
        for a_x, b_x in zip(a, b):
            sim += abs(a_x - b_x)
        return (len(a) - sim) / len(a)

    def character_image(self, image_path):
        hash_type = self.config.get_image_retrieval_method()
        hist_code = normalization(get_hist(image_path, 16))
        if hash_type == "PSH":
            hash_code = imagehash.phash(Image.open(image_path), hash_size=4, highfreq_factor=4)
        elif hash_type == "AvgHASH":
            hash_code = imagehash.average_hash(Image.open(image_path), hash_size=4)
        elif hash_type == "DiffHASH":
            hash_code = imagehash.dhash(Image.open(image_path), hash_size=4)
        else:
            hash_code = imagehash.whash(Image.open(image_path), image_scale=16, hash_size=4, mode="haar")
        hash_code = list(itertools.chain(*hash_code.hash))
        hash_code = [0 if x else 1 for x in hash_code]

        print(len(hash_code))
        return hash_code, hist_code

    def character_directory(self, image_dir):
        cur_num = 1
        for image_name in os.listdir(image_dir):
            image_path_name = os.path.join(image_dir, image_name)
            hash_code, hist_code = self.character_image(image_path_name)
            self.save(image_path_name, hash_code, hist_code)
            print("Finish %d" % cur_num)
            LOG.info("Finish %d" % cur_num)
            cur_num += 1

    def save(self, image_path_name, hash_code, hist_code):
        item = {"image_path_name": image_path_name, "hist_code": hist_code}
        file_name = transform(hash_code)
        feature_dir = os.path.join(self.config.get_feature_base_root(), self.config.get_feature_dir(self.config.get_image_retrieval_method()))
        if not os.path.exists(feature_dir):
            os.mkdir(feature_dir)

        file_path_name = os.path.join(feature_dir, file_name)
        try:
            with open(file_path_name, "a") as f:
                item = json.dumps(item) + "\n"
                f.write(item)
        except Exception as e:
            print(e, file_path_name, len(file_path_name))

    def load_data(self):
        feature_dir = self.config.get_feature_dir(self.config.get_image_retrieval_method())
        feature_dir_path = os.path.join(self.config.get_feature_base_root(), feature_dir)

        if not os.path.exists(feature_dir_path):
            return

        file_names = os.listdir(feature_dir_path)
        for file_name in file_names:
            file_path_name = os.path.join(feature_dir_path, file_name)
            for line in open(file_path_name):
                item = json.loads(line.strip())
                item["hash_code"] = r_transform(file_name)
                if file_name not in self.image_database.keys():
                    self.image_database[file_name] = list()
                self.image_database[file_name].append(item)
