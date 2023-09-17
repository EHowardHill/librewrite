import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    visible: true
    width: 800
    height: 600
    title: "Scrollable Rich Text Window"

    Column {
        Button {
            text: "Bold"
            // Add your bold functionality here
        }

        Button {
            text: "Italic"
            // Add your italic functionality here
        }

        Flickable {
            width: parent.width
            height: parent.height - 100 // Adjust the height as needed
            contentHeight: textEdit.contentHeight // Set contentHeight to textEdit's contentHeight
            clip: true

            TextArea {
                id: textEdit
                wrapMode: TextEdit.Wrap
                focus: true
                selectByMouse: true // Enable text selection with the mouse
                width: parent.width // Set the width to the parent's width

                onTextChanged: {
                    // Add any necessary text handling logic here
                }
            }
        }
    }
}
