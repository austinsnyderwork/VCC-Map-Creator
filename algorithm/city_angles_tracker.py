import math

from .poly_management import TypedPolygon
from . import spatial_analysis


class Angle:

    def __init__(self, obtuse_angle, acute_angle):
        self.obtuse_angle = obtuse_angle
        self.acute_angle = acute_angle


def calculate_angle_between_points(x1: float, y1: float, x2: float, y2: float, center_coord: tuple):
    angle1 = math.atan2(y1 - center_coord[1], x1 - center_coord[0])
    angle1 = math.degrees(angle1)
    angle2 = math.atan2(y2 - center_coord[1], x2 - center_coord[0])
    angle2 = math.degrees(angle2)

    return angle1 - angle2

def get_angle(angle1: float, angle2: float) -> Angle:
    min_angle, max_angle = min(angle1, angle2), max(angle1, angle2)
    if max_angle - min_angle <= 180:
        acute_angle = max_angle - min_angle
        obtuse_angle = (360 - max_angle) + min_angle
    else:
        acute_angle = (360 - max_angle) + min_angle
        obtuse_angle = max_angle - min_angle

    return Angle(obtuse_angle=obtuse_angle,
                 acute_angle=acute_angle)

def calculate_angle_from_positive_x_axis(x1: float, y1: float, center_coord: tuple):
    angle = math.atan2(y1 - center_coord[1], x1 - center_coord[0])
    angle = math.degrees(angle)
    if angle < 0:
        angle += 360
    return angle

def get_reflex_angle_range(angle1: float, angle2: float):
    min_angle, max_angle = min(angle1, angle2), max(angle1, angle2)

    if max_angle - min_angle <= 180:
        reflex_range = (0, min_angle), (max_angle, 360)
        return reflex_range
    else:
        reflex_range = (min_angle, max_angle)
        return reflex_range

def angles_in_reflex_range(reflex_range, angles: list[float]) -> bool:
    # There can be 1-2 range tuples, depending on the reflex angle
    for range_ in reflex_range:
        for angle in angles:
            if range_[0] < angle < range_[1]:
                return True
    return False


class CityAnglesTracker:

    def __init__(self, city_name: str, city_coord: tuple, lines: list[TypedPolygon]):
        self.city_name = city_name
        self.city_coord = city_coord
        self.lines = lines

        self.angles = {}
        self.most_open_angle = None

    def _get_line_angles(self):
        for line_poly in self.lines:
            angle = calculate_angle_from_positive_x_axis(x1=line_poly.centroid.x,
                                                         y1=line_poly.centroid.y,
                                                         center_coord=self.city_coord)
            self.angles[angle] = line_poly
            self.angles = {key: self.angles[key] for key in sorted(self.angles.keys())}
        return self.angles

    def find_largest_angle(self):
        if len(self.angles) == 0:
            self._get_line_angles()

        angles_list = list(self.angles.keys())
        largest_angle = -1
        largest_angle_lines = (None, None)
        for i, (angle, line) in enumerate(self.angles.items()):
            next_i = i + 1 if i < len(self.angles) else 0
            next_angle = angles_list[next_i]
            angle_obj = get_angle(angle1=angle,
                                  angle2=next_angle)
            reflex_range = get_reflex_angle_range(angle1=angle,
                                                  angle2=next_angle)
            other_angles = [self.angles[idx] for idx in range(len(self.angles)) if idx not in (i, next_i)]
            if angles_in_reflex_range(reflex_range=reflex_range,
                                      angles=other_angles):
                btwn_angle = angle_obj.acute_angle
            else:
                btwn_angle = angle_obj.obtuse_angle

            if btwn_angle > largest_angle:
                largest_angle = btwn_angle
                largest_angle_lines = (line, self.angles[btwn_angle])

        return largest_angle, largest_angle_lines

