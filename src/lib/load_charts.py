import os
import re
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from jinja2 import Environment
# import mpld3

from lib.logger import DEBUG, INFO
import lib.constants as Constants
import lib.utils as Utils


class LoadCharts(object):
    def __init__(self, parsed_args):
        self.parsed_args = parsed_args
        relative_data_file = parsed_args.data_file or Constants.DEFAULT_DATA_FILE
        INFO("Data file: %s" % relative_data_file)
        self.project_dir = Utils.get_project_dir()
        self.charts_dir = os.path.join(
            self.project_dir, Constants.RELATIVE_CHARTS_DIR)
        self.data_file_path = os.path.join(
            self.project_dir, relative_data_file)
        self.fatalities_df = pd.read_csv(self.data_file_path)
        min_yr = self.fatalities_df["year"].min()
        max_yr = self.fatalities_df["year"].max()
        self.start_year = parsed_args.compare_start_year or min_yr
        self.end_year = parsed_args.compare_end_year or max_yr
        DEBUG("Compare statistics will be generated between years %s and %s" %
              (self.start_year, self.end_year))
        assert min_yr <= self.start_year
        assert max_yr >= self.end_year
        self.jinja_env = Environment()
        sns.set()
        sns.set_context("notebook", font_scale=1.5,
                        rc={"lines.linewidth": 2.5})

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

    def chart_fatalities_per_state_compare(self):
        fig, ax = plt.subplots()
        ax.set_title(
            'Change in Road Fatalities per State between %s and %s' % (self.start_year, self.end_year))
        change_by_state = self.fatalities_df[self.fatalities_df['year'].isin(
            [self.start_year, self.end_year])].groupby(['state', 'year']).size().reset_index(name='Road Fatalities')
        ax.set_xlim(0, change_by_state.index.size)
        ax.set_yticks(
            np.arange(0, change_by_state["Road Fatalities"].max(), Constants.STEP_SIZE))
        sns.barplot(x='state', y='Road Fatalities', hue='year', data=change_by_state.sort_values(
            by='Road Fatalities'), ax=ax)

        self._generate_chart(ax, fig, rotate_xlabels=True)

    def chart_fatalities_per_state(self):
        fig, ax = plt.subplots()
        ax.set_title('Road Fatalities by State')
        ax.set_ylabel('Road Fatalities')
        ax.set_xlabel('State')

        df = self.fatalities_df.groupby('state').size().sort_values()

        ax.set_xlim(0, df.index.size)
        # ax.set_yticks(np.arange(0, df.values.max(), Constants.STEP_SIZE))
        ax.bar(df.index, df.values, align='center')

        self._generate_chart(ax, fig, rotate_xlabels=True)

    def chart_fatalities_per_hour_compare(self):
        fig, ax = plt.subplots()
        ax.set_title(
            'Change in Road Fatalities per Hour between %s and %s' % (self.start_year, self.end_year))
        change_by_hour = self.fatalities_df[self.fatalities_df['year'].isin(
            [self.start_year, self.end_year])].groupby(['hour', 'year']).size().reset_index(name='Road Fatalities')
        sns.barplot(x='hour', y='Road Fatalities', hue='year', data=change_by_hour.sort_values(
            by='Road Fatalities'), ax=ax)

        self._generate_chart(ax, fig, rotate_xlabels=True)

    def chart_fatalities_by_hour(self):
        fig, ax = plt.subplots()
        ax.set_title('Road Fatalities by Hour')
        ax.set_ylabel('Road Fatalities')
        df = self.fatalities_df.groupby('hour').size()
        ax.bar(df.index, df.values)
        self._generate_chart(ax, fig)

    def chart_fatalities_by_gender_compare(self):
        self._chart_fatalities_by_field_compare(field="gender")

    def chart_fatalities_by_gender(self):
        fig, ax = plt.subplots()
        ax.set_title('Road Fatalities by Gender')
        df = self.fatalities_df.groupby('gender').size()
        ax.pie(df.values, labels=df.index, autopct='%1.1f%%',
               textprops={"fontsize": 7})
        self._generate_chart(ax, fig)

    def chart_fatalities_by_road_user_roles_compare(self):
        self._chart_fatalities_by_field_compare(field="road_user")

    def chart_fatalities_by_road_user_roles(self):
        fig, ax = plt.subplots()
        ax.set_title('Road Fatalities by Road user roles')
        df = self.fatalities_df.groupby('road_user').size()
        ax.pie(df.values, labels=df.index, autopct='%1.1f%%',
               textprops={"fontsize": 7})
        self._generate_chart(ax, fig)

    def _chart_fatalities_by_field_compare(self, field):
        fig, (ax1, ax2) = plt.subplots(1, 2)
        ax1.set_title(
            'Change in Road Fatalities by %s between %s and %s' % (field.capitalize(), self.start_year, self.end_year))
        ax1.set_title(self.start_year)
        ax2.set_title(self.end_year)
        df = self.fatalities_df[self.fatalities_df['year'].isin(
            [self.start_year])].groupby(field).size()
        ax1.pie(df.values, labels=df.index, autopct='%1.1f%%',
                textprops={"fontsize": 7})
        df = self.fatalities_df[self.fatalities_df['year'].isin(
            [self.end_year])].groupby(field).size()
        ax2.pie(df.values, labels=df.index, autopct='%1.1f%%',
                textprops={"fontsize": 7})
        self._generate_chart(ax=(ax1, ax2), fig=fig)

    def chart_fatalities_by_crash_type_compare(self):
        self._chart_fatalities_by_field_compare(field="crash_type")

    def chart_fatalities_by_crash_type(self):
        fig, ax = plt.subplots()
        ax.set_title('Road Fatalities by Crash type')
        df = self.fatalities_df.groupby('crash_type').size()
        ax.pie(df.values, labels=df.index,
               autopct='%1.1f%%', textprops={"fontsize": 7})
        self._generate_chart(ax, fig)

    def chart_fatalities_by_age_compare(self):
        fig, (ax1, ax2) = plt.subplots(1, 2)
        ax1.text(0.5, 1, self.start_year,
                 transform=ax1.transAxes, fontsize=10)
        ax2.text(0.5, 1, self.end_year,
                 transform=ax2.transAxes, fontsize=10)
        filtered = self.fatalities_df.loc[self.fatalities_df['year']
                                          == self.start_year, 'age']
        sns.histplot(filtered, bins=range(
            0, filtered.values.max()+(Constants.STEP_SIZE*2), Constants.STEP_SIZE), kde=False, ax=ax1)
        filtered = self.fatalities_df.loc[self.fatalities_df['year']
                                          == self.end_year, 'age']
        sns.histplot(filtered, bins=range(
            0, filtered.values.max()+(Constants.STEP_SIZE*2), Constants.STEP_SIZE), kde=False, ax=ax2)
        self._generate_chart(ax=(ax1, ax2), fig=fig)

    def chart_fatalities_by_age(self):
        fig, ax = plt.subplots()
        ax.set_title('Road Fatalities by Age')
        ax.set_xlabel('Age')
        # STEP_SIZE*2 is needed because range does not
        # include the end value and hist() again doesn't include
        # and count the end range i.e, 10 -20 means it counts values
        # from 10 to 19 without including 20.
        bins = range(0, self.fatalities_df["age"].max(
        )+(Constants.STEP_SIZE*2), Constants.STEP_SIZE)
        ax.hist(self.fatalities_df["age"], bins)
        self._generate_chart(ax, fig)

    def chart_fatalities_by_speed_limit(self):
        fig, ax = plt.subplots()
        ax.set_title('Road Fatalities by Speed limit')
        ax.set_ylabel('Road Fatalities')
        bins = range(0, self.fatalities_df["speed_limit"].max(
        )+(Constants.STEP_SIZE*2), Constants.STEP_SIZE)
        ax.hist(self.fatalities_df["age"], bins)
        self._generate_chart(ax, fig)

    def chart_fatalities_by_speed_limit_compare(self):
        fig, ax = plt.subplots()
        ax.set_title('Change in Road Fatalities by speed limit between %s and %s' % (
            self.start_year, self.end_year))
        ax.set_xlabel('Speed Limit')
        ax.set_ylabel('Road Fatalities')
        self.fatalities_df.loc[self.fatalities_df['year'] == self.start_year, 'speed_limit'].value_counts(
        ).sort_index().plot(ax=ax, xlim=[10, 150], label=self.start_year)
        self.fatalities_df.loc[self.fatalities_df['year'] == self.end_year, 'speed_limit'].value_counts(
        ).sort_index().plot(ax=ax, xlim=[10, 150], label=self.end_year)
        ax.legend()
        self._generate_chart(ax, fig)

    def chart_fatalities_by_weekday_compare(self):
        self._chart_fatalities_by_field_compare(field="dayweek")

    def chart_fatalities_by_weekday(self):
        fig, ax = plt.subplots()
        ax.set_title('Road Fatalities by Week Days')

        df = self.fatalities_df.groupby('dayweek').size()

        custom_dict = {
            'Monday': 1,
            "Tuesday": 2,
            "Wednesday": 3,
            "Thursday": 4,
            "Friday": 5,
            "Saturday": 6,
            "Sunday": 7
        }
        df = df.sort_index(key=lambda x: x.map(custom_dict))
        ax.pie(df.values, labels=df.index,
               autopct='%1.1f%%', textprops={"fontsize": 7})
        self._generate_chart(ax, fig, grid=False)

    def _generate_chart(self, ax, fig, grid=True, rotate_xlabels=False):
        if not isinstance(ax, (list, tuple)):
            ax = [ax]
        for ax_unit in ax:
            if rotate_xlabels:
                ax_unit.tick_params(axis='both', which='major',
                                    labelsize=7, rotation=90)
            else:
                ax_unit.tick_params(axis='both', which='major', labelsize=7)
            # plt.yticks(fontsize=7)
            if ax_unit:
                ax_unit.grid(grid)
        level = 2  # min stack level expected
        while True:
            caller = Utils.get_caller_name(level=level)
            if caller.startswith("chart_"):
                break
            level += 1
        caller = re.sub(r'^chart_', "", caller)
        INFO("Generated %s" % caller)
        fig.savefig(os.path.join(self.charts_dir,
                    caller + ".jpg"), bbox_inches='tight')
        # mpld3 offers interactive charts but it changes the
        # formatting of what matplotlib graph originally offered
        # So going with the approach of saving in jpg format.
        # Eg: It changes year 1970 to 1,970, etc.,

        # mpld3.save_html(fig, os.path.join(self.charts_dir, caller + ".html"))

    @staticmethod
    def get_base_template():
        return """
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Australian Road Fatalities</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-GLhlTQ8iRABdZLl6O3oVMWSktQOp6b7In1Zl3/Jr59b6EGGoI1aFkw7cmDA6j6gD" crossorigin="anonymous">
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous"></script>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container-fluid">
            <a class="navbar-brand" href="#">Home</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavDropdown" aria-controls="navbarNavDropdown" aria-expanded="false" aria-label="Toggle navigation">
              <span class="navbar-toggler-icon"></span>
            </button>
          <div class="collapse navbar-collapse" id="navbarNavDropdown">
            <ul class="navbar-nav">
              <li class="nav-item dropdown">
                <a class="nav-link dropdown-toggle" href="#" id="navbarDropdownMenuLink" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                    Impact of individual fields over the years
                </a>
                <ul class="dropdown-menu" aria-labelledby="navbarDropdownMenuLink">
                  <li><a class="dropdown-item" href="auto/age_gender.html">Age and Gender</a></li>
                  <li><a class="dropdown-item" href="auto/state.html">State </a></li>
                  <li><a class="dropdown-item" href="auto/dayweek_hour_year.html">Dayweek, Hour and Year</a></li>
                  <li><a class="dropdown-item" href="auto/road_user.html">Road User Role</a></li>
                  <li><a class="dropdown-item" href="auto/crash_type.html">Crash Type</a></li>
                  <li><a class="dropdown-item" href="auto/speed_limit.html">Speed Limit</a></li>
                 </ul>
              </li>
              <li class="nav-item dropdown">
                <a class="nav-link dropdown-toggle" href="#" id="navbarDropdownMenuLink" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                    Compare Statistics between two years
                </a>
                <ul class="dropdown-menu" aria-labelledby="navbarDropdownMenuLink">
                    <li><a class="dropdown-item" href="auto/compare/age_gender.html">Age and Gender</a></li>
                    <li><a class="dropdown-item" href="auto/compare/state.html">State </a></li>
                    <li><a class="dropdown-item" href="auto/compare/dayweek_hour_year.html">Dayweek, Hour and Year</a></li>
                    <li><a class="dropdown-item" href="auto/compare/road_user.html">Road User</a></li>
                    <li><a class="dropdown-item" href="auto/compare/crash_type.html">Crash Type</a></li>
                    <li><a class="dropdown-item" href="auto/compare/speed_limit.html">Speed Limit</a></li>
                </ul>
              </li>
            </ul>
          </div>
        </div>
      </nav>
{content}
</body>
</html>
"""

    def generate_html_pages(self):
        groups = [
            ["age", "gender"],
            ["state"],
            ["dayweek", "hour", "year"],
            ["road_user"],
            ["crash_type"],
            ["speed_limit"]
        ]
        for grp in groups:
            self.generate_html_page(grp)

    def generate_html_page(self, grp):
        template = self.get_base_template()
        content = """
        {% for field in grp -%}
        <h3>{{ field }}</h3>
        <div>
            # Individual statistics

            # Compare Statistics
        </div>
"""

        template.format(content=content)
        jinja_template = self.jinja_env.from_string(template)
        final_content = jinja_template.render()
