# -*- coding: utf-8 -*-

import os

from PIL import Image
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QListWidget, QListView, QApplication, QMessageBox, QListWidgetItem
from PyQt5 import QtWidgets, QtCore


FILE_TYPE = ['png', 'jpg', 'jpeg', 'tif', 'bmp', 'gif']
IMAGE_FOR = ['RGB', 'RGBA']


class ImageInfo(QListWidgetItem):
    def __init__(self, name_path, sim):
        super(ImageInfo, self).__init__()
        self.name_path = name_path
        self.sim = sim


class ImageBrowser(QtWidgets.QWidget):

    def __init__(self):
        super(ImageBrowser, self).__init__()
        self.__init_ui()

    def __init_dir(self):
        self.setWindowTitle("Image Viewer")
        self.setMinimumSize(1200, 500)
        self.dirModel = QtWidgets.QDirModel(self)

        # 只显示文件夹
        self.dirModel.setFilter(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot)

        # 文件夹列表view
        self.dirTreeView = QtWidgets.QTreeView()

        # 绑定model
        self.dirTreeView.setModel(self.dirModel)
        self.dirTreeView.hideColumn(1)
        self.dirTreeView.hideColumn(2)
        self.dirTreeView.hideColumn(3)
        self.dirTreeView.setMinimumSize(200, 200)

        # DirTree事件响应
        self.dirTreeView.selectionModel().selectionChanged.connect(self.dir_tree_clicked)

    def __init_ui(self):
        self.lock = QtCore.QMutex()
        layout = QtWidgets.QHBoxLayout()
        self.__init_dir()
        self.__init_image()
        layout.addWidget(self.dirTreeView)
        layout.addWidget(self.imageListView)
        self.setLayout(layout)

    def __init_image(self):
        self.imageListView = QListWidget()
        self.imageListView.setViewMode(QListView.IconMode)
        self.imageListView.setIconSize(QSize(80, 80))
        self.imageListView.setSpacing(20)
        self.imageListView.setMovement(QListWidget.Static)
        self.imageListView.setResizeMode(QListWidget.Adjust)

    def add_image(self, path):
        if not self.lock.tryLock(timeout=1):
            QMessageBox.about(self, "Warning", "Image dir is showing, wait please!")
            return

        self.imageListView.clear()
        for idx, item in enumerate(os.listdir(path)):
            if not item.split('.')[-1] in FILE_TYPE:
                continue
            try:
                img = ImageInfo(name_path=path + "/" + item, sim=0)
                print(img.name_path)
                icon = QIcon()
                image = Image.open(img.name_path)
                if image.mode not in IMAGE_FOR:
                    image = image.convert(IMAGE_FOR[0])
                image = image.toqpixmap().scaled(70, 70)
                icon.addPixmap(image)
                img.setIcon(icon)
                self.imageListView.addItem(img)
                print(self.imageListView.count())

                if idx % 10 == 0:
                    QApplication.processEvents()
            except Exception as e:
                print(e)
        QApplication.processEvents()
        self.lock.unlock()

    def dir_tree_clicked(self):
        path = self.dirModel.filePath(self.dirTreeView.selectedIndexes()[0])
        self.add_image(path)
