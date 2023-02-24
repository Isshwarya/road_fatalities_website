# Road Fatalities Website generator

A python script to generate static html pages for road fatalities using input data file given in csv format. Whenever new input data is available, append the data to the file data/traffic.csv and rerun this script to update the statistics captured. To view the website, open the generated index.html locally from the browser. index.html has links to all other pages and all other pages as well links back to home page (which is index.html). Also screenshots of website generated is captured in "output" folder.

## Installation

Any vanilla centos VM with python3 installed should work. Clone this GIT repository (https://github.com/Isshwarya/road_fatalities_website.git), setup virtualenv to install the requirements locally. Once the virtualenv is activated, install the requirements listed in requirements.txt by running

```bash
cd <project_dir>
pip install requirements.txt
```

Then run this script as given in the examples section.

## Usage

```bash
usage: generate_website.py [-h] [-f DATA_FILE] [-s COMPARE_START_YEAR] [-e COMPARE_END_YEAR] [-d]

Road Fatalities website updater

optional arguments:
  -h, --help            show this help message and exit
  -f DATA_FILE, --data_file DATA_FILE
                        Relative path to fatalities data file in csv format inside the project directory
  -s COMPARE_START_YEAR, --compare_start_year COMPARE_START_YEAR
                        Year1 or start year for generating comparison statistics between two years.Defaults to minimum year in the given data.
  -e COMPARE_END_YEAR, --compare_end_year COMPARE_END_YEAR
                        Year2 or end year for generating comparison statistics between two years.Defaults to maximum year in the given data.
  -d, --debug           Enable debug logs

```

## Examples

```bash
cd <src directory>
export PYTHONPATH=.
# Basic usage
./bin/generate_website.py

# To run with different data file
./bin/generate_website.py -f data/my_local_data.csv

# To generate comparison statistics for custom years:
./bin/generate_website.py -s 2019 -e 2021

```
