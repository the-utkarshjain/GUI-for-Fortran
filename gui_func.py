from gui_base import GUIBase, PlotEncapsulator
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
    def _nonblocking_execute_external_code(cls, exe_file_path: str, thread_queue: list):
        def target_func(x):
            return subprocess.call([x])

        t = threading.Thread(target=target_func, args=(exe_file_path,))
        thread_queue.append(t)
        t.start()

    @classmethod
    @PlotEncapsulator
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
    def _inplace_update_variable_dictionary(cls, first_file_path: str, second_file_path: str, third_file_path: str, variable_dictionary: dict) -> None:
        pass

    @classmethod
    def _write_updated_values(cls, first_file_path: str, second_file_path: str, third_file_path: str, variable_dictionary: dict) -> None:
        pass