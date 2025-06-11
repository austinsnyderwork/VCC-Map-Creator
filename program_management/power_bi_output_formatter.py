import pandas as pd

from visual_elements.attributes_resolver import VisualElementAttributesResolver
from visual_elements.element_classes import TextBox, Line, CityScatter, VisualElement


class PowerBiOutputFormatter:

    def __init__(self):
        self.vis_element_columns = {
            Line: ['x_data', 'y_data', 'facecolor', 'linestyle', 'linewidth', 'zorder'],
            CityScatter: ['city_coord', 'marker', 'facecolor', 'edgecolor', 'size', 'label', 'zorder'],
            TextBox: ['poly_coord', 'city_name', 'fontsize', 'font', 'fontweight', 'fontcolor', 'zorder']
        }

        self._cols = {'type': []}
        for ve_type in self.vis_element_columns.keys():
            cols = [f"{ve_type.__name__.lower()}_{col}" for col in self.vis_element_columns[ve_type]]
            self._cols.update({col: [] for col in cols})

    def _add_row(self, row_data: dict):
        new_row = {col: "" for col in self._cols}
        new_row.update(row_data)
        for c, v in new_row.items():
            self._cols[c].append(v)

    def _create_line_row(self, line: Line):
        cols = {
            'x_data': line.x_data,
            'y_data': line.y_data,
            'facecolor': line.map_attributes['facecolor'],
            'linestyle': line.map_attributes['linestyle'],
            'linewidth': line.map_attributes['linewidth'],
            'zorder': line.map_attributes['zorder']
        }
        cols = {f"{Line.__name__.lower()}_{col}": v for col, v in cols.items()}
        cols['type'] = Line.__name__.lower()
        self._add_row(cols)

    def _create_scatter_row(self, scatter: CityScatter):
        map_att = scatter.map_attributes
        cols = {
            'city_coord': scatter.coord.lon_lat,
            'marker': map_att['marker'],
            'facecolor': map_att['facecolor'],
            'edgecolor': map_att['edgecolor'] if 'edgecolor' in map_att else "",
            'size': scatter.radius,
            'label': map_att['label'] if 'label' in map_att else "",
            'zorder': map_att['zorder']
        }
        cols = {f"{CityScatter.__name__.lower()}_{col}": v for col, v in cols.items()}
        cols['type'] = CityScatter.__name__.lower()
        self._add_row(cols)

    def _create_text_box_row(self, text_box: TextBox):
        map_att = text_box.map_attributes
        cols = {
            'poly_coord': text_box.centroid_coord.lon_lat,
            'city_name': text_box.city_name,
            'fontsize': map_att['fontsize'],
            'fontcolor': map_att['fontcolor'],
            'font': map_att['font'],
            'fontweight': map_att['fontweight'],
            'zorder': map_att['zorder']
        }
        cols = {f"{TextBox.__name__.lower()}_{col}": v for col, v in cols.items()}
        cols['type'] = TextBox.__name__.lower()
        self._add_row(cols)

    def create_df(self, visual_elements: list[VisualElement]):
        for ve in visual_elements:
            ve.map_attributes = VisualElementAttributesResolver.resolve_map_attributes(ve)
            if isinstance(ve, CityScatter):
                self._create_scatter_row(ve)
            elif isinstance(ve, TextBox):
                self._create_text_box_row(ve)
            elif isinstance(ve, Line):
                self._create_line_row(ve)

        return pd.DataFrame(self._cols)

