import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    visible: true
    width: 480
    height: 320
    title: "Menu Select"

    ListView {
        id: fileListView
        anchors.fill: parent
        model: fileModel
        delegate: Item {
            width: parent.width
            height: 50

            Button {
                text: model.display
                onClicked: {
                    edit_window.file_name = model.name
                    edit_window.save_button.text = model.name
                    edit_window.loadText()
                    main_window.currentIndex = 1
                }
            }
        }
    }

    TextField {
        id: textInput
        placeholderText: "Enter a new file name"
        Layout.fillWidth: true
    }

    Button {
        text: "New"
        onClicked: {
            edit_window.file_name = textInput.text
            edit_window.save_button.text = textInput.text
            edit_window.loadText()
            main_window.currentIndex = 1
        }
    }

    ListModel {
        id: fileModel
    }
}
