# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PIL import Image

from ImageBrowser import ImageInfo, ImageBrowser
from ImageSearchFactory import ImageSearchFactory
from utils import Config


class ImageRetrieval(QMainWindow):
    def __init__(self):
        super(ImageRetrieval, self).__init__()

        self.__init_config()
        self.__init_ui()
        self.__init_method()

    def __init_config(self):
        self.__config = Config("data//", "config.json")

    def __init_ui(self):

        # 系统图标
        system_icon = 'ui\\system.png'
        search_button_icon = 'ui\\search.png'
        open_button_icon = 'ui\\open.png'
        about_icon = 'ui\\about.png'
        system_name = 'ImageRetrieval'

        # 菜单项
        menu_bar = self.menuBar()
        about_action = QAction(QIcon(about_icon), '&About', self)
        about_action.setStatusTip('About')
        about_action.triggered.connect(self.about)

        help_menu = menu_bar.addMenu('Help')
        help_menu.addAction(about_action)

        # 载入图像显示区域
        layout = QVBoxLayout()
        image_show_group_box = QGroupBox("Image Show")
        self.image_show = QLabel()
        self.image_show.setMinimumSize(200, 200)
        self.curr_img_path = None
        below_layout = QHBoxLayout()

        # 图像搜索按钮
        self.search_image = QPushButton()
        self.search_image.setText("Search")
        self.search_image.setIcon(QIcon(search_button_icon))
        self.search_image.clicked.connect(self.on_search_image)

        # 图像载入按钮
        self.load_image = QPushButton()
        self.load_image.setText("Load Image")
        self.load_image.setIcon(QIcon(open_button_icon))
        self.load_image.clicked.connect(self.on_load_image)

        below_layout.addWidget(self.load_image)
        below_layout.addWidget(self.search_image)
        layout.addWidget(self.image_show)
        layout.addLayout(below_layout)
        image_show_group_box.setMinimumSize(300, 300)
        image_show_group_box.setLayout(layout)

        # 图像检索结果显示区域
        search_result_group_box = QGroupBox("Search Result")
        self.image_list = QListWidget()
        self.image_list.setViewMode(QListView.IconMode)
        self.image_list.setIconSize(QSize(100, 100))
        self.image_list.setSpacing(20)
        self.image_list.setMovement(QListWidget.Static)
        self.image_list.setMinimumSize(550, 300)
        self.image_show.setAlignment(QtCore.Qt.AlignCenter)
        self.image_list.setResizeMode(QListWidget.Adjust)
        self.image_list.itemDoubleClicked.connect(self.on_image_list_double_clicked)

        layout = QVBoxLayout()
        layout.addWidget(self.image_list)
        search_result_group_box.setLayout(layout)

        # 文件浏览
        image_group_box = QGroupBox("Image browser")
        layout = QHBoxLayout()
        layout.addWidget(ImageBrowser())
        image_group_box.setLayout(layout)

        # 设置整体页面布局
        layout = QHBoxLayout()
        layout.addWidget(image_show_group_box)
        layout.addWidget(search_result_group_box)

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(image_group_box)
        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)
        self.setWindowTitle(system_name)
        self.setMinimumSize(1550, 800)
        self.setWindowIcon(QIcon(system_icon))
        self.move_center()

    def __init_method(self):
        self.image_retrieval = ImageSearchFactory(self.__config)

    def move_center(self):
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2))

    def on_image_list_double_clicked(self, index):
        image_path_name = index.name_path
        self.set_image_show(image_path_name)

    def show_result(self, image_list):
        max_return_num = self.__config.get_max_return_num(self.__config.get_image_retrieval_method())
        min_sim = self.__config.get_min_sim(self.__config.get_image_retrieval_method())

        self.image_list.clear()
        for idx, img in enumerate(image_list):
            if img["sim"] >= 0.01 * min_sim:
                img = ImageInfo(name_path=img["image_path"], sim=img["sim"])
                show_img = self.adjust_image(img.name_path)
                if show_img:
                    icon = QIcon()
                    icon.addPixmap(show_img)
                    img.setIcon(icon)
                    img.setText("%s" % str(round(img.sim, 4)))
                    self.image_list.addItem(img)
            if idx % 10 == 0 or idx == len(image_list) - 1:
                QApplication.processEvents()

            # 触发刷新
            if self.image_list.count() >= max_return_num:
                break

    def on_search_image(self):
        instance = self.image_retrieval.get_instance()
        image_list = instance.search(self.curr_img_path)
        self.show_result(image_list)

    @staticmethod
    def adjust_image(image_path):
        img = Image.open(image_path)
        if img.mode != 'RGB' and img.mode != 'RGBA':
            img = img.convert('RGB')
        img = img.resize((200, 200))
        return img.toqpixmap()

    def on_load_image(self):
        image_path_name, image_type = QFileDialog.getOpenFileName(self, "打开图片", "", "*.jpg;;*.png;;All Files(*)")
        if image_path_name:
            self.set_image_show(image_path_name)

    def set_image_show(self, image_path_name):
        self.curr_img_path = image_path_name
        img = ImageRetrieval.adjust_image(image_path_name)
        self.image_show.setScaledContents(True)
        self.image_show.setPixmap(img)

    def about(self):
        QMessageBox.about(self, "About Application", "This <b>application</b> is kira's graduation project demo, "
                                                     "a typical cbir system.")


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    main_window = ImageRetrieval()
    main_window.show()
    # main_window.showFullScreen()
    # main_window.showMaximized()
    sys.exit(app.exec_())
