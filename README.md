![E.ON EBC RWTH Aachen University](./_static/EBC_Logo.png)

# NaCoSy

Calculate CO2 factors and other national energy system data with test reference year weather data.

Project for modelling a national power system.  
Based on the solution of a unit commitment problem a national power plant dispatch should be generated.  
This dispatch plan can be used to generate dynamic  
emission profiles for considered system.

## Easy-to-use-tutorial

In order to use NaCoSy, go to the folder *settings*. 
Only in this folder, you are supposed to change anything. 

In the subfolder *testreferenceyear*, you can upload the test reference year (TRY) data files of another on- and/or offshore station. The generation of wind- and pv-power plants get generated with a support vector machine as regressor.
If you do not know how to retrieve the new test reference year data from the German Meteorological Service (DWD), check out the "tutorial" folder. 

The files *example_consumption.csv* and *example_generation.csv* you should extract from SMARD (Link: https://www.smard.de/en/downloadcenter/download_market_data).
Keep in mind to extract csv files from a **whole year** please. 

In the *settings.ini* file, all relevant settings are specified and explained. 

The results you can find in the *results* folder.


## Further information

NaCoSy uses much preliminary processed data, that get loaded into the modell. 
As stated above, the wind- and pv-power generation, gets estimated with a regression analysis, using a support vector machine with an rbf-kernel.
The parameters and the train data of the support vector regression (SVR) were calculated in another program. Thus, they can be found in the data folder. 
Also, if you use the same TRY data with the same settings, in the main file there is a "shortcut" to not calculate the generation with the SVR again. 

The settings file is read out by a ConfigParser and gets written into a dict. 

Within the *power_system\example_unit_commitment.py* file, the consumption and generation files are read in. They then get spead into variant and constant production of regenerative energy power plants as well as conventional production. 
The programm then maskes use of the pypsa applicaton and stores all types of power plants into the grid - the national energy system.
Afterwards, the power plant dispatch gets optimized and the results get stored.

# Further developments - outlook

The example consumption is still just taken from SMARD, which also can forecast the consumption. A goal for future developments though, could be to generate the power consumption profiles based on different possible scenarios. 
The same goes also for non-variant regenerative power plants (like biogas and water).
