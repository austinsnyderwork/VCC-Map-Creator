import math

from .poly_management import TypedPolygon


class LinePair:

    def __init__(self, line1: TypedPolygon, line2: TypedPolygon, min_angle: float = None, max_angle: float = None,
                 reflex_angle_range: tuple = None, acute_angle_range: tuple = None):
        self.line1 = line1
        self.line2 = line2

        self.min_angle = min_angle
        self.max_angle = max_angle

        self.reflex_angle_range = reflex_angle_range
        self.acute_angle_range = acute_angle_range

        self.can_use_reflex = None
        self.usable_angle_range = None
        self.usable_angle = None

    def get_reflex_angle_range(self):
        if self.max_angle - self.min_angle <= 180:
            reflex_range = (0, self.min_angle), (self.max_angle, 360)
            return reflex_range
        else:
            reflex_range = (self.min_angle, self.max_angle)
            return reflex_range

    def use_reflex(self, use: bool):
        if use:
            self.can_use_reflex = True
            self.usable_angle_range = self.reflex_angle_range
            self.usable_angle = convert_range_to_angle(self.usable_angle_range)
        else:
            self.can_use_reflex = False
            self.usable_angle_range = self.acute_angle_range
            self.usable_angle = convert_range_to_angle(self.usable_angle_range)


def convert_range_to_angle(angle_range):
    angle = 0
    for range_ in angle_range:
        angle += range_[1] - range_[0]
    return angle


def get_line_pair(line1: TypedPolygon, line2: TypedPolygon, angle1: float, angle2: float) -> LinePair:
    min_angle, max_angle = min(angle1, angle2), max(angle1, angle2)
    if max_angle - min_angle <= 180:
        acute_angle_range = max_angle, min_angle
        reflex_angle_range = (0, min_angle), (max_angle, 360)
    else:
        acute_angle_range = (0, min_angle), (max_angle, 360)
        reflex_angle_range = max_angle, min_angle

    return LinePair(line1=line1,
                    line2=line2,
                    min_angle=min_angle,
                    max_angle=max_angle,
                    reflex_angle_range=reflex_angle_range,
                    acute_angle_range=acute_angle_range)


def calculate_angle_from_positive_x_axis(x1: float, y1: float, center_coord: tuple):
    angle = math.atan2(y1 - center_coord[1], x1 - center_coord[0])
    angle = math.degrees(angle)
    if angle < 0:
        angle += 360
    return angle


def angles_in_reflex_range(reflex_range, angles: list[float]) -> bool:
    # There can be 1-2 range tuples, depending on the reflex angle
    for range_ in reflex_range:
        for angle in angles:
            if range_[0] < angle < range_[1]:
                return True
    return False


def determine_line_quadrant(angle):
    if 0 <= angle < 90:
        return 'Quadrant 1'
    elif 90 <= angle < 180:
        return 'Quadrant 2'
    elif 180 <= angle < 270:
        return 'Quadrant 3'
    else:
        return 'Quadrant 4'


class CityAnglesTracker:

    def __init__(self, city_name: str, city_coord: tuple, lines: list[TypedPolygon]):
        self.city_name = city_name
        self.city_coord = city_coord
        self.lines = lines

        self.line_pairs = self._create_line_pairs()

        self.angles = {}

    def _get_line_angles(self):
        for line_poly in self.lines:
            angle = calculate_angle_from_positive_x_axis(x1=line_poly.centroid.x,
                                                         y1=line_poly.centroid.y,
                                                         center_coord=self.city_coord)
            self.angles[angle] = line_poly
            self.angles = {key: self.angles[key] for key in sorted(self.angles.keys())}
        return self.angles

    def _create_line_pairs(self) -> list[LinePair]:
        if len(self.angles) == 0:
            self._get_line_angles()

        angles_list = list(self.angles.keys())

        if len(angles_list) == 1:
            opposite_angle = (angles_list[0] + 180) % 360
            line_pair = LinePair(line1=self.lines[0], line2=self.lines[0], min_angle=opposite_angle,
                                 max_angle=opposite_angle)
            return [line_pair]

        line_pairs = []
        for i, (angle, line) in enumerate(self.angles.items()):
            next_i = i + 1 if i < len(self.angles) else 0
            next_angle = angles_list[next_i]
            next_line = self.angles[next_angle]

            line_pair = get_line_pair(line1=line,
                                      line2=next_line,
                                      angle1=angle,
                                      angle2=next_angle)
            line_pairs.append(line_pair)

            reflex_range = line_pair.get_reflex_angle_range()
            other_angles = [self.angles[idx] for idx in range(len(self.angles)) if idx not in (i, next_i)]
            can_use_reflex = not angles_in_reflex_range(reflex_range=reflex_range,
                                                        angles=other_angles)
            line_pair.use_reflex(use=can_use_reflex)

        return line_pairs

    def find_best_spot(self, ):

