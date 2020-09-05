from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.svm import SVR
from joblib import dump, load
import pandas as pd
import numpy as np

def run_regression(data,settings,on_try,off_try,scenario):

    # process try data
    pv_try_in = pd.concat([on_try['Globalstrahlung[J/cm^2]'],on_try['Lufttemperatur[°C]']], join='inner', axis=1)

    won_try_in = pd.concat([on_try['Windgeschw.[m/s]'], on_try['Lufttemperatur[°C]'],
                         on_try['Luftdruck[hPa]']], join='inner', axis=1)

    woff_try_in = pd.concat([off_try['Windgeschw.[m/s]'], off_try['Lufttemperatur[°C]'],
                          off_try['Luftdruck[hPa]']], join='inner', axis=1)


    # introduce scaler for better SVR results
    pv_regr_data = data['pv_data']
    # scale input data
    scaler = MinMaxScaler(feature_range=(0, 1))
    Xpv = scaler.fit_transform(data['pv_data'])
    ypv = data['pv_res']
    Xwon = scaler.fit_transform(data['won_data'])
    ywon = data['won_res']
    Xwoff = scaler.fit_transform(data['woff_data'])
    ywoff = data['woff_res']
    # scale try data
    pv_try = scaler.fit_transform(pv_try_in)
    won_try = scaler.fit_transform(won_try_in)
    woff_try = scaler.fit_transform(woff_try_in)

    # apply svr to TRY weather data
    # load best SVRs from before (already calculated!)
    # TODO: FIX WIND SVR ?? WHY ARE ALL VALUES THE SAME??
    pvSVR = load(settings['svr_folder'] + '\\pv_best_svr.joblib')
    windSVR = load(settings['svr_folder'] + '\\wind_best_svr.joblib')

    # fit SVR to given data and predict TRY power generation
    pvSVR.fit(Xpv, ypv)
    pv_pred = pvSVR.predict(pv_try)
    pv_pred = pd.DataFrame(pv_pred.reshape((-1,1)))
    windSVR.fit(Xwon, ywon)
    won_pred = windSVR.predict(won_try)
    won_pred = pd.DataFrame(won_pred.reshape((-1,1)))
    woff_pred = windSVR.predict(woff_try)
    woff_pred = pd.DataFrame(woff_pred.reshape((-1,1)))

    power_predictions_norm = pd.concat([pv_pred,won_pred,woff_pred],join='inner',axis=1)
    power_predictions_norm.columns = ['Photovoltaik[MW]','Wind Onshore[MW]','Wind Offshore[MW]']

    # calculate generated power with installed power
    power_inst = scenario.nes
    power_predictions = pd.concat([power_predictions_norm['Wind Offshore[MW]'] * power_inst.wind_offshore,
                                    power_predictions_norm['Wind Onshore[MW]'] * power_inst.wind_onshore,
                                    power_predictions_norm['Photovoltaik[MW]'] * power_inst.pv],
                                   join='inner',axis=1)
    power_predictions.index = pv_try_in.index.values

    print("Finished calculating the power production for the Test-Reference-Year!")
    print("Saving try_generation data in pickle.")
    pd.to_pickle(power_predictions,settings['path_trygendata'],protocol=4)

    return power_predictions

