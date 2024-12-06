# ui/MainWindow.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, \
    QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QDesktopWidget
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")

        # Get screen resolution
        screen = QDesktopWidget().screenGeometry()
        screen_width = screen.width()
        screen_height = screen.height()

        # Set window size to 80% of screen size
        window_width = int(screen_width * 0.6)
        window_height = int(screen_height * 0.6)

        # Set the window position to the center of the screen
        window_x = int((screen_width - window_width) / 2)
        window_y = int((screen_height - window_height) / 2)

        self.setGeometry(window_x, window_y, window_width, window_height)

        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("""
            QWidget {
                background-color: #F0F0F0;
                border: 1px solid #D3D3D3;
                border-radius: 5px;
            }
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #D3D3D3;
                border-radius: 5px;
            }
            QLabel {
                background-color: transparent;
                border: none;
            }                              
        """)
        self.setCentralWidget(self.central_widget)

        self.layout = QHBoxLayout(self.central_widget)

        self.button_widget = QWidget()
        self.button_layout = QVBoxLayout(self.button_widget)
        # align buttons to the top
        self.button_layout.setAlignment(Qt.AlignTop)
        button_widget_style = """
        QWidget {
            background-color: #F9F9F9;
            border-radius: 15px;
            border: 1px solid #E0E0E0;
        }
        """
        self.button_widget.setStyleSheet(button_widget_style)
        # Add shadow effect
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)  # Increase blur radius for a softer shadow
        shadow.setXOffset(0)
        shadow.setYOffset(6)  # Slightly increase the offset for a more pronounced effect
        shadow.setColor(Qt.gray)  # Use a gray color for a more subtle shadow
        self.button_widget.setGraphicsEffect(shadow)
        
        self.page_layout = QStackedWidget()

        self.layout.addWidget(self.button_widget)
        self.layout.addWidget(self.page_layout)

        self.pages = []
        self.initUI()

    def initUI(self):
        # Add pages
        from ui.TrainSet import TrainSetPage
        from ui.page2 import Page2
        from ui.Predict import PredictPage

        self.pages.append(TrainSetPage())
        self.pages.append(Page2())
        self.pages.append(PredictPage())

        for page in self.pages:
            self.page_layout.addWidget(page)

        # Add buttons to switch pages
        self.page1_button = QPushButton("Build TrainSet")
        self.page2_button = QPushButton("Train Model")
        self.page3_button = QPushButton("Predict")

        self.buttons = [self.page1_button, self.page2_button, self.page3_button]

        self.page1_button.clicked.connect(lambda: self.switch_page(0))
        self.page2_button.clicked.connect(lambda: self.switch_page(1))
        self.page3_button.clicked.connect(lambda: self.switch_page(2))

        # Define styles to buttons
        self.button_style = """
        QPushButton {
            font-size: 16px;
            padding: 32px 16px;
            border: 1px solid #A6A6A6;
            border-radius: 8px;
            background-color: #E1E1E1;
            color: black;
            border: none;
        }
        QPushButton:hover {
            background-color: #D1D1D1;
        }
        QPushButton:pressed {
            background-color: #C1C1C1;
        }
        """

        self.highlighted_button_style = """
        QPushButton {
            font-size: 16px;
            padding: 32px 16px;
            border: 1px solid #A6A6A6;
            border-radius: 8px;
            background-color: #ADD8E6;
            color: white;
            border: none;
        }
        """
        # background-color: #87CEEB  # SkyBlue
        

        self.button_layout.addWidget(self.page1_button)
        self.button_layout.addWidget(self.page2_button)
        self.button_layout.addWidget(self.page3_button)
        

        # Set the first page as the current page
        self.switch_page(0)

    def switch_page(self, index):
        self.page_layout.setCurrentIndex(index)
        for i, button in enumerate(self.buttons):
            if i == index:
                button.setStyleSheet(self.highlighted_button_style)
            else:
                button.setStyleSheet(self.button_style)

    