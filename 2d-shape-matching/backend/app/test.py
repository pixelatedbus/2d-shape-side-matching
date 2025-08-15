from .core.processing import generate_side_profiles
from .core.shape import Shape
from .core.compare import find_best_matching_shape, find_best_matching_shape_concurrent, compare_shapes
from .db.helper import get_all_images, get_raw_image_by_id
from .db.session import SessionLocal # Import SessionLocal, NOT get_db
from time import time

def test_full_pipeline():
    """
    A simple integration test to generate profiles and fetch from the database.
    """
    print("--- Running Test: Generating Side Profiles ---")
    try:
        # Make sure the image path is correct relative to the project root
        img_path = str("../images/puzzle5.png")
        img_path2 = str("../images/puzzle6.png")
        side_profiles = generate_side_profiles(img_path, rotation_step=30)
        side_profiles2 = generate_side_profiles(img_path2, rotation_step=30)

        print(f"Successfully generated {len(side_profiles)} side profiles.")
        for i, profile in enumerate(side_profiles[:10]): # Print first 3 for brevity
            print(f"  Profile {i} (Angle {profile.angle}): {profile.profile[:10]}...")
        
        shape = Shape(side_profiles)
        shape2 = Shape(side_profiles2)
        print(f"Created Shape object: {shape}")

    except Exception as e:
        print(f"An error occurred during profile generation: {e}")
        return

    print("\n--- Running Test: Fetching from Database ---")
    # --- Correct Database Session Handling ---
    # 1. Create a session instance directly from the factory
    db_session = SessionLocal()
    try:
        start_time = time()
        # 2. Pass the actual session object to your helper function
        all_shapes_from_db = get_all_images(db_session)
        # find the best match for the generated shape

        best_matches = find_best_matching_shape_concurrent(shape, all_shapes_from_db, ins_weight=10.0, del_weight=10.0)
        print(f"Found {len(best_matches)} best matches.")
        for match in best_matches[:3]:  # Print first 3 matches for brevity
            print(f"  Match: {match[1].id}, Distance: {match[0]:.2f}, Profiles: {match[2].angle} vs {match[3].angle}")
            sus = get_raw_image_by_id(db_session, match[1].id)
            print(f"  Raw image source: {sus.img_src}")
        end_time = time()
        
        print(f"Time taken: {end_time - start_time:.4f} seconds.")
        # compare shape 1 shape 2
        shape_comparison = compare_shapes(shape, shape2)
        print(f"Shape comparison result: {shape_comparison[0]}")

    except Exception as e:
        print(f"An error occurred during database fetch: {e}")
    finally:
        # 3. Always close the session when you are done
        print("Closing database session.")
        db_session.close()

if __name__ == "__main__":
    test_full_pipeline()