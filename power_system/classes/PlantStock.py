# -*- coding: utf-8 -*-
# Created July 2017

import pypsa

__author__ = "Markus Schumacher"
__version__ = "0.1.0"
__email__ = "mschumacher@eonerc.rwth-aachen.de"
__status__ = "Development"


class PlantStock(object):
    """Description of plant stock in the considered power system
    
    Parameters
    ----------
    plant_tech : list of PlantTech objects
    
    Attributes
    """

    def __init__(self, plant_techs):
        """Constructor of PlantStock object
        """

        self.plant_techs = plant_techs

