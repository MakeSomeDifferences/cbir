# -*- coding: utf-8 -*-

import os.path

from ImageSearchFactory import ImageSearchFactory
from utils import Config

if __name__ == '__main__':

    # 预先计算特征
    config = Config(os.path.join(os.curdir, "data"), "config.json")
    search = ImageSearchFactory(config).get_instance()
    search.character_directory(search.config.get_data_base_root())
