import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    visible: true
    width: 800
    height: 600
    title: "Gnimble"

    MenuSelect {
        id: menuSelect
    }

    TextEditHandler {
        id: textEditHandler
        anchors.fill: parent
        visible: false
    }
}
