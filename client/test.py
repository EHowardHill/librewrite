import sys
import pywifi
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QDialog,
    QVBoxLayout,
    QListWidget,
    QMessageBox,
)


def get_wifi_ssids():
    wifi = pywifi.PyWiFi()
    ssids = []
    iface = wifi.interfaces()[0]
    iface.scan()
    scan_results = iface.scan_results()
    ssids = list(
        sorted(set([result.ssid for result in scan_results if result.ssid != ""]))
    )
    return ssids


class PopupWindow(QDialog):
    def __init__(self, items):
        super().__init__()
        self.setWindowTitle("Select a Wi-Fi Network")
        self.layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.addItems(items)
        self.list_widget.itemClicked.connect(self.show_message_box)
        self.layout.addWidget(self.list_widget)
        self.setLayout(self.layout)

    def show_message_box(self, item):
        selected_item_text = item.text()
        QMessageBox.information(
            self, "Selected Item", f"You selected: {selected_item_text}"
        )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.setGeometry(100, 100, 400, 200)

        self.button = QPushButton("Open Popup")
        self.button.clicked.connect(self.open_popup)
        self.setCentralWidget(self.button)

    def open_popup(self):
        items = get_wifi_ssids()
        popup = PopupWindow(items)
        popup.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
