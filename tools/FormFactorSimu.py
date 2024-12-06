import numpy as np
import bornagain as ba
from bornagain import deg, nm
import matplotlib.pyplot as plt
from tqdm import tqdm
import tensorflow as tf

def generate_gaussian_matrix(size=20 , mu1_min=0, mu1_max=1, mu2_min=0, mu2_max=1, 
                             sigma1_min=0.01, sigma1_max=0.5, sigma2_min=0.01, sigma2_max=0.5, covariance_min=0, covariance_max=1):
    x = np.linspace(0, 1, size)
    y = np.linspace(0, 1, size)
    x, y = np.meshgrid(x, y)
    
    # Flatten the coordinates
    pos = np.empty(x.shape + (2,))
    pos[:, :, 0] = x
    pos[:, :, 1] = y
    
    # Randomly generated parameters
    mu1 = np.random.uniform(mu1_min, mu1_max)
    mu2 = np.random.uniform(mu2_min, mu2_max)
    sigma1 = np.random.uniform(sigma1_min, sigma1_max)
    sigma2 = np.random.uniform(sigma2_min, sigma2_max)
    covariance = np.random.uniform(covariance_min, covariance_max)

    # mu1, mu2 = np.random.uniform(0, 1, 2)
    # sigma1, sigma2 = np.random.uniform(0.01, 0.5, 2)
    # covariance = np.random.uniform(0, 1)
    
    # covariance matrix
    cov_matrix = np.array([[sigma1**2, covariance * sigma1 * sigma2],
                           [covariance * sigma1 * sigma2, sigma2**2]])
    
    mu = np.array([mu1, mu2])
    
    # Generate a 2D Gaussian distribution
    rv = np.random.multivariate_normal(mu, cov_matrix, (size, size))
    g = np.exp(-0.5 * np.einsum('...k,kl,...l->...', pos - mu, np.linalg.inv(cov_matrix), pos - mu))
    
    return g / g.sum()

def get_sample(R,h):
    # Define materials
    materials = get_materials()
    material_Particle = ba.RefractiveMaterial("Particle", materials["gold"][0], materials["gold"][1])
    material_Substrate = ba.RefractiveMaterial("Substrate", materials["silicon"][0], materials["silicon"][1])
    material_Vacuum = ba.RefractiveMaterial("Vacuum", 0.0, 0.0)

    # Define form factors
    ff = ba.HemiEllipsoid(R*nm, R*nm, h*nm)

    # Define particles
    particle = ba.Particle(material_Particle, ff)

    # Define particle layouts
    layout = ba.ParticleLayout()
    layout.addParticle(particle, 1.0)
    layout.setTotalParticleSurfaceDensity(0.01)
    
    # Define roughness
    roughness = ba.LayerRoughness(3, 0.3, 5*nm)

    # Define layers
    layer_1 = ba.Layer(material_Vacuum)
    layer_1.addLayout(layout)
    layer_2 = ba.Layer(material_Substrate)

    # Define sample
    sample = ba.MultiLayer()
    sample.addLayer(layer_1)
    sample.addLayerWithTopRoughness(layer_2, roughness)

    return sample


def get_simulation(sample,incident_angle = 0.395, wavelength = 0.09472):
    # Define GISAS simulation:
    beam = ba.Beam(100000000.0, wavelength * nm, incident_angle * deg)

    detector = ba.RectangularDetector(128, 172.0, 128, 172.0)
    detector.setPerpendicularToDirectBeam(3000.0, 86.0, 10.0)
    simulation = ba.ScatteringSimulation(beam, sample, detector)
    return simulation

# generate a dictionary of materials's delta and beta, key is the material name
# for gold (E = 13091.00): delta = 1.7065e-05, beta = 2.0640e-6
# for silicon (E = 13091.00): delta = 2.8402e-06, beta = 2.5265e-08
def get_materials():
    materials = {}
    materials["gold"] = (1.7065e-05, 2.0640e-6)
    materials["silicon"] = (2.8402e-06, 2.5265e-08)
    return materials

def generate_data(hr_data_dict, num_sets, dist_gaussians = 4, size = 20 ,s1_min=0.01, s1_max=0.5, s2_min=0.01, s2_max=0.5):
    final_data_list = []
    gaussian_matrices_hR_list = []

    for n in tqdm(range(num_sets)):
        random_weights_hR = np.random.dirichlet(alpha=[1] * dist_gaussians, size=1)[0]

        gaussian_matrices_hR_1 = generate_gaussian_matrix(size, sigma1_min = s1_min, sigma1_max=s1_max, sigma2_min=s2_min, sigma2_max=s2_max) * random_weights_hR[dist_gaussians-1]
        gaussian_matrices_hR = sum(generate_gaussian_matrix(size,sigma1_min=0.01, sigma1_max=0.5, sigma2_min=0.01, sigma2_max=0.5) * random_weights_hR[i] for i in range(dist_gaussians-1)) + gaussian_matrices_hR_1

        # 归一化
        gaussian_matrices_hR /= gaussian_matrices_hR.sum()

        # 假设 hr_data_dict 已经预先计算并存储好
        final_data = np.zeros((128, 128))

        for i in range(size):
            for j in range(size):
                # Get hr_data from pre-calculated hr_data_dict
                hr_data = hr_data_dict[(i, j)]
                final_data += hr_data * gaussian_matrices_hR[i, j]

        # Storing results
        final_data_list.append(final_data)
        gaussian_matrices_hR_list.append(gaussian_matrices_hR)

    return np.array(final_data_list), np.array(gaussian_matrices_hR_list)


def serialize_example(input_data, output_data):
    feature = {
        'input': tf.train.Feature(float_list=tf.train.FloatList(value=input_data)),
        'output': tf.train.Feature(float_list=tf.train.FloatList(value=output_data))
    }
    example_proto = tf.train.Example(features=tf.train.Features(feature=feature))
    return example_proto.SerializeToString()

def write_tfrecord(input_data, output_data, filename):
    print(f"Writing {filename}")
    with tf.io.TFRecordWriter(filename) as writer:
        for inp, out in tqdm(zip(input_data, output_data), total=len(input_data), desc=f"Writing {filename}"):
            example = serialize_example(inp.flatten(), out.flatten())
            writer.write(example)