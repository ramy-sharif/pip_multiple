import pafy
import sys
import vlc
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *


class SideGrip(QWidget):
    def __init__(self, parent, edge):
        QWidget.__init__(self, parent)
        if edge == Qt.LeftEdge:
            self.setCursor(Qt.SizeHorCursor)
            self.resizeFunc = self.resizeLeft
        elif edge == Qt.TopEdge:
            self.setCursor(Qt.SizeVerCursor)
            self.resizeFunc = self.resizeTop
        elif edge == Qt.RightEdge:
            self.setCursor(Qt.SizeHorCursor)
            self.resizeFunc = self.resizeRight
        else:
            self.setCursor(Qt.SizeVerCursor)
            self.resizeFunc = self.resizeBottom
        self.mousePos = None

    def resizeLeft(self, delta):
        window = self.window()
        width = max(window.minimumWidth(), window.width() - delta.x())
        geo = window.geometry()
        geo.setLeft(geo.right() - width)
        window.setGeometry(geo)

    def resizeTop(self, delta):
        window = self.window()
        height = max(window.minimumHeight(), window.height() - delta.y())
        geo = window.geometry()
        geo.setTop(geo.bottom() - height)
        window.setGeometry(geo)

    def resizeRight(self, delta):
        window = self.window()
        width = max(window.minimumWidth(), window.width() + delta.x())
        window.resize(width, window.height())

    def resizeBottom(self, delta):
        window = self.window()
        height = max(window.minimumHeight(), window.height() + delta.y())
        window.resize(window.width(), height)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mousePos = event.pos()

    def mouseMoveEvent(self, event):
        if self.mousePos is not None:
            delta = event.pos() - self.mousePos
            self.resizeFunc(delta)

    def mouseReleaseEvent(self, event):
        self.mousePos = None

class MainWindow(QMainWindow):
    _gripSize = 1

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs, )
        self.center()
        self.oldPos = self.pos()
        self.mute = False

        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlags(flags)
        self.sideGrips = [
            SideGrip(self, Qt.LeftEdge),
            SideGrip(self, Qt.TopEdge),
            SideGrip(self, Qt.RightEdge),
            SideGrip(self, Qt.BottomEdge),
        ]

        # corner grips should be "on top" of everything, otherwise the side grips
        # will take precedence on mouse events, so we are adding them *after*;
        # alternatively, widget.raise_() can be used
        self.cornerGrips = [QSizeGrip(self) for i in range(4)]
        self.sizeHint = lambda: QSize(720, 480)
        self.move(100, 10)

        self.videoFrame = QFrame()
        self.videoFrame.installEventFilter(self)
        self.setCentralWidget(self.videoFrame)

        self.vlcInstance = vlc.Instance(
            ['--video-on-top', '--input-repeat=9999'])
        self.videoPlayer = self.vlcInstance.media_player_new()
        url, ok = QInputDialog.getText(
            self, 'Text Input Dialog', 'Enter video link:')
        if not ok:
            self.close()
        self.videoPlayer.video_set_mouse_input(False)
        self.videoPlayer.video_set_key_input(False)

        # creating pafy object of the video
        video = pafy.new(url)

        # getting best stream
        best = video.getbest()

        playurl = best.url

        media = self.vlcInstance.media_new(playurl)
        media.get_mrl()
        self.videoPlayer.set_media(media)

        self.resize(640, 480)
        if sys.platform.startswith('linux'):  # for Linux using the X Server
            self.videoPlayer.set_xwindow(self.videoFrame.winId())
        elif sys.platform == "win32":  # for Windows
            self.videoPlayer.set_hwnd(int(self.videoFrame.winId()))
        elif sys.platform == "darwin":  # for MacOS
            self.videoPlayer.set_nsobject(int(self.videoFrame.winId()))
        # self.vlcInstance.vlm_set_loop(media, True)
        self.videoPlayer.play()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # def eventFilter(self, watched, event):
    #     print(event)
    #     if event.type() == QtCore.QEvent.MouseButtonPress:
    #         self.mousePressEvent(event)
    #     if event.type() == QtCore.QEvent.MouseButtonRelease:
    #         self.mouseReleaseEvent(event)
    #     if event.type() == QtCore.QEvent.MouseMove:
    #         self.mouseMoveEvent(event)
    #     return super(MainWindow, self).eventFilter(watched, event)

    # def initUI(self):
    #     self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    #     self.setAttribute(Qt.WA_TranslucentBackground)
    #     self.adjustSize()
    #     self.setGeometry(
    #         QStyle.alignedRect(
    #             Qt.LeftToRight,
    #             Qt.AlignCenter,
    #             self.size(),
    #             QApplication.instance().desktop().availableGeometry()
    #         )
    #     )
    def switch_mute(self):
        self.mute = not self.mute
        self.videoPlayer.audio_set_mute(self.mute)

    def restart(self):
        url, ok = QInputDialog.getText(
            self, 'Text Input Dialog', 'Enter video link:')
        if not ok:
            self.close()
        self.videoPlayer.video_set_mouse_input(False)
        self.videoPlayer.video_set_key_input(False)

        # creating pafy object of the video
        video = pafy.new(url)

        # getting best stream
        best = video.getbest()

        playurl = best.url

        media = self.vlcInstance.media_new(playurl)
        media.get_mrl()
        self.videoPlayer.set_media(media)

        self.resize(640, 480)
        if sys.platform.startswith('linux'):  # for Linux using the X Server
            self.videoPlayer.set_xwindow(self.videoFrame.winId())
        elif sys.platform == "win32":  # for Windows
            self.videoPlayer.set_hwnd(int(self.videoFrame.winId()))
        elif sys.platform == "darwin":  # for MacOS
            self.videoPlayer.set_nsobject(int(self.videoFrame.winId()))
        # self.vlcInstance.vlm_set_loop(media, True)
        self.videoPlayer.play()


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.__press_pos = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.__press_pos = QPoint()

    def mouseMoveEvent(self, event):
        if not self.__press_pos.isNull():
            self.move(self.pos() + (event.pos() - self.__press_pos))

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_M:
            self.switch_mute()
        if event.key() == QtCore.Qt.Key_Escape:
            self.restart()

        event.accept()
    @property
    def gripSize(self):
        return self._gripSize

    def setGripSize(self, size):
        if size == self._gripSize:
            return
        self._gripSize = max(2, size)
        self.updateGrips()

    def updateGrips(self):
        self.setContentsMargins(*[self.gripSize] * 4)

        outRect = self.rect()
        # an "inner" rect used for reference to set the geometries of size grips
        inRect = outRect.adjusted(self.gripSize, self.gripSize,
                                  -self.gripSize, -self.gripSize)

        # top left
        self.cornerGrips[0].setGeometry(
            QRect(outRect.topLeft(), inRect.topLeft()))
        # top right
        self.cornerGrips[1].setGeometry(
            QRect(outRect.topRight(), inRect.topRight()).normalized())
        # bottom right
        self.cornerGrips[2].setGeometry(
            QRect(inRect.bottomRight(), outRect.bottomRight()))
        # bottom left
        self.cornerGrips[3].setGeometry(
            QRect(outRect.bottomLeft(), inRect.bottomLeft()).normalized())

        # left edge
        self.sideGrips[0].setGeometry(
            0, inRect.top(), self.gripSize, inRect.height())
        # top edge
        self.sideGrips[1].setGeometry(
            inRect.left(), 0, inRect.width(), self.gripSize)
        # right edge
        self.sideGrips[2].setGeometry(
            inRect.left() + inRect.width(),
            inRect.top(), self.gripSize, inRect.height())
        # bottom edge
        self.sideGrips[3].setGeometry(
            self.gripSize, inRect.top() + inRect.height(),
            inRect.width(), self.gripSize)

    def resizeEvent(self, event):
        QMainWindow.resizeEvent(self, event)
        self.updateGrips()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("VLC Test")

    self = MainWindow()
    app.exec_()
