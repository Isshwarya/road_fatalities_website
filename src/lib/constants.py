import os

DEFAULT_DATA_FILE = os.path.join("data", "traffic.csv")
RELATIVE_CHARTS_DIR = os.path.join("static", "auto", "charts")
PRIMARY_ROAD_USERS = ('Driver', 'Passenger', 'Motorcycle rider', 'Pedestrian')
INVOLVEMENT_COLUMNS = ['bus_involvement',
                       'rigid_truck_involvement', 'articulated_truck_involvement']
STARTING_YEAR = 2006
