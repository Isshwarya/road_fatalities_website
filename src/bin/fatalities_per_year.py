import matplotlib.pyplot as plt
import pandas as pd

import os

project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
charts_dir = os.path.join(project_dir, "static", "auto", "charts")
file_path = os.path.join(project_dir, "data", "traffic.csv")
fatalities_df = pd.read_csv(file_path)
fig, ax = plt.subplots(
    #figsize=(10, 6)
    )
ax.set_title('Road Fatalities by Year')
ax.set_ylabel('Road Fatalities')
df = fatalities_df.groupby('year').size()
ax.plot(df.index, df.values)
fig.savefig(os.path.join(charts_dir, 'fatalities_by_year.png'), bbox_inches='tight')

fig1, ax1 = plt.subplots(
    #figsize=(10, 6)
    )
ax1.set_title('ABC')
ax1.set_ylabel('Road DEF')
df1 = fatalities_df.groupby('year').size()
ax1.plot(df1.index, df1.values)
fig1.savefig(os.path.join(charts_dir, 'fatalities_by_year_1.png'), bbox_inches='tight')