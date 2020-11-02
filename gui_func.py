from gui_base import GUIBase, PlotEncapsulator
import threading
import time
import numpy as np
import matplotlib.pyplot as plt
import os
import hashlib
import random

class GUIMain(GUIBase):

    def __init__(self, *args, **kwargs):
        super(GUIMain, self).__init__(*args, **kwargs)

    @classmethod
    def _refresh_utility(cls, first_file_path: str, second_file_path: str, third_file_path: str, memory: dict) -> bool:
        
        isupdates = False
        checksum_file_1 = hashlib.md5(open(first_file_path).read()).hexdigest()
        checksum_file_2 = hashlib.md5(open(second_file_path).read()).hexdigest()
        checksum_file_3 = hashlib.md5(open(third_file_path).read()).hexdigest()

        if(memory.get(first_file_path, None) != checksum_file_1):
            memory[first_file_path] = checksum_file_1
            isupdates = True

        if(memory.get(second_file_path, None) != checksum_file_2):
            memory[second_file_path] = checksum_file_2
            isupdates = True
            
        if(memory.get(third_file_path, None) != checksum_file_3):
            memory[third_file_path] = checksum_file_3
            isupdates = True  

        if(isupdates == False):
            print("No updates found in the input file.")

        return isupdates

    @classmethod
    def _nonblocking_execute_external_code(cls, exe_file_path: str, thread_queue: list):
        t = threading.Thread(target = lambda x: os.system(exe_file_path) , args = (random.randint(1, 10),))
        thread_queue.append(t)
        t.start()

    @classmethod
    @PlotEncapsulator
    def _plot_first_2D_data(cls, output_file_path: str, time_file_path: str):
        pass

    @classmethod
    @PlotEncapsulator
    def _plot_second_2D_data(cls, output_file_path: str, time_file_path: str):
        pass

    @classmethod
    @PlotEncapsulator
    def _plot_both_2D_data(cls, output_file_path: str, time_file_path: str):
        pass
