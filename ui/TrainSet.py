from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, \
	QLabel, QLineEdit, QComboBox, QSpinBox, QPushButton, QCheckBox, \
		QGroupBox, QGridLayout, QSizePolicy, QScrollArea, QFileDialog, \
		QDoubleSpinBox, QMessageBox, QFrame, QSplitter
from PyQt5.QtGui import QImage, QPixmap, QDragEnterEvent, QDropEvent
from PyQt5.QtCore import Qt, QTimer
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib.cm as cm
import time
from tools.Detector import Detector
import matplotlib.pyplot as plt
import importlib
import threading

from resources.style import *
from tools.ParameterSectionMethods import *
from tools.shared_data import SharedData
from tools.ParticleSectionMethods import *

class ParameterSection(QWidget):
	def __init__(self):
		super().__init__()
		self.shared_data = SharedData()
		self.sddSimuWindow = None
		self.image = None
		self.file_name = None

		'''
		############################################
		############################################
		############################################
		#	   Binding functions to classes        #
		############################################
		############################################
		############################################
		'''

		self.changeStyle = changeStyle.__get__(self)
		self.updatePreview = updatePreview.__get__(self)
		self.openFileDialog = openFileDialog.__get__(self)
		self.tifRead = tifRead.__get__(self)
		self.clear = clear.__get__(self)
		self.updateDetector = updateDetector.__get__(self)
		self.changeDetector = changeDetector.__get__(self)
		self.dragEnterEvent = dragEnterEvent.__get__(self)
		self.dropEvent = dropEvent.__get__(self)
		self.clearThresholdMask = clearThresholdMask.__get__(self)
		self.open_sddSimu = open_sddSimu.__get__(self)
		self.update_shared_data = update_shared_data.__get__(self)

		self.initUI()
		
		self.update_shared_data()
		self.updateDetector()

		# set the right_layout to be disabled by default
		for i in range(self.right_layout.count()):
			widget = self.right_layout.itemAt(i).widget()
			if widget is not None:
				widget.setEnabled(False)

	def initUI(self):
		self.setAcceptDrops(True) # Enable drag and drop

		main_layout = QHBoxLayout()
		left_layout = QVBoxLayout()
		grid_layout = QGridLayout()
		self.right_layout = QVBoxLayout()

		'''
		############################################
		############################################
		############################################
		#			    Left Layout                #
		############################################
		############################################
		############################################
		'''
		'''
		############################################
		#			    Alpha Incident             #
		############################################
		'''
		alpha_in_label = QLabel("α<sub>in</sub> (deg):")
		alpha_in_label.setToolTip('Incident Angle')
		self.alpha_in_input = QLineEdit()
		self.alpha_in_input.setText("0.4")
		self.alpha_in_input.editingFinished.connect(self.update_shared_data)
		self.alpha_in_input.editingFinished.connect(self.updateDetector)

		'''
		############################################
		#			       Lambda                  #
		############################################
		'''
		lambda_label = QLabel("λ (nm):")
		lambda_label.setToolTip('Wavelength of the incident beam')
		self.lambda_input = QLineEdit()
		self.lambda_input.setText("0.1023")
		self.lambda_input.editingFinished.connect(self.update_shared_data)
		self.lambda_input.editingFinished.connect(self.updateDetector)

		'''
		############################################
		#			     Distance                  #
		############################################
		'''
		distance_label = QLabel("SDD (mm):")
		distance_label.setToolTip('Sample to Detector Distance')
		self.distance_input = QLineEdit()
		self.distance_input.setText("3000")
		self.distance_input.editingFinished.connect(self.update_shared_data)
		self.distance_input.editingFinished.connect(self.updateDetector)


		'''
		############################################
		#			  Vertical GroupBox            #
		############################################
		'''
		self.vertical_group_box = QGroupBox("Vertical")
		vertical_layout = QGridLayout()

		'''
		############################################
		#			  Detector Vertical            #
		############################################
		'''
		detector_v_label = QLabel("Detector v (mm):")
		detector_v_label.setToolTip('Vertical detector size')
		self.detector_v_input = QLineEdit()
		self.detector_v_input.setText("172")
		self.detector_v_input.textChanged.connect(self.update_shared_data)
		self.detector_v_input.textChanged.connect(self.updateDetector)
		bins_v_label = QLabel("Bins v:")
		bins_v_label.setToolTip('Number of bins in the vertical direction')
		self.bins_v_input = QLineEdit()
		self.bins_v_input.setText("128")
		self.bins_v_input.textChanged.connect(self.update_shared_data)
		self.bins_v_input.textChanged.connect(self.updateDetector)
		center_v_label = QLabel("Center y (bin):")
		center_v_label.setToolTip('Center of the vertical detector')
		self.center_v_input = QDoubleSpinBox()
		self.center_v_input.setRange(0, float(self.bins_v_input.text()))
		self.center_v_input.setValue(64.0)
		self.center_v_input.setSingleStep(1)
		self.center_v_input.setStyleSheet("background-color: white;")
		self.center_v_input.valueChanged.connect(self.updatePreview)
		self.center_v_input.valueChanged.connect(self.update_shared_data)

		vertical_layout.addWidget(detector_v_label, 0, 0)
		vertical_layout.addWidget(self.detector_v_input, 0, 1)
		vertical_layout.addWidget(bins_v_label, 1, 0)
		vertical_layout.addWidget(self.bins_v_input, 1, 1)
		vertical_layout.addWidget(center_v_label, 2, 0)
		vertical_layout.addWidget(self.center_v_input, 2, 1)

		self.vertical_group_box.setLayout(vertical_layout)
		

		'''
		############################################
		#			  Horizontal GroupBox          #
		############################################
		'''
		self.horizontal_group_box = QGroupBox("Horizontal")
		horizontal_layout = QGridLayout()

		'''
		############################################
		#			  Detector horizental          #
		############################################
		'''
		detector_h_label = QLabel("Detector h (mm):")
		detector_h_label.setToolTip('Horizontal detector size')
		self.detector_h_input = QLineEdit()
		self.detector_h_input.setText("172")
		self.detector_h_input.textChanged.connect(self.update_shared_data)
		self.detector_h_input.textChanged.connect(self.updateDetector)
		bins_h_label = QLabel("Bins h:")
		bins_h_label.setToolTip('Number of bins in the horizontal direction')
		self.bins_h_input = QLineEdit()
		self.bins_h_input.setText("128")
		self.bins_h_input.textChanged.connect(self.update_shared_data)
		self.bins_h_input.textChanged.connect(self.updateDetector)
		center_h_label = QLabel("Center x (bin):")
		center_h_label.setToolTip('Center of the horizontal detector')
		self.center_h_input = QDoubleSpinBox()
		self.center_h_input.setRange(0, float(self.bins_h_input.text()))
		self.center_h_input.setValue(64.0)
		self.center_h_input.setSingleStep(1)
		self.center_h_input.setStyleSheet("background-color: white;")
		self.center_h_input.valueChanged.connect(self.updatePreview)
		self.center_h_input.valueChanged.connect(self.update_shared_data)
	

		horizontal_layout.addWidget(detector_h_label, 0, 0)
		horizontal_layout.addWidget(self.detector_h_input, 0, 1)
		horizontal_layout.addWidget(bins_h_label, 1, 0)
		horizontal_layout.addWidget(self.bins_h_input, 1, 1)
		horizontal_layout.addWidget(center_h_label, 2, 0)
		horizontal_layout.addWidget(self.center_h_input, 2, 1)
		self.horizontal_group_box.setLayout(horizontal_layout)

		
		'''
		##############################################
		#	Area of preview the detector's patterns  #
		##############################################
		'''
		self.preview_image = QLabel()
		self.preview_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


		'''
		############################################
		#			   Confirm Button              #
		############################################
		'''
		self.confirm_button = QPushButton("Confirm")
		self.confirm_button.setToolTip('Please confirm the parameters first, and then continue to the next step')
		self.confirm_button.setFixedSize(80, 30)
		self.confirm_button.setStyleSheet("""
			QPushButton {
				background-color: #f0f0f0;
				border: 1px solid #d3d3d3;
				border-radius: 5px;
				padding: 5px;
			}
			QPushButton:hover {
				background-color: #e0e0e0;
				border: 1px solid #c3c3c3;
			}
			QPushButton:pressed {
				background-color: #d0d0d0;
				border: 1px solid #b3b3b3;
			}
		""")
		self.confirm_button.clicked.connect(lambda: self.changeStyle(self.group_box))

		'''
		############################################
		#				Clear Button               #
		############################################
		'''
		clear_button = QPushButton("Clear")
		clear_button.setToolTip('Clear the parameters')
		clear_button.setFixedSize(80, 30)
		clear_button.setStyleSheet("""
			QPushButton {
				background-color: #f0f0f0;
				border: 1px solid #d3d3d3;
				border-radius: 5px;
				padding: 5px;
			}
			QPushButton:hover {
				background-color: #e0e0e0;
				border: 1px solid #c3c3c3;
			}
			QPushButton:pressed {
				background-color: #d0d0d0;
				border: 1px solid #b3b3b3;
			}
		""")
		clear_button.clicked.connect(self.clear)

		'''
		############################################
		#				Input Files                #
		############################################
		'''
		input_files_button = QPushButton("Files")
		input_files_button.setToolTip('Select the input files')
		input_files_button.setFixedSize(80, 30)
		input_files_button.setStyleSheet("""
			QPushButton {
				background-color: #f0f0f0;
				border: 1px solid #d3d3d3;
				border-radius: 5px;
				padding: 5px;
			}
			QPushButton:hover {
				background-color: #e0e0e0;
				border: 1px solid #c3c3c3;
			}
			QPushButton:pressed {
				background-color: #d0d0d0;
				border: 1px solid #b3b3b3;
			}
		""")
		input_files_button.clicked.connect(self.openFileDialog)

		'''
		############################################
		#				SDD Simulate               #
		############################################
		'''
		sddSimu_button = QPushButton("SDD Simulate",self)
		sddSimu_button.setFixedSize(80, 30)
		sddSimu_button.clicked.connect(self.open_sddSimu)
		sddSimu_button.setStyleSheet(button_style)

		'''
		############################################
		#	         Detector Choose               #
		############################################
		'''
		self.detector_model_box = QComboBox(self)
		self.detector_model_box.setStyleSheet(ComboBox_style)
		self.detector_model_box.addItems(['Costom','Pilatus 1M', 'Pilatus 2M'])
		self.detector_model_box.currentIndexChanged.connect(self.changeDetector)

		'''
		############################################
		# ↑↑↑↑ Left Layout ←←←←← Add Widget ↓↓↓↓   #
		############################################
		'''
		button_layout = QHBoxLayout()
		grid_layout.addWidget(alpha_in_label, 0, 0)
		grid_layout.addWidget(self.alpha_in_input, 0, 1)
		grid_layout.addWidget(lambda_label, 0, 2)
		grid_layout.addWidget(self.lambda_input, 0, 3)
		grid_layout.addWidget(distance_label, 0, 4)
		grid_layout.addWidget(self.distance_input, 0, 5)
		grid_layout.addWidget(self.vertical_group_box, 1, 3, 1, 3)
		grid_layout.addWidget(self.horizontal_group_box, 1, 0, 1, 3)

		button_layout = QHBoxLayout()
		button_layout.addWidget(self.confirm_button)
		button_layout.addWidget(clear_button)
		button_layout.addWidget(sddSimu_button)
		button_layout.addWidget(self.detector_model_box)
		button_layout.addStretch()
		button_layout.addWidget(input_files_button, Qt.AlignRight)
		grid_layout.addLayout(button_layout, 4, 0, 1, 6)

		'''
		############################################
		############################################
		############################################
		#			  Middle Layout                #
		############################################
		############################################
		############################################
		'''
		self.scroll_area = QScrollArea()
		self.scroll_area.setWidgetResizable(True)
		self.scroll_area.setWidget(self.preview_image)

		'''
		############################################
		############################################
		############################################
		#			   Right Layout                #
		############################################
		############################################
		############################################
		'''
		'''
		############################################
		#				Color Scale                #
		############################################
		'''
		# adjust the colorbar, choose linear or log scale
		colorscale_label = QLabel("Colorscale:")
		self.colorscale_box = QComboBox()
		self.colorscale_box.addItem("Linear")
		self.colorscale_box.addItem("Log")
		self.colorscale_box.setToolTip('Select an option to adjust the scale of the colorbar')
		self.colorscale_box.currentIndexChanged.connect(self.tifRead)
		self.colorscale_box.currentIndexChanged.connect(self.updatePreview)
		self.colorscale_box.currentIndexChanged.connect(self.update_shared_data)

		'''
		############################################
		#				Color Bar                  #
		############################################
		'''
		colorbar_min_label = QLabel("Min:")
		self.colorbar_min_input = QDoubleSpinBox()
		self.colorbar_min_input.setRange(0, 1e6)
		self.colorbar_min_input.valueChanged.connect(self.updatePreview)
		self.colorbar_min_input.valueChanged.connect(self.update_shared_data)
		colorbar_max_label = QLabel("Max:")
		self.colorbar_max_input = QDoubleSpinBox()
		self.colorbar_max_input.setRange(0, 1e6)
		self.colorbar_max_input.valueChanged.connect(self.updatePreview)
		self.colorbar_max_input.valueChanged.connect(self.update_shared_data)

		'''
		############################################
		#	         Threshold Mask                #
		############################################
		'''
		threshold_mask_min_label = QLabel("Threshold Mask min:")
		self.threshold_mask_min_input = QLineEdit()
		self.threshold_mask_min_input.setFixedSize(90, 15)
		self.threshold_mask_min_input.editingFinished.connect(self.tifRead)
		self.threshold_mask_min_input.editingFinished.connect(self.updatePreview)
		self.threshold_mask_min_input.editingFinished.connect(self.update_shared_data)
		
		threshold_mask_max_label = QLabel("Threshold Mask max:")
		self.threshold_mask_max_input = QLineEdit()
		self.threshold_mask_max_input.setFixedSize(90, 15)
		self.threshold_mask_max_input.editingFinished.connect(self.tifRead)
		self.threshold_mask_max_input.editingFinished.connect(self.updatePreview)
		self.threshold_mask_max_input.editingFinished.connect(self.update_shared_data)

		threshold_mask_clear_button = QPushButton("Clear Threshold")
		threshold_mask_clear_button.clicked.connect(self.clearThresholdMask)
		threshold_mask_clear_button.setStyleSheet("""
			QPushButton {
				background-color: #f0f0f0;
				border: 1px solid #d3d3d3;
				border-radius: 5px;
				padding: 5px;
			}
			QPushButton:hover {
				background-color: #e0e0e0;
				border: 1px solid #c3c3c3;
			}
			QPushButton:pressed {
				background-color: #d0d0d0;
				border: 1px solid #b3b3b3;
			}
		""")
	

		self.right_layout.addWidget(colorscale_label, alignment=Qt.AlignTop)
		self.right_layout.addWidget(self.colorscale_box, alignment=Qt.AlignTop)
		self.right_layout.addWidget(colorbar_min_label, alignment=Qt.AlignTop)
		self.right_layout.addWidget(self.colorbar_min_input, alignment=Qt.AlignTop)
		self.right_layout.addWidget(colorbar_max_label, alignment=Qt.AlignTop)
		self.right_layout.addWidget(self.colorbar_max_input, alignment=Qt.AlignTop)
		self.right_layout.addWidget(threshold_mask_min_label, alignment=Qt.AlignTop)
		self.right_layout.addWidget(self.threshold_mask_min_input, alignment=Qt.AlignTop)
		self.right_layout.addWidget(threshold_mask_max_label, alignment=Qt.AlignTop)
		self.right_layout.addWidget(self.threshold_mask_max_input, alignment=Qt.AlignTop)

		self.right_layout.addStretch()

		self.right_layout.addWidget(threshold_mask_clear_button, alignment=Qt.AlignBottom)
		# hide the self.right_layout if the image is not loaded
		


		self.group_box = QGroupBox("Parameters")
		self.group_box.setLayout(grid_layout)
		
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
		
		left_layout.addWidget(self.group_box)
		main_layout.addLayout(left_layout)
		main_layout.addWidget(self.scroll_area)

		main_layout.addLayout(self.right_layout)
		
		self.setLayout(main_layout)	

class ParticleSection(QWidget):
	def __init__(self):
		super().__init__()
		self.shared_data = SharedData()

		self.update_display = update_display.__get__(self)
		self.update_shape_parameters = update_shape_parameters.__get__(self)
		self.update_shared_data = Particle_update_shared_data.__get__(self)
		self.simulate_pattern = simulate_pattern.__get__(self)

		self.initUI()
		
	def initUI(self):
		main_layout = QHBoxLayout()
		left_layout = QVBoxLayout()

		'''
		############################################
		############################################
		############################################
		#			   Left Layout                 #
		############################################
		############################################
		############################################
		'''

		'''
		############################################
		#			  Shape Choose                 #
		############################################
		'''
		shape_layout = QHBoxLayout()
		shape_label = QLabel("Shape:")
		self.shape_combo = QComboBox()
		self.shape_combo.addItems(["Ellipsoid", "Hemisphere", "Sphere"])
		shape_layout.addWidget(shape_label)
		shape_layout.addWidget(self.shape_combo)
		left_layout.addLayout(shape_layout)

		'''
		############################################
		#			    Ellipsoid                  #
		############################################
		'''
		self.ellipsoid_group = QGroupBox("Ellipsoid")
		self.ellipsoid_group.setStyleSheet("""
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
		ellipsoid_layout = QGridLayout()
		ellipsoid_layout.addWidget(QLabel("H_min (nm):"), 0, 0)
		self.ellipsoid_h1 = QLineEdit('0.05')
		ellipsoid_layout.addWidget(self.ellipsoid_h1, 0, 1)
		ellipsoid_layout.addWidget(QLabel("H_max (nm):"), 0, 2)
		self.ellipsoid_h2 = QLineEdit('20.0')
		ellipsoid_layout.addWidget(self.ellipsoid_h2, 0, 3)

		ellipsoid_layout.addWidget(QLabel("R_min (nm):"), 1, 0)
		self.ellipsoid_r1 = QLineEdit()
		ellipsoid_layout.addWidget(self.ellipsoid_r1, 1, 1)
		ellipsoid_layout.addWidget(QLabel("R_max (nm):"), 1, 2)
		self.ellipsoid_r2 = QLineEdit()
		ellipsoid_layout.addWidget(self.ellipsoid_r2, 1, 3)

		self.ellipsoid_group.setLayout(ellipsoid_layout)

		self.ellipsoid_r1.editingFinished.connect(self.update_shared_data)
		self.ellipsoid_r2.editingFinished.connect(self.update_shared_data)
		self.ellipsoid_h1.editingFinished.connect(self.update_shared_data)
		self.ellipsoid_h2.editingFinished.connect(self.update_shared_data)

		'''
		############################################
		#			    Hemisphere                 #
		############################################
		'''
		# Hemisphere parameters
		self.hemisphere_group = QGroupBox("Hemisphere")
		self.hemisphere_group.setStyleSheet("""
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
		
		hemisphere_layout = QGridLayout()
		hemisphere_layout.addWidget(QLabel("H_min (nm):"), 0, 0)
		self.hemisphere_h1 = QLineEdit()
		hemisphere_layout.addWidget(self.hemisphere_h1, 0, 1)
		hemisphere_layout.addWidget(QLabel("H_max (nm):"), 0, 2)
		self.hemisphere_h2 = QLineEdit()
		hemisphere_layout.addWidget(self.hemisphere_h2, 0, 3)

		hemisphere_layout.addWidget(QLabel("R_min (nm):"), 1, 0)
		self.hemisphere_r1 = QLineEdit()
		hemisphere_layout.addWidget(self.hemisphere_r1, 1, 1)
		hemisphere_layout.addWidget(QLabel("R_max (nm):"), 1, 2)
		self.hemisphere_r2 = QLineEdit()
		hemisphere_layout.addWidget(self.hemisphere_r2, 1, 3)

		self.hemisphere_group.setLayout(hemisphere_layout)

		self.hemisphere_r1.editingFinished.connect(self.update_shared_data)
		self.hemisphere_r2.editingFinished.connect(self.update_shared_data)
		self.hemisphere_h1.editingFinished.connect(self.update_shared_data)
		self.hemisphere_h2.editingFinished.connect(self.update_shared_data)

		'''
		############################################
		#			       Sphere                  #
		############################################
		'''
		# Sphere parameters
		self.sphere_group = QGroupBox("Sphere")
		self.sphere_group.setStyleSheet("""
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
		sphere_layout = QGridLayout()
		sphere_layout.addWidget(QLabel("R_min (nm):"), 0, 0)
		self.sphere_r1 = QLineEdit()
		sphere_layout.addWidget(self.sphere_r1, 0, 1)
		sphere_layout.addWidget(QLabel("R_max (nm):"), 0, 2)
		self.sphere_r2 = QLineEdit()
		sphere_layout.addWidget(self.sphere_r2, 0, 3)

		self.sphere_group.setLayout(sphere_layout)

		self.sphere_r1.editingFinished.connect(self.update_shared_data)
		self.sphere_r2.editingFinished.connect(self.update_shared_data)

		left_layout.addWidget(self.ellipsoid_group)
		left_layout.addWidget(self.hemisphere_group)
		left_layout.addWidget(self.sphere_group)

		# Initially hide all parameter groups
		# self.ellipsoid_group.hide()
		self.hemisphere_group.hide()
		self.sphere_group.hide()

		# Connect the combo box signal to a slot
		self.shape_combo.currentIndexChanged.connect(self.update_shape_parameters)

		
		'''
		############################################
		#			       Bins                  #
		############################################
		'''
		bins_layout = QHBoxLayout()
		bins_label = QLabel("Bins:")
		self.bins_input = QLineEdit()
		self.bins_input.setText("20")
		# bins_layout.addWidget(bins_label)
		# bins_layout.addWidget(self.bins_input)
		# left_layout.addLayout(bins_layout)

		'''
		############################################
		#			 Distribution No.              #
		############################################
		'''
		distribute_num_layout = QHBoxLayout()
		distribute_num_label = QLabel("Distribute num:")
		self.distribute_num_input = QSpinBox()
		self.distribute_num_input.setValue(3)
		self.distribute_num_input.setStyleSheet(SpinBox_style)
		self.distribute_num_input.setMinimum(1)
		

		'''
		############################################
		#			 Simulate Button               #
		############################################
		'''
		self.simulate_button = QPushButton("Simulate")
		self.simulate_button.setFixedSize(80, 30)
		self.simulate_button.setStyleSheet(button_style)
		self.simulate_button.clicked.connect(self.simulate_pattern)

		'''
		############################################
		#			 Add Button to Left            #
		############################################
		'''
		distribute_num_layout.addWidget(distribute_num_label)
		distribute_num_layout.addWidget(self.distribute_num_input)
		distribute_num_layout.addWidget(bins_label)
		distribute_num_layout.addWidget(self.bins_input)
		distribute_num_layout.addWidget(self.simulate_button, alignment=Qt.AlignRight)
		
		left_layout.addLayout(distribute_num_layout)
		# Image placeholders
		image_layout = QHBoxLayout()
		self.image_placeholder1 = QLabel("Image 1")
		self.image_placeholder2 = QLabel("Image 2")
		image_layout.addWidget(self.image_placeholder1)
		image_layout.addWidget(self.image_placeholder2)
		left_layout.addLayout(image_layout)

		'''
		############################################
		############################################
		############################################
		#			   Right Layout                 #
		############################################
		############################################
		############################################
		'''
		self.right_layout_group = QGroupBox("Set Range")
		self.right_layout_group.setStyleSheet("""
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
		self.right_layout = QVBoxLayout()
		
		'''
		############################################
		#              Alpha Range                 #
		############################################
		'''
		alpha_layout = QHBoxLayout()
		alpha_checkbox = QCheckBox()
		alpha_checkbox.setFixedWidth(15)
		alpha_checkbox.setStyleSheet("QCheckBox { border: none; background-color: transparent; }")
		alpha_label = QLabel("α<sub>in</sub> (deg):")
		alpha_layout.addWidget(alpha_checkbox)
		alpha_layout.addWidget(alpha_label, alignment=Qt.AlignLeft)
		self.right_layout.addLayout(alpha_layout)
		self.right_layout_group.setLayout(self.right_layout)

		# Creating a QLabel or Input Box to Display Content
		self.input_layout = QHBoxLayout()
		self.alpha_input1 = QLineEdit()
		self.alpha_input1.setStyleSheet("QLineEdit { border: 1px solid black; }")

		self.alpha_input2 = QLineEdit()
		self.alpha_input2.setStyleSheet("QLineEdit { border: 1px solid black; }")
		self.input_layout.addWidget(self.alpha_input1)
		dash_line = QFrame()
		dash_line.setFrameShape(QFrame.HLine)
		dash_line.setFrameShadow(QFrame.Sunken)
		dash_line.setFixedWidth(20)
		dash_line.setLineWidth(1)
		dash_line.setStyleSheet("color: black; background-color: black;")
		self.input_layout.addWidget(dash_line)
		self.input_layout.addWidget(self.alpha_input2)
		self.input_layout_widget = QWidget()
		self.input_layout_widget.setLayout(self.input_layout)
		self.input_layout_widget.setStyleSheet("QWidget { border: none; background-color: None; }")
		self.input_layout_widget.setVisible(False)

		self.right_layout.addWidget(self.input_layout_widget)

		alpha_checkbox.stateChanged.connect(lambda state: self.input_layout_widget.setVisible(state == Qt.Checked))

		# Adding additional input fields for Lambda, Center_x, and Center_y

		'''
		############################################
		#             Lambda Range                 #
		############################################
		'''
		lambda_layout = QHBoxLayout()
		lambda_checkbox = QCheckBox()
		lambda_checkbox.setFixedWidth(15)
		lambda_checkbox.setStyleSheet("QCheckBox { border: none; background-color: transparent; }")
		lambda_label = QLabel("λ (nm):")
		lambda_layout.addWidget(lambda_checkbox)
		lambda_layout.addWidget(lambda_label, alignment=Qt.AlignLeft)
		self.right_layout.addLayout(lambda_layout)

		self.lambda_input_layout = QHBoxLayout()
		self.lambda_input1 = QLineEdit()
		self.lambda_input1.setStyleSheet("QLineEdit { border: 1px solid black; }")

		self.lambda_input2 = QLineEdit()
		self.lambda_input2.setStyleSheet("QLineEdit { border: 1px solid black; }")
		self.lambda_input_layout.addWidget(self.lambda_input1)
		lambda_dash_line = QFrame()
		lambda_dash_line.setFrameShape(QFrame.HLine)
		lambda_dash_line.setFrameShadow(QFrame.Sunken)
		lambda_dash_line.setFixedWidth(20)
		lambda_dash_line.setLineWidth(1)
		lambda_dash_line.setStyleSheet("color: black; background-color: black;")
		self.lambda_input_layout.addWidget(lambda_dash_line)
		self.lambda_input_layout.addWidget(self.lambda_input2)
		self.lambda_input_layout_widget = QWidget()
		self.lambda_input_layout_widget.setLayout(self.lambda_input_layout)
		self.lambda_input_layout_widget.setStyleSheet("QWidget { border: none; background-color: None; }")
		self.lambda_input_layout_widget.setVisible(False)

		self.right_layout.addWidget(self.lambda_input_layout_widget)

		lambda_checkbox.stateChanged.connect(lambda state: self.lambda_input_layout_widget.setVisible(state == Qt.Checked))

		'''
		############################################
		#            Center_x Range                #
		############################################
		'''
		center_x_layout = QHBoxLayout()
		center_x_checkbox = QCheckBox()
		center_x_checkbox.setFixedWidth(15)
		center_x_checkbox.setStyleSheet("QCheckBox { border: none; background-color: transparent; }")
		center_x_label = QLabel("Center X (mm):")
		center_x_layout.addWidget(center_x_checkbox)
		center_x_layout.addWidget(center_x_label, alignment=Qt.AlignLeft)
		self.right_layout.addLayout(center_x_layout)

		self.center_x_input_layout = QHBoxLayout()
		self.center_x_input1 = QLineEdit()
		self.center_x_input1.setStyleSheet("QLineEdit { border: 1px solid black; }")

		self.center_x_input2 = QLineEdit()
		self.center_x_input2.setStyleSheet("QLineEdit { border: 1px solid black; }")
		self.center_x_input_layout.addWidget(self.center_x_input1)
		center_x_dash_line = QFrame()
		center_x_dash_line.setFrameShape(QFrame.HLine)
		center_x_dash_line.setFrameShadow(QFrame.Sunken)
		center_x_dash_line.setFixedWidth(20)
		center_x_dash_line.setLineWidth(1)
		center_x_dash_line.setStyleSheet("color: black; background-color: black;")
		self.center_x_input_layout.addWidget(center_x_dash_line)
		self.center_x_input_layout.addWidget(self.center_x_input2)
		self.center_x_input_layout_widget = QWidget()
		self.center_x_input_layout_widget.setLayout(self.center_x_input_layout)
		self.center_x_input_layout_widget.setStyleSheet("QWidget { border: none; background-color: None; }")
		self.center_x_input_layout_widget.setVisible(False)

		self.right_layout.addWidget(self.center_x_input_layout_widget)

		center_x_checkbox.stateChanged.connect(lambda state: self.center_x_input_layout_widget.setVisible(state == Qt.Checked))

		'''
		############################################
		#            Center_y Range                #
		############################################
		'''
		center_y_layout = QHBoxLayout()
		center_y_checkbox = QCheckBox()
		center_y_checkbox.setFixedWidth(15)
		center_y_checkbox.setStyleSheet("QCheckBox { border: none; background-color: transparent; }")
		center_y_label = QLabel("Center Y (mm):")
		center_y_layout.addWidget(center_y_checkbox)
		center_y_layout.addWidget(center_y_label, alignment=Qt.AlignLeft)
		self.right_layout.addLayout(center_y_layout)

		self.center_y_input_layout = QHBoxLayout()
		self.center_y_input1 = QLineEdit()
		self.center_y_input1.setStyleSheet("QLineEdit { border: 1px solid black; }")

		self.center_y_input2 = QLineEdit()
		self.center_y_input2.setStyleSheet("QLineEdit { border: 1px solid black; }")
		self.center_y_input_layout.addWidget(self.center_y_input1)
		center_y_dash_line = QFrame()
		center_y_dash_line.setFrameShape(QFrame.HLine)
		center_y_dash_line.setFrameShadow(QFrame.Sunken)
		center_y_dash_line.setFixedWidth(20)
		center_y_dash_line.setLineWidth(1)
		center_y_dash_line.setStyleSheet("color: black; background-color: black;")
		self.center_y_input_layout.addWidget(center_y_dash_line)
		self.center_y_input_layout.addWidget(self.center_y_input2)
		self.center_y_input_layout_widget = QWidget()
		self.center_y_input_layout_widget.setLayout(self.center_y_input_layout)
		self.center_y_input_layout_widget.setStyleSheet("QWidget { border: none; background-color: None; }")
		self.center_y_input_layout_widget.setVisible(False)

		self.right_layout.addWidget(self.center_y_input_layout_widget)

		center_y_checkbox.stateChanged.connect(lambda state: self.center_y_input_layout_widget.setVisible(state == Qt.Checked))

		self.right_layout.addStretch()

		'''
		############################################
		#               Scroll Area                #
		############################################
		'''

		right_scroll_area = QScrollArea()
		right_scroll_area.setWidgetResizable(True)
		right_scroll_area.setWidget(self.right_layout_group)

		'''
		############################################
		############################################
		############################################
		#			   Main Layout                 #
		############################################
		############################################
		############################################
		'''

		main_layout.addLayout(left_layout)
		main_layout.addWidget(right_scroll_area)
		main_layout.addStretch()
		main_layout.setStretchFactor(left_layout, 5)
		main_layout.setStretchFactor(right_scroll_area, 1)
		self.setLayout(main_layout)


class PreprocessingSection(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		layout = QVBoxLayout()

		# Preprocessing options
		self.option1 = QCheckBox("Option 1")
		self.option2 = QCheckBox("Option 2")
		self.option3 = QCheckBox("Option 3")
		layout.addWidget(self.option1)
		layout.addWidget(self.option2)
		layout.addWidget(self.option3)

		# Image preview
		self.image_preview = QLabel("Image Preview")
		layout.addWidget(self.image_preview)

		self.setLayout(layout)

class TrainSetPage(QWidget):
	def __init__(self):
		super().__init__()
		self.shared_data = SharedData()
		self.initUI()

	def initUI(self):
		layout = QVBoxLayout()

		# Creating QSplitter for main layout
		main_splitter = QSplitter(Qt.Vertical)

		# Parameter section
		self.parameter_section = ParameterSection()
		main_splitter.addWidget(self.parameter_section)

		# Particle section
		self.particle_section = ParticleSection()
		main_splitter.addWidget(self.particle_section)

		# Preprocessing section
		self.preprocessing_section = PreprocessingSection()
		main_splitter.addWidget(self.preprocessing_section)

		# Set stretch factors to adjust size ratios
		main_splitter.setStretchFactor(0, 1)  # Parameter section
		main_splitter.setStretchFactor(1, 2)  # Particle section
		main_splitter.setStretchFactor(2, 1)  # Preprocessing section

		scroll_area = QScrollArea()
		scroll_area.setWidget(main_splitter)
		scroll_area.setWidgetResizable(True)
		scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

		layout.addWidget(scroll_area)
		self.setLayout(layout)

		threading.Thread(target=self.lazyLoadModules).start()
		
	def lazyLoadModules(self):
		# Delayed Loading Module
		self.shared_data.global_modules['form_factor_simu'] = importlib.import_module('tools.FormFactorSimu')
		while 'form_factor_simu' not in self.shared_data.global_modules:
			time.sleep(0.1)
		self.form_factor_simu = self.shared_data.global_modules['form_factor_simu']
