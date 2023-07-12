import sys

from tools.debug import DebugWindow, Qt


def test_debug_window():
    app = Qt.QApplication(sys.argv)
    window = DebugWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    test_debug_window()
