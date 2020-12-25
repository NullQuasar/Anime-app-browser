from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtGui import QImage, QPalette, QBrush
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QMessageBox
import os
import re
import urllib.parse
import requests
import sys

class MainWindow(QtWidgets.QMainWindow):
    resized = QtCore.pyqtSignal()
    def __init__(self):
     
        super(MainWindow, self).__init__()
        self.currentPath = os.getcwd().replace('\\', '/')
        uic.loadUi(self.currentPath + '/AnimeSearcher.ui', self)
        #sys.setrecursionlimit(10000)

        self.anime = self.SearchInput.toPlainText()
        self.cap = ''
        self.urls = []
        nums = re.findall(r'\d+', self.anime)

        if len(nums) > 0:
            self.cap = nums[len(nums)-1]

        
        self.animeflvOp.stateChanged.connect(self.animeflvChecked)
        self.animefenixOp.stateChanged.connect(self.animefenixChecked)
        self.tioanimeOp.stateChanged.connect(self.tioanimeChecked)
        self.monoschinosOp.stateChanged.connect(self.monoschinosChecked)
        self.searchButton.clicked.connect(self.setQuery)
        self.resized.connect(self.resizeWindowAction)

        # Set background image:
        self.currentBackground = self.currentPath + "/AnimeSearcherImages/" + 'background9.jpg'
        oImage = QImage(self.currentBackground)
        sImage = oImage.scaled(QSize(1126,704))                   # resize Image to widgets size
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))                        
        self.setPalette(palette)

        # Set banner image:
        #bannerImage = self.currentPath + '/AnimeSearcherImages/banner.jpg'
        #self.steticImage.setStyleSheet("background-image : url(C:/Users/Usuario/Desktop/Informática/Programacion/GitHub/AnimeSearcher/AnimeSearcherImages/banner.jpg); border : 2px solid blue") 

        #MainWindow.setStyleSheet("background-image: url(AnimeSearcher/background.jpg)")
        self.checkedOps = set()  
        self.openInBrowser()

        """
        if True:
            import threading
            event = threading.Event()
            event.set()
            thread = threading.Thread(target=self.variantBackground, args=(event,))
            thread.start()
        """
            


    def resizeEvent(self, event):
        self.resized.emit()
        return super(MainWindow, self).resizeEvent(event)


    def resizeWindowAction(self):
        oImage = QImage(self.currentBackground)
        sImage = oImage.scaled(QSize(self.width(), self.height()))                   # resize Image to widgets size
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))                        
        self.setPalette(palette)


    def animeflvChecked(self):
        self.checkedOps.add('https://www3.animeflv.net')

    def animefenixChecked(self):
        self.checkedOps.add('https://www.animefenix.com')

    def tioanimeChecked(self):
        self.checkedOps.add('https://tioanime.com')

    def monoschinosChecked(self):
        self.checkedOps.add('https://monoschinos2.com')


    def typeOfSearch(self):
        if len(self.checkedOps) > 0:
            if self.isEpisode():
                for p in self.checkedOps:
                    self.SearchByEpisode(p)
            else:
                for p in self.checkedOps:
                    self.SearchAnime(p)
                    print(p)
        else:
            msg = QMessageBox()
            msg.setWindowTitle('Platform!')
            msg.setText('Please select the platform(s)')
            msg.setIcon(QMessageBox.Information)

            x = msg.exec_()


    def openInBrowser(self):
        # Open links in browser
        if self.openBrowser.isChecked():
            for p in self.urls:
                os.system('start ' + p)

    def setQuery(self):
        print('Debug! ', self.checkedOps)
        self.urls.clear()
        self.Results.clear()
        self.anime = self.SearchInput.toPlainText()
        self.SearchInput.setText(self.anime.title())
        
        # Set cap
        nums = re.findall(r'\d+', self.anime)
        if len(nums) > 0:
            self.cap = nums[len(nums)-1]
            
        # Verify input
        if self.anime == '':
            msg = QMessageBox()
            msg.setWindowTitle('Anime')
            msg.setText('Please type your anime!')
            msg.setIcon(QMessageBox.Information)

            x = msg.exec_()

        else:
            self.typeOfSearch()
            self.openInBrowser()

    def isEpisode(self):
        # Determinar tipo de busqueda (consulta o capitulo)
        if len(self.cap) == 0:
            return False
        else:
            return True



    # If the self.anime is not found it probes some common parameters like tv and hd
    def ProbeOtherParameters(self, url):
        parameters = ['tv', 'hd']

        index = url.find('-' + self.cap)
        found = False
        for i in parameters:
            
            url = url[:index] + '-' + i + url[index:]
            print('Probando ' + url)

            if requests.get(url).status_code == 404:
                print('Pagina no encontrada.')
                print('Probando siguiente parametro...')

            else:
                print('Encontrado: ' + url)
                self.anime = url
                self.SearchByEpisode(platform)
                found = True
                break
        
        if not found:
            print('Anime o capitulo no encontrado')



    def SearchAnime(self, platform):
        #query = urllib.parse.quote(query) Dont work
        query = self.anime.replace(' ', '+')

        if platform == 'https://www3.animeflv.net':
            param = '/browse?q=' # Param for animeflv

        elif platform == 'https://www.animefenix.com': # Param for animefenix
            param = '/animes?q='

        elif platform == 'https://tioanime.com': # Param for tioanime
            param = '/directorio?q='

        elif platform == 'https://monoschinos2.com': # Param for monoschinos
            param = '/search?q='


        url = platform + param + query

        self.Results.addItem(QtWidgets.QListWidgetItem(url))
        self.urls.append(url)
        print('Añadido a la lista.')



    def SearchByEpisode(self, platform):
        query = self.anime.replace(' ', '-').lower()
        url = platform + '/ver/' + query

        print(requests.get(url).status_code) # Debug
        if requests.get(url).status_code == 404:
            print('Pagina no encontrada.')
            print('Probando con otros parametros...')
            self.ProbeOtherParameters(url)
            
        else:
            self.Results.addItem(QtWidgets.QListWidgetItem(url))
            self.urls.append(url)
            print('Añadido a la lista.')



    def variantBackground(self, event):
        from time import sleep

        sleepTime = 60
        path = self.currentPath + '/AnimeSearcherImages/'
        backgrounds = os.listdir(path)

        # Constantly change the background
        while True:
            for image in backgrounds:
                self.currentPath = path + image
                self.resizeWindowAction()
                event.wait(sleepTime)
                
        

            

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())