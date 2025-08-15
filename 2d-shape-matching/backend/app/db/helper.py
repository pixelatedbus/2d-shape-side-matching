from sqlalchemy.orm import Session
from typing import List, Dict, Any
import numpy as np
import json
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from .models import Image, Base
from ..core.shape import Shape, SideProfile

def _db_image_to_shape(db_image: Image) -> Shape | None:
    """
    Converts a database Image object into an application-level Shape object.
    """
    if not db_image:
        return None
    
    side_profiles = []
    if db_image.extracted_features:
        # The features are stored as a JSON string/dict, so we parse them
        features_data = db_image.extracted_features
        if isinstance(features_data, str):
            features_data = json.loads(features_data)
        
        for feature in features_data:
            profile_array = np.array(feature["profile"], dtype=int)
            side_profiles.append(SideProfile(profile=profile_array, angle=feature["angle"]))
            
    return Shape(id=db_image.id, side_profiles=side_profiles)

def get_image_by_id(db: Session, image_id: int) -> Shape | None:
    """
    Fetches a single image from the database and returns it as a Shape object.
    """
    db_image = db.query(Image).filter(Image.id == image_id).first()
    return _db_image_to_shape(db_image)

def get_raw_image_by_id(db: Session, image_id: int) -> Image | None:
    """
    Fetches a single raw Image object from the database by its ID.
    """
    return db.query(Image).filter(Image.id == image_id).first()

def get_image_by_name(db: Session, image_name: str) -> Shape | None:
    """
    Fetches a single image from the database by its filename and returns it as a Shape object.
    """
    db_image = db.query(Image).filter(Image.img_name == image_name).first()
    return _db_image_to_shape(db_image)

def get_all_images(db: Session) -> List[Shape]:
    """
    Fetches all images from the database and returns them as a list of Shape objects.
    """
    db_images = db.query(Image).all()
    return [_db_image_to_shape(db_img) for db_img in db_images if db_img]

def create_image_metadata(db: Session, img_name: str, img_src: str) -> Image:
    """
    Creates a new image record in the database with basic metadata.
    """
    new_image = Image(img_name=img_name, img_src=img_src)
    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    return new_image

def cache_image_features(db: Session, image_id: int, features: List[Dict[str, Any]]) -> Image | None:
    """
    Updates an existing image record to add its cached features.
    """
    db_image = db.query(Image).filter(Image.id == image_id).first()
    if db_image:
        db_image.extracted_features = features
        db.commit()
        db.refresh(db_image)
        return db_image
    return None

def clear_all_data(db: Session):
    """
    Deletes all records from the images table. For testing purposes.
    """
    try:
        num_rows_deleted = db.query(Image).delete()
        db.commit()
        print(f"Successfully deleted {num_rows_deleted} rows from the images table.")
    except Exception as e:
        print(f"An error occurred while clearing data: {e}")
        db.rollback()
if __name__ == "__main__":
    # This block demonstrates how to correctly use the clear_all_data function for testing.
    # It sets up a temporary engine and session.
    print("--- Running Test: Clearing Database ---")
    
    # Load environment variables to get the database URL
    # Assumes this script is in backend/app/db
    env_path = Path(__file__).resolve().parents[2] / '.env'
    load_dotenv(dotenv_path=env_path)
    DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        print("DATABASE_URL not found. Cannot run test.")
    else:
        # Create a temporary engine and session factory
        engine = create_engine(DATABASE_URL)
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create a session
        db_session = TestingSessionLocal()
        
        # Call the function with the correctly bound session
        clear_all_data(db=db_session)
        
        # Close the session
        db_session.close()
    
    print("--- Test Complete ---")