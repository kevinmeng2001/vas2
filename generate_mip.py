from skimage import io
import numpy as np
import napari
import matplotlib.pyplot as plt
import sys
from skimage.util import random_noise

def normalize_image(matrix):
    norm = np.linalg.norm(matrix)
    matrix = matrix/norm  # normalized matrix
    return matrix

def add_noise(image, type):
    if type == 'speckle':
        # print(image)
        normalize_image(image)
        mean = 0
        var = 0.05
        noisy=random_noise(image, mode=type, mean=mean, var=var)
        return noisy
    
    return "Noise type is not an acceptable format"

data_path = sys.argv[0]
DEBUG = sys.argv[1]
demand_vectors = sys.argv[2]
demand_values = sys.argv[3]
tree_number = sys.argv[4]

print('Generating MIP Image...')
dir = data_path.split()[0] + '/original_image/*.jpg'
im_collection = io.imread_collection(dir)
im_3d = im_collection.concatenate()

im_max = np.max(im_3d, axis=0)
# This is just to match the orientation in 3D Slicer when loading the image slices
im_max = np.flip(im_max, 0)
plt.imsave('mip_' + str(tree_number) + '.png', im_max, cmap='gray')

noisy_im = add_noise(im_max, 'speckle')
plt.imsave('mip_noisy_' + str(tree_number) + '.png', noisy_im, cmap='gray')

print('Generating Oxygen Demand Ground Truth..')
# Convert the string to a list of integers for the oxygen demand coordinates
coordinates = demand_vectors.split()
regions = []
for val in coordinates:
    try:
        regions.append(int(val))
    except:
        pass

# Convert the string to a list of integers for the oxygen demand values
demands = demand_values.split()
values = []
for val in demands:
    try:
        values.append(float(val))
    except:
        pass

# Create a 3D Numpy array that represents the oxygen demand map of the tree
# Every 6 iterations in the regions list results in 1 iteration in the values list (Following VascuSynth file convention)
oxygen_demand_cube= np.ones((int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7])))
# Create sphere
def sphere_idx(shape, radius, position):
    assert len(position) == len(shape)
    n = len(shape)
    position = np.array(position).reshape((-1,) + (1,) * n)
    arr = np.linalg.norm(np.indices(shape) - position, axis=0)
    return (arr > radius).astype('int64') # + value (for gradient)
for idx, value in enumerate(values):
    region = regions[idx*6:idx*6 + 6]
    print('region: ', region)
    radius = int((region[3] - region[0])//2)

    x0, y0, z0 = region[0] + radius, region[1] + radius,  region[2] + radius

    if value != 1:
        arr_temp = sphere_idx((int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7])), radius, (x0, y0, z0))
        oxygen_demand_cube = np.where(arr_temp < 1, arr_temp, oxygen_demand_cube)



min = np.min(oxygen_demand_cube, axis=2)

# This is just to match the orientation in 3D slicer when loading the image slices
min = np.rot90(min,1)
plt.imsave('oxMap_' + str(tree_number) + '.png', min, cmap='gray', vmin=0, vmax=1)
print('All done MIP Script!')
# print('Generating 3D Oxygen Demand Cube...')
# first = datetime.now()
# data = oxygen_demand_cube
# fig = plt.figure()
# ax = fig.add_subplot(projection='3d')
# cmap = plt.get_cmap('binary')
# norm = plt.Normalize(data.min(), data.max())
# ax.voxels(data, facecolors=cmap(norm(data)), alpha=0.3)
# plt.savefig('oxDemandCube.png')
# second = datetime.now()
# print('Time to generate 3D Oxygen Demand Cube: ', (second-first).total_seconds())

# viewer = napari.view_image(oxygen_demand_cube, name = 'oxMap', rendering='minip')
# viewer.dims.ndisplay = 3
# viewer.camera.zoom = 2
# viewer.axes.visible = True
# napari.run()

if DEBUG == 'True':
    print('Intializing 3D rendering w/ napari...')
    # viewer = napari.Viewer()
    viewer = napari.view_image(im_3d, name = 'tree')
    viewer.dims.ndisplay = 3
    viewer.camera.zoom = 2
    viewer.axes.visible = True
    napari.run()