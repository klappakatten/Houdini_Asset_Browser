from PySide2.QtWidgets import *
from PySide2.QtCore import *


class CategoryPanel(QWidget):
    def __init__(self, categories):
        super().__init__()
        self.category_list_widget = QListWidget()
        self.categories = categories

        self.init_ui()

        self.add_categories()

        self.show_active_sub_categories()


    @property
    def categories(self):
        return self._categories

    @categories.setter
    def categories(self, new_active_category):
        self._categories = new_active_category
        self.add_categories()

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.category_list_widget.setMinimumSize(50, 0)
        self.category_list_widget.horizontalScrollBar().hide()
        main_layout.addWidget(self.category_list_widget)
        self.setLayout(main_layout)

    def get_active_category(self):
        if self.category_list_widget.currentItem():
            return self.category_list_widget.currentItem().data(Qt.UserRole)
        else:
            return None

    def add_categories(self):
        self.category_list_widget.clear()
        if len(self.categories) == 0:
            return
        for category in self.categories:
            if len(category.assets) != 0:
                self.add_category_widget(category,100,35,16, False)
                for sub_category in category.sub_categories:
                    if sub_category.name in category.name:
                        continue
                    self.add_category_widget(sub_category,100,20,13,False)
        self.category_list_widget.setCurrentRow(0)

    def add_category_widget(self, category, width, height, font_size, bold):
        qsize = QSize(width, height)
        category_widget_item = QListWidgetItem()
        category_widget_item.setText(category.name.title())
        category_widget_item.setSizeHint(qsize)
        font = category_widget_item.font()
        font.setBold(bold)
        font.setPixelSize(font_size)
        category_widget_item.setFont(font)
        category_widget_item.setData(Qt.UserRole, category)
        return self.category_list_widget.addItem(category_widget_item)

    def show_active_sub_categories(self):
        active_category = self.get_active_category()

        try:
            active_category_parent = active_category.parent
        except Exception as e:
            active_category_parent = None
            #print(e)

        for i in range(self.category_list_widget.count()):
            category_list_widget_item = self.category_list_widget.item(i)
            category = category_list_widget_item.data(Qt.UserRole)

            if category.parent is None:
                category_list_widget_item.setHidden(False)
            elif category == active_category_parent:
                category_list_widget_item.setHidden(False)
            elif category.parent == active_category:
                category_list_widget_item.setHidden(False)
            elif category.parent == active_category_parent and active_category_parent is not None:
                category_list_widget_item.setHidden(False)
            else:
                category_list_widget_item.setHidden(True)



