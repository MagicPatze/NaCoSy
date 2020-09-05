import pandas as pd
from power_system.classes.Scenario import Scenario
from methods.reading_in import read_settings

settings = read_settings()
PATH_DATA = r'power_system\data'
PATH_PLOT = r'power_system\results'
PATH_OUT = r'power_system\results'

SCENARIO = Scenario(
        path_scenario=settings['path_scenario'],
        file_scenario=settings['filename_scenario'],
        reference=False,
        start_cases=dict(bes=None, ds=None, nes=settings['nes_scenario'], ga=None),
        node_name='example')

scenario_year = str(SCENARIO.nes.id[-4:])

# fpo: updated timestamp syntax
START = pd.Timestamp(year=int(scenario_year), month= 2, day=1, hour=0, minute=0)
END = pd.Timestamp(year=int(scenario_year), month=2, day=3, hour=23, minute=30)
RESOLUTION = pd.Timedelta('30Min')  # Resolution in seconds
RANGE = pd.date_range(start=START, end=END, freq=RESOLUTION)
STEPS = len(RANGE)
YEAR = pd.date_range(start='{}0101'.format(scenario_year),
                        periods=35040,
                        freq=RESOLUTION)
"""YEAR = pd.DatetimeIndex(start='{}0101'.format(scenario_year),
                        periods=35040,
                        freq=RESOLUTION)"""
IDX_START = YEAR.get_loc(START)
IDX_END = YEAR.get_loc(END) + 1

RFACT = RESOLUTION / pd.Timedelta('1H')
PLOT = True
