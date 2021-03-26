""" GUI modules """
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from PyQt5.QtGui import QBrush, QImage, QPalette
from PyQt5.QtCore import QSize
from PyQt5 import QtCore, QtGui, QtWidgets, uic

""" Scrapping """
import requests

""" Useful modules """
import os
import sys
import re

#sys.stderr = open('error_log.txt', 'a') # set stderr custom output file


""" Class for user interface """
class MainWindow(QtWidgets.QMainWindow):
    resized = QtCore.pyqtSignal()

    def __init__(self):

        super(MainWindow, self).__init__()

        # Current path variable
        self.currentPath = os.getcwd().replace('\\', '/')
        uic.loadUi(self.currentPath + '/AnimeBrowser.ui', self)

        self.resized.connect(self.resizeWindowAction)

        # Useless for the current code
        """
        if True:
            import threading
            event = threading.Event()
            event.set()
            thread = threading.Thread(
                target=self.variantBackground, args=(event,))
            thread.start()
        """

    def resizeEvent(self, event):
        self.resized.emit()
        return super(MainWindow, self).resizeEvent(event)


    def resizeWindowAction(self):
        self.set_background(self.width(), self.height())

        # Center items
        from PyQt5.QtWidgets import QDesktopWidget
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


# =======================================================================================================

""" Class with functions to scrape the websites """
class GetAnime(MainWindow):
    def __init__(self):
        super(GetAnime, self).__init__()

        # Backgrounds path
        self.backgrounds_path = self.currentPath + "/AnimeBrowserImages/"

        # Set basic variables needed for search
        self.anime = self.SearchInput.text()
        self.cap = ''
        self.urls = []
        nums = re.findall(r'\d+', self.anime)
        self.checkedOps = set()  # Checked websites to search

        # Check if is there any number to search by episode
        if len(nums) > 0:
            self.cap = nums[len(nums)-1]

        # Choose websites for search anime
        self.animeflvOp.stateChanged.connect(self.animeflvChecked)
        self.animefenixOp.stateChanged.connect(self.animefenixChecked)
        self.tioanimeOp.stateChanged.connect(self.tioanimeChecked)
        self.monoschinosOp.stateChanged.connect(self.monoschinosChecked)

        self.searchButton.clicked.connect(self.set_query)
        self.change_bg.installEventFilter(self)

        # Set background image:
        self.make_background_folder()
        self.image_index = 0
        self.currentBackground = self.backgrounds_path + 'background4.jpg'
        self.set_background()

        # Check if open-in-browser is activated
        self.open_in_browser()


    def make_background_folder(self):
        self.files = os.listdir(self.backgrounds_path)
        # There is an error, rename files even while they are already named, and the order make the program to delete some files in the process
        images = len(self.files)
        for x in range(images):
            c_image = self.backgrounds_path + self.files[x]

            if not self.files[x].startswith('background'):
                os.system('mv {} {}background{}.{}'.format(
                    c_image, self.backgrounds_path, str(x+1), c_image[c_image.rfind('.')+1:]))


    def set_background(self, dx=1126, dy=704):
        oImage = QImage(self.currentBackground)

        # resize Image to widgets size
        sImage = oImage.scaled(QSize(dx, dy))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)


    def animeflvChecked(self):
        if self.animeflvOp.isChecked():
            self.checkedOps.add('https://www3.animeflv.net')
        else:
            self.checkedOps.remove('https://www3.animeflv.net')


    def animefenixChecked(self):
        if self.animefenixOp.isChecked():
            self.checkedOps.add('https://www.animefenix.com')
        else:
            self.checkedOps.remove('https://www.animefenix.com')


    def tioanimeChecked(self):
        if self.tioanimeOp.isChecked():
            self.checkedOps.add('https://tioanime.com')
        else:
            self.checkedOps.remove('https://tioanime.com')


    def monoschinosChecked(self):
        if self.monoschinosOp.isChecked():
            self.checkedOps.add('https://monoschinos2.com')
        else:
            self.checkedOps.remove('https://monoschinos2.com')


    def typeOfSearch(self):
        if len(self.checkedOps) > 0:
            if self.is_episode():
                for p in self.checkedOps:
                    self.search_by_episode(p)
            else:
                for p in self.checkedOps:
                    self.search_anime(p)
                    print(p)
        else:
            msg = QMessageBox()
            msg.setWindowTitle('Platform!')
            msg.setText('Please select the platform(s)')
            msg.setIcon(QMessageBox.Information)

            x = msg.exec_()


    # Open links in browser
    def open_in_browser(self):
        if self.openBrowser.isChecked():
            for p in self.urls:
                os.system('start ' + p)
                print('Open in browser > ' + p)


    def set_query(self):
        print('Debug! ', self.checkedOps)

        def clear_list():
            self.urls.clear()
            self.Results.clear()
            self.cap = ''

        clear_list()

        self.anime = self.SearchInput.text()
        self.anime = re.sub('[^A-Za-z0-9 ]+', ' ', self.anime)
        self.anime = re.sub(' +', ' ', self.anime)
        print(self.anime)

        # Verify input
        if self.anime == '':
            msg = QMessageBox()
            msg.setWindowTitle('Anime')
            msg.setText('Please type your anime!')
            msg.setIcon(QMessageBox.Information)

            x = msg.exec_()

        else:
            self.SearchInput.setText(self.anime.title())

            def set_cap(name):
                nums = re.findall(r'\d+', name)
                if len(nums) > 0 and not name.startswith(''.join(nums)):
                    self.cap = nums[len(nums)-1]

            # Verify if input is a list
            if ',' in self.anime:
                self.anime = self.anime.split(',')
                for a in self.anime:
                    set_cap(a)
                    self.anime = a
                    self.typeOfSearch()
                    self.open_in_browser()
                    clear_list()

            else:
                set_cap(self.anime)
                self.typeOfSearch()
                self.open_in_browser()


    def is_episode(self):
        # Determinar tipo de busqueda (consulta o capitulo)
        if len(self.cap) == 0:
            return False
        else:
            return True


    # If the self.anime is not found it probes some common parameters like tv and hd
    def probe_parameters(self, url, p):
        parameters = ['tv', 'hd', 'latino']

        index = url.find('-' + self.cap)
        found = False
        for i in parameters:

            newQuery = url[:index] + '-' + i + url[index:]
            print('Trying ' + newQuery)

            if requests.get(newQuery).status_code == 404:
                print('Page not found.')
                print('Trying other parameters...')

            else:
                print('Found: ' + newQuery)
                self.Results.addItem(QtWidgets.QListWidgetItem(newQuery))
                self.urls.append(newQuery)
                print('Added to the list.')
                found = True
                return

        if not found:
            print('Anime or anime episode not found')
            msg = QMessageBox()
            msg.setWindowTitle('Not found')
            msg.setText('Anime or anime episode not found! :(')
            msg.setIcon(QMessageBox.Critical)

            x = msg.exec_()


    def search_anime(self, platform):
        # query = urllib.parse.quote(query) Dont work
        query = self.anime.replace(' ', '+')

        if platform == 'https://www3.animeflv.net':
            param = '/browse?q='  # Param for animeflv

        elif platform == 'https://www.animefenix.com':  # Param for animefenix
            param = '/animes?q='

        elif platform == 'https://tioanime.com':  # Param for tioanime
            param = '/directorio?q='

        elif platform == 'https://monoschinos2.com':  # Param for monoschinos
            param = '/search?q='

        url = platform + param + query

        self.Results.addItem(QtWidgets.QListWidgetItem(url))
        self.urls.append(url)
        print('Added to the list.')


    def search_by_episode(self, platform):
        query = self.anime.replace(' ', '-').lower()
        url = platform + '/ver/' + query

        print(requests.get(url).status_code)  # Debug
        if requests.get(url).status_code == 404:
            print('Page not found.')
            print('Trying other parameters...')
            self.probe_parameters(url, platform)

        else:
            self.Results.addItem(QtWidgets.QListWidgetItem(url))
            self.urls.append(url)
            print('Added to the list.')


    # In development
    """ def variantBackground(self, event):
        from time import sleep

        sleepTime = 60
        path = self.currentPath + '/AnimeSearcherImages/'
        backgrounds = os.listdir(path)

        # Constantly change the background
        while True:
            for image in backgrounds:
                self.currentPath = path + image
                self.resizeWindowAction()
                event.wait(sleepTime) """


    def prev_background(self):
        self.image_index -= 1
        if self.image_index <= 0:
            self.image_index = len(self.files) - 1

        self.currentBackground = self.backgrounds_path + \
            self.files[self.image_index]
        self.set_background()


    def next_background(self):
        self.image_index += 1
        if self.image_index >= len(self.files):
            self.image_index = 0

        self.currentBackground = self.backgrounds_path + \
            self.files[self.image_index]
        self.set_background()


    def custom_background(self):
        fname = QFileDialog.getOpenFileName(
            self, 'Open file', self.currentPath, 'Images (*.jpg *.jpeg *.png *.gif *.jfif *.bmp)')

        if os.path.isfile(fname[0]):
            self.currentBackground = fname[0]
            self.set_background()

            print('Selected file > ', fname)


    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:

            if event.button() == QtCore.Qt.LeftButton:
                print(obj.objectName(), "Left click")
                self.prev_background()

            elif event.button() == QtCore.Qt.RightButton:
                print(obj.objectName(), "Right click")
                self.next_background()

            elif event.button() == QtCore.Qt.MiddleButton:
                print(obj.objectName(), "Middle click")
                self.custom_background()

        self.resizeWindowAction()
        return QtCore.QObject.event(obj, event)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = GetAnime()
    window.show()
    sys.exit(app.exec_())
