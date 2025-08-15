import time
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.db import helper as db_helper
from app.core.processing import generate_side_profiles
from app.core.compare import find_best_matching_shape_concurrent
from app.core.shape import Shape
from app.schemas import SearchResponse, SearchResultItem

router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
IMAGES_DIR = PROJECT_ROOT / "images"

TEMP_UPLOAD_DIR = Path("temp_uploads")
TEMP_UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/search", response_model=SearchResponse)
async def search_for_match(
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    threshold: float = Form(...)
):
    """
    This is the main endpoint for the application. It accepts an image,
    processes it, compares it against the database, and returns the best matches.
    """
    start_time = time.time()

    # 1. Save the uploaded file temporarily to get a file path
    try:
        temp_file_path = TEMP_UPLOAD_DIR / file.filename
        with temp_file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    try:
        print(f"Processing query image: {file.filename}")
        query_side_profiles = generate_side_profiles(str(temp_file_path))
        query_shape = Shape(side_profiles=query_side_profiles, id=-1)

        print("Fetching candidate shapes from the database...")
        candidate_shapes = db_helper.get_all_images(db)
        if not candidate_shapes:
            raise HTTPException(status_code=404, detail="No shapes found in the database to compare against.")

        results = find_best_matching_shape_concurrent(query_shape, candidate_shapes)
        
        filtered_results = [res for res in results if res[0] <= threshold]

        formatted_results = []
        for score, shape_obj, _, _ in filtered_results:
            db_image = db_helper.get_raw_image_by_id(db, shape_obj.id)
            if db_image:
                formatted_results.append(
                    SearchResultItem(
                        img_name=db_image.img_name,
                        img_src=db_image.img_src,
                        score=score,
                    )
                )

        end_time = time.time()
        
        return SearchResponse(
            search_time=end_time - start_time,
            results=formatted_results
        )

    finally:
        # 7. Clean up the temporary file
        if temp_file_path.exists():
            temp_file_path.unlink()
