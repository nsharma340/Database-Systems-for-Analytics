import sys
from PyQt5.QtWidgets import QApplication
from BikeStoreMainWin import BikeStoreMainWin

app = QApplication(sys.argv)
window = BikeStoreMainWin()
app.exec_()