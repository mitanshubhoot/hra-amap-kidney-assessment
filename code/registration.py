# import subprocess

# import numpy as np
# import open3d as o3d

# from dataclass import PipelineStepOutput, Projection
# from utils.transforms import txt_to_numpy, txt_to_pandas, numpy_to_pointcloud
# from utils.preprocess import normalize, normalize_bcpd

# def global_registration(source_pointcloud, target_pointcloud, params):
#     distance_threshold = params['voxel_size'] * params['global_distance_threshold_factor']
#     # normalize
#     normalized_source_pointcloud, source_normalization_params = normalize(source_pointcloud, return_params=True)
#     normalized_target_pointcloud, target_normalization_params = normalize(target_pointcloud, return_params=True)

#     # downsample
#     normalized_source_downsampled_pointcloud = normalized_source_pointcloud.voxel_down_sample(params['voxel_size'])
#     normalized_target_downsampled_pointcloud = normalized_target_pointcloud.voxel_down_sample(params['voxel_size'])

#     # compute features
#     source_fpfh_features = compute_features(normalized_source_downsampled_pointcloud, params)
#     target_fpfh_features = compute_features(normalized_target_downsampled_pointcloud, params)

#     # register
#     result = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(normalized_source_downsampled_pointcloud, 
#                                                                                       normalized_target_downsampled_pointcloud, 
#                                                                                       source_fpfh_features,
#                                                                                       target_fpfh_features, 
#                                                                                       True, 
#                                                                                       distance_threshold,
#                                                                                       o3d.pipelines.registration.TransformationEstimationPointToPoint(False), 
#                                                                                       3,
#                                                                                       [o3d.pipelines.registration.CorrespondenceCheckerBasedOnEdgeLength(params['global_edge_length_threshold_factor']), 
#                                                                                        o3d.pipelines.registration.CorrespondenceCheckerBasedOnDistance(distance_threshold)], 
#                                                                                       o3d.pipelines.registration.RANSACConvergenceCriteria(params['global_max_iterations'], params['global_max_correspondence']))
#     # return
#     return PipelineStepOutput(stage='Global', 
#                               input={'Source': source_pointcloud, 
#                                      'Target': target_pointcloud}, 
#                               output={'Source': normalized_source_pointcloud,
#                                       'Target': normalized_target_pointcloud},
#                               transform=result.transformation, 
#                               normalization={'Source': source_normalization_params, 
#                                              'Target': target_normalization_params})

# def refine_registration(source, target, params, global_registration_result):
#     distance_threshold = params['voxel_size'] * params['refine_distance_threshold_factor']
#     result = o3d.pipelines.registration.registration_icp(source.pointcloud, 
#                                                          target.pointcloud, 
#                                                          distance_threshold, 
#                                                          global_registration_result.transform, 
#                                                          o3d.pipelines.registration.TransformationEstimationPointToPlane())
#     return RegistrationResult(type='Refined', 
#                               transform=result.transformation)


# def rigid_registration(source, target, params):
#     # first we do a quick global registration using RANSAC
#     global_registration = global_registration(source, target, params)

#     # then we refine the registration using ICP Point to Plane
#     rigid_registration = refine_registration(source, target, params, global_registration.transform)

#     # apply transform
#     source.transformed_rigid = source.pointcloud.transform(source.refine_registration)
    
#     return source


# def nonrigid_registration(source, target, params):
#     # save the source and target point clouds 
#     np.savetxt(f"../../{source.file_name}.txt", np.array(source.transformed_rigid.points), delimiter=',')
#     np.savetxt(f"../../{target.file_name}.txt", np.array(target.pointcloud.points), delimiter=',')

#     # run BCPD
#     result = subprocess.run(['./bcpd', 
#                              '-x', f"../{target.file_name}.txt", 
#                              '-y', f"../{source.file_name}.txt", 
#                              '-J', '300', '-K', '70', '-p', '-c', str(params['distance_threshold']), '-r', str(params['seed']), '-n', str(params['max_iterations']), '-l', str(params['lambda']), '-b', str(params['beta']),
#                              '-s', 'A'], 
#                              cwd="../../bcpd",
#                              capture_output=True)
    
#     # record transformations
#     source.dvf = np.genfromtxt('../../bcpd/output_u.txt') - normalize_bcpd(source.pointcloud)
#     source.translation_nonrigid = txt_to_numpy('../../bcpd/output_t.txt')
#     source.scale_nonrigid = txt_to_numpy('../../bcpd/output_s.txt')
#     source.rotation_nonrigid = txt_to_numpy('../../bcpd/output_r.txt')

#     # record correspondences
#     source.correspondence = txt_to_pandas('../../bcpd/output_e.txt')
    
#     # record transform
#     source.transformed_nonrigid = numpy_to_pointcloud(txt_to_numpy('../../bcpd/output_y.txt'))

#     return source