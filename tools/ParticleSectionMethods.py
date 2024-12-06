import numpy as np
from PyQt5.QtCore import Qt
import time
import tqdm
from tools.shared_data import SharedData



def update_display(self, state):
	if state == Qt.Checked:
		self.display_label.setVisible(False)
		self.input_layout_widget.setVisible(True)
	else:
		self.display_label.setVisible(True)
		self.input_layout_widget.setVisible(False)
		
def update_shape_parameters(self, index):
	self.ellipsoid_group.hide()
	self.hemisphere_group.hide()
	self.sphere_group.hide()
	
	if index == 0:  # Ellipsoid
		self.ellipsoid_group.show()
	elif index == 1:  # Hemisphere
		self.hemisphere_group.show()
	elif index == 2:  # Sphere
		self.sphere_group.show()

def simulate_pattern(self):

	self.shared_data = SharedData()
	while 'form_factor_simu' not in self.shared_data.global_modules:
		time.sleep(0.1)
	form_factor_simu = self.shared_data.global_modules['form_factor_simu']

	size = self.shared_data.data['bins_input']

	R_bins = np.linspace(0.05, 20, size + 1)
	h_bins = np.linspace(0.05, 20, size + 1)
	hr_data_dict = {}
	for i in tqdm(range(size)):
		for j in range(size):
			R = (R_bins[i] + R_bins[i+1]) / 2
			h = (h_bins[j] + h_bins[j+1]) / 2
			sample = get_sample(R,h)
			simulation = get_simulation(sample)
			result = simulation.simulate()
			hr_data_dict[(i,j)] = result.array()

def Particle_update_shared_data(self):
	def safe_float_conversion(line_edit, default=0.0):
		text = line_edit.text()
		return float(text) if text else default

	def safe_int_conversion(line_edit, default=0):
		text = line_edit.text()
		return int(text) if text else default

	def safe_spinbox_value(spinbox, default=0):
		return spinbox.value() if spinbox.value() is not None else default

	self.shared_data.data['hemisphere_h1'] = safe_float_conversion(self.hemisphere_h1)
	self.shared_data.data['hemisphere_r2'] = safe_float_conversion(self.hemisphere_r2)
	self.shared_data.data['hemisphere_r1'] = safe_float_conversion(self.hemisphere_r1)
	self.shared_data.data['hemisphere_h2'] = safe_float_conversion(self.hemisphere_h2)

	self.shared_data.data['ellipsoid_h1'] = safe_float_conversion(self.ellipsoid_h1)
	self.shared_data.data['ellipsoid_r1'] = safe_float_conversion(self.ellipsoid_r1)
	self.shared_data.data['ellipsoid_h2'] = safe_float_conversion(self.ellipsoid_h2)
	self.shared_data.data['ellipsoid_r2'] = safe_float_conversion(self.ellipsoid_r2)

	self.shared_data.data['sphere_r1'] = safe_float_conversion(self.sphere_r1)
	self.shared_data.data['sphere_r2'] = safe_float_conversion(self.sphere_r2)

	self.shared_data.data['bins_input'] = safe_int_conversion(self.bins_input)
	self.shared_data.data['distribute_num_input'] = safe_int_conversion(self.distribute_num_input)

	self.shared_data.data['lambda_input1'] = safe_float_conversion(self.lambda_input1)
	self.shared_data.data['lambda_input2'] = safe_float_conversion(self.lambda_input2)
	self.shared_data.data['center_x_input1'] = safe_float_conversion(self.center_x_input1)
	self.shared_data.data['center_x_input2'] = safe_float_conversion(self.center_x_input2)
	self.shared_data.data['center_y_input1'] = safe_float_conversion(self.center_y_input1)
	self.shared_data.data['center_y_input2'] = safe_float_conversion(self.center_y_input2)
	self.shared_data.data['alpha_input1'] = safe_float_conversion(self.alpha_input1)
	self.shared_data.data['alpha_input2'] = safe_float_conversion(self.alpha_input2)
	# pass
