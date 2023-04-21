import numpy as np

def normalize(pcd):
    return pcd.scale(1 / np.max(pcd.get_max_bound() - pcd.get_min_bound()), center=pcd.get_center())

def mean_bcpd(source_cloud):
    source_array = np.array(source_cloud.points)
    mean = np.mean(source_array, axis=0)
    return mean

def scale_bcpd(source_cloud, mean):
    source_array = np.array(source_cloud.points)
    scale = np.sqrt(np.sum(np.square(source_array - mean)) / (source_array.shape[0] * source_array.shape[1]))
    return scale

def normalize_bcpd(source_cloud, mean, scale):
    source_array = np.array(source_cloud.points)
    source_array -= mean
    source_array /= scale
    return source_array

def denormalize_bcpd(source_array, mean, scale):
    source_array = np.array(source_array)
    source_array *= scale
    source_array += mean
    return source_array