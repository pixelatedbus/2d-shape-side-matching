from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import time
from typing import List, Tuple

from .shape import SideProfile, Shape
import numpy as np
from .processing import ShapeProcessor

def weighted_levenshtein(sp1: SideProfile, sp2: SideProfile, ins_weight: float, del_weight: float) -> float:
    
    arr_dist1: np.ndarray = sp1
    arr_dist2: np.ndarray = sp2
    len1, len2 = len(arr_dist1), len(arr_dist2)

    dp = np.zeros((len1 + 1, len2 + 1))
    for i in range(len1 + 1):
        for j in range(len2 + 1):
            if i == 0:
                dp[i][j] = j * ins_weight
            elif j == 0:
                dp[i][j] = i * del_weight
            else:
                cost = abs(arr_dist1[i - 1] - arr_dist2[j - 1])
                dp[i][j] = min(
                    dp[i - 1][j] + del_weight,  # Deletion
                    dp[i][j - 1] + ins_weight,  # Insertion
                    dp[i - 1][j - 1] + cost      # Substitution
                )

    return dp[len1][len2]

def compare_shapes(shape1: Shape, shape2: Shape, ins_weight: float = 10.0, del_weight: float = 10.0, threshold: float = 200.0, compressed: bool = True) -> Tuple[float, SideProfile, SideProfile]:
    if not shape1.side_profiles or not shape2.side_profiles:
        raise ValueError("Both shapes must have side profiles to compare.")
    
    minimum_distance = float('inf')
    total_distance = 0.0
    total_compressed_distance = 0.0

    sp1 = shape1.get_all_side_profiles()
    sp2 = shape2.get_all_side_profiles()
    sp2 = [SideProfile(ShapeProcessor.invert_side_profile(profile.profile), angle=profile.angle) for profile in sp2]
    index_prof1, index_prof2 = 0, 0
    time_start = time.time()

    for i in range(len(sp1)):
        for j in range(len(sp2)):
            if compressed:
                compressed_sp1 = compress_side_profile(sp1[i])
                compressed_sp2 = compress_side_profile(sp2[j])
                quick_distance = weighted_levenshtein(compressed_sp1.profile, compressed_sp2.profile, ins_weight, del_weight)
                quick_distance2 = weighted_levenshtein(compressed_sp1.profile, compressed_sp2.profile[::-1], ins_weight, del_weight)
                total_compressed_distance += quick_distance
                if quick_distance >= threshold and quick_distance2 >= threshold:
                    continue
            
                # Calculate both distances first
                distance1 = weighted_levenshtein(sp1[i].profile, sp2[j].profile, ins_weight, del_weight)
                distance2 = weighted_levenshtein(sp1[i].profile, sp2[j].profile[::-1], ins_weight, del_weight)

                best_local_distance = min(distance1, distance2)

                if best_local_distance < minimum_distance:
                    minimum_distance = best_local_distance
                    index_prof1 = i
                    index_prof2 = j
            total_distance += best_local_distance

    time_end = time.time()
    return minimum_distance, sp1[index_prof1], sp2[index_prof2]

def compress_side_profile(side_profile: SideProfile, factor: int = 8) -> SideProfile:
    profile = side_profile.profile
    if len(profile) < factor:
        return side_profile 

    compressed_profile = []
    for i in range(0, len(profile), factor):
        chunk = profile[i:i + factor]
        if len(chunk) == factor:
            compressed_value = np.mean(chunk)
            compressed_profile.append(int(compressed_value))

    return SideProfile(np.array(compressed_profile, dtype=int), angle=side_profile.angle)

def find_best_matching_shape(shape: Shape, all_shapes: List[Shape], ins_weight: float = 10.0, del_weight: float = 10.0) -> List[Tuple[float, Shape, SideProfile, SideProfile]]:
    results = []
    
    for candidate_shape in all_shapes:
        if not candidate_shape.side_profiles:
            continue
        
        min_distance, best_sp1, best_sp2 = compare_shapes(shape, candidate_shape, ins_weight, del_weight)
        results.append((min_distance, candidate_shape, best_sp1, best_sp2))
    
    # Sort by distance
    results.sort(key=lambda x: x[0])
    
    return results

def _compare_task(args: Tuple) -> Tuple[float, Shape, SideProfile, SideProfile]:
    query_shape, candidate_shape, ins_weight, del_weight, threshold, use_compression = args
    score, sp1, sp2 = compare_shapes(query_shape, candidate_shape, ins_weight, del_weight, threshold, use_compression)
    return score, candidate_shape, sp1, sp2

def find_best_matching_shape_concurrent(query_shape: Shape, candidate_shapes: List[Shape], **kwargs) -> List[Tuple[float, Shape, SideProfile, SideProfile]]:
    start_time = time.time()
    print(f"\n--- Starting concurrent search against {len(candidate_shapes)} shapes ---")
    
    best_overall_score = float('inf')
    best_match_shape = None
    best_match_profiles = (None, None)

    tasks = []
    for candidate in candidate_shapes:
        if query_shape.id is not None and query_shape.id == candidate.id:
            continue
        task_args = (
            query_shape, candidate, 
            kwargs.get('ins_weight', 10.0), 
            kwargs.get('del_weight', 10.0),
            kwargs.get('threshold', 2500.0),
            kwargs.get('use_compression', True)
        )
        tasks.append(task_args)

    with ProcessPoolExecutor() as executor:
        future_to_task = {executor.submit(_compare_task, task): task for task in tasks}
        results = []

        for future in as_completed(future_to_task):
            try:
                result = future.result()
                results.append(result)
                score, shape, sp1, sp2 = result
                if score < best_overall_score:
                    best_overall_score = score
                    best_match_shape = shape
                    best_match_profiles = (sp1, sp2)
                    print(f"New best match found: {best_overall_score} with shape {shape.id}")
            except Exception as e:
                print(f"Error processing task: {e}")
    
    results.sort(key=lambda x: x[0])

    end_time = time.time()
    print(f"\n--- Full Search Complete ---")
    print(f"Total time taken: {end_time - start_time:.4f} seconds")

    return results