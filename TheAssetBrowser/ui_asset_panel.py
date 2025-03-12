from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

from . import houdini_nodes
from . import  utility

def create_icon(image_path, background_color):
    image_pixmap = QPixmap(image_path)
    color_pixmap = QPixmap(image_pixmap.size())
    color_pixmap.fill(background_color)
    painter = QPainter(color_pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
    painter.drawPixmap(0, 0, image_pixmap)
    painter.end()
    return QIcon(color_pixmap)

class AssetPanel(QWidget):
    def __init__(self, active_category, asset_list):
        super().__init__()
        self.asset_list_widget = QListWidget()
        self.completer_list = []
        self._item_size = 200
        self.max_item_size = 300
        self.min_item_size = 100
        self.size_increment = 50
        self.completer = QCompleter(self.completer_list)
        self.active_category = active_category
        self.asset_list = asset_list
        self.search_bar = QLineEdit()
        self.plus_size_button = QPushButton("+")
        self.minus_size_button = QPushButton("-")

        self.init_ui()

        self.connect_signals()

    @property
    def asset_list(self):
        return self._asset_list

    @asset_list.setter
    def asset_list(self, new_list):
        self._asset_list = new_list
        self.add_assets()
        self.display_active_list_items()

    @property
    def active_category(self):
        return self._active_category

    @active_category.setter
    def active_category(self, new_active_category):
        self._active_category = new_active_category
        self.display_active_list_items()

    @property
    def item_size(self):
        return self._item_size

    @item_size.setter
    def item_size(self, new_item_size):
        self._item_size = utility.clamp(new_item_size,self.min_item_size,self.max_item_size)
        if self.asset_list_widget and self.asset_list_widget.count() > 0:
            self.asset_list_widget.setIconSize(QSize(self._item_size, self._item_size * 0.7))
            self.asset_list_widget.setMinimumWidth(self.item_size + 20)
            self.asset_list_widget.setMinimumHeight(int(self.item_size / 2))
            for asset_item_widget in self.get_list_widget_items():
                asset_item_widget.setSizeHint(QSize(self._item_size, self._item_size * 0.7))

    def init_ui(self):
        main_layout = QVBoxLayout()
        content_layout = QVBoxLayout()
        search_layout = QHBoxLayout()
        icon_size_layout = QVBoxLayout()

        # List View Settings
        self.asset_list_widget.setSortingEnabled(True)
        self.asset_list_widget.setViewMode(QListWidget.IconMode)
        self.asset_list_widget.setDragEnabled(False)
        self.asset_list_widget.setAcceptDrops(False)
        self.asset_list_widget.setDropIndicatorShown(False)
        self.asset_list_widget.setMinimumWidth(self.item_size + 20)
        self.asset_list_widget.setMinimumHeight(int(self.item_size / 2))
        self.asset_list_widget.setResizeMode(QListView.ResizeMode.Adjust)
        self.asset_list_widget.setIconSize(QSize(self.item_size, int(self.item_size * 0.7)))
        self.asset_list_widget.setAutoScroll(True)

        # Search Bar
        self.search_bar.setPlaceholderText("Search here...")

        # Completer
        self.completer.setCaseSensitivity(Qt.CaseSensitivity(False))
        self.completer.setFilterMode(Qt.MatchContains)
        self.search_bar.setCompleter(self.completer)

        self.plus_size_button.setFixedSize(QSize(15,15))
        self.minus_size_button.setFixedSize(QSize(15,15))

        icon_size_layout.addWidget(self.minus_size_button)
        icon_size_layout.addWidget(self.plus_size_button)

        search_layout.addWidget(self.search_bar)
        search_layout.addLayout(icon_size_layout,10)

        content_layout.addLayout(search_layout)
        content_layout.addWidget(self.asset_list_widget)

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    def connect_signals(self):
        self.asset_list_widget.itemActivated.connect(
            lambda: houdini_nodes.create_import_nodes(self.asset_list_widget.currentItem().data(Qt.UserRole)))

        self.search_bar.textChanged.connect(self.filter_search_items)
        self.completer.activated.connect(self.search_selection_pressed)
        self.plus_size_button.clicked.connect(self.increase_item_size)
        self.minus_size_button.clicked.connect(self.decrease_item_size)

    def increase_item_size(self):
        self.item_size += self.size_increment

    def decrease_item_size(self):
        self.item_size -= self.size_increment

    def add_assets(self):
        self.asset_list_widget.clear()
        self.completer_list.clear()

        for asset in self.asset_list:
            asset_item_widget = QListWidgetItem()
            asset_item_widget.setText(asset.name)
            asset_icon = create_icon(asset.icon, QColor(32, 32, 32))
            asset_item_widget.setIcon(asset_icon)
            asset_item_widget.setSizeHint(QSize(self.item_size, int(self.item_size * 0.8)))
            asset_item_widget.setData(Qt.UserRole, asset)
            self.asset_list_widget.addItem(asset_item_widget)
            self.completer_list.append(asset.name)
        self.update_completer_list(self.completer_list)

    def update_completer_list(self, new_completer_list):
        completer_model = QStringListModel(new_completer_list)
        self.completer.setModel(completer_model)

    def update_icons(self):
            for asset_item_widget in self.get_list_widget_items():
                asset = asset_item_widget.data(Qt.UserRole)
                if "default" in asset.icon.lower() or asset.icon == "":
                    for texture in utility.get_dir_contents(asset.path,".png",".jpg"):
                        if "thumbnail" in texture.lower():
                            icon = create_icon(texture,QColor(32,32,32))
                            asset_item_widget.setIcon(icon)
                            asset.icon = texture

    def display_active_list_items(self):
        for list_widget_item in self.get_list_widget_items():
            list_widget_item.setHidden(True)
            asset = list_widget_item.data(Qt.UserRole)
            active_category_assets = self.active_category.assets
            if asset in active_category_assets:
                list_widget_item.setHidden(False)

    def get_search_filter_active_items(self):
        popup = self.completer.popup()
        model = popup.model()
        active_items = []
        for row in range(model.rowCount()):
            index = model.index(row, 0)
            active_items.append(index.data())
        return active_items

    def search_selection_pressed(self, e):
        text = e
        self.search_bar.setText(text)
        for list_widget_item in self.get_list_widget_items():
            list_widget_item.setHidden(True)
            if list_widget_item.text() == e:
                list_widget_item.setHidden(False)

    def filter_search_items(self):
        if self.search_bar.text() == "":
            self.display_active_list_items()
            return
        list_widget_items = self.get_list_widget_items()
        for list_item in list_widget_items:
            data = list_item.data(Qt.UserRole)
            list_item.setHidden(True)
            if list_item.text() in self.get_search_filter_active_items() and data in self.active_category.assets:
                list_item.setHidden(False)

    def get_list_widget_items(self):
        list_widget_items = []
        for i in range(self.asset_list_widget.count()):
            item = self.asset_list_widget.item(i)
            list_widget_items.append(item)
        return list_widget_items
