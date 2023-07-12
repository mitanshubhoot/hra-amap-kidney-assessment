import numpy as np
import open3d as o3d

from utils.conversions import pointcloud_to_numpy, numpy_to_pointcloud

def scale(pointcloud, kind='unit'):
    if kind == 'unit':
        return np.max(pointcloud.get_max_bound() - pointcloud.get_min_bound())
    elif kind == 'stddev':
        array = pointcloud_to_numpy(pointcloud)
        return np.sqrt(np.sum(np.square(array - mean)) / (array.shape[0] * array.shape[1]))
    else:
        raise ValueError("kind parameter should be one of unit or stddev")    

# def denormalize_icp(normalized_pointcloud, params):
#     # get scale
#     scale = params['scale']
#     # calculate center
#     center = params['center']
#     # denormalize
#     pointcloud = normalized_pointcloud.scale((1 / scale), center=center)
#     return pointcloud

def mean(pointcloud):
    array = pointcloud_to_numpy(pointcloud)
    mean = np.mean(array, axis=0)
    return mean

def scale_for_bcpd(array, mean):
    scale = np.sqrt(np.sum(np.square(array - mean)) / (array.shape[0] * array.shape[1]))
    return scale

# def normalize_bcpd(pointcloud, scale=None, mean=None, return_params=False):
#     array = pointcloud_to_numpy(pointcloud)
#     # calculate mean
#     if not isinstance(mean, np.ndarray):
#         mean = mean_bcpd(array)

#     # calculate scale
#     if not isinstance(scale, float):
#         scale = scale_bcpd(array, mean)

#     # normalize and return
#     array -= mean
#     array /= scale

#     # convert back to pointcloud
#     normalized_pointcloud = numpy_to_pointcloud(array)

#     if return_params:
#         return (normalized_pointcloud, 
#                 {'scale': scale, 'mean': mean})
#     else:
#         normalized_pointcloud

# def denormalize_bcpd(pointcloud, mean=None, scale=None):
#     array = pointcloud_to_numpy(pointcloud)
#     # calculate mean
#     if not isinstance(mean, np.ndarray):
#         mean = mean_bcpd(pointcloud)

#     # calculate scale
#     if not isinstance(scale, float):
#         scale = scale_bcpd(pointcloud, mean)

#     # de-normalize
#     array *= scale
#     array += mean

#     # convert back to pointcloud
#     denormalized_pointcloud = numpy_to_pointcloud(array)
#     return denormalized_pointcloud

def compute_features(pointcloud, params):
        # estimate normals
        radius_normal = params['voxel_size'] * 2
        pointcloud.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, 
                                                                         max_nn=params['max_nn']))

        # compute features
        radius_feature = params['voxel_size'] * 5
        fpfh_features = o3d.pipelines.registration.compute_fpfh_feature(pointcloud, 
                                                                        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_feature, 
                                                                                                             max_nn=params['max_nn']))

        return fpfh_features