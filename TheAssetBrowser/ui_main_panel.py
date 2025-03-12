from importlib import reload

from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

from . import ui_category_panel
from . import ui_asset_panel
from . import ui_path_panel
from . import Items
from . import utility
from . import houdini_nodes

reload(Items)
reload(ui_category_panel)
reload(ui_asset_panel)
reload(ui_path_panel)
reload(utility)
reload(houdini_nodes)

class UiMainWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.category_start_width = [120]
        self.path_start_width = [33, 100]

        try:
            self.asset_browser_root_path = utility.get_value_from_json(utility.get_json_path(), 'asset_path')
        except ValueError as e:
            print(
                f"failed to find root path setting from: {utility.get_dir(__file__)}/settings.json, edit json or add asset folder to the asset folder path input {e}")
            self.asset_browser_root_path = ""

        self.asset_manager = Items.AssetManager()
        self.init_asset_manager()

        self.category_panel = ui_category_panel.CategoryPanel(self.asset_manager.categories)
        self.asset_panel = ui_asset_panel.AssetPanel(self.category_panel.get_active_category(),self.asset_manager.assets)
        self.path_panel = ui_path_panel.PathPanel(self.asset_browser_root_path)

        self.init_ui()

        self.connect_signals()

    def init_ui(self):
        # Set Style Sheet
        style_str = utility.read_text_file_to_string(f'{utility.get_dir(__file__)}/style.qss')
        self.setStyleSheet(style_str)

        main_layout = QVBoxLayout()

        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.addWidget(self.category_panel)
        content_splitter.addWidget(self.asset_panel)
        content_splitter.setCollapsible(1, False)
        content_splitter.setSizes(self.category_start_width)
        content_splitter.setStretchFactor(1, 3)

        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.addWidget(self.path_panel)
        main_splitter.addWidget(content_splitter)
        main_splitter.setSizes(self.path_start_width)
        main_splitter.setStretchFactor(1, 3)
        main_splitter.setCollapsible(1, False)

        main_layout.addWidget(main_splitter)

        self.setLayout(main_layout)

    def connect_signals(self):
        self.path_panel.generate_thumbnail_button.clicked.connect(self.generate_thumbnails)
        self.category_panel.category_list_widget.currentItemChanged.connect(self.update_active_category)
        self.path_panel.file_path_line_edit.textChanged.connect(self.update_asset_path)

    def update_asset_path(self):
        try:
            self.asset_browser_root_path = self.path_panel.file_path_line_edit.text()
            self.init_asset_manager()
            self.category_panel.categories = self.asset_manager.categories
            self.asset_panel.asset_list = self.asset_manager.assets
            self.asset_panel.active_category = self.category_panel.get_active_category()
        except PermissionError as e:
            print(e)

    def update_active_category(self):
        active_category = self.category_panel.get_active_category()
        if active_category is None:
            active_category = Items.Category("","")
        self.asset_panel.active_category = active_category
        self.category_panel.show_active_sub_categories()

    def generate_thumbnails(self):
        houdini_nodes.generate_missing_thumbnails(self.asset_manager.assets)
        self.asset_panel.update_icons()

    def init_asset_manager(self):
        self.asset_manager = Items.AssetManager()

        if not utility.path_exists(self.asset_browser_root_path):
            return

        # loop through category directories
        for category_dir_path in utility.get_sub_dirs(self.asset_browser_root_path):
            category_name = utility.get_basename(category_dir_path).lower()
            category = Items.Category(category_dir_path, category_name)
            sub_categories_map = {}

            # loop through asset directories
            for asset_dir_path in utility.get_sub_dirs(category_dir_path):
                thumbnail = utility.get_dir(__file__) + "/icons/default.jpg"
                meshes = utility.get_dir_contents(asset_dir_path, ".fbx")
                textures = utility.get_dir_contents(asset_dir_path, [".jpg", ".png"])
                config = utility.get_dir_contents(asset_dir_path, ".json")

                if not meshes and not textures:
                    continue

                mesh = meshes[0] if meshes else "default"

                for texture in textures:
                    if "thumbnail" in texture.lower():
                        thumbnail = texture
                        break

                tags = [category_name]

                if config:
                    name = utility.get_value_from_json(config[0], "name")
                    config_categories = utility.get_value_from_json(config[0], "categories")
                    if config_categories is not None:
                        tags.extend(config_categories)
                else:
                    name = utility.get_basename(asset_dir_path)

                tags = list(set(tags))
                asset = Items.Asset(asset_dir_path,name, mesh, textures, thumbnail, tags)
                category.add_asset(asset)
                self.asset_manager.add_asset(asset)

                for tag in tags:
                    tag = tag.lower()
                    if tag not in sub_categories_map:
                        sub_categories_map[tag] = Items.Category("", tag, category)
                    sub_categories_map[tag].add_asset(asset)

            for sub_category in sub_categories_map.values():
                category.add_sub_category(sub_category)

            self.asset_manager.add_category(category)