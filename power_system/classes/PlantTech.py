# -*- coding: utf-8 -*-
# Created July 2017

import pandas as pd
import numpy as np


__author__ = "Markus Schumacher"
__version__ = "0.1.0"
__email__ = "mschumacher@eonerc.rwth-aachen.de"
__status__ = "Development"


class PlantTech(object):
    """Description of plant technology that is part of the plant stock in a
    power system

    Parameters
    ----------
    plant_type : str
        Type of power plant, e.g. hard_coal

    p_nom : float
        Nominal installed capacity [MW]

    emission_factor : float
        emission factor of produced electricity for plant type [kg/MWh]
        fpo : This has to be [t/MWh] !

    marginal_cost : float
        marginal production cost of electricity for plant type [EUR/MWh]
    """

    def __init__(self,
                 plant_type,
                 p_nom,
                 fuel_cost,
                 o_m_cost,
                 co2_price,
                 emission_factor,
                 num_blocks=1,
                 p_profile=0,
                 p_min_pu=0,
                 p_max_pu=1,
                 ramp_limit_up=1,
                 ramp_limit_down=1,
                 ramp_limit_start_up=1,
                 ramp_limit_shut_down=1,
                 min_up_time=0,
                 min_down_time=0,
                 start_up_cost=0,
                 shut_down_cost=0,
                 renewable=False,
                 curtailable=True,
                 committable=True):
        """Constructor of plant technology object
        """

        self.plant_type = plant_type
        self.renewable = renewable
        self.curtailable = curtailable
        self.p_nom = p_nom
        self.num_blocks = num_blocks
        self.ramp_limit_up = ramp_limit_up
        self.ramp_limit_down = ramp_limit_down
        self.ramp_limit_start_up = ramp_limit_start_up
        self.ramp_limit_shut_down = ramp_limit_shut_down
        self.min_up_time = min_up_time
        self.min_down_time = min_down_time
        self.start_up_cost = start_up_cost
        self.shut_down_cost = shut_down_cost
        self.committable = committable
        self.emission_factor = emission_factor[plant_type]
        self.marginal_cost = (fuel_cost[plant_type] +
                              o_m_cost +
                              co2_price * self.emission_factor)

        if renewable:
            self.p_max_pu = p_profile / p_nom
            _p_min_pu = np.array([self.p_max_pu.values,
                                  (np.ones_like(self.p_max_pu.values) *
                                   p_min_pu)]).T
            _p_min_pu = pd.DataFrame(index=p_profile.index,
                                     data=_p_min_pu).min(axis=1)

            self.p_min_pu = _p_min_pu if curtailable else self.p_max_pu
        else:
            self.p_max_pu = p_max_pu
            self.p_min_pu = p_min_pu

