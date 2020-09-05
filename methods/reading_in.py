import pandas as pd, numpy as np
import datetime, os, sys
from configparser import ConfigParser


def read_settings():

    # read out settings
    config = ConfigParser(inline_comment_prefixes='#')
    config.read('settings\settings.ini')

    settings = {}
    settings['try_onshore_folder'] = config['TRY']['onshore_folder']
    settings['try_offshore_folder'] = config['TRY']['offshore_folder']
    settings['try_year'] = config['TRY']['year']
    settings['try_which'] = config['TRY']['which']

    settings['svr_folder'] = config['regression']['svr_data_folder']
    settings['weather_onshore_folder'] = config['regression']['weather_onshore_folder']
    settings['weather_offshore_folder'] = config['regression']['weather_offshore_folder']
    settings['power_folder'] = config['regression']['power_data_folder']

    settings['path_scenario'] = config['power_system']['path_scenario']
    settings['filename_scenario'] = config['power_system']['filename_scenario']
    settings['nes_scenario'] = config.getint('power_system','scenario')
    settings['vre_scaling'] = config.getfloat('power_system','vre_scaling')
    settings['co2_price'] = config.getfloat('power_system','co2_price')
    settings['path_trygendata'] = config['power_system']['path_trygendata']
    settings['path_gendata'] = config['power_system']['path_gendata']
    settings['path_consdata'] = config['power_system']['path_consdata']
    settings['path_results'] = config['power_system']['path_out']
    settings['consumption_start_date'] = config['power_system']['consumption_start_date']
    settings['consumption_end_date'] = config['power_system']['consumption_end_date']
    settings['plot_results'] = config.getboolean('power_system','plot_results')

    settings['ef_hard_coal'] = config.getfloat('ef_agg','hard_coal')
    settings['ef_lignite'] = config.getfloat('ef_agg','lignite')
    settings['ef_gas_combined_cycle'] = config.getfloat('ef_agg','gas_combined_cycle')
    settings['ef_gas_open_cycle'] = config.getfloat('ef_agg','gas_open_cycle')
    settings['ef_nuclear'] = config.getfloat('ef_agg','nuclear')
    settings['ef_biomass'] = config.getfloat('ef_agg','biomass')
    settings['ef_run_of_river'] = config.getfloat('ef_agg','run_of_river')
    settings['ef_wind_onshore'] = config.getfloat('ef_agg','wind_onshore')
    settings['ef_wind_offshore'] = config.getfloat('ef_agg','wind_offshore')
    settings['ef_pv'] = config.getfloat('ef_agg','pv')

    settings['mc_hard_coal'] = config.getfloat('mc','hard_coal')
    settings['mc_lignite'] = config.getfloat('mc','lignite')
    settings['mc_gas_combined_cycle'] = config.getfloat('mc','gas_combined_cycle')
    settings['mc_gas_open_cycle'] = config.getfloat('mc','gas_open_cycle')
    settings['mc_nuclear'] = config.getfloat('mc','nuclear')
    settings['mc_biomass'] = config.getfloat('mc','biomass')
    settings['mc_run_of_river'] = config.getfloat('mc','run_of_river')
    settings['mc_wind_onshore'] = config.getfloat('mc','wind_onshore')
    settings['mc_wind_offshore'] = config.getfloat('mc','wind_offshore')
    settings['mc_pv'] = config.getfloat('mc','pv')


    # doc link configparser: https://docs.python.org/3/library/configparser.html
    """
    a = config['TRY']['start_date']
    b = config.get('section','entry')
    c = config.getint()
    d = config.getfloat()
    e = config.getboolean()
    """

    return settings

def read_try(settings):

    rowstoskip2015 = list(range(30))
    rowstoskip2015.append(33)
    rowstoskip2045 = list(range(32))
    rowstoskip2045.append(35)
    elements = {}
    elements['onshore'] = os.listdir(settings['try_onshore_folder'])
    elements['offshore'] = os.listdir(settings['try_offshore_folder'])

    df_both = {}
    for element in elements:
        try:
            if settings['try_year'] == '2015':
                if settings['try_which'] == 'summer':
                    df_both[element] = pd.read_csv(
                        settings['try_'+element+'_folder']+'\\'+ elements[element][1],
                        skiprows=rowstoskip2015, header=0, sep='\s+', usecols=['t', 'p', 'WG', 'B', 'D'])
                    print("You chose year 2015 with extreme summer as reference year.")
                elif settings['try_which'] == 'winter':
                    df_both[element] = pd.read_csv(
                        settings['try_'+element+'_folder']+'\\'+ elements[element][2],
                        skiprows=rowstoskip2015, header=0, sep='\s+', usecols=['t', 'p', 'WG', 'B', 'D'])
                    print("You chose year 2015 with extreme winter as reference year.")
                elif settings['try_which'] == 'normal':
                    df_both[element] = pd.read_csv(
                        settings['try_'+element+'_folder']+'\\'+ elements[element][0],
                        skiprows=rowstoskip2015, header=0, sep='\s+', usecols=['t', 'p', 'WG', 'B', 'D'])
                    print("You chose year 2015 with normal weather as reference year.")
            elif settings['try_year'] == '2045':
                if settings['try_which'] == 'summer':
                    df_both[element] = pd.read_csv(
                        settings['try_'+element+'_folder']+'\\'+ elements[element][4],
                        skiprows=rowstoskip2045, header=0, sep='\s+', usecols=['t', 'p', 'WG', 'B', 'D'])
                    print("You chose year 2045 with extreme summer as reference year.")
                elif settings['try_which'] == 'winter':
                    df_both[element] = pd.read_csv(
                        settings['try_'+element+'_folder']+'\\'+ elements[element][5],
                        skiprows=rowstoskip2045, header=0, sep='\s+', usecols=['t', 'p', 'WG', 'B', 'D'])
                    print("You chose year 2045 with extreme winter as reference year.")
                elif settings['try_which'] == 'normal':
                    df_both[element] = pd.read_csv(
                        settings['try_'+element+'_folder']+'\\'+ elements[element][3],
                        skiprows=rowstoskip2045, header=0, sep='\s+', usecols=['t', 'p', 'WG', 'B', 'D'])
                    print("You chose year 2045 with normal weather as reference year.")
            else:
                raise ValueError

        except ValueError:
            sys.exit("Error! Check settings file for correctness!")

        # fix dates for year
        start_index = pd.Timestamp(year=int(settings['try_year']), month=1, day=1, hour=1)
        df_both[element]['date'] = ""
        for i in df_both[element].index:
            df_both[element].at[i, 'date'] = start_index + datetime.timedelta(hours=i)

        df_both[element].set_index(df_both[element]['date'], drop=True, inplace=True)
        df_both[element] = df_both[element].drop(columns=['date'])

    df_onshore = df_both['onshore']
    df_offshore = df_both['onshore']

    return df_onshore, df_offshore

def preprocess_try(df):

    # radiation columns are split in TRY into direct and diffuse radiation as mean value of hour [W/m^2]
    # add direct and diffuse values and multiply by 0.36 for [J/cm^2] per hour
    df['G'] = df['B']+df['D']
    df = df.drop(columns=['B','D'])
    df['G'] = df['G'] * 0.36

    # rename columns
    df.columns = ['Lufttemperatur[°C]','Luftdruck[hPa]','Windgeschw.[m/s]','Globalstrahlung[J/cm^2]']

    return df

def read_regr_input(settings):

    onshoredata = pd.read_pickle(settings['weather_onshore_folder'] + '\weather_onshore.pkl')
    offshoredata = pd.read_pickle(settings['weather_offshore_folder'] + '\weather_offshore.pkl')
    powerdata = pd.read_pickle(settings['power_folder'] + '\power_norm.pkl')

    data = {}

    data['pv_data'] = pd.concat([onshoredata['Globalstrahlung Onshore[J/cm^2]'],
                                 onshoredata['Lufttemperatur Onshore[°C]']],join='inner', axis=1)

    data['pv_res'] = pd.concat([powerdata['Photovoltaik[MWh]']])

    data['won_data'] = pd.concat([onshoredata['Windgeschw. Onshore[m/s]'],
                         onshoredata['Lufttemperatur Onshore[°C]'],
                        onshoredata['Luftdruck Onshore[hPa]']], join='inner', axis=1)

    data['won_res'] = pd.concat([powerdata['Wind Onshore[MWh]']])

    data['woff_data'] = pd.concat([offshoredata['Windgeschw. Offshore[m/s]'],
                         offshoredata['Lufttemperatur Offshore[°C]'],
                        offshoredata['Luftdruck Offshore[hPa]']], join='inner', axis=1)
    data['woff_res'] = pd.concat([powerdata['Wind Offshore[MWh]']])

    return data


#--------------------------------------------------
