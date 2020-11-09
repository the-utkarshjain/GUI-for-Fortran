from gui_base import GUIBase, PlotEncapsulator, GUI_exception
import threading
import time
import numpy as np
import matplotlib.pyplot as plt
import os
import hashlib
import random
import subprocess

class GUIMain(GUIBase):

    def __init__(self, *args, **kwargs):
        super(GUIMain, self).__init__(*args, **kwargs)

    @classmethod
    @GUI_exception
    def _refresh_utility(cls, first_file_path: str, second_file_path: str, third_file_path: str, memory: dict) -> bool:
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

        return isupdates

    @classmethod
    @GUI_exception
    def _nonblocking_execute_external_code(cls, exe_file_path: str, thread_queue: list):
        def target_func(x):
            return subprocess.call([x])

        t = threading.Thread(target=target_func, args=(exe_file_path,))
        thread_queue.append(t)
        t.start()

    @classmethod
    @PlotEncapsulator
    @GUI_exception
    def _plot_first_2D_data(cls, output_file_path: str, time_file_path: str):
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

        plt.plot(time,conc)
        plt.xlabel('Time')
        plt.ylabel('Concentration')
        plt.title('Concentration-Time graph')

    @classmethod
    @PlotEncapsulator
    @GUI_exception
    def _plot_second_2D_data(cls, output_file_path: str, time_file_path: str):
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

        plt.plot(time,conc1, label='1')
        plt.plot(time,conc2, label='2')
        plt.xlabel('Time')
        plt.ylabel('Concentration')
        plt.title('Concentration-Time graph')
        plt.legend()
    
    @classmethod
    @GUI_exception
    def _inplace_update_variable_dictionary(cls, first_file_path: str, second_file_path: str, third_file_path: str, variable_dictionary: dict) -> None:        
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
        try:
            file1 = open(first_file_path, "w")
            lines = ["Mesopore seepage velocity", "Macropore seepage velocity", "Solute mass transfer rate b/w meso-micropore", "Solute mass transfer rate b/w meso-macropore", "Dispersivity", "No. of observation time steps"]
            for line in lines:
                file1.write(variable_dictionary[line]+str("\n"))
        finally:
            file1.close()

        try:
            file3 = open(third_file_path, "w")
            lines = ["nz", "nm"]
            for line in lines[:-1]:
                file3.write(variable_dictionary[line]+str(" "))
            file3.write(variable_dictionary[lines[-1]]+str("\n"))
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
        pass

    @GUI_exception
    def _import_timestamps_data(self, first_file_path: str, second_file_path: str, third_file_path: str) -> list:
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

print(time_series)

    @GUI_exception
    def _export_concentration_data(self, time_series: list, first_file_path: str, second_file_path: str, third_file_path: str) -> None:
        pass

    @GUI_exception
    def _import_concentration_data(self, first_file_path: str, second_file_path: str, third_file_path: str) -> list:
        try:
            file1 = open(first_file_path, "r")
            for i in range(6):
                file1.readline()
            concentration_data = file1.read().splitlines()
        finally:
            file1.close()
        consentration_series = [float(i) for i in concentration_data]
        return consentration_series