# -*- coding: utf-8 -*-
# Created March 2018

import pypsa

__author__ = "Markus Schumacher"
__version__ = "0.1.0"
__email__ = "mschumacher@eonerc.rwth-aachen.de"
__status__ = "Development"


class Network(pypsa.Network):
    """Network on national energy system (NES) level that inherits from 
    pypsa.
    
    Parameters
    ----------
    power_plants : instance of object PlantStock
    
    profiles : instance of object Profiles
    
    
    Attributes
    ----------
    
    
    """

    def __init__(self, snapshots, plant_techs, profiles=0, bus="bus"):
        """Constructor of Network instance
        """

        super(Network, self).__init__()

        self.set_snapshots(snapshots=snapshots)
        self.add("Bus", bus)
        self.plant_techs = plant_techs
        self.profiles = profiles
        self.attach_generators()

    def attach_generators(self, bus="bus"):
        """Add committable power plants that form the plant stock to the 
        considered network instance
        """

        for _tech in self.plant_techs:
            for _block in range(_tech.num_blocks):
                p_nom_block = _tech.p_nom / _tech.num_blocks
                self.add("Generator",
                         bus=bus,
                         name=_tech.plant_type + "_{}".format(_block),
                         p_nom=p_nom_block,
                         p_min_pu=_tech.p_min_pu,
                         p_max_pu=_tech.p_max_pu,
                         ramp_limit_start_up=_tech.ramp_limit_start_up,
                         ramp_limit_shut_down=_tech.ramp_limit_shut_down,
                         ramp_limit_up=_tech.ramp_limit_up,
                         ramp_limit_down=_tech.ramp_limit_down,
                         min_up_time=_tech.min_up_time,
                         min_down_time=_tech.min_down_time,
                         start_up_cost=_tech.start_up_cost * p_nom_block,
                         shut_down_cost=_tech.shut_down_cost * p_nom_block,
                         marginal_cost=_tech.marginal_cost,
                         committable=_tech.committable)
