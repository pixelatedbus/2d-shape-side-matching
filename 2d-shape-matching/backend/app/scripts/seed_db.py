import os
import json
import numpy as np
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from ..db.models import Base, Image
from ..core.processing import generate_side_profiles, SideProfile

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / '.env')

project_root = Path(__file__).resolve().parents[2] 
IMAGE_DIRECTORY = project_root / "images" / "kite" 
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found")

# --- Database Setup ---
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_database():

    db = SessionLocal()
    print("--- Starting Database Seeding ---")
    print(f"Connecting to database...")

    # Ensure the 'images' table exists
    Base.metadata.create_all(bind=engine)

    try:
        # --- Stage 1: Seed basic image metadata ---
        print(f"\n--- Stage 1: Checking for new images in {IMAGE_DIRECTORY} ---")
        image_files = list(IMAGE_DIRECTORY.glob('*.png')) + \
                      list(IMAGE_DIRECTORY.glob('*.jpg')) + \
                      list(IMAGE_DIRECTORY.glob('*.jpeg'))

        if not image_files:
            print(f"No images found in {IMAGE_DIRECTORY}. Aborting.")
            return

        for image_path in image_files:
            exists = db.query(Image).filter(Image.img_name == image_path.name).first()
            if not exists:
                new_image = Image(
                    img_name=image_path.name,
                    img_src=str(image_path.relative_to(project_root)) 
                )
                db.add(new_image)
                print(f"Adding metadata for {image_path.name} to the database.")
        
        db.commit()
        print("Metadata seeding complete.")

        all_images_in_db = db.query(Image).all()
        for db_image in all_images_in_db:
            if db_image.extracted_features is not None:
                print(f"Features for {db_image.img_name} already cached. Skipping.")
                continue
            
            print(f"Processing {db_image.img_name} to generate features...")
            full_image_path = str(project_root / db_image.img_src)
            
            side_profiles_objects: list[SideProfile] = generate_side_profiles(full_image_path)
            
            features_to_cache = []
            for sp in side_profiles_objects:
                features_to_cache.append({
                    "angle": sp.angle,
                    "profile": sp.profile.tolist()
                })
            
            db_image.extracted_features = features_to_cache
            print(f"Successfully generated and caching features for {db_image.img_name}.")

        db.commit()
        print("Feature caching complete.")

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        db.rollback()
    finally:
        print(f"\nTotal images in database: {db.query(Image).count()}")
        db.close()
        print("Database session closed.")

if __name__ == "__main__":
    seed_database()