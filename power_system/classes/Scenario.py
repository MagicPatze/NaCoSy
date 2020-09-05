# created February 2018
# by Markus Schumacher

import pandas as pd
import os
import platform
import copy

from os.path import join as pjoin

__author__ = "Markus Schumacher"
__version__ = "0.1.0"
__email__ = "mschumacher@eonerc.rwth-aachen.de"
__status__ = "Development"


class Scenario(object):
    """
    Class describing a scenario that is used for power system calculation.
    The scenario information is read from an .xlsx file.

    Parameters
    ----------
    path_scenario : str
        Path where the scenario .xls file is located

    file_scenario : str
        Name of the specific scenario .xls file

    start_cases : dict
        Number of the case to start with (default: 1)
    """

    def __init__(self,
                 path_scenario,
                 file_scenario,
                 reference,
                 start_cases,
                 stop_cases=dict(nes=None),
                 node_name=None):
        
        """ Constructor for Scenario instance
        """
        linux = platform.system() == "Linux"
        if path_scenario and file_scenario:
            if node_name:
                self.node_name = node_name
            else:
                self.node_name = os.uname()[1] if linux else os.environ.get(
                    'COMPUTERNAME')
            self.reference = reference
            self._case = copy.deepcopy(start_cases)
            self.start_cases = start_cases
            self.stop_cases = stop_cases
            # for _key in self.stop_cases.keys():
            #     if not self.stop_cases[_key]:
            #         self.stop_cases[_key] = len(self._bes_data.index)
            self.filepath_scenario = pjoin(path_scenario, file_scenario)

            if self.start_cases["nes"]:
                self._nes_data = pd.read_excel(io=self.filepath_scenario,
                                               sheet_name='NES_' + self.node_name,
                                               header=2,
                                               index_col=0)
                self._nes = self._nes_data.loc[self._case['nes'],
                            'id': 'pumped_hydro']
                if not self.stop_cases["nes"]:
                    self.stop_cases["nes"] = len(self._nes_data.index)
            else:
                self._nes_data = None

    @property
    def case(self):
        return self._case

    @case.setter
    def case(self, val):
        for k in val.keys():
            self._case[k] = int(val[k])
            self.read_case(domain=k)

    @property
    def num_nes_cases(self):
        if self.stop_cases["nes"]:
            _num_nes_cases = self.stop_cases["nes"] - self.start_cases["nes"] + 1
        else:
            _num_nes_cases = len(self._nes_data.index) - self.start_cases["nes"] + 1
        return _num_nes_cases

    @property
    def nes(self):
        return self._nes

    def next_case(self, domain):
        """ Method to jump to the next case (row of .xls file)
        """
        for _d in domain:
            self.case[_d] += 1
            self.read_case(_d)

    def read_case(self, domain, case_num=None):
        """Method to read the current case from file.
        """
        try:
            if case_num:
                self.case = {domain: case_num}

            if domain == 'nes':
                self._nes = self._nes_data.loc[self._case[domain],
                            'id': 'pumped_hydro']

        except KeyError as err:
            print(err)
