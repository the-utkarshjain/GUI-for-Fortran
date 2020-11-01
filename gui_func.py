from gui_base import GUIBase, PlotEncapsulator
import threading
import time
import numpy as np
import matplotlib.pyplot as plt


class GUIMain(GUIBase):

    def __init__(self, *args, **kwargs):
        super(GUIMain, self).__init__(*args, **kwargs)

    @classmethod
    def _refresh_utility(cls, first_file_path: str, second_file_path: str, third_file_path: str, memory: dict) -> bool:
        pass

    @classmethod
    def _nonblocking_execute_external_code(cls, exe_file_path: str, thread_queue: list):
        pass

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