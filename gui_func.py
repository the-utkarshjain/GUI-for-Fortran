"""
@name 
    `gui_func.py`

@description 
    `src file for GUI Main class, subclass of <GUIBase>`

@package 
    `GUI for Fortran/C++ Application`

@official_repository 
    `https://github.com/the-utkarshjain/GUI-for-Fortran`

@contributors 
    * Abhishek Bhardwaj
    * Utkarsh Jain
    * Jhalak Choudhary
    * Navya
    * Om Pandey`

"""

from gui_base import GUIBase, PlotEncapsulator, GUI_exception
import threading
import time
import numpy as np
import matplotlib.pyplot as plt
import os
import hashlib
import random
import subprocess
from copy import deepcopy
import math

class GUIMain(GUIBase):
    r'''
    Primary class to be used for
    implementation.
    '''
    def __init__(self, *args, **kwargs):
        super(GUIMain, self).__init__(*args, **kwargs)

    @classmethod
    @GUI_exception
    def _refresh_utility(cls, first_file_path: str, second_file_path: str, third_file_path: str, memory: dict) -> bool:
        r'''
        Function to check if any input file is changed/updated
        and run the executable in case files are changed/updated.
        '''
        isupdates = False
        checksum_file_1 = hashlib.sha256(open(first_file_path, 'r').read().encode('utf-8')).hexdigest()
        checksum_file_2 = hashlib.sha256(open(second_file_path, 'r').read().encode('utf-8')).hexdigest()
        checksum_file_3 = hashlib.sha256(open(third_file_path, 'r').read().encode('utf-8')).hexdigest()

        if memory.get(first_file_path, None) != checksum_file_1:
            memory[first_file_path] = checksum_file_1
            isupdates = True

        if memory.get(second_file_path, None) != checksum_file_2:
            memory[second_file_path] = checksum_file_2
            isupdates = True
            
        if memory.get(third_file_path, None) != checksum_file_3:
            memory[third_file_path] = checksum_file_3
            isupdates = True  

        if isupdates == False:
            print("No updates found in the input file.")

        return type(isupdates) is bool

    @classmethod
    @GUI_exception
    def _nonblocking_execute_external_code(cls, exe_file_path: str, thread_queue: list):
        r'''
        Function to execute the fortran
        executable and generate output file.
        '''
        def target_func(x):
            return subprocess.call([x])

        t = threading.Thread(target=target_func, args=(exe_file_path,))
        thread_queue.append(t)
        t.start()

    @classmethod
    @PlotEncapsulator
    @GUI_exception
    def _plot_first_2D_data(cls, output_file_path: str, time_file_path: str):
        r'''
        Function to plot experimental data
        with reespect to timestamp.
        '''
        time = []
        conc = []

        with open(time_file_path,'r') as file:
            data = file.read().splitlines()
            for row in range(1,len(data)):
                if row>int(data[0]):
                    time.append(float(data[row]))

        with open(output_file_path,'r') as file:
            data = file.read().splitlines()
            for line in data:
                x, y = line.split()
                x = float(x)
                conc.append(x)

        plt.scatter(time,conc, marker='o', color='black')
        plt.xlabel('Time')
        plt.ylabel('Concentration')
        plt.title('Concentration-Time graph')

    @classmethod
    @PlotEncapsulator
    @GUI_exception
    def _plot_second_2D_data(cls, output_file_path: str, time_file_path: str):
        r'''
        Function to plot simulation data
        with reespect to timestamp.
        '''
        time = []
        conc = []

        with open(time_file_path,'r') as file:
            data = file.read().splitlines()
            for row in range(1,len(data)):
                if row>int(data[0]):
                    time.append(float(data[row]))

        with open(output_file_path,'r') as file:
            data = file.read().splitlines()
            for line in data:
                x, y = line.split()
                y = float(y)
                conc.append(y)

        plt.plot(time,conc)
        plt.xlabel('Time')
        plt.ylabel('Concentration')
        plt.title('Concentration-Time graph')

    @classmethod
    @PlotEncapsulator
    @GUI_exception
    def _plot_both_2D_data(cls, output_file_path: str, time_file_path: str):
        r'''
        Function to plot simulation and experimental data
        on same canvas.
        '''
        time = []
        conc1 = []
        conc2=[]

        with open(time_file_path,'r') as file:
            data = file.read().splitlines()
            for row in range(1,len(data)):
                if row>int(data[0]):
                    time.append(float(data[row]))

        with open(output_file_path,'r') as file:
            data = file.read().splitlines()
            for line in data:
                x, y = line.split()
                x, y = float(x), float(y)
                conc1.append(x)
                conc2.append(y)

        plt.scatter(time,conc1, marker='o',label='1',color='black')
        plt.plot(time,conc2, label='2')
        plt.xlabel('Time')
        plt.ylabel('Concentration')
        plt.title('Concentration-Time graph')
        plt.legend()
    
    @classmethod
    @GUI_exception
    def _inplace_update_variable_dictionary(cls, first_file_path: str, second_file_path: str, third_file_path: str, variable_dictionary: dict) -> None:        
        r'''
        Function to update variable dictionary in place 
        using the manually entered values
        '''
        try:
            file1 = open(first_file_path, "r")
            variable_dictionary["Mesopore seepage velocity"] = file1.readline().strip()
            variable_dictionary["Macropore seepage velocity"] = file1.readline().strip()
            variable_dictionary["Solute mass transfer rate b/w meso-micropore"] = file1.readline().strip()
            variable_dictionary["Solute mass transfer rate b/w meso-macropore"] = file1.readline().strip()
            variable_dictionary["Dispersivity"] = file1.readline().strip()
            variable_dictionary["No. of observation time steps"] = file1.readline().strip()
        finally:
            file1.close()

        try:
            file3 = open(third_file_path, "r")
            line = file3.readline().split()
            variable_dictionary["nz"] = line[0]
            variable_dictionary["nm"] = line[1]
            line = file3.readline().split()
            variable_dictionary["Length"] = line[0]
            variable_dictionary["Bulk density of porous media"] = line[1]
            variable_dictionary["Run time"] = line[2]
            variable_dictionary["Pulse time"] = line[3]
            variable_dictionary["delta_t"] = line[4]
            variable_dictionary["delta_x"] = line[5]
            line = file3.readline().split()
            variable_dictionary["Porosity of the macropore region"] = line[0]
            variable_dictionary["Porosity of the mesopore region"] = line[1]
            variable_dictionary["Porosity of the micropore region"] = line[2]
            line = file3.readline().split()
            variable_dictionary["Instantaneous sorption fraction in macropore region"] = line[0]
            variable_dictionary["Instantaneous sorption fraction in mesopore region"] = line[1]
            variable_dictionary["Instantaneous sorption fraction in micropore region"] = line[2]
            variable_dictionary["Fraction of sorption site available for macropore region"] = line[3]
            variable_dictionary["Fraction of sorption site available for mesopore region"] = line[4]
            variable_dictionary["Fraction of sorption site available for immobile region"] = line[5]
            line = file3.readline().split()
            variable_dictionary["Equilibrium sorption coefficient in macropore region"] = line[0]
            variable_dictionary["Equilibrium sorption coefficient in mesopore region"] = line[1]
            variable_dictionary["Equilibrium sorption coefficient in micropore region"] = line[2]
            variable_dictionary["Rate-limited sorbed coefficient in macropore region"] = line[3]
            variable_dictionary["Rate-limited sorbed coefficient in mesopore region"] = line[4]
            variable_dictionary["Rate-limited sorbed coefficient in micropore region"] = line[5]
        finally:
            file3.close()

    @classmethod
    @GUI_exception
    def _write_updated_values(cls, first_file_path: str, second_file_path: str, third_file_path: str, variable_dictionary: dict) -> None:
        r'''
        Function to update values (manually entered by user)
        in the files from the variable dictionary.
        '''
        try:
            with open(first_file_path, "r") as f:
                temp = f.readlines()
            file1 = open(first_file_path, "w")
            lines = ["Mesopore seepage velocity", "Macropore seepage velocity", "Solute mass transfer rate b/w meso-micropore", "Solute mass transfer rate b/w meso-macropore", "Dispersivity", "No. of observation time steps"]
            for line in lines[:-1]:
                file1.write(variable_dictionary[line]+str("\n"))
            file1.write(str(int(float(variable_dictionary[lines[-1]])))+str("\n"))
            file1.write("".join(temp[6:]))
        finally:
            file1.close()

        try:
            file3 = open(third_file_path, "w")
            lines = ["nz", "nm"]
            for line in lines[:-1]:
                file3.write(str(int(float(variable_dictionary[line])))+str(" "))
            file3.write(str(int(float(variable_dictionary[lines[-1]])))+str("\n"))
            lines = ["Length", "Bulk density of porous media", "Run time", "Pulse time", "delta_t", "delta_x"]
            for line in lines[:-1]:
                file3.write(variable_dictionary[line]+str(" "))
            file3.write(variable_dictionary[lines[-1]]+str("\n"))
            lines = ["Porosity of the macropore region", "Porosity of the mesopore region", "Porosity of the micropore region"]
            for line in lines[:-1]:
                file3.write(variable_dictionary[line]+str(" "))
            file3.write(variable_dictionary[lines[-1]]+str("\n"))
            lines = ["Instantaneous sorption fraction in macropore region", "Instantaneous sorption fraction in mesopore region", "Instantaneous sorption fraction in micropore region", "Fraction of sorption site available for macropore region", "Fraction of sorption site available for mesopore region", "Fraction of sorption site available for immobile region"]
            for line in lines[:-1]:
                file3.write(variable_dictionary[line]+str(" "))
            file3.write(variable_dictionary[lines[-1]]+str("\n"))
            lines = ["Equilibrium sorption coefficient in macropore region", "Equilibrium sorption coefficient in mesopore region", "Equilibrium sorption coefficient in micropore region", "Rate-limited sorbed coefficient in macropore region", "Rate-limited sorbed coefficient in mesopore region", "Rate-limited sorbed coefficient in micropore region"]
            for line in lines[:-1]:
                file3.write(variable_dictionary[line]+str(" "))
            file3.write(variable_dictionary[lines[-1]]+str("\n"))
        finally:
            file3.close()

    @GUI_exception
    def _export_timestamps_data(self, time_series: list, first_file_path: str, second_file_path: str, third_file_path: str) -> None:
        r'''
        Function to export timestamp data
        to an external file.
        '''
        time_series_copy = map(lambda x: str(x), time_series)
        as_string = "\n".join(time_series_copy)

        with open(second_file_path, "w") as f:
            f.write(as_string)

    @GUI_exception
    def _import_timestamps_data(self, first_file_path: str, second_file_path: str, third_file_path: str) -> list:
        r'''
        Function to import time-stamp data
        manually.
        '''
        try:
            file2 = open(second_file_path, "r")
            skip = int(file2.readline())
            for i in range(skip):
                file2.readline()
            timestamps_data = file2.read().splitlines()
        finally:
            file2.close()
        time_series = [float(i) for i in timestamps_data]
        return time_series

    @GUI_exception
    def _export_concentration_data(self, time_series: list, first_file_path: str, second_file_path: str, third_file_path: str) -> None:
        r'''
        Function to export concentration data
        to an external file.
        '''
        time_series_copy = map(lambda x: str(x), time_series)
        as_string = "\n".join(time_series_copy)

        with open(first_file_path, "w") as f:
            f.write(as_string)

    @GUI_exception
    def _import_concentration_data(self, first_file_path: str, second_file_path: str, third_file_path: str) -> list:
        r'''
        Function to import concentration data
        manually.
        '''
        try:
            file1 = open(first_file_path, "r")
            for i in range(6):
                file1.readline()
            concentration_data = file1.read().splitlines()
        finally:
            file1.close()
        consentration_series = [float(i) for i in concentration_data]
        return consentration_series

    @GUI_exception
    def _initialize_variables(self):
        r'''
        Function to initialise variables in accordance with 
        the modes as suggested in first feedback.
        '''
        return {
            "ADE": {
                "nz": None,
                "nm": None,
                "Length": None,
                "Bulk density of porous media": None,
                "Run time": None,
                "Pulse time": None,
                "delta_t": None,
                "delta_x": None,
                "Porosity of the macropore region": None,
                "Porosity of the mesopore region": 1e-16,
                "Porosity of the micropore region": 1e-16,
                "Instantaneous sorption fraction in macropore region": 1,
                "Instantaneous sorption fraction in mesopore region": 1e-16,
                "Instantaneous sorption fraction in micropore region": 1e-16,
                "Fraction of sorption site available for macropore region": 1,
                "Fraction of sorption site available for mesopore region": 1e-16,
                "Fraction of sorption site available for immobile region": 1e-16,
                "Equilibrium sorption coefficient in macropore region": None,
                "Equilibrium sorption coefficient in mesopore region": 1e-16,
                "Equilibrium sorption coefficient in micropore region": 1e-16,
                "Rate-limited sorbed coefficient in macropore region": 1e-16,
                "Rate-limited sorbed coefficient in mesopore region": 1e-16,
                "Rate-limited sorbed coefficient in micropore region": 1e-16,
                "Mesopore seepage velocity": 1e-16,
                "Macropore seepage velocity": None,
                "Solute mass transfer rate b/w meso-micropore": 1e-16,
                "Solute mass transfer rate b/w meso-macropore": 1e-16,
                "Dispersivity": None,
                "No. of observation time steps": None,
            },

            "MIM": {
                 "nz": None,
                "nm": None,
                "Length": None,
                "Bulk density of porous media": None,
                "Run time": None,
                "Pulse time": None,
                "delta_t": None,
                "delta_x": None,
                "Porosity of the macropore region": None,
                "Porosity of the mesopore region": 1e-16,
                "Porosity of the micropore region": 1e-16,
                "Instantaneous sorption fraction in macropore region": None,
                "Instantaneous sorption fraction in mesopore region": None,
                "Instantaneous sorption fraction in micropore region": 1e-16,
                "Fraction of sorption site available for macropore region": None,
                "Fraction of sorption site available for mesopore region": None,
                "Fraction of sorption site available for immobile region": 1e-16,
                "Equilibrium sorption coefficient in macropore region": None,
                "Equilibrium sorption coefficient in mesopore region": None,
                "Equilibrium sorption coefficient in micropore region": None,
                "Rate-limited sorbed coefficient in macropore region": 1e-16,
                "Rate-limited sorbed coefficient in mesopore region": 1e-16,
                "Rate-limited sorbed coefficient in micropore region": 1e-16,
                "Mesopore seepage velocity": 1e-16,
                "Macropore seepage velocity": None,
                "Solute mass transfer rate b/w meso-micropore": 1e-16,
                "Solute mass transfer rate b/w meso-macropore": None,
                "Dispersivity": None,
                "No. of observation time steps": None,
            },

            "MPNE": {
                "nz": None,
                "nm": None,
                "Length": None,
                "Bulk density of porous media": None,
                "Run time": None,
                "Pulse time": None,
                "delta_t": None,
                "delta_x": None,
                "Porosity of the macropore region": None,
                "Porosity of the mesopore region": None,
                "Porosity of the micropore region": 1e-16,
                "Instantaneous sorption fraction in macropore region": None,
                "Instantaneous sorption fraction in mesopore region": None,
                "Instantaneous sorption fraction in micropore region": 1e-16,
                "Fraction of sorption site available for macropore region": None,
                "Fraction of sorption site available for mesopore region": None,
                "Fraction of sorption site available for immobile region": 1e-16,
                "Equilibrium sorption coefficient in macropore region": None,
                "Equilibrium sorption coefficient in mesopore region": None,
                "Equilibrium sorption coefficient in micropore region": 1e-16,
                "Rate-limited sorbed coefficient in macropore region": None,
                "Rate-limited sorbed coefficient in mesopore region": None,
                "Rate-limited sorbed coefficient in micropore region": None,
                "Mesopore seepage velocity": None,
                "Macropore seepage velocity": None,
                "Solute mass transfer rate b/w meso-micropore": 1e-16,
                "Solute mass transfer rate b/w meso-macropore": None,
                "Dispersivity": None,
                "No. of observation time steps": None,
            },

            "DADE": {
                "nz": None,
                "nm": None,
                "Length": None,
                "Bulk density of porous media": None,
                "Run time": None,
                "Pulse time": None,
                "delta_t": None,
                "delta_x": None,
                "Porosity of the macropore region": None,
                "Porosity of the mesopore region": None,
                "Porosity of the micropore region": 1e-16,
                "Instantaneous sorption fraction in macropore region": 1e-16,
                "Instantaneous sorption fraction in mesopore region": 1e-16,
                "Instantaneous sorption fraction in micropore region": 1e-16,
                "Fraction of sorption site available for macropore region": 1e-16,
                "Fraction of sorption site available for mesopore region": 1e-16,
                "Fraction of sorption site available for immobile region": 1e-16,
                "Equilibrium sorption coefficient in macropore region": 1e-16,
                "Equilibrium sorption coefficient in mesopore region": 1e-16,
                "Equilibrium sorption coefficient in micropore region": 1e-16,
                "Rate-limited sorbed coefficient in macropore region": 1e-16,
                "Rate-limited sorbed coefficient in mesopore region": 1e-16,
                "Rate-limited sorbed coefficient in micropore region": 1e-16,
                "Mesopore seepage velocity": None,
                "Macropore seepage velocity": None,
                "Solute mass transfer rate b/w meso-micropore": 1e-16,
                "Solute mass transfer rate b/w meso-macropore": None,
                "Dispersivity": None,
                "No. of observation time steps": None,
            }
        }