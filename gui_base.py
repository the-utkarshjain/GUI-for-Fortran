"""
@name 
    `gui_base.py`

@description 
    `src file for GUI base class`

@package 
    `GUI for Fortran/C++ Application`

@official_repository 
    `https://github.com/the-utkarshjain/GUI-for-Fortran`

@contributors 
    * Abhishek Bhardwaj
    * Utkarsh Jain
    * Jhalak Choudhary
    * Navya
    * Om Pandey

@dependency
    * PySimpleGUI >= v4.30.0
    * numpy >= v18.0
    * matplotlib >= v3.3.2

"""


r'''
Import necessary packages,
works only for python >= v3.7
'''

import sys
ver_error = "GUI script works for python version >= 3.7" 
try:
    assert sys.version_info >= (3, 7) 
except AssertionError as aE:
    raise OSError(ver_error)
import functools
import PySimpleGUI as sg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import io
import pickle
from collections import deque
import os
import shutil
import warnings
import uuid
from gui_radio import GUIVariableSetter, GUILimitSetter, GUIModeInitializer
import subprocess
from collections import defaultdict
import threading
import time


class _ToolbarGUI(NavigationToolbar2Tk):
    r'''
    Create custom toolbar for <matplotplib.pyplot>
    '''

    def __init__(self, *args, **kwargs):
        super(_ToolbarGUI, self).__init__(*args, **kwargs)


def GUI_exception(f):
    r'''
    Wrapper function to handle GUI function 
    exceptions
    '''

    @functools.wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            GUIError(f.__name__, e)
    return func



class GUIError(RuntimeError):
    r'''
    Custom exception class to raise GUI errors
    '''

    def __init__(self, name, message):

        ID = str(uuid.uuid1())
        GUI_Warning = "[{}] Error in {}: {}".format(ID, name, message)
        warnings.warn(GUI_Warning)
        sg.popup(GUI_Warning, title="Error")


def PlotEncapsulator(func):
    r'''
    Wrapper function to catch matplotlib figure into <matplotlib.pyplot.figure> 
    '''
    def encapsulator(*args, **kwargs):
        plt.figure(1)
        fig = plt.gcf()
        buf = io.BytesIO()
        pickle.dump(fig, buf)
        buf.seek(0)
        fig = pickle.load(buf)
        DPI = fig.get_dpi()
        fig.set_size_inches(407 * 2 / float(DPI), 407 / float(DPI))
        func(*args, **kwargs)
        plt.grid()
        return fig
    return encapsulator


class GUIBase(object):
    r'''
    <__main__.GUIBase> class implementing GUI skeleton.
    Note: This is super class, use GUIMain class during implementation

    Usage:
        >>> GUI = GUIMain(window_size=(800, 700), title="GUI", auto_size_buttons=False, 
                auto_size_text=False, finalize=True, element_justification='center', resizable=True)

        >>> while True:
                event, values = GUI.window.read(timeout=50)

                if event == GUI.WIN_CLOSED:
                    break 
    '''

    def __init__(self, window_size, theme="Dark Teal 4", **kwargs):

        self._window_size = window_size
        self._extra_argument = kwargs
        self._refreshed = False
        self._first_input_path = "./in_1.dat" if os.path.exists("./in_1.dat") else None
        self._second_input_path = "./in_2.dat" if os.path.exists("./in_2.dat") else None
        self._third_input_path = "./in_3.dat" if os.path.exists("./in_3.dat") else None
        self._exe_file_path = "./test.exe" if os.path.exists("./test.exe") else None
        self._refresh_memory = {}
        self._thread_queue = deque()
        self._GUIKeys = {}
        self._window = None
        self._rendered_layout = None
        sg.theme(theme)
        self.WIN_CLOSED = sg.WIN_CLOSED
        self.PopupAnimated = sg.PopupAnimated
        self.DEFAULT_BASE64_LOADING_GIF = sg.DEFAULT_BASE64_LOADING_GIF
        self.processing = False
        self._VariableDict = {
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
            "Porosity of the micropore region": None,
            "Instantaneous sorption fraction in macropore region": None,
            "Instantaneous sorption fraction in mesopore region": None,
            "Instantaneous sorption fraction in micropore region": None,
            "Fraction of sorption site available for macropore region": None,
            "Fraction of sorption site available for mesopore region": None,
            "Fraction of sorption site available for immobile region": None,
            "Equilibrium sorption coefficient in macropore region": None,
            "Equilibrium sorption coefficient in mesopore region": None,
            "Equilibrium sorption coefficient in micropore region": None,
            "Rate-limited sorbed coefficient in macropore region": None,
            "Rate-limited sorbed coefficient in mesopore region": None,
            "Rate-limited sorbed coefficient in micropore region": None,
            "Mesopore seepage velocity": None,
            "Macropore seepage velocity": None,
            "Solute mass transfer rate b/w meso-micropore": None,
            "Solute mass transfer rate b/w meso-macropore": None,
            "Dispersivity": None,
            "No. of observation time steps": None,
        }
        self.is_initialized = False
        self._base_value = [[idx, "NA"] for idx in range(1, 43)] 
        self._timestamp_value = [[idx, "NA"] for idx in range(1, 43)]

        if not os.path.exists("./.tmp"):
            os.mkdir("./.tmp")
        


    def _create_plot_tab(self, toolbar_key, plot_key, plot_size=(400*2, 400), bg_color="#DAE0E6"):

        tab_layout = [[
            sg.Column(
                layout=[
                    [sg.Canvas(key=toolbar_key)],
                    [sg.Canvas(key=plot_key,
                        size=plot_size)]
                ],
                background_color=bg_color,
                pad=(6, 2)
            )]
        ]

        return tab_layout

    def _create_search_tab(self):
        tab_layout = [[
            sg.Column(
                layout=[
                    [sg.Text("Variable Editor")],
                    [sg.Input(size=(45, 1), enable_events=True, key='-SEARCH-', default_text="")],
                    [sg.Listbox(list(self._VariableDict.keys()), size=(45, 20), enable_events=True, key='-SEARCH-LIST-', 
                                            auto_size_text=True, pad=(5, 20))],
                    ]
            ), 
            sg.VSeperator(),
            sg.Column(
                layout=
                    [
                        [sg.Text("Variable Values")],
                        [sg.Table(values=[[x, str(self._VariableDict[x])] for x in self._VariableDict.keys()], headings=["Variable", "Current Value"],
                        col_widths=90, justification='left', font=("Helvetica 10 bold"),
                        num_rows=8, key="-VARIABLE-TABLE-", row_height=42, vertical_scroll_only=False, alternating_row_color="black")]
                ]
            )
            ]
        ]
        return tab_layout


    def _create_editable_table_tab(self):
        tab_layout = [[
            sg.Column(
                layout=[
                    [sg.Text("Base Values", justification="center")],
                    [sg.Table(values=self._base_value, headings=["S.No", "Current Value"],
                        col_widths=90, justification='left', font=("Helvetica 10 bold"),
                        num_rows=8, key="-BASE-VALUE-TABLE-", row_height=42, vertical_scroll_only=True, alternating_row_color="lightblue", enable_events=True)],
                    [sg.Button("Import Data", enable_events=True, key="-BASE-COPY-", auto_size_button=True)]],
                        element_justification="center"
            ), 
            sg.VSeperator(),
            sg.Column(
                layout=
                    [
                        [sg.Text("Timestamp Values", justification="center")],
                        [sg.Table(values=self._timestamp_value, headings=["S.No", "Current Value"],
                        col_widths=90, justification='left', font=("Helvetica 10 bold"),
                        num_rows=8, key="-TIMESTAMP-TABLE-", row_height=42, vertical_scroll_only=True, alternating_row_color="lightblue", enable_events=True)],
                        [sg.Button("Import Data", enable_events=True, key="-TIMESTAMP-COPY-", auto_size_button=True)]
                ],
                element_justification="center"
            )
            ]
        ]

        return tab_layout


    @staticmethod
    def _draw_plot_with_toolbar(canvas, fig, canvas_toolbar):
        if canvas.children:
            for child in canvas.winfo_children():
                child.destroy()
        if canvas_toolbar.children:
            for child in canvas_toolbar.winfo_children():
                child.destroy()
        figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
        figure_canvas_agg.draw()
        toolbar = _ToolbarGUI(figure_canvas_agg, canvas_toolbar)
        toolbar.update()
        figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=1)


    @classmethod
    def _refresh_utility(cls, first_file_path: str, second_file_path: str, third_file_path: str, memory: dict) -> bool:
        """
        name: _refresh_utility
        definition: gui_func.py
        description: Checks if any of the input files are changed/updated.
        @params:
        1. cls: Class object
        2. first_file_path: Path of the first input file
        3. second_file_path: Path of the second input file
        4. third_file_path: Path of the third input file
        5. memory: A dictionary containing previous md5 fingerprint
        @returns: Bool:True, if any updates detected. Bool:False othewise.
        """
        raise NotImplementedError("This function needs to be implemented in child class by `Utkarsh Jain`")

    @classmethod
    def _nonblocking_execute_external_code(cls, exe_file_path: str, thread_queue: list):
        """
        name: _nonblocking_execute_external_code
        definition: gui_func.py
        description: Runs the modeling in a seperate thread to keep thr GUI interactive.
        @params:
        1. cls: Class object
        2. exe_file_path: Path of the exec file
        3. thread_queue: List of all the running threads
        @returns: None
        """
        raise NotImplementedError("This function needs to be implemented in child class by `Om Pandey`")

    @classmethod
    @PlotEncapsulator
    def _plot_first_2D_data(cls, output_file_path: str, time_file_path: str):
        """
        name: _plot_first_2D_data
        definition: gui_func.py
        description: Plot the concentration vs time graph for experimental data.
        @params:
        1. cls: Class object
        2. output_file_path: Path of the file containing the experimental data
        3. time_file_path: Path of the file containing the time stamps
        @returns: None
        """
        raise NotImplementedError("This function needs to be implemented in child class by `Navya`")

    @classmethod
    @PlotEncapsulator
    def _plot_second_2D_data(cls, output_file_path: str, time_file_path: str):
        """
        name: _plot_second_2D_data
        definition: gui_func.py
        description: Plot the concentration vs time graph for experimental data.
        @params:
        1. cls: Class object
        2. output_file_path: Path of the file containing the simulated data
        3. time_file_path: Path of the file containing the time stamps
        @returns: None
        """
        raise NotImplementedError("This function needs to be implemented in child class by `Navya`")

    @classmethod
    @PlotEncapsulator
    def _plot_both_2D_data(cls, output_file_path: str, time_file_path: str):
        """
        name: _plot_second_2D_data
        definition: gui_func.py
        description: Plot the combined experimental and simulated data in a single graph.
        @params:
        1. cls: Class object
        2. output_file_path: Path of the file containing the simulated data
        3. time_file_path: Path of the file containing the time stamps
        @returns: None
        """
        raise NotImplementedError("This function needs to be implemented in child class by `Navya`")
    
    # This function generates the overall GUI and controls the overall placements of different components.
    def _create_layout(self):

        self._GUIKeys = {
            "File1 Browse": "-FILE1-",
            "File2 Browse": "-FILE2-",
            "File3 Browse": "-FILE3-",
            "File4 Browse": "-FILE4-",
            "Refresh": "-REFRESH-",
            "log": "-output-",
            "plot_1_toolbar": "controls_plot_1",
            "plot_1_canvas":  "fig_plot_1",
            "plot_2_toolbar": "controls_plot_2",
            "plot_2_canvas":  "fig_plot_2",
            "plot_3_toolbar": "controls_plot_3",
            "plot_3_canvas":  "fig_plot_3"
        }

        plot1_layout = self._create_plot_tab("controls_plot_1", "fig_plot_1")
        plot2_layout = self._create_plot_tab("controls_plot_2", "fig_plot_2")
        plot3_layout = self._create_plot_tab("controls_plot_3", "fig_plot_3")
        plot4_layout = self._create_search_tab()
        plot5_layout = self._create_editable_table_tab()

        layout = [
            [sg.Text('Plotter/Optimiser GUI', justification='center', size=(50, 1), font=("Helvetica 20 bold"))],
            [sg.Input(key='-FILE1-', visible=False, enable_events=True), sg.B(button_text="File1 Browse", key="File1 Browse", visible=False),
            sg.Input(key='-FILE2-', visible=False, enable_events=True), sg.B(button_text="File2 Browse", key="File2 Browse", visible=False),
            sg.Input(key='-FILE3-', visible=False, enable_events=True), sg.B(button_text="File3 Browse", key="File3 Browse", visible=False),
            sg.Input(key='-FILE4-', visible=False, enable_events=True), sg.B(button_text="EXE Browse", key="EXE Browse", visible=False),
            sg.Button(button_text="Run / Refresh", key="-REFRESH-"),
            sg.Button(button_text="PE Mode", key="PE/FM")],
            [sg.TabGroup([[sg.Tab('Experimental Plot', plot1_layout), sg.Tab('Simulation Plot', plot2_layout),
                                                         sg.Tab('Dual Plot', plot3_layout),
                                                         sg.Tab('Variable Editor', plot4_layout, visible=False),
                                                         sg.Tab('Experimental Data', plot5_layout)]])],
            [sg.Text('Logs', font=("Helvetica 15 bold"), justification='center', size=(50, 1))],
            [sg.Output(size=(114, 10), key="-output-")]

        ]

        self._rendered_layout = layout
        return self._rendered_layout

    @property
    def window(self):
        if not self.is_initialized:
            try:
                self._inplace_update_variable_dictionary(self._first_input_path, self._second_input_path, self._third_input_path, self._VariableDict)
            except Exception:
                pass
            variable_dict = self._initialize_variables()
            modes = variable_dict.keys()
            all_variables = self._VariableDict.keys()
            initializer = GUIModeInitializer(modes, all_variables, variable_dict, auto_dict=self._VariableDict)
            result = initializer.run()
            if result == None:
                raise SystemExit("GUI operation terminated")
            self._VariableDict = result
            for key in self._VariableDict:
                self._VariableDict[key] = str(self._VariableDict[key])
            self._write_updated_values(self._first_input_path, self._second_input_path, self._third_input_path, self._VariableDict)
            self.is_initialized = True

        if self._window:
            return self._window
        else:
            self._window = sg.Window(size=self._window_size, **self._extra_argument, 
                layout=self._rendered_layout if self._rendered_layout else self._create_layout())

            return self._window

    # Function to plot all the three graphs and display them in their repsective tabs.
    def _draw_plots(self):

        fig1 = self._plot_first_2D_data("./output.dat", self._second_input_path)
        fig2 = self._plot_second_2D_data("./output.dat", self._second_input_path)
        fig3 = self._plot_both_2D_data("./output.dat", self._second_input_path)
        self._draw_plot_with_toolbar(self.window['fig_plot_1'].TKCanvas, fig1, self.window['controls_plot_1'].TKCanvas)
        self._draw_plot_with_toolbar(self.window['fig_plot_2'].TKCanvas, fig2, self.window['controls_plot_2'].TKCanvas)
        self._draw_plot_with_toolbar(self.window['fig_plot_3'].TKCanvas, fig3, self.window['controls_plot_3'].TKCanvas)

    # Function to check if any thread is still running.
    def _is_any_thread_running(self):

        if self._thread_queue:
            for idx in range(len(self._thread_queue)):
                curr_thread = self._thread_queue.popleft()
                if curr_thread.is_alive():
                    self._thread_queue.append(curr_thread)
                else:
                    curr_thread.join()
                    self._draw_plots()
        
        return True if self._thread_queue else False

    # Controls the functionality of the Run/Refresh buttons. Checks if all the files are uploaded or not.
    def refresh(self):

        if self._first_input_path is None:
            sg.Popup("Path of Input file 1 is not defined")
            return 
        elif self._second_input_path is None:
            sg.Popup("Path of Input file 2 is not defined")
            return 
        elif self._third_input_path is None:
            sg.Popup("Path of Input file 3 is not defined")
            return    

        is_refresh_required = False
        is_refresh_required = self._refresh_utility(self._first_input_path, self._second_input_path, self._third_input_path, self._refresh_memory)

        if is_refresh_required is False:
            return
        
        if self._exe_file_path is None:
            sg.Popup("Path of test.exe is not defined")
            return

        self._nonblocking_execute_external_code(self._exe_file_path, self._thread_queue)
        self.window["-VARIABLE-TABLE-"].update(values=[[x, str(self._VariableDict[x])] for x in self._VariableDict.keys()])
        to_write = self._import_timestamps_data(self.first_input_path, self.second_input_path, self.third_input_path)
        self._timestamp_value = [[idx+1, val] for idx, val in enumerate(to_write)]
        to_write = self._import_concentration_data(self.first_input_path, self.second_input_path, self.third_input_path)
        self._base_value = [[idx+1, val] for idx, val in enumerate(to_write)]
        self.window["-BASE-VALUE-TABLE-"].update(values=self._base_value)
        self.window["-TIMESTAMP-TABLE-"].update(values=self._timestamp_value)

    @property
    def is_processing(self):
        return self._is_any_thread_running() or self.processing

    def freeze_buttons(self):
        self.window["File1 Browse"].update(disabled=True)
        self.window["File2 Browse"].update(disabled=True)
        self.window["File3 Browse"].update(disabled=True)
        self.window["EXE Browse"].update(disabled=True)
        self.window["-REFRESH-"].update(disabled=True)
        self.window["PE/FM"].update(disabled=True)

    def unfreeze_buttons(self):
        self.window["File1 Browse"].update(disabled=False)
        self.window["File2 Browse"].update(disabled=False)
        self.window["File3 Browse"].update(disabled=False)
        self.window["EXE Browse"].update(disabled=False)
        self.window["-REFRESH-"].update(disabled=False)
        self.window["PE/FM"].update(disabled=False)

    @property
    def first_input_path(self):
        return self._first_input_path

    @property
    def second_input_path(self):
        return self._second_input_path

    @property
    def third_input_path(self):
        return self._third_input_path

    @property
    def exe_file_path(self):
        return self._exe_input_path

    @first_input_path.setter
    def first_input_path(self, path):
        if path:
            ext = os.path.basename(path)
            new_path = "./in_1.dat"
            shutil.copy(path, new_path)
            self._first_input_path = new_path

    @second_input_path.setter
    def second_input_path(self, path):
        if path:
            ext = os.path.basename(path)
            new_path = "./in_2.dat"
            shutil.copy(path, new_path)
            self._second_input_path = new_path

    @third_input_path.setter
    def third_input_path(self, path):
        if path:
            ext = os.path.basename(path)
            new_path = "./in_3.dat"
            shutil.copy(path, new_path)
            self._third_input_path = new_path

    @exe_file_path.setter
    def exe_file_path(self, path):
        if path:
            ext = os.path.basename(path)
            new_path = "./test.exe"
            shutil.copy(path, new_path)
            self._exe_file_path = new_path

    def refresh_search_list(self, params):
        if params != "":
            new_values = [x for x in self._VariableDict.keys() if params.lower().replace(" ", "") in x.lower().replace(" ", "")]
            self.window['-SEARCH-LIST-'].update(values=new_values)
        else:
            self.window['-SEARCH-LIST-'].update(values=list(self._VariableDict.keys()))

    def update_variable(self, variable_name):
        temp = sg.popup_get_text("Enter value for {}".format(variable_name), default_text=str(self._VariableDict[variable_name] \
                                                                if variable_name in self._VariableDict \
                                                                and self._VariableDict[variable_name] is not None else ""))
        if temp:
            self._VariableDict[variable_name] = temp
            self.window["-VARIABLE-TABLE-"].update(values=[[x, str(self._VariableDict[x])] for x in self._VariableDict.keys()])
            self._write_updated_values(self._first_input_path, self._second_input_path, self._third_input_path, self._VariableDict)

    @classmethod
    def _inplace_update_variable_dictionary(cls, first_file_path: str, second_file_path: str, third_file_path: str, variable_dictionary: dict) -> None:

        raise NotImplementedError("This function needs to be implemented in child class")

    @classmethod
    def _write_updated_values(cls, first_file_path: str, second_file_path: str, third_file_path: str, variable_dictionary: dict) -> None:

        raise NotImplementedError("This function needs to be implemented in child class")

    def edit_table_cells(self, table_key, row_value):
        if table_key == "-BASE-VALUE-TABLE-":
            new_val = sg.popup_get_text("Enter value for entry {} from Base Values".format(row_value+1), default_text=str(self._base_value[row_value][1]))
            if new_val:
                row_value = int(row_value)
                self._base_value[row_value][1] = float(new_val)
                self.window[table_key].update(values=self._base_value)
                to_save = ['2.64E-01', '3.60E-01', '4.70E-05', '5.20E-01', '9.76E-03', len(self._base_value)] + list(map(lambda x: x[1], self._base_value))
                self._VariableDict["No. of observation time steps"] = str(len(self._base_value))
                self._export_concentration_data(to_save, self.first_input_path, self.second_input_path, self.third_input_path)
                self._write_updated_values(self.first_input_path, self.second_input_path, self.third_input_path, self._VariableDict)

        if table_key == "-TIMESTAMP-TABLE-":
            new_val = sg.popup_get_text("Enter value for entry {} from Timestamps".format(row_value+1), default_text=str(self._timestamp_value[row_value][1]))
            if new_val:
                row_value = int(row_value)
                self._timestamp_value[row_value][1] = float(new_val)
                self.window[table_key].update(values=self._timestamp_value)
                to_save = [1, 16.87] + list(map(lambda x: x[1], self._timestamp_value))
                self._export_timestamps_data(to_save, self.first_input_path, self.second_input_path, self.third_input_path)

    def _new_window_for_copy_paste(self):
        layout = [[sg.Text('< Data Importer >', font=('Consolas', 10), size=(90, 1), key='_INFO_', justification="left")],
                  [sg.Multiline(font=('Consolas', 12), size=(90, 25), key='_BODY_')],
                  [sg.Button("Save", enable_events=True, key="-save-")]]

        window = sg.Window('Edit Window', layout=layout, margins=(0, 0), return_keyboard_events=True, finalize=True, element_justification="center")

        while True:
            events, values = window.read()

            if events == sg.WINDOW_CLOSED:
                break
            if events == "-save-":
                break
                
        window.close()
        return values["_BODY_"] if values and values.get("_BODY_", None) else ""

    def import_data(self, section_key):
        value = self._new_window_for_copy_paste()

        if section_key == "-BASE-COPY-":
            value = value.split("\n")
            value = list(filter(lambda x: len(x) > 0, value))

            self._base_value = [[idx+1, val] for idx, val in enumerate(value)]
            to_save = ['2.64E-01', '3.60E-01', '4.70E-05', '5.20E-01', '9.76E-03', len(self._base_value)] + list(map(lambda x: x[1], self._base_value))
            self.window["-BASE-VALUE-TABLE-"].update(values=self._base_value)
            self._VariableDict["No. of observation time steps"] = str(len(self._base_value))
            self._export_concentration_data(to_save, self.first_input_path, self.second_input_path, self.third_input_path)
            self._write_updated_values(self.first_input_path, self.second_input_path, self.third_input_path, self._VariableDict)


        if section_key == "-TIMESTAMP-COPY-":
            value = value.split("\n")
            value = list(filter(lambda x: len(x) > 0, value))

            self._timestamp_value = [[idx+1, val] for idx, val in enumerate(value)]
            self.window["-TIMESTAMP-TABLE-"].update(values=self._timestamp_value)
            to_save = [1, 16.87] + list(map(lambda x: x[1], self._timestamp_value))
            self._export_timestamps_data(to_save, self.first_input_path, self.second_input_path, self.third_input_path)

    def _export_timestamps_data(self, time_series: list, first_file_path: str, second_file_path: str, third_file_path: str) -> None:

        raise NotImplementedError("This function is to be implemented in child class")

    def _import_timestamps_data(self, first_file_path: str, second_file_path: str, third_file_path: str) -> list:
        """
        name: _import_timestamps_data
        definition: gui_func.py
        description: parsing the timestamps from the file for plotting.
        @params:
        1. cls: Class object
        2. first_file_path: Path of the first input file
        3. second_file_path: Path of the second input file
        4. third_file_path: Path of the third input file
        @returns: List of all the timestamps.
        """
        raise NotImplementedError("This function is to be implemented in child class")

    def _export_concentration_data(self, time_series: list, first_file_path: str, second_file_path: str, third_file_path: str) -> None:

        raise NotImplementedError("This function is to be implemented in child class")

    def _import_concentration_data(self, first_file_path: str, second_file_path: str, third_file_path: str) -> list:
        """
        name: _import_concentration_data
        definition: gui_func.py
        description: parsing the concentration dat from the file for plotting.
        @params:
        1. cls: Class object
        2. first_file_path: Path of the first input file
        3. second_file_path: Path of the second input file
        4. third_file_path: Path of the third input file
        @returns: List of all the concentration values.
        """
        raise NotImplementedError("This function is to be implemented in child class")

    def run_parameter_estimation(self):

        variable_name = [
            "Mesopore seepage velocity",
            "Macropore seepage velocity",
            "Solute mass transfer rate b/w meso-micropore",
            "Solute mass transfer rate b/w meso-macropore",
            "Dispersivity",
        ]
        variable_alias = {
            "Mesopore seepage velocity": "qs",
            "Macropore seepage velocity": "qf",
            "Solute mass transfer rate b/w meso-micropore": "omegaim",
            "Solute mass transfer rate b/w meso-macropore": "omegasf",
            "Dispersivity": "alpha"
        }

        ve = GUIVariableSetter(variable_name)
        variable_state = ve.run()
        if variable_state is None:
        	print(">>> PE Mode was cancelled")
        	return None

        with open("in_1.tpl", "w") as f:
            f.write("ptf #\n")
            for key in variable_alias:
                if variable_state[key] == "determined":
                    f.write("{}\n".format(self._VariableDict[key]))
                else:
                    f.write("# {} #\n".format(variable_alias[key]))
            f.write("{}\n".format(len(self._base_value)))
            f_values = map(lambda x: str(x[1]), self._base_value)
            f.write("\n".join(f_values))

        process = subprocess.Popen("tempchek.exe in_1.tpl", shell=True, stdout=subprocess.PIPE)
        process_out = "{}".format(process.stdout.read().decode("utf-8"))
        print(">>> [INFO] Running tempchek")
        print(process_out)

        if "No errors encountered" in process_out:
            print("Executed Successfully")
            # print(process_out)

        with open("in_1.par", "w") as f:
            f.write("single point\n")
            for key in variable_alias:
                if variable_state[key] != "determined":
                    f.write("{} {} 1.0 0.0\n".format(variable_alias[key], variable_state[key]))
        
        process = subprocess.Popen("tempchek.exe in_1.tpl in_1.dat in_1.par", shell=True, stdout=subprocess.PIPE)
        process_out = "{}".format(process.stdout.read().decode("utf-8"))
        print(">>> [INFO] Running tempchek again")
        print(process_out)

        with open("output.ins", "w") as f:
            f.write("pif #\n")
            to_write = ["l1 (o{})19:26".format(idx) for idx in range(1, len(self._base_value)+1)]
            f.write("\n".join(to_write))

        process = subprocess.Popen("inschek.exe output.ins output.dat", shell=True, stdout=subprocess.PIPE)
        process_out = "{}".format(process.stdout.read().decode("utf-8"))
        print(">>> [INFO] Running inschek")
        print(process_out)

        with open("measure.obf", "w") as f:
            to_write = map(lambda x: "o{} {}".format(x[0], x[1]), self._base_value)
            f.write("\n".join(to_write))

        process = subprocess.Popen("pestgen.exe test in_1.par measure.obf", shell=True, stdout=subprocess.PIPE)
        process_out = "{}".format(process.stdout.read().decode("utf-8"))
        print(">>> [INFO] Running pestgen")
        print(process_out)
        

        test_pst = ""

        with open("test.pst", "r") as f:
            test_pst = f.readlines()

        test_pst_store = defaultdict(list)
        curr = None

        for line in test_pst:
            if "*" in line:
                curr = line.replace("\n", "")
            elif curr:
                test_pst_store[curr].append(line.replace("\n", ""))

        variable_name = {}

        for ln in test_pst_store["* parameter data"]:
            line = ln.split()
            variable_name[line[0]] = {"lower": line[4], "upper": line[5]}

        bound_gui = GUILimitSetter(variable_name)
        variable_state = bound_gui.run()

        if variable_state is None:
        	print(">>> PE Mode was cancelled")
        	return None


        for idx, ln in enumerate(test_pst_store["* parameter data"]):
            line = ln.split()
            test_pst_store["* parameter data"][idx] = "  ".join([line[0], line[1], line[2], line[3], variable_state[line[0]]["lower"], variable_state[line[0]]["upper"]] + line[6:])

       
        test_pst_store["* model command line"][0] = "test"
        test_pst_store["* model input/output"][0] = "in_1.tpl  in_1.dat"
        test_pst_store["* model input/output"][1] = "output.ins  output.dat"

        with open("test.pst", "w") as f:
            f.write("pcf\n")
            for key in test_pst_store:
                f.write("{}\n".format(key))
                if test_pst_store[key]:
                    f.write("\n".join(test_pst_store[key]))
                    f.write("\n")

        process = subprocess.Popen("pestchek.exe test", shell=True, stdout=subprocess.PIPE)
        process_out = "{}".format(process.stdout.read().decode("utf-8"))
        print(">>> [INFO] Running pestchek")
        print(process_out)
        
        def pest_process(obj):
            obj.processing = True
            process = subprocess.Popen("pest.exe test", shell=True, stdout=subprocess.PIPE)
            process_out = "{}".format(process.stdout.read().decode("utf-8"))
            print(">>> [INFO] Running pest")
            print(process_out)
            # print(process_out)
            obj.processing = False

        pest_thread = threading.Thread(target=pest_process, args=(self,), daemon=True)
        pest_thread.start()

        while self.processing:
            self.PopupAnimated(self.DEFAULT_BASE64_LOADING_GIF, background_color='green', transparent_color='green')
            self.freeze_buttons()
            time.sleep(0.1)
        
        self.PopupAnimated(None)
        self.unfreeze_buttons()

        test_rec = {}

        with open("test.rec", "r") as f:
            test_rec = f.readlines()

        for idx, line in enumerate(test_rec):
            test_rec[idx] = test_rec[idx].replace("\n", "")

        test_rec_store = defaultdict(list)
        curr = None

        for line in test_rec:
            if "----->" in line:
                curr = line.replace("\n", "")
            if curr:
                test_rec_store[curr].append(line.replace("\n", ""))


        def show_information(content, title):
            layout = [[sg.Multiline(default_text=content, size=(60,20))]]
            window = sg.Window(title=title, layout=layout)
            events, values = window.read(close=True)

        if not test_rec_store["K-L information statistics ----->"] or not test_rec_store["Parameters ----->"]:
            sg.popup_error("Some error occurred, please check logs for more info\n")
        else:
            show_information("\n".join(test_rec_store["K-L information statistics ----->"]), title="K-L information statistics")
            show_information("\n".join(test_rec_store["Parameters ----->"]), title="Parameter Estimation Result")

    @GUI_exception
    def _initialize_variables(self):

        raise NotImplementedError("This method is to be implemented in child class")

