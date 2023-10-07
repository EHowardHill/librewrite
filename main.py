import sys
import os
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
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
from PyQt5.QtGui import QTextCharFormat, QTextDocument, QFontDatabase, QFont


def resolve_name(fn):
    return "stories/" + fn.replace(" ", "_") + ".md"


def define_name(fn):
    return fn.replace("_", " ").replace(".md", "")


class WindowMenu(QWidget):
    load_file = pyqtSignal(str)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def refresh(self):
        self.text_input.setText("")
        for i in reversed(range(self.file_layout.count())):
            widget = self.file_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.file_layout.addStretch()
        self.file_list = os.listdir("stories")
        for filename in self.file_list:
            if filename.endswith(".md"):
                file_button = QPushButton(define_name(filename), self)
                file_button.clicked.connect(
                    lambda _, name=filename: self.switch_to_textedit(name)
                )
                self.file_layout.addWidget(file_button)

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
        self.button.clicked.connect(self.switch_to_new_file)
        self.new_layout.addWidget(self.button)

        main_hv = QHBoxLayout(self)
        main_widget = QWidget(self)
        main_widget.setFixedWidth(480)

        main_hv.addWidget(main_widget)
        main_hv.addStretch()

        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(self.new_element)
        main_layout.addWidget(scroll_area)

        self.layout = main_hv
        self.refresh()

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

    def switch_to_new_file(self):
        self.load_file.emit(self.text_input.text())
        self.main_window.setCurrentIndex(1)

    def switch_to_textedit(self, name):
        self.load_file.emit(name)
        self.main_window.setCurrentIndex(1)


class WindowText(QWidget):
    refresh = pyqtSignal()

    def __init__(self, main_window):
        super().__init__()
        self.initUI()
        self.main_window = main_window

    def initUI(self):
        self.file_name = ""

        self.text_edit = QTextEdit()
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.text_edit.setFocus()

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

        button_bar = QWidget()
        button_layout = QHBoxLayout(button_bar)
        button_layout.addWidget(self.bold_button)
        button_layout.addWidget(self.italic_button)
        button_layout.addStretch()
        button_layout.addWidget(self.word_count)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.back_button)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(button_bar)

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.text_edit)
        scroll_area.setWidgetResizable(True)

        self.setLayout(layout)
        self.load_text()

    def go_back(self):
        self.save_text()
        self.refresh.emit()
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
        text = self.text_edit.toMarkdown()
        if text:
            document = QTextDocument()
            document.setMarkdown(text)
            htm = document.toMarkdown()

            with open(resolve_name(self.file_name), "w") as file:
                file.write(htm.strip())
            self.save_button.setText(self.file_name)

    def load_text(self):
        try:
            with open(resolve_name(self.file_name), "r") as file:
                html_content = file.read()
                self.text_edit.setMarkdown(html_content)
        except FileNotFoundError:
            self.text_edit.setMarkdown("")

    def text_changed(self):
        self.word_count_amount = len(self.text_edit.toPlainText().split(" "))

        self.save_button.setText(self.file_name + " *")
        self.word_count.setText(" " + str(self.word_count_amount))

    def load_file(self, name):
        self.file_name = define_name(name)
        self.load_text()
        self.save_button.setText(self.file_name)

class MainWindow(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        window_menu = WindowMenu(self)
        self.addWidget(window_menu)

        window_text = WindowText(self)
        self.addWidget(window_text)

        self.setWindowTitle("Gnimble")
        self.setGeometry(app.primaryScreen().geometry())

        window_menu.load_file.connect(window_text.load_file)
        window_text.refresh.connect(window_menu.refresh)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    font_garamond = QFontDatabase.addApplicationFont("LibreBaskerville-Regular.ttf")
    fontstr = QFontDatabase.applicationFontFamilies(font_garamond)[0]
    font = QFont(fontstr, 14)
    app.setFont(font)

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
    app.setStyleSheet(dark_stylesheet)

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())
