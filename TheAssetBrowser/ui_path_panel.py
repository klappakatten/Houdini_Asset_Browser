from PySide2.QtWidgets import *
from PySide2.QtCore import *

from . import utility

class PathPanel(QWidget):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.file_path_line_edit = QLineEdit()
        self.json_root = utility.get_json_path()
        self.file_select_button = QPushButton("File")
        self.generate_thumbnail_button = QPushButton("Generate Missing Thumbnails")

        self.init_ui()

        self.connect_signals()

    def init_ui(self):
        main_layout = QVBoxLayout()

        tab_widget = QTabWidget()

        file_path_label = QLabel("Asset Folder Path")
        file_path_label.setBuddy(self.file_path_line_edit)
        file_path_layout = QHBoxLayout()
        file_path_layout.addWidget(file_path_label)
        file_path_layout.addWidget(self.file_path_line_edit)
        file_path_layout.addWidget(self.file_select_button)

        generate_thumbnails_layout = QVBoxLayout()
        generate_thumbnails_layout.addWidget(self.generate_thumbnail_button)

        self.file_path_line_edit.setText(self.path)
        self.file_path_line_edit.setPlaceholderText("Enter path here...")
        self.file_path_line_edit.setReadOnly(True)
        self.file_path_line_edit.setFocusPolicy(Qt.NoFocus)


        settings_layout = QVBoxLayout()
        settings_layout.addLayout(file_path_layout)
        settings_layout.setAlignment(Qt.AlignTop)

        settings_tab = QWidget()
        settings_tab.setLayout(settings_layout)

        thumbnail_tab = QWidget()
        thumbnail_tab.setLayout(generate_thumbnails_layout)

        tab_widget.addTab(settings_tab, "Settings")
        tab_widget.addTab(thumbnail_tab, "Generate Thumbnails")

        main_layout.addWidget(tab_widget)

        self.setLayout(main_layout)

    def connect_signals(self):
        self.file_select_button.pressed.connect(self.file_button_clicked)

    def file_button_clicked(self):
        path = QFileDialog.getExistingDirectory()
        if path:
            self.file_path_line_edit.setText(path)
        else:
            self.file_path_line_edit.setText("")

