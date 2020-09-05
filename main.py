"""
Welcome to NaCoSy, your python script for generating CO2 factors and prices of national power systems,
based on weather data and installed power plants.

In this main script, you run the operation. In the settings.ini script, you specify the settings of your operation.
Leave the rest to us!
More advice following here soon!

"""


"""
Workflow von NaCoSy: 

1. Already preliminary processed data get loaded into the modell: 
    - weather Data to train SVR (offshore data were missing too much data)(x-axis values) # done
    - power data for svr training(y-axis values) # done
    - best params for pv and wind SVR! (BOTH!)
    - installed power dataframes # done 
    This data gets loaded into the programm, to train the SVR. 
    
    therefore, just plant the excel/pickle files in the data folders. 
2. Load TRY(testreference-year) data into the model and format it properly. # done
3. Use the SVR to generate a timespecific production of power 
4. Connect this with the power_system files to generate the desired co2 factors and stuff. 

"""
# TODO: Example consumption is still just taken from a historical year. Find a way to generate the power consumption profiles for future scenarios
# TODO: Same as generation from not variant regenerative and conventional power plants!
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVR

from methods.reading_in import read_try,read_settings, preprocess_try, read_regr_input
from methods.regression import run_regression
from power_system.classes.Scenario import Scenario
from power_system.example_unit_commitment import example_unit_commitment

print("Begin preprocessing the data.")
# read out settings from settings.ini
settings = read_settings()
# read out try data
onshore_try,offshore_try = read_try(settings)
# preprocess try data
onshore_try = preprocess_try(onshore_try)
offshore_try = preprocess_try(offshore_try)

scenario = Scenario(
        path_scenario=settings['path_scenario'],
        file_scenario=settings['filename_scenario'],
        reference=False,
        start_cases=dict(bes=None, ds=None, nes=settings['nes_scenario'], ga=None),
        node_name='example')

# read weather and power data for regression
data = read_regr_input(settings)
print("Preprocessing done!")
# read and fit support vector regression
print("Now starting to fit Support Vector Regression!")
power_predictions = run_regression(data,settings,onshore_try,offshore_try,scenario)
print("Successfully completed regression with Support Vector Machine!")
#power_predictions = pd.read_pickle(settings['path_trygendata'])

# TODO: horizon-werte in example_unit_commitment mal durchprobieren

# load in everything necessary from power_systems
# here just copy the run script from the example script
# if the run script is way too long, cmake another method script out of it
# allow scipt to copy from config file, just like right now. But now, load configs from settings.ini file in config.py

# print output data and safe them properly


# this is enough to run the whole thing
example_unit_commitment(scenario=scenario,settings=settings, vre_scaling=settings['vre_scaling'])


print("okay")