import os
import matplotlib.pyplot as plt
# import mpld3
import pandas as pd
import numpy as np

import lib.utils as Utils
import lib.constants as Constants
from lib.logger import DEBUG, INFO


class LoadCharts(object):
    def __init__(self, parsed_args):
        relative_data_file = parsed_args.data_file or Constants.DEFAULT_DATA_FILE
        self.project_dir = Utils.get_project_dir()
        self.charts_dir = os.path.join(
            self.project_dir, Constants.RELATIVE_CHARTS_DIR)
        self.data_file_path = os.path.join(
            self.project_dir, relative_data_file)
        self.fatalities_df = pd.read_csv(self.data_file_path)

    def run(self):
        INFO("Processing input data")
        self.process_data()
        INFO("Updating all charts")
        for method in Utils.get_all_method_names(self):
            if method.startswith("chart_"):
                getattr(self, method)()
        INFO("Completed generating static files for the website")

    def process_data(self):
        DEBUG("Filtering applicable years")
        self.fatalities_df = self.fatalities_df[(
            self.fatalities_df['year'] > Constants.STARTING_YEAR)].dropna()
        DEBUG("Populating hours and minutes columns from time")
        self.fatalities_df['hour'] = self.fatalities_df['time'].apply(
            lambda x: int(str(x).split(':')[0]))
        self.fatalities_df['minutes'] = self.fatalities_df['time'].apply(
            lambda x: int(str(x).split(':')[1]))
        DEBUG("Populating unrecognized road_users as 'others'")
        self.fatalities_df.loc[~self.fatalities_df['road_user'].isin(
            Constants.PRIMARY_ROAD_USERS), 'road_user'] = 'Other'
        DEBUG("Populating involvement column")
        self.fatalities_df['involvement'] = self.fatalities_df.apply(lambda x: 'yes' if any(
            x[col] == 'yes' for col in Constants.INVOLVEMENT_COLUMNS) else 'no', axis=1)

    def chart_fatalities_per_year(self):
        fig, ax = plt.subplots()
        ax.set_title('Road Fatalities by Year')
        ax.set_ylabel('Road Fatalities')
        ax.set_xlabel('Year')
        df = self.fatalities_df.groupby('year').size()
        ax.plot(df.index, df.values)
        self._generate_chart(ax, fig)

    def chart_fatalities_per_state(self):
        fig, ax = plt.subplots()
        ax.set_title('Road Fatalities by State')
        ax.set_ylabel('Road Fatalities')
        ax.set_xlabel('State')

        df = self.fatalities_df.groupby('state').size().sort_values()

        ax.set_xlim(0, df.index.size)
        plt.xticks(rotation=90, fontsize=7)
        ax.set_yticks(np.arange(0, df.values.max(), 5))
        ax.bar(df.index, df.values, align='center', width=0.5)

        self._generate_chart(ax, fig)

    def chart_fatalities_by_hour(self):
        fig, ax = plt.subplots()
        ax.set_title('Road Fatalities by Hour')
        ax.set_ylabel('Road Fatalities')
        df = self.fatalities_df.groupby('hour').size()
        ax.bar(df.index, df.values)
        self._generate_chart(ax, fig)

    def _generate_chart(self, ax, fig):
        ax.grid(True)
        caller = Utils.get_caller_name(level=2)
        INFO("Generated %s" % caller)
        fig.savefig(os.path.join(self.charts_dir,
                    caller + ".jpg"), bbox_inches='tight')
        # mpld3 offers interactive charts but it changes the
        # formatting of what matplotlib graph originally offered
        # So going with the approach of saving in jpg format to
        # keep the scope of the assignment simple.
        # mpld3.save_html(fig, os.path.join(self.charts_dir, caller + ".html"))
