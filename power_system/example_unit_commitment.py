# -*- coding: utf-8 -*-
# Created January 2018


""" Example script showing how to create a simple UC using pypsa. Power system
profiles for Germany can be found at https://www.smard.de
"""

# Ignore warnings
import warnings

warnings.filterwarnings("ignore")

# Built-in packages
import pandas as pd
import numpy as np
from os.path import join as pjoin
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Internal packages
from power_system.classes.Network import Network
from power_system.classes.PlantTech import PlantTech
from power_system.config import PATH_DATA, PATH_PLOT, PATH_OUT, \
    RANGE, STEPS, IDX_START, IDX_END, RFACT, PLOT, \
    SCENARIO

__author__ = "Markus Schumacher"
__email__ = "mschumacher@eonerc.rwth-aachen.de"
__status__ = "Development"


def example_unit_commitment(scenario,settings,vre_scaling, export_grid=False):
    print("The power system scenario you chose:")
    print(scenario.nes)

    ef_agg = {'hard_coal': settings['ef_hard_coal'],
                'lignite': settings['ef_lignite'],
                'gas_combined_cycle': settings['ef_gas_combined_cycle'],
                'gas_open_cycle': settings['ef_gas_open_cycle'],
                'nuclear': settings['ef_nuclear'],
                'biomass': settings['ef_biomass'],
                'run_of_river': settings['ef_run_of_river'],
                'wind_onshore': settings['ef_wind_onshore'],
                'wind_offshore': settings['ef_wind_offshore'],
                'pv': settings['ef_pv']}

    mc = {'hard_coal': settings['mc_hard_coal'],
          'lignite': settings['mc_lignite'],
          'gas_combined_cycle': settings['mc_gas_combined_cycle'],
          'gas_open_cycle': settings['mc_gas_open_cycle'],
          'nuclear': settings['mc_nuclear'],
          'biomass': settings['mc_biomass'],
          'run_of_river': settings['mc_run_of_river'],
          'wind_onshore': settings['mc_wind_onshore'],
          'wind_offshore': settings['mc_wind_offshore'],
          'pv': settings['mc_pv']}

    co2_price = settings['co2_price']
    PATH_OUT = settings['path_results']
    PATH_PLOT = settings['path_results']
    IDX_START = (datetime.strptime(settings['consumption_start_date'],"%d.%m.%Y"))
    IDX_END = (datetime.strptime(settings['consumption_end_date'],"%d.%m.%Y") - timedelta(seconds=3600))
    marginal_cost = pd.Series(mc)
    RFACT = 1 # for 1 hour values 1, else resolution/1h
    STEPS = len(pd.date_range(start=IDX_START,end=IDX_END,freq='1H'))

    # Read variable renewable energy (vre) production data from file
    vre_production = pd.read_pickle(settings['path_trygendata'])
    vre_production.columns = ['wind_offshore', 'wind_onshore', 'pv']
    # Scale vre production with specific factors
    vre_production *= settings['vre_scaling']

    # Read electricity consumption hourly
    el_load = pd.read_csv(settings['path_consdata'],
                          header=0,
                          sep=';',
                          thousands='.',
                          decimal=',',
                          usecols=[2],
                          na_values='-').bfill().iloc[::4]

    #el_load.index = vre_production.index
    #TODO: Unterschied, den ich bisher gefundenhabe: grid.snapshots freq nicht gleich. mla hiermit probieren:
    el_load.index = pd.date_range(start=pd.Timestamp(year=int(settings['try_year']), month= 1, day=1, hour=1, minute=0),
                                  end=pd.Timestamp(year=int(settings['try_year'])+1, month= 1, day=1, hour=0, minute=0),
                                  freq='1H')
    #el_load.index = pd.date_range(start=IDX_START,end=IDX_END,freq='1H')
    el_load.columns = ['total_load']

    el_load.to_csv(
        pjoin(PATH_OUT, "electric_load_{}.csv".format(scenario.nes.id)))

    # the other generation data is getting loaded in.
    # the profiles of the renewable data is taken from it and scaled with the new power_system data.

    #  Read cre production data from file
    cre_production = pd.read_csv(settings['path_gendata'],
        usecols=[2, 3],
        header=0,
        sep=';',
        thousands='.',
        decimal=',',
        na_values='-').bfill().iloc[::4]

    cre_production.index = vre_production.index
    cre_production.columns = ['biomass', 'run_of_river']


    conv_production = pd.read_csv(settings['path_gendata'],
        usecols=range(8, 14),
        header=0,
        sep=';',
        thousands='.',
        decimal=',',
        na_values='-').bfill().iloc[::4]
    conv_production.index = vre_production.index
    conv_production.columns = ['nuclear', 'lignite', 'hard_coal',
                               'gas', 'pumped_hydro', 'others']

    #  Calculate residual electrical load from total load and vre production
    res_load = pd.DataFrame(
        # data=el_load.total_load - vre_production.sum(axis=1),
        data=el_load.total_load.values,
        columns=['residual_load'],
        index=el_load.index)

    # Add Generators as virtual representations

    plant_techs = []

    if scenario.nes.gas_open_cycle > 0:
        plant_techs.append(PlantTech(plant_type="gas_open_cycle",
                                     num_blocks=10,
                                     p_nom=scenario.nes.gas_open_cycle,
                                     p_min_pu=0.2,
                                     fuel_cost=mc,
                                     o_m_cost=0.7,
                                     co2_price=co2_price,
                                     emission_factor=ef_agg))

    if scenario.nes.gas_combined_cycle > 0:
        plant_techs.append(
            PlantTech(plant_type="gas_combined_cycle",
                      num_blocks=10,
                      p_nom=scenario.nes.gas_combined_cycle,
                      p_min_pu=0.2,
                      ramp_limit_start_up=1,
                      ramp_limit_shut_down=1,
                      ramp_limit_up=0.5,
                      ramp_limit_down=0.5,
                      start_up_cost=44,
                      shut_down_cost=0,
                      min_up_time=3 * 4,
                      min_down_time=3 * 4,
                      fuel_cost=mc,
                      o_m_cost=0.8,
                      co2_price=co2_price,
                      emission_factor=ef_agg,
                      committable=True))

    if scenario.nes.hard_coal > 0:
        plant_techs.append(PlantTech(plant_type="hard_coal",
                                     num_blocks=10,
                                     p_nom=scenario.nes.hard_coal,
                                     p_min_pu=0.35,
                                     ramp_limit_start_up=1. / (3 * 4),
                                     ramp_limit_shut_down=1. / (2 * 4),
                                     ramp_limit_up=0.25,
                                     ramp_limit_down=0.5,
                                     start_up_cost=251,
                                     shut_down_cost=0,
                                     min_up_time=5 * 4,
                                     min_down_time=6.5 * 4,
                                     fuel_cost=mc,
                                     o_m_cost=2,
                                     co2_price=co2_price,
                                     emission_factor=ef_agg,
                                     committable=True))

    if scenario.nes.lignite > 0:
        plant_techs.append(PlantTech(plant_type="lignite",
                                     num_blocks=10,
                                     p_nom=scenario.nes.lignite,
                                     p_min_pu=0.35,
                                     ramp_limit_start_up=1. / (5 * 4),
                                     ramp_limit_shut_down=1. / (3 * 4),
                                     ramp_limit_up=0.25,
                                     ramp_limit_down=0.5,
                                     start_up_cost=251,
                                     shut_down_cost=0,
                                     min_up_time=5 * 4,
                                     min_down_time=6.5 * 4,
                                     fuel_cost=mc,
                                     o_m_cost=2,
                                     co2_price=co2_price,
                                     emission_factor=ef_agg,
                                     committable=True))

    if scenario.nes.nuclear > 0:
        plant_techs.append(PlantTech(plant_type="nuclear",
                                     num_blocks=10,
                                     p_nom=scenario.nes.nuclear,
                                     p_min_pu=0.7,
                                     ramp_limit_start_up=1. / (5 * 4),
                                     ramp_limit_shut_down=1. / (3 * 4),
                                     ramp_limit_up=0.25,
                                     ramp_limit_down=0.5,
                                     start_up_cost=663,
                                     shut_down_cost=0,
                                     min_up_time=12 * 4,
                                     min_down_time=24 * 4,
                                     fuel_cost=mc,
                                     o_m_cost=0.0,
                                     co2_price=co2_price,
                                     emission_factor=ef_agg,
                                     committable=True))

    if scenario.nes.biomass > 0:
        plant_techs.append(PlantTech(plant_type="biomass",
                                     renewable=True,
                                     curtailable=True,
                                     p_nom=scenario.nes.biomass,
                                     p_min_pu=0.0,
                                     p_profile=cre_production.biomass,
                                     fuel_cost=mc,
                                     o_m_cost=2,
                                     co2_price=co2_price,
                                     emission_factor=ef_agg,
                                     committable=False))
    if scenario.nes.run_of_river > 0:
        plant_techs.append(PlantTech(plant_type="run_of_river",
                                     renewable=True,
                                     curtailable=False,
                                     p_nom=scenario.nes.run_of_river,
                                     p_min_pu=1.0,
                                     p_profile=cre_production.run_of_river,
                                     fuel_cost=mc,
                                     o_m_cost=0.7,
                                     co2_price=co2_price,
                                     emission_factor=ef_agg,
                                     committable=False))

    if scenario.nes.wind_offshore > 0:
        plant_techs.append(PlantTech(plant_type="wind_offshore",
                                     renewable=True,
                                     curtailable=True,
                                     p_nom=scenario.nes.wind_offshore,
                                     p_min_pu=0.0,
                                     p_profile=vre_production.wind_offshore,
                                     fuel_cost=mc,
                                     o_m_cost=0.99,
                                     co2_price=co2_price,
                                     emission_factor=ef_agg,
                                     committable=False))

    if scenario.nes.wind_onshore > 0:
        plant_techs.append(PlantTech(plant_type="wind_onshore",
                                     renewable=True,
                                     curtailable=True,
                                     p_nom=scenario.nes.wind_onshore,
                                     p_min_pu=0.0,
                                     p_profile=vre_production.wind_onshore,
                                     fuel_cost=mc,
                                     o_m_cost=1.0,
                                     co2_price=co2_price,
                                     emission_factor=ef_agg,
                                     committable=False))
    if scenario.nes.pv > 0:
        plant_techs.append(PlantTech(plant_type="pv",
                                     renewable=True,
                                     curtailable=True,
                                     p_nom=scenario.nes.pv,
                                     p_min_pu=0.0,
                                     p_profile=vre_production.pv,
                                     fuel_cost=mc,
                                     o_m_cost=1.01,
                                     co2_price=co2_price,
                                     emission_factor=ef_agg,
                                     committable=False))

    # Create national grid
    grid = Network(snapshots=el_load.index,
                   plant_techs=plant_techs)

    grid.add("StorageUnit", name="pumped_hydro", bus="bus",
             p_nom=scenario.nes.pumped_hydro,
             max_hours=8,
             efficiency_store=0.88, efficiency_dispatch=0.88,
             marginal_cost=0)

    #  Add residual load that has to be covered by conventional power plants
    grid.add("Load", name="load", bus="bus",
             p_set=res_load.residual_load)

    # TODO: Mal ausprobieren, ob mit horizon = 1 oder höher was anderes raus kommt
    horizon = 1
    for _s, _t in enumerate(grid.snapshots[::24]):
        # horizon = 1 if _t == grid.snapshots[-96*horizon:-]
        """        grid.lopf(
            pd.DatetimeIndex(start=_t, periods=24 * horizon, freq='1H'),
            solver_name='gurobi',
            solver_options={'MIPGap': 1e-2, 'QCPDual': 0})"""
        grid.lopf(
            pd.DatetimeIndex(pd.date_range(start=_t, periods=24 * horizon, freq='60Min')),
            solver_name='gurobi',
            solver_options={'MIPGap': 1e-2, 'QCPDual': 0})
        horizon = horizon - 1 if _s == len(
            grid.snapshots[::24]) - horizon else horizon
        print(_t)
        if horizon == 0:
            break

    #  Get optimization results of unit commitment problem
    pp_dispatch_agg = pd.DataFrame(index=grid.snapshots)

    for _k in ef_agg.keys():
        pp_dispatch_agg[_k] = grid.generators_t.p.loc[:,
                              grid.generators_t.p.columns.str.startswith(
                                  _k)].sum(axis=1)

    pp_dispatch_agg[pp_dispatch_agg < 0] = 0

    # emission_factors = grid.emission_factors
    emission_fact_t = pd.DataFrame(data=np.zeros(STEPS),
                                   index=grid.snapshots,
                                   columns=['mix'])
    cost_t = pd.DataFrame(data=np.zeros(STEPS),
                          index=grid.snapshots,
                          columns=['mix'])

    # Calculate MIXED emission with given emission factors
    emission_fact = pd.Series(ef_agg)

    emission_t = pp_dispatch_agg.mul(
        emission_fact[pp_dispatch_agg.columns] * RFACT
    )

    emission_fact_t['mix'] = emission_t.sum(axis=1) / (
            el_load.total_load * RFACT)

    #  Calculate MIXED power price with given marginal cost per pp type
    total_cost_t = pp_dispatch_agg.mul(
        marginal_cost[pp_dispatch_agg.columns] * RFACT
    )

    cost_t['mix'] = total_cost_t.sum(axis=1) / (
            pp_dispatch_agg.sum(axis=1) * RFACT)

    #  ------------------Plot some results -----------------------------------

    if settings['plot_results']:
        pp_types = ['nuclear',
                    'lignite',
                    'hard_coal',
                    'gas_combined_cycle',
                    'gas_open_cycle']

        el_load.plot()
        ax = plt.gca()
        ax.set_ylabel('Electric load in MW')
        ax.legend()
        plt.tight_layout()
        plt.savefig(pjoin(PATH_PLOT, 'electric_load.png'), dpi=300)
        plt.close()

        vre_production.plot.area()
        ax = plt.gca()
        ax.set_ylabel('VRE generation in MW')
        ax.legend()
        plt.tight_layout()
        plt.savefig(pjoin(PATH_PLOT, 'vre_production.png'), dpi=300)
        plt.close()

        pp_dispatch_agg.loc[:, pp_types].plot(subplots=True)
        fig = plt.gcf()
        ax0 = fig.add_subplot(111, frame_on=False)
        ax0.set_xticks([])
        ax0.set_yticks([])
        ax0.set_ylabel('Generation in MW', labelpad=45)
        plt.tight_layout()
        plt.savefig(pjoin(PATH_PLOT, 'power_plant_dispatch.png'), dpi=300)
        plt.close()

        emission_fact_t.plot()
        ax = plt.gca()
        ax.set_ylabel('CO2 factor in t/MWh')
        ax.legend()
        plt.tight_layout()
        plt.savefig(pjoin(PATH_PLOT, 'co2_factor.png'), dpi=300)
        plt.savefig(pjoin(PATH_PLOT, 'co2_factor.pdf'), dpi=300)
        plt.close()

        cost_t.plot()
        ax = plt.gca()
        ax.set_ylabel('Mixed generation cost in EUR/MWh')
        ax.legend()
        plt.tight_layout()
        plt.savefig(pjoin(PATH_PLOT, 'marginal_cost.png'), dpi=300)
        plt.close()

    if export_grid:
        grid.export_to_csv_folder(
            csv_folder_name=r'results\grid')
