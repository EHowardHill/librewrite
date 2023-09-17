import sys
import os
from PyQt6.QtCore import Qt, QTime
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QStackedWidget,
    QTextEdit,
    QScrollArea,
    QWidget,
    QLineEdit,
    QMessageBox,
)
from PyQt6.QtGui import QTextCharFormat, QTextDocument, QFontDatabase, QFont

def resolve_name(fn):
    return "stories/" + fn.replace(" ", "_") + ".htm"

def define_name(fn):
    return fn.replace("_", " ").replace(".htm", "")

class TextEditHandler(QWidget):
    new_window = None

    def __init__(self, main_window):
        self.file_name = ""

        self.text_edit = QTextEdit()
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.text_edit.setFocus()

        self.main_window = main_window

        self.bold_button = QPushButton("B")
        self.bold_button.setFixedWidth(50)
        self.bold_button.setFlat(True)
        self.bold_button.setStyleSheet("QPushButton { font-weight: bold; }")
        self.bold_button.clicked.connect(self.toggle_bold)

        self.italic_button = QPushButton("I")
        self.italic_button.setFixedWidth(50)
        self.italic_button.setFlat(True)
        self.italic_button.setStyleSheet("QPushButton { font-style: italic; }")
        self.italic_button.clicked.connect(self.toggle_italic)

        self.save_button = QPushButton(self.file_name)
        self.save_button.clicked.connect(self.save_text)

        self.back_button = QPushButton("Back")
        self.back_button.setFlat(True)
        self.back_button.clicked.connect(self.go_back)

        self.word_count_amount = 0
        self.word_count = QLabel()

        self.text_edit.textChanged.connect(self.text_changed)

        self.load_text()

    def go_back(self):
        self.save_text()
        self.new_window.refresh()
        main_window.setCurrentIndex(0)

    def toggle_bold(self):
        cursor = self.text_edit.textCursor()
        format = cursor.charFormat()
        font = format.font()

        font.setBold(not font.bold())
        format.setFont(font)

        cursor.mergeCharFormat(format)
        self.text_edit.setTextCursor(cursor)

    def toggle_italic(self):
        cursor = self.text_edit.textCursor()
        italic = cursor.charFormat().fontItalic()

        format = QTextCharFormat()
        format.setFontItalic(not italic)
        cursor.mergeCharFormat(format)
        self.text_edit.setTextCursor(cursor)

    def save_text(self):
        text = self.text_edit.toHtml()
        if text:
            document = QTextDocument()
            document.setHtml(text)
            htm = document.toHtml()

            with open(resolve_name(self.file_name), "w") as file:
                file.write(htm)
            self.save_button.setText(self.file_name)

    def load_text(self):
        try:
            with open(resolve_name(self.file_name), "r") as file:
                html_content = file.read()
                self.text_edit.setHtml(html_content)
        except FileNotFoundError:
            pass

    def text_changed(self):
        self.word_count_amount = len(self.text_edit.toPlainText().split(" "))

        self.save_button.setText(self.file_name + " *")
        self.word_count.setText(" " + str(self.word_count_amount))

class MenuSelect(QWidget):
    def __init__(self, edit_window):
        super().__init__()
        self.initUI()
        self.edit_window = edit_window

    def refresh(self):
        self.sync_btn.setText("Sync to USB *")
        self.update_time_label()
        self.update_battery_label()

        for i in reversed(range(self.file_layout.count())):
            widget = self.file_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.file_list = os.listdir("stories")
        self.file_layout.addStretch()
        for filename in self.file_list:
            if filename.endswith(".htm"):
                file_button = QPushButton(define_name(filename), self)
                file_button.clicked.connect(
                    lambda _, name=filename: self.switch_to_textedit(name)
                )
                self.file_layout.addWidget(file_button)

    def update_time_label(self):
        current_time = QTime.currentTime().toString("h:mm AP")
        self.time_lbl.setText(current_time)

    def update_battery_label(self):

        try:
            # Read the battery status from /sys/class/power_supply
            with open('/sys/class/power_supply/BAT0/capacity', 'r') as file:
                percentage = file.read().strip()
                self.battery_lbl.setText("Battery: " + str(percentage) + "%")
        except FileNotFoundError:
            self.battery_lbl.setText("No Battery")

    def save_to_drive(self):

        uid = os.getuid()
        gid = os.getgid()

        try:
            os.system(f"sudo mount -o uid={uid},gid={gid} /dev/sdb1 /mnt")
            os.system("mkdir -p /mnt/stories")
            os.system("cp -r ./stories/* /mnt/stories")
            os.system("cp -r /mnt/stories/* ./stories")
            os.system("sudo umount /mnt")
            self.sync_btn.setText("Sync to USB")
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText(str(e))
            msg.setWindowTitle("Error Alert")
            msg.exec()

    def initUI(self):
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)

        self.file_layout = QVBoxLayout()
        scroll_widget.setLayout(self.file_layout)

        self.new_element = QWidget()
        self.new_layout = QHBoxLayout(self.new_element)

        self.text_input = QLineEdit(self)
        self.new_layout.addWidget(self.text_input)

        self.button = QPushButton("New", self)
        self.button.clicked.connect(self.new_file)
        self.new_layout.addWidget(self.button)

        main_hv = QHBoxLayout(self)
        main_widget = QWidget(self)
        main_widget.setFixedWidth(480)

        extra_vb = QVBoxLayout(self)
        self.sync_btn = QPushButton(self)
        self.sync_btn.setText("Sync to USB *")

        font = QFont()
        font.setPointSize(46)

        self.time_lbl = QLabel("5:03 PM")
        self.time_lbl.setFont(font)
        self.time_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.battery_lbl = QLabel("53% Battery")
        self.battery_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)

        extra_vb.addWidget(self.sync_btn)
        extra_vb.addStretch()
        extra_vb.addWidget(self.battery_lbl)
        extra_vb.addWidget(self.time_lbl)

        extra_widget = QWidget()
        extra_widget.setLayout(extra_vb)

        main_hv.addWidget(main_widget)
        main_hv.addStretch()
        main_hv.addWidget(extra_widget)

        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(self.new_element)
        main_layout.addWidget(scroll_area)

        self.layout = main_hv
        self.refresh()

    def new_file(self):
        self.edit_window.file_name = define_name(self.text_input.text())
        self.edit_window.save_button.setText(define_name(self.text_input.text()))
        self.edit_window.load_text()
        main_window.setCurrentIndex(1)

    def switch_to_textedit(self, name):
        self.edit_window.file_name = define_name(name)
        self.edit_window.save_button.setText(define_name(name))
        self.edit_window.load_text()
        main_window.setCurrentIndex(1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    dark_stylesheet = """
        QStackedWidget {
            background-color: black;
            background-repeat: no-repeat;
            background-position: center;
            color: white;
        }
        QWidget {
            background-color: black;
            color: white;
        }
        QPushButton {
            background-color: black;
            color: white;
            border: 1px solid white;
            border-radius: 4px;
            padding: 10px;
        }
        QPushButton:hover {
            background-color: #303030;
        }
        QTextEdit {
            background-color: black;
            color: white;
            margin: 12px;
        }
        QLabel {
            color: white;
        }
        QLineEdit {
            border: 1px solid rgb(50, 104, 168);
            border-radius: 4px;
            padding: 10px;
        }
    """

    font_garamond = QFontDatabase.addApplicationFont("Sanchez-Regular.ttf")
    fontstr = QFontDatabase.applicationFontFamilies(font_garamond)[0]
    font = QFont(fontstr, 14)
    app.setFont(font)
    app.setStyleSheet(dark_stylesheet)

    main_window = QStackedWidget()

    text_edit_handler = TextEditHandler(main_window)
    window1 = MenuSelect(text_edit_handler)
    text_edit_handler.new_window = window1

    scroll_area = QScrollArea()
    scroll_area.setWidget(text_edit_handler.text_edit)
    scroll_area.setWidgetResizable(True)

    button_bar = QWidget()
    button_layout = QHBoxLayout(button_bar)
    button_layout.addWidget(text_edit_handler.bold_button)
    button_layout.addWidget(text_edit_handler.italic_button)
    button_layout.addWidget(text_edit_handler.word_count)
    button_layout.addStretch()
    button_layout.addWidget(text_edit_handler.save_button)
    button_layout.addWidget(text_edit_handler.back_button)

    layout = QVBoxLayout()
    layout.addWidget(scroll_area)
    layout.addWidget(button_bar)

    central_widget = QWidget()
    central_widget.setLayout(layout)

    main_window.addWidget(window1)
    main_window.addWidget(central_widget)

    main_window.setWindowTitle("Gnimble")
    screen = app.primaryScreen().geometry()
    main_window.setGeometry(screen)
    main_window.show()

    sys.exit(app.exec())
