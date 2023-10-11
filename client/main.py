import sys
import pywifi
from PyQt5.QtCore import Qt, pyqtSignal, QThread
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
from PyQt5.QtGui import QTextCharFormat, QTextDocument, QFontDatabase, QFont, QPixmap
from requests import post, get, ConnectionError
from os import system, listdir, getuid, getgid, path, popen
from json import dumps
from datetime import datetime

date_format = "%Y-%m-%d %H:%M:%S"


def get_wifi_ssids():
    wifi = pywifi.PyWiFi()
    ssids = []
    iface = wifi.interfaces()[1]
    iface.scan()
    scan_results = iface.scan_results()
    ssids = list(
        sorted(set([result.ssid for result in scan_results if result.ssid != ""]))
    )
    return ssids


def resolve_name(fn):
    return "stories/" + fn.replace(" ", "_") + ".md"


def define_name(fn):
    return fn.replace("_", " ").replace(".md", "")


class RetrieveID(QThread):
    finished = pyqtSignal(str)

    def run(self):
        # https://gnimble.live
        try:
            mac = popen(
                "ip link show | awk '/ether/ {print $2}' | tail -n 1"
            ).readline()
            response = post(
                "https://gnimble.live",
                data={"method": "retrieve_id", "mac_address": mac},
            )
            data = response.json()
            self.finished.emit(data["code"])
        except Exception as e:
            print(str(e))
            self.finished.emit("connect to the internet\nto sync documents")


class WindowSettings(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def switch_to_textedit(self, name):
        self.addPassword(name)

    def refresh(self):
        for i in reversed(range(self.file_layout.count())):
            widget = self.file_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.file_layout.addStretch()
        self.file_list = get_wifi_ssids()
        print(self.file_list)
        for filename in self.file_list:
            file_button = QPushButton(define_name(filename), self)
            file_button.clicked.connect(
                lambda _, name=filename: self.switch_to_textedit(name)
            )
            self.file_layout.addWidget(file_button)

    def connect(self):
        try:
            system(
                f'nmcli device wifi connect "{self.pw_label.text()}" password "{self.pw_text.text()}"'
            )

            self.main_window.setCurrentIndex(0)
            for i in reversed(range(self.file_layout.count())):
                widget = self.file_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
        except Exception as e:
            print(str(e))

    def addPassword(self, name):
        try:
            status = system(f'nmcli device wifi connect "{name}"')
            if "No network" not in status:
                self.main_window.setCurrentIndex(0)
        except Exception as e:
            print(str(e))
        for i in reversed(range(self.pw_layout.count())):
            widget = self.pw_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.pw_layout.addStretch()
        self.pw_label = QLabel(name)
        self.pw_label.setStyleSheet("QLabel { font-size: 48pt; padding: 10px; }")
        self.pw_layout.addWidget(self.pw_label)
        self.pw_text = QLineEdit()
        self.pw_layout.addWidget(self.pw_text)
        self.pw_select = QPushButton("Connect")
        self.pw_select.clicked.connect(self.connect)
        self.pw_layout.addWidget(self.pw_select)
        self.pw_layout.addStretch()

    def initUI(self):
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)

        self.file_layout = QVBoxLayout()
        scroll_widget.setLayout(self.file_layout)

        main_hv = QHBoxLayout(self)
        self.main_widget = QWidget(self)
        self.main_widget.setFixedWidth(480)

        self.pw_layout = QVBoxLayout()

        main_hv.addWidget(self.main_widget)
        main_hv.addStretch()
        main_hv.addLayout(self.pw_layout)
        main_hv.addStretch()

        main_layout = QVBoxLayout(self.main_widget)
        main_layout.addWidget(scroll_area)

        self.layout = main_hv

        for i in reversed(range(self.file_layout.count())):
            widget = self.file_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.file_layout.addStretch()
        self.file_list = get_wifi_ssids()
        print(self.file_list)
        for filename in self.file_list:
            file_button = QPushButton(define_name(filename), self)
            file_button.clicked.connect(
                lambda _, name=filename: self.switch_to_textedit(name)
            )
            self.file_layout.addWidget(file_button)


class WindowMenu(QWidget):
    load_file = pyqtSignal(str)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def retrieve_id(self):
        self.worker_thread = RetrieveID()
        self.worker_thread.finished.connect(self.update_label)
        self.worker_thread.start()

    def update_label(self, text):
        self.label_id.setText(text)

    def refresh(self):
        self.text_input.setText("")
        for i in reversed(range(self.file_layout.count())):
            widget = self.file_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.file_layout.addStretch()
        self.file_list = listdir("stories")
        for filename in self.file_list:
            if filename.endswith(".md"):
                file_button = QPushButton(define_name(filename), self)
                file_button.clicked.connect(
                    lambda _, name=filename: self.switch_to_textedit(name)
                )
                self.file_layout.addWidget(file_button)

    def is_connected(self):
        try:
            response = get("http://www.google.com", timeout=5)
            return response.status_code == 200
        except ConnectionError:
            return False

    def sync(self):
        if self.is_connected:
            code = self.label_id.text()
            response = {"method": "sync", "code": code}
            stories = {}
            for f in listdir("stories/"):
                url = "stories/" + f
                contents = ""
                with open(url, "r") as r:
                    contents = r.read()
                dt = str(path.getmtime(url))
                print(dt)
                stories[f] = {
                    "datetime": dt,
                    "contents": contents.replace("\n\n","\n"),
                }
            response["stories"] = dumps(stories)
            new = post("https://gnimble.live", data=response).json()
            for f in new["stories"]:
                if f in stories:
                    if new["stories"][f]["datetime"] > stories[f]["datetime"]:
                        with open("stories/" + f, "w") as w:
                            print(" >>> ")
                            print(new["stories"][f]["contents"])
                            w.write(new["stories"][f]["contents"])
                else:
                    with open("stories/" + f, "w") as w:
                        print(" >>> ")
                        print(new["stories"][f]["contents"])
                        w.write(new["stories"][f]["contents"])
            self.btn_sync.setText("Sync to Gnimble.live")
            self.refresh()
        else:
            self.main_window.setCurrentIndex(2)

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

        self.extra_layout = QVBoxLayout()
        self.label_id = QLabel("")
        self.label_id.setStyleSheet("QLabel { font-size: 48pt; padding: 10px; }")
        self.btn_sync = QPushButton("Sync to Gnimble.live *")
        self.btn_sync.setFixedWidth(256)
        self.btn_sync.clicked.connect(self.sync)

        self.extra_layout.addWidget(self.label_id)
        self.extra_layout.addWidget(self.btn_sync)
        self.extra_layout.addStretch()

        main_hv = QHBoxLayout(self)
        self.main_widget = QWidget(self)
        self.main_widget.setFixedWidth(480)

        main_hv.addLayout(self.extra_layout)
        main_hv.addStretch()
        main_hv.addWidget(self.main_widget)

        main_layout = QVBoxLayout(self.main_widget)
        main_layout.addWidget(self.new_element)
        main_layout.addWidget(scroll_area)

        self.layout = main_hv
        self.refresh()
        self.retrieve_id()

    def save_to_drive(self):
        uid = getuid()
        gid = getgid()

        try:
            system(f"sudo mount -o uid={uid},gid={gid} /dev/sdb1 /mnt")
            system("mkdir -p /mnt/stories")
            system("cp -r ./stories/* /mnt/stories")
            system("cp -r /mnt/stories/* ./stories")
            system("sudo umount /mnt")
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
                self.text_edit.setMarkdown(file.read().replace("\n", "\n\n").replace("<br>", "\n\n\n\n"))
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

        window_settings = WindowSettings(self)
        self.addWidget(window_settings)

        self.setWindowTitle("Gnimble")
        self.setGeometry(app.primaryScreen().geometry())

        window_menu.load_file.connect(window_text.load_file)
        window_text.refresh.connect(window_menu.refresh)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    font_garamond = QFontDatabase.addApplicationFont("./YoungSerif-Regular.ttf")
    fontstr = QFontDatabase.applicationFontFamilies(font_garamond)[0]
    font = QFont(fontstr, 14)
    app.setFont(font)

    dark_stylesheet = """
        QStackedWidget {
            background-image: url('patterns/leaves.jpg');
            background-position: center;
            color: white;
        }
        QScrollArea {
            background-color: black;
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
