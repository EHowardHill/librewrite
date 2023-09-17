import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QTextEdit,
    QScrollArea,
    QWidget,
)
from PyQt5.QtGui import QTextCharFormat, QTextDocument, QFontDatabase, QFont


def resolve_name(fn):
    return "stories/" + fn.replace(" ", "_") + ".htm"


class TextEditHandler:
    def __init__(self, main_window):
        self.file_name = "My Story"

        self.text_edit = QTextEdit()
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
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

        self.word_count_amount = 0
        self.word_count = QLabel()

        self.text_edit.textChanged.connect(
            self.text_changed
        )  # Connect textChanged signal

        # Load content from "saved_text.htm" when the program starts
        self.load_text()

    def toggle_bold(self):
        cursor = self.text_edit.textCursor()
        format = cursor.charFormat()
        font = format.font()

        # Toggle bold formatting for the current selection
        font.setBold(not font.bold())
        format.setFont(font)

        # Merge the modified format with the current cursor position
        cursor.mergeCharFormat(format)
        self.text_edit.setTextCursor(cursor)

    def toggle_italic(self):
        cursor = self.text_edit.textCursor()
        italic = cursor.charFormat().fontItalic()

        # Toggle italic formatting for the current selection
        format = QTextCharFormat()
        format.setFontItalic(not italic)
        cursor.mergeCharFormat(format)
        self.text_edit.setTextCursor(cursor)

    def save_text(self):
        text = self.text_edit.toHtml()
        if text:
            # Create a QTextDocument to save as RTF
            document = QTextDocument()
            document.setHtml(text)
            htm = document.toHtml()  # Convert to RTF format

            with open(resolve_name(self.file_name), "w") as file:
                file.write(htm)
            self.save_button.setText("My Story")

    def load_text(self):
        try:
            with open(resolve_name(self.file_name), "r") as file:
                html_content = file.read()
                self.text_edit.setHtml(html_content)
        except FileNotFoundError:
            # Handle the case where the file is not found
            pass

    def text_changed(self):
        self.word_count_amount = len(self.text_edit.toPlainText().split(" "))

        # Update the modified state when the text changes
        self.save_button.setText(self.file_name + " *")
        self.word_count.setText(" " + str(self.word_count_amount))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Use the Fusion style

    # Dark mode stylesheet
    dark_stylesheet = """
        QMainWindow {
            background-color: black;
            background-image: url("patterns/main.jpeg");
            background-repeat: no-repeat;
            background-position: center;
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
    """

    font_garamond = QFontDatabase.addApplicationFont("Sanchez-Regular.ttf")
    fontstr = QFontDatabase.applicationFontFamilies(font_garamond)[0]
    font = QFont(fontstr, 14)
    app.setFont(font)
    app.setStyleSheet(dark_stylesheet)

    window = QMainWindow()
    window.setWindowTitle("Gnimble")
    window.setGeometry(100, 100, 640, 480)

    text_edit_handler = TextEditHandler(window)

    scroll_area = QScrollArea()
    scroll_area.setWidget(text_edit_handler.text_edit)
    scroll_area.setWidgetResizable(True)

    # Button bar
    button_bar = QWidget()
    button_layout = QHBoxLayout(button_bar)
    button_layout.addWidget(text_edit_handler.bold_button)
    button_layout.addWidget(text_edit_handler.italic_button)
    button_layout.addWidget(text_edit_handler.word_count)
    button_layout.addStretch()
    button_layout.addWidget(text_edit_handler.save_button)  # Add the Save button

    layout = QVBoxLayout()
    layout.addWidget(scroll_area)
    layout.addWidget(button_bar)

    central_widget = QWidget()
    central_widget.setLayout(layout)
    window.setCentralWidget(central_widget)
    window.show()
    sys.exit(app.exec_())
