import pandas as pd


class DataPreparer:

    def __init__(self, df: pd.DataFrame):
        self.df = df

    @staticmethod
    def _count_outpatient_visiting_clinics(row, num_visiting_clinics: dict):
        origin = row['point_of_origin']
        outpatient = row['community']

        if outpatient not in num_visiting_clinics:
            num_visiting_clinics[outpatient] = {
                'count': 0,
                'visiting_clinics': set()
            }

        if origin not in num_visiting_clinics[outpatient]['visiting_clinics']:
            num_visiting_clinics[outpatient]['count'] += 1
            num_visiting_clinics[outpatient]['visiting_clinics'].add(origin)

    def create_outpatient_num_visiting_clinics_map(self):
        num_visiting_clinics = {}
        self.df.apply(self._count_outpatient_visiting_clinics, axis=1, num_visiting_clinics=num_visiting_clinics)

        visiting_list = []
        for outpatient, data in num_visiting_clinics.items():
            visiting_list.append({
                'name': outpatient,
                'num_visiting_clinics': data['count']
            })



        city_elements = self.vis_map_creator.plot_num_visiting_clinics_map(visiting_list)

        show_pause = 360
        self.vis_map_creator.show_map(show_pause=show_pause)

