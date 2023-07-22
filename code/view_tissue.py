import sys
sys.path.append('/Users/bhargavdesai/Desktop/IU/RA/CNS/hra-amap/code')

import trimesh
import numpy as np
from organ import Organ
from tissue import TissueBlock

from utils.io import read_json

from copy import deepcopy
from scipy.spatial.transform import Rotation  

def build_transformation_matrix(rotation, translation):
    # find rotation matrix from angles
    rotation_matrix = Rotation.from_euler(seq='xyz', angles=rotation, degrees=True).as_matrix()

    # convert to 4x4 transformation matrix
    transform = np.empty((4, 4))
    transform[:3, :3] = rotation_matrix
    transform[:3, 3] = translation
    transform[3, :] = [0, 0, 0, 1]

    return transform

def transform(mesh, matrix, scaling=None):
    # apply scaling
    if scaling:
        mesh = mesh.apply_scale(scaling)

    # apply transformation
    mesh = mesh.apply_transform(matrix)

    return mesh

def get_orientation(target_mesh):
    T = target_mesh.bounding_box_oriented.primitive.transform 
    rotation = T[:3, :3]
    euler_angle = Rotation.from_matrix(rotation).as_euler('xyz', degrees=True)
    return euler_angle

# load a sample JSON LD
# this file is taken from https://github.com/hubmapconsortium/hra-rui-locations-processor/blob/3d37b718e8030de35ceddb8e77ccae9e8f416193/examples/all-features/rui_locations.jsonld#L79
jsonld = read_json(path='/Users/bhargavdesai/Desktop/IU/RA/CNS/rui_locations.jsonld')

# get donors
donors = jsonld['@graph']
print(f'Number of donors found: {len(donors)}')

# pick a donor and get number of samples
donor = donors[0]

# each sample has an associated tissue block, pick the first sample
sample = donor['samples'][0]

# create a spatial tissue block from the sample 
# this can now be used with the .project() method of any registered organ
block = TissueBlock(sample=sample)

# copy target organ
target = deepcopy(block.target)

# transformations to place the target at the origin
rotation = [0, 0, 0]
translation = [-0.04005157, -0.175776139, 0.139386386] 
# Brain [0.0682786554, -0.7565191, 0.0846749842]
# Kidney [-0.04005157, -0.175776139, 0.139386386]
# Liver [0.133268759, -0.279973656, 0.089579314]
transformation_matrix = build_transformation_matrix(rotation, translation)
target = transform(mesh=target, matrix=transformation_matrix)

# create sample tissue block and reference axes
box = trimesh.creation.box(extents=block.size, origin=[0, 0, 0])
axes = trimesh.creation.axis()

# transform box
block_transformation_matrix = build_transformation_matrix(rotation=block.rotation, translation=block.translation)
box = transform(mesh=box, matrix=block_transformation_matrix)

# add colors for visualization
target.visual.face_colors[:] = np.array([255, 182, 193, 50])
block.visual.face_colors[:] = np.array([255, 215, 0, 255])
axes.visual.face_colors[:] = np.array([255, 255, 204, 50])


# show
trimesh.scene.Scene(geometry=[target, target.bounding_box.as_outline(), axes, box]).show()








