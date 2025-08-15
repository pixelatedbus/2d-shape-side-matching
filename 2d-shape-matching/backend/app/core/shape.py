import numpy as np
#judol-detector-468402
#gcloud builds submit --tag gcr.io/judol-detector-468402/shape-matcher-backend ./backend
class SideProfile:
    def __init__(self, profile: np.ndarray, angle: int = 0):
        self.profile = profile
        self.angle = angle

    def __repr__(self):
        return f"SideProfile(angle={self.angle}, mean_distance={np.mean(self.profile):.2f}"
    

class Shape:
    def __init__(self, side_profiles: list[SideProfile], id: int = None):
        self.side_profiles = side_profiles
        self.id = id # for database getting

    def __repr__(self):
        return f"Shape(id={self.id}, num_profiles={len(self.side_profiles)})"

    def get_side_profile(self, index: int) -> SideProfile:
        if 0 <= index < len(self.side_profiles):
            return self.side_profiles[index]
        else:
            raise IndexError("Index out of range for side profiles.")
        
    def get_all_side_profiles(self) -> list[SideProfile]:
        return self.side_profiles
    
    def add_side_profile(self, profile: np.ndarray, angle: int = 0):
        new_profile = SideProfile(profile, angle)
        self.side_profiles.append(new_profile)
