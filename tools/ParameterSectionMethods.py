from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, \
	QLabel, QLineEdit, QComboBox, QSpinBox, QPushButton, QCheckBox, \
		QGroupBox, QGridLayout, QSizePolicy, QScrollArea, QFileDialog, \
		QDoubleSpinBox, QMessageBox, QFrame, QSplitter
from PyQt5.QtGui import QImage, QPixmap, QDragEnterEvent, QDropEvent
from PyQt5.QtCore import Qt
import numpy as np
import fabio
from PIL import Image, ImageDraw, ImageFont
import matplotlib.cm as cm
from tools.Detector import Detector

from resources.style import *

def changeStyle(self, group_box):
    self.updatePreview()
    # Modify the style of QGroupBox
    group_box.setStyleSheet("""
        QGroupBox {
            background-color: #e6f7ff;
            border: 1px solid #d3d3d3;
            border-radius: 5px; 
            margin-top: 3ex;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 3px;
            color: #333;
            font-weight: bold;
        }
    """)

def updatePreview(self):
    bins_v = int(self.bins_v_input.text())
    bins_h = int(self.bins_h_input.text())
    v_detector = float(self.detector_v_input.text())
    h_detector = float(self.detector_h_input.text())
    self.center_v_input.setRange(0, float(self.bins_v_input.text()))
    self.center_h_input.setRange(0, float(self.bins_h_input.text()))
    
    if self.image is None:
        # Generate noise image
        gray_array = np.random.randint(0, 256, (bins_v, bins_h), dtype=np.uint8)
        # if self.sender() != self.confirm_button:
        # 	return

    else:
        if self.colorscale_box.currentText() == "Linear":
            gray_array = self.image.copy()
            gray_array[gray_array < 0] = 0
            gray_array[gray_array < self.colorbar_min_input.value()] = self.colorbar_min_input.value()
            gray_array[gray_array > self.colorbar_max_input.value()] = self.colorbar_max_input.value()
        elif self.colorscale_box.currentText() == "Log":
            gray_array = self.image.copy()
            gray_array[gray_array < 0] = 0
            gray_array = np.log(gray_array + 1e-6)
            gray_array[gray_array < self.colorbar_min_input.value()] = self.colorbar_min_input.value()
            gray_array[gray_array > self.colorbar_max_input.value()] = self.colorbar_max_input.value()
            gray_array = (gray_array / np.max(gray_array) * 255).astype(np.uint8)
        gray_array = np.flipud(gray_array)
        self.bins_h_input.setText(str(gray_array.shape[1]))
        self.bins_v_input.setText(str(gray_array.shape[0]))
        bins_v = int(self.bins_v_input.text())
        bins_h = int(self.bins_h_input.text())
        self.center_v_input.setRange(0, float(self.bins_v_input.text()))
        self.center_h_input.setRange(0, float(self.bins_h_input.text()))
        

    # Convert to PIL Image
    jet_array = cm.jet(gray_array / 255.0)
    jet_array = (jet_array[:, :, :3] * 255).astype(np.uint8)

    image = Image.fromarray(jet_array)

    # Create a new image with extra space for arrows and text
    new_width = bins_h + 60  # Extra space for arrows and text
    new_height = bins_v + 60  # Extra space for arrows and text

    # Option 1: Create a new transparent image
    new_image = Image.new("RGBA", (new_width, new_height), (0, 0, 0, 0))  # Create a new transparent image
    new_image.paste(image.convert("RGBA"), (30, 30))  # Paste the original image in the center

    # Option 2: Create a new gray image
    # new_image = Image.new("L", (new_width, new_height), color=128)  # Create a new gray image
    # new_image.paste(image, (30, 30))  # Paste the original image in the center

    # Draw arrows and text
    draw = ImageDraw.Draw(new_image)
    font = ImageFont.load_default()

    # Draw vertical arrow and text
    draw.line((20, 30, 20, bins_v + 30), fill=(0, 0, 0, 255), width=1)
    draw.polygon([(15, 30), (25, 30), (20, 20)], fill=(0, 0, 0, 255))
    draw.polygon([(15, bins_v + 30), (25, bins_v + 30), (20, bins_v + 40)], fill=(0, 0, 0, 255))

    # Create a new image for the vertical text
    text_image = Image.new('RGBA', (100, 20), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_image)
    text_draw.text((0, 0), f'{v_detector} mm; {bins_v} bins', fill=(0, 0, 0, 255), font=font)
    rotated_text_image = text_image.rotate(90, expand=True)
    new_image.paste(rotated_text_image, (5, bins_v // 2 - 15), rotated_text_image)

    # Draw horizontal arrow and text
    draw.line((30, bins_v + 40, bins_h + 30, bins_v + 40), fill=(0, 0, 0, 255), width=1)
    draw.polygon([(30, bins_v + 35), (30, bins_v + 45), (20, bins_v + 40)], fill=(0, 0, 0, 255))
    draw.polygon([(bins_h + 30, bins_v + 35), (bins_h + 30, bins_v + 45), (bins_h + 40, bins_v + 40)], fill=(0, 0, 0, 255))
    draw.text((bins_h // 2 - 15, bins_v + 45), f'{h_detector} mm; {bins_h} bins', fill=(0, 0, 0, 255), font=font)

    draw.text((bins_h // 2 + 10, 15), "Detector", fill=(0, 0, 0, 255), font=font)

    # draw center point
    x_center = self.center_h_input.text()
    y_center = self.center_v_input.text()
    scatter_size = np.min([bins_h, bins_v]) // 50
    draw.ellipse((float(x_center) + 30 - scatter_size, float(y_center) + 30 - scatter_size, float(x_center) + 30 + scatter_size, float(y_center) + 30 + scatter_size), fill=(255, 0, 0, 255))

    if self.sddSimuWindow is not None and self.sender() == self.sddSimuWindow.confirm_button:
        for i in range(len(self.sddSimuWindow.line_edits)):
            try:
                if self.sddSimuWindow.combo_box.currentText() == 'q':
                    q = float(self.sddSimuWindow.line_edits[i].text())
                    qz = self.qz

                    column_index = 0
                    column_data = qz[:, column_index]

                    max_index = np.argmax(np.abs(column_data))
                    min_index = np.argmin(np.abs(column_data))

                    max_value = column_data[max_index]
                    min_value = column_data[min_index]
                    value_difference = max_value - min_value

                    pixel_distance = abs(max_index - min_index)

                    if pixel_distance != 0:
                        step_size = value_difference / pixel_distance
                        radius = np.abs(q / step_size)
                    else:
                        step_size = 0
                        radius = 0  


                    linewidth = np.min([bins_h, bins_v]) // 50
                    draw.ellipse(
                        (float(x_center) + 30 - radius, float(y_center) + 30 - radius, 
                        float(x_center) + 30 + radius, float(y_center)+ 30 + radius), 
                        outline=(255, 0, 0, 255),  # red border
                        width=linewidth  # Border width of 2 pixels
                    )

                if self.sddSimuWindow.combo_box.currentText() == 'd':
                    d = float(self.sddSimuWindow.line_edits[i].text())
                    q = 2*np.pi / d
                    qz = self.qz

                    column_index = 0
                    column_data = qz[:, column_index]

                    max_index = np.argmax(np.abs(column_data))
                    min_index = np.argmin(np.abs(column_data))

                    max_value = column_data[max_index]
                    min_value = column_data[min_index]
                    value_difference = max_value - min_value

                    pixel_distance = abs(max_index - min_index)

                    if pixel_distance != 0:
                        step_size = value_difference / pixel_distance
                        radius = np.abs(q / step_size)
                    else:
                        step_size = 0
                        radius = 0  

                    print(radius)
                    linewidth = np.min([bins_h, bins_v]) // 50
                    draw.ellipse(
                        (float(x_center) + 30 - radius, float(y_center) + 30 - radius, 
                        float(x_center) + 30 + radius, float(y_center)+ 30 + radius), 
                        outline=(255, 0, 0, 255),  # red border
                        width=linewidth  # Border width of 2 pixels
                    )
            except:
                print('Error')



    # Convert back to QImage
    qimage = QImage(new_image.tobytes(), new_image.width, new_image.height, new_image.width * 4, QImage.Format_RGBA8888)

    # Convert to QPixmap and set to QLabel
    pixmap = QPixmap.fromImage(qimage)
    
    scroll_area_size = self.scroll_area.size()
    self.preview_image.setPixmap(pixmap.scaled(scroll_area_size, Qt.KeepAspectRatio))

def openFileDialog(self):
    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly
    self.file_name, _ = QFileDialog.getOpenFileName(self, "Select Input File", "", "Tiff Files (*.tiff *.tif *.cbf)", options=options)
    if self.file_name:
        print(f"Selected file: {self.file_name}")
        self.tifRead()
        self.updatePreview()

def tifRead(self):
    if self.file_name is None:
        return

    # Enable the right_layout
    for i in range(self.right_layout.count()):
        widget = self.right_layout.itemAt(i).widget()
        if widget is not None:
            widget.setEnabled(True)

    if self.file_name.lower().endswith('.tif') or self.file_name.lower().endswith('.tiff'):
        with Image.open(self.file_name) as img:
            self.image = np.array(img, dtype=np.float32)
    elif self.file_name.lower().endswith('.cbf'):
        img = fabio.open(self.file_name)
        self.image = img.data.astype(np.float32)
    else:
        QMessageBox.warning(self, "File error", "Unsupported file format")
        return

    min_text = self.threshold_mask_min_input.text()
    max_text = self.threshold_mask_max_input.text()

    if min_text or max_text:
        if not min_text:
            self.image[self.image > float(max_text)] = 0
            if not max_text.isdigit():
                self.threshold_mask_max_input.setText("")
                QMessageBox.warning(self, "Input error", "Maximum threshold must be a number")
                return
        elif not max_text:
            if not min_text.isdigit():
                self.threshold_mask_min_input.setText("")
                QMessageBox.warning(self, "Input error", "Minimum threshold must be numeric")
                return
            self.image[self.image < float(min_text)] = 0
        else:
            if not max_text.isdigit():
                self.threshold_mask_max_input.setText("")
                QMessageBox.warning(self, "Input error", "Maximum threshold must be a number")
                return
            if not min_text.isdigit():
                self.threshold_mask_min_input.setText("")
                QMessageBox.warning(self, "Input error", "Minimum threshold must be numeric")
                return
            min_value = float(min_text)
            max_value = float(max_text)
            self.image[(self.image < min_value) | (self.image > max_value)] = 0

    if self.colorscale_box.currentText() == "Log":
        self.colorbar_min_input.setValue(np.min(np.log(self.image.copy() + 1e-6)))
        self.colorbar_max_input.setValue(np.max(np.log(self.image.copy() + 1e-6)))
    elif self.colorscale_box.currentText() == "Linear":
        self.colorbar_min_input.setValue(np.min(self.image.copy()))
        self.colorbar_max_input.setValue(np.max(self.image.copy()))

    return self.image

def clear(self):
    self.alpha_in_input.setText("0.4")
    self.lambda_input.setText("0.1023")
    self.detector_v_input.setText("172")
    self.bins_v_input.setText("128")
    self.center_v_input.setValue(64)
    self.detector_h_input.setText("172")
    self.bins_h_input.setText("128")
    self.center_h_input.setValue(64)
    self.image = None
    self.group_box.setStyleSheet("""
        QGroupBox {
            background-color: #f0f0f0;
            border: 1px solid #d3d3d3;
            border-radius: 5px;
            margin-top: 3ex;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 3px;
            color: #333;
            font-weight: bold;
        }
    """)
    self.vertical_group_box.setStyleSheet("""
        QGroupBox {
            background-color: none;
            border: 1px solid #d3d3d3;
            border-radius: 5px;
            margin-top: 2ex;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 3px;
            color: #333;
        }
    """)
    self.horizontal_group_box.setStyleSheet("""
        QGroupBox {
            background-color: none;
            border: 1px solid #d3d3d3;
            border-radius: 5px;
            margin-top: 2ex;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 3px;
            color: #333;
        }
    """)
    
    self.updatePreview()
    self.preview_image.clear()
    self.file_name = None
    self.threshold_mask_min_input.clear()
    self.threshold_mask_max_input.clear()

    self.update_shared_data()

    for i in range(self.right_layout.count()):
        widget = self.right_layout.itemAt(i).widget()
        if widget is not None:
            widget.setEnabled(False)

def updateDetector(self):
    detector_params = [ int(self.bins_v_input.text()), float(self.detector_v_input.text()), int(self.bins_h_input.text()), float(self.detector_h_input.text())]
    beam_center = [float(self.center_v_input.text()), float(self.center_h_input.text())]
    distance = float(self.distance_input.text())
    theta_in_deg = float(self.alpha_in_input.text())
    wavelength = float(self.lambda_input.text())

    detector = Detector(detector_params, beam_center, distance, theta_in_deg, wavelength)
    self.qx, self.qy, self.qz, self.qr = detector.calculate_q_vectors()

    print('detector_params:', detector_params)
    print('beam_center:', beam_center)
    print('distance:', distance)
    print('theta_in_deg:', theta_in_deg)
    print('wavelength:', wavelength)

def changeDetector(self):
    if self.detector_model_box.currentText() == 'Costom':
        self.detector_h_input.setEnabled(True)
        self.detector_v_input.setEnabled(True)
        self.bins_h_input.setEnabled(True)
        self.bins_v_input.setEnabled(True)
        self.center_h_input.setEnabled(True)
        self.center_v_input.setEnabled(True)
    elif self.detector_model_box.currentText() == 'Pilatus 1M':
        self.detector_h_input.setEnabled(False)
        self.detector_v_input.setEnabled(False)
        self.bins_h_input.setEnabled(False)
        self.bins_v_input.setEnabled(False)
        self.detector_h_input.setText("168.732")
        self.detector_v_input.setText("179.396")
        self.bins_h_input.setText("981")
        self.bins_v_input.setText("1043")
        self.center_h_input.setValue(400)
        self.center_v_input.setValue(800)
    elif self.detector_model_box.currentText() == 'Pilatus 2M':
        self.detector_h_input.setEnabled(False)
        self.detector_v_input.setEnabled(False)
        self.bins_h_input.setEnabled(False)
        self.bins_v_input.setEnabled(False)
        self.detector_h_input.setText("253.7")
        self.detector_v_input.setText("288.788")
        self.bins_h_input.setText("1475")
        self.bins_v_input.setText("1679")
        self.center_h_input.setValue(700)
        self.center_v_input.setValue(1300)

def dragEnterEvent(self, event: QDragEnterEvent):
    if event.mimeData().hasUrls():
        event.acceptProposedAction()

def dropEvent(self, event: QDropEvent):
    for url in event.mimeData().urls():
        file_path = url.toLocalFile()
        if file_path.lower().endswith(('.tiff', '.tif')):
            print(f"Selected file: {file_path}")
            self.file_name = file_path
            self.tifRead()
            self.updatePreview()
            break

def clearThresholdMask(self):
    self.threshold_mask_min_input.clear()
    self.threshold_mask_max_input.clear()
    self.tifRead()
    self.updatePreview()

def update_shared_data(self):
    self.shared_data.data["alpha_in"] = float(self.alpha_in_input.text())
    self.shared_data.data["lambda"] = float(self.lambda_input.text())
    self.shared_data.data["detector_v"] = float(self.detector_v_input.text())
    self.shared_data.data["bins_v"] = int(self.bins_v_input.text())
    self.shared_data.data["center_v"] = float(self.center_v_input.text())
    self.shared_data.data["detector_h"] = float(self.detector_h_input.text())
    self.shared_data.data["bins_h"] = int(self.bins_h_input.text())
    self.shared_data.data["center_h"] = float(self.center_h_input.text())
    self.shared_data.data["image"] = self.image
    self.shared_data.data["file_name"] = self.file_name
    self.shared_data.data["colorscale"] = self.colorscale_box.currentText()
    self.shared_data.data["colorbar_min"] = self.colorbar_min_input.value()
    self.shared_data.data["colorbar_max"] = self.colorbar_max_input.value()
    self.shared_data.data["threshold_mask_min"] = self.threshold_mask_min_input.text()
    self.shared_data.data["threshold_mask_max"] = self.threshold_mask_max_input.text()

def open_sddSimu(self):
    self.sddSimuWindow = sddSimuWindow(self)
    self.sddSimuWindow.show()

class sddSimuWindow(QWidget):
	def __init__(self, parent):
		super().__init__()
		self.parent = parent
		self.initUI()
	
	def initUI(self):
		self.setWindowTitle('Parameter Window')
		self.setGeometry(150, 150, 300, 200)
		
		self.layout = QVBoxLayout()
		
		# drop-down selection box
		self.combo_box = QComboBox(self)
		self.combo_box.addItems(['q', 'd'])
		self.combo_box.currentIndexChanged.connect(self.update_fields)
		self.layout.addWidget(self.combo_box)
		
		# Dynamic field layout
		self.fields_layout = QVBoxLayout()
		self.layout.addLayout(self.fields_layout)
		
		# Initialization Fields
		self.update_fields()
		
		# Confirmation Button
		self.confirm_button = QPushButton('Show', self)
		self.confirm_button.clicked.connect(self.confirm)
		self.layout.addWidget(self.confirm_button)
		
		self.setLayout(self.layout)

	def update_fields(self):
		# Clear existing fields
		for i in reversed(range(self.fields_layout.count())):
			widget = self.fields_layout.itemAt(i).widget()
			if widget is not None:
				widget.deleteLater()
		
		# Get current selection
		current_choice = self.combo_box.currentText()

		self.line_edits = []
		# Dynamically adding fields
		for i in range(1, 5):
			label = QLabel(f'{current_choice}_{i}', self)
			line_edit = QLineEdit(self)
			self.fields_layout.addWidget(label)
			self.fields_layout.addWidget(line_edit)
			self.line_edits.append(line_edit)

	def confirm(self):
		self.parent.updatePreview()