from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QFileDialog, QVBoxLayout
from PyQt5.QtCore import Qt
from tools.shared_data import SharedData
import resources.style as style

class ModelLoad(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.model_file = None
        self.shared_data = SharedData()

    def initUI(self):
        main_layout = QVBoxLayout()
        KerasImportLayout = QHBoxLayout()

        KerasImportButton = QPushButton("Import Keras File")
        KerasImportButton.setStyleSheet(style.button_style)
        KerasImportButton.setFixedSize(120, 30)
        KerasImportButton.clicked.connect(self.loadKeras)
        KerasImportLayout.addWidget(KerasImportButton, alignment=Qt.AlignLeft)

        self.KerasImportLabel = QLabel("Please choose a Keras file")
        KerasImportLayout.addWidget(self.KerasImportLabel, alignment=Qt.AlignLeft)

        KerasImportLayout.addStretch()

        main_layout.addLayout(KerasImportLayout)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        self.setAcceptDrops(True)

    def loadKeras(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Keras File", "", "Keras Files (*.keras);;All Files (*)", options=options)
        if fileName:
            self.KerasImportLabel.setText(fileName)
            self.model_file = fileName
            self.shared_data.data['model_file'] = self.model_file
        else:
            self.KerasImportLabel.setText("Please choose a Keras file")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            fileName = url.toLocalFile()
            if fileName.endswith('.h5'):
                self.KerasImportLabel.setText(fileName)
                break
        else:
            self.KerasImportLabel.setText("Please choose a Keras file")

class PredictPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        modelLoad = ModelLoad()
        layout.addWidget(modelLoad)

        self.setLayout(layout)