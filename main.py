
import sys
from PyQt5.QtCore import*
from PyQt5.QtWidgets import*
from PyQt5.QtWebEngineWidgets import*

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.browser=QWebEngineView()
        self.browser.setUrl(QUrl('http://localhost:8085'))
        self.setCentralWidget(self.browser)
        self.showMaximized()
        
        navbar = QToolBar()
        self.addToolBar(navbar)
        
        back_btn=QAction('Back',self)
        back_btn.triggered.connect(self.browser.back)
        navbar.addAction(back_btn)

        forward_btn=QAction('forward',self)
        forward_btn.triggered.connect(self.browser.forward)
        navbar.addAction(forward_btn)

        reload_btn=QAction('Reload',self)
        reload_btn.triggered.connect(self.browser.reload)
        navbar.addAction(reload_btn)

        home_btn=QAction('Home',self)
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)

        self.url_bar =QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)
        self.browser.urlChanged.connect(self.update_url)

    def navigate_home(self):
        self.browser.setUrl(QUrl('http://localhost:8085/'))
    
    def navigate_to_url(self):
        query= self.url_bar.text()
        if not query.startswith("http://") and not query.startswith("http://"):
            local_url = f"http://localhost:8085/{query}.html"
            self.browser.setUrl(QUrl(local_url))
            
        else:
            self.browser.setUrl(QUrl(query))
    
    def update_url(self, q):
        self.url_bar.setText(q.toString())

app =QApplication(sys.argv)
QApplication.setApplicationName('Avater: The Last Broweser')
window=MainWindow()
window.show()
sys.exit(app.exec_())
