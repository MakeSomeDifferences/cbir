# -*- coding: utf-8 -*-

from imageRetrieval import ImageHashRetrievalRetrieval


class ImageSearchFactory:

    def __init__(self, config):
        self.config = config
        self.image_retrieval = dict()

    def get_instance(self):
        image_retrieval_method = self.config.get_image_retrieval_method()
        if image_retrieval_method not in self.image_retrieval.keys():
            self.image_retrieval[image_retrieval_method] = ImageHashRetrievalRetrieval(self.config)
            self.image_retrieval[image_retrieval_method].load_data()
        return self.image_retrieval[image_retrieval_method]
