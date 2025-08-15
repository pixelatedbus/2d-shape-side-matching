import numpy as np
from .shape import SideProfile
import cv2 

class ImageProcessor:

    @staticmethod
    def load_image(image_path: str) -> np.ndarray:
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Image not found at {image_path}")
        return image
    
    @staticmethod
    def rotate_image(image: np.ndarray, angle: float, center: tuple = None) -> np.ndarray:
        if center is None:
            center = (image.shape[1] // 2, image.shape[0] // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated_image = cv2.warpAffine(image, rotation_matrix, (image.shape[1], image.shape[0]), flags=cv2.INTER_NEAREST)
        return rotated_image
    
    @staticmethod
    def create_mask(image: np.ndarray) -> np.ndarray:
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        return mask
    
class ShapeProcessor:
    @staticmethod
    def get_contour_from_mask(mask: np.ndarray) -> np.ndarray:
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            raise ValueError("No contours found in the mask")
        
        main_contour = max(contours, key=cv2.contourArea)
        return main_contour
    
    @staticmethod
    def get_centre(shape_contour: np.ndarray) -> tuple:
        M = cv2.moments(shape_contour)
        if M["m00"] == 0:
            raise ValueError("Shape has no area, cannot compute center")
        
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        return (cx, cy)
    @staticmethod
    def invert_side_profile(profile: np.ndarray) -> np.ndarray:
        if not isinstance(profile, np.ndarray):
            raise ValueError("Profile must be a NumPy array")
        
        max_value = np.max(profile)
        return max_value - profile
    
    @staticmethod
    def get_left_profile_bounded(mask_image: np.ndarray) -> np.ndarray:
        profile = []

        contours, _ = cv2.findContours(mask_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return np.array([], dtype=int)

        main_contour = max(contours, key=cv2.contourArea)
        
        x, y, w, h = cv2.boundingRect(main_contour)
        
        bounding_left_x = x

        for y_row in range(y, y + h):
            shape_pixel_indices = np.where(mask_image[y_row] == 255)[0]

            if shape_pixel_indices.size > 0:
                leftmost_x_in_row = shape_pixel_indices.min()
                distance = leftmost_x_in_row - bounding_left_x
                profile.append(distance)
            else:
                profile.append(0)
                
        return np.array(profile, dtype=int)

    @staticmethod
    def get_left_profile(mask_image: np.ndarray) -> np.ndarray:
        """
        Extracts the left profile of a shape from its mask image.
        The distance is measured from the left edge of the image canvas.
        """
        height, _ = mask_image.shape
        profile = []

        for y in range(height):
            shape_pixel_indices = np.where(mask_image[y] == 255)[0]

            if shape_pixel_indices.size > 0:
                # The leftmost pixel's x-coordinate is the distance
                leftmost_x = shape_pixel_indices.min()
                distance = leftmost_x
                profile.append(distance)
            else:
                profile.append(0)
                
        return np.array(profile, dtype=int)

def generate_side_profiles(img_path: str, rotation_step: int = 30) -> list[SideProfile]:
    image = ImageProcessor.load_image(img_path)
    mask = ImageProcessor.create_mask(image)
    contour = ShapeProcessor.get_contour_from_mask(mask)
    center = ShapeProcessor.get_centre(contour)
    side_profiles = []

    for angle in range(0, 360, rotation_step):
        rotated_mask = ImageProcessor.rotate_image(mask, angle, center)
        left_profile = ShapeProcessor.get_left_profile_bounded(rotated_mask)
        side_profiles.append(SideProfile(angle=angle, profile=left_profile))

    return side_profiles


        

    
