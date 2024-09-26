from polygons import polygon_factory


def verify_poly_validity(poly, name):
    if not poly.is_valid:
        raise ValueError(f"{name} poly was invalid on creation.")


def reduce_poly_width(poly, width_adjustment: float):
    x_min, y_min, x_max, y_max = poly.bounds
    poly_width = x_max - x_min
    width_adjust_percent = width_adjustment / 100.0
    width_change = poly_width * width_adjust_percent
    x_min = x_min + (width_change / 2)
    x_max = x_max - (width_change / 2)
    poly = poly_creation.create_poly(poly_type='rectangle',
                                     x_min=x_min,
                                     y_min=y_min,
                                     x_max=x_max,
                                     y_max=y_max)
    return poly

