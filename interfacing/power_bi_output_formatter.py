import pandas as pd


from visualization_elements import Line, CityScatter, Best


class PowerBiOutputFormatter:

    def __init__(self, vis_elements: dict = None):
        self.vis_elements = vis_elements

        self.vis_element_columns = {
            Line: ['x_data', 'y_data', 'color', 'linestyle', 'linewidth', 'zorder'],
            CityScatter: ['city_coord', 'marker', 'color', 'edgecolor', 'size', 'label', 'zorder'],
            Best: ['poly_coord', 'city_name', 'fontsize', 'font', 'color', 'fontweight', 'zorder']
        }

        self.ele_type_to_col_name = {
            Line: 'line',
            CityScatter: 'scatter',
            Best: 'text'
        }

        self.cols = ['type']
        for ele_type in self.vis_element_columns.keys():
            new_cols = self.format_column_names(vis_element_type=ele_type)
            self.cols.extend(new_cols)

        self.rows = []

    def format_column_names(self, vis_element=None, vis_element_type=None):
        if vis_element:
            vis_element_type = type(vis_element)
        col_names = self.vis_element_columns[vis_element_type]
        col_names = [f"{self.ele_type_to_col_name[vis_element_type]}_{col_name}" for col_name in col_names]
        return col_names

    def _create_new_row(self, vis_element):
        new_row = {col: "" for col in self.cols}
        new_row['type'] = vis_element.class_string
        map_attributes = vis_element.get_map_attributes()
        for col_name, value in map_attributes.items():
            f_col_name = f"{self.ele_type_to_col_name[type(vis_element)]}_{col_name}"
            if f_col_name not in self.cols:
                continue
            new_row[f_col_name] = value
        return new_row

    def add_visualization_elements(self, vis_elements: list):
        new_rows = [self._create_new_row(vis_element) for vis_element in vis_elements]
        self.rows.extend(new_rows)

    def create_df(self):
        return pd.DataFrame(self.rows, columns=self.cols)

