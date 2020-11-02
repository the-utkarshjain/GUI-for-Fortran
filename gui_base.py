import PySimpleGUI as sg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import io
import pickle
from collections import deque
import os
import shutil


class _ToolbarGUI(NavigationToolbar2Tk):

    def __init__(self, *args, **kwargs):
        super(_ToolbarGUI, self).__init__(*args, **kwargs)


def PlotEncapsulator(func):

    def encapsulator(*args, **kwargs):
        plt.figure(1)
        fig = plt.gcf()
        DPI = fig.get_dpi()
        fig.set_size_inches(407 * 2 / float(DPI), 407 / float(DPI))
        func(*args, **kwargs)
        plt.grid()
        return fig

    return encapsulator


class GUIBase(object):

    def __init__(self, window_size, theme="Dark Teal 4", **kwargs):

        self._window_size = window_size
        self._extra_argument = kwargs
        self._refreshed = False
        self._first_input_path = None
        self._second_input_path = None
        self._third_input_path = None
        self._exe_file_path = None
        self._refresh_memory = {}
        self._thread_queue = deque()
        self._GUIKeys = {}
        self._window = None
        self._rendered_layout = None
        sg.theme(theme)
        self.WIN_CLOSED = sg.WIN_CLOSED
        self.PopupAnimated = sg.PopupAnimated
        self.DEFAULT_BASE64_LOADING_GIF = sg.DEFAULT_BASE64_LOADING_GIF

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
        raise NotImplementedError("This function needs to be implemented in child class by `Om Pandey`")

    @classmethod
    @PlotEncapsulator
    def _plot_first_2D_data(cls, output_file_path: str, time_file_path: str):
        raise NotImplementedError("This function needs to be implemented in child class by `Navya`")

    @classmethod
    @PlotEncapsulator
    def _plot_second_2D_data(cls, output_file_path: str, time_file_path: str):
        raise NotImplementedError("This function needs to be implemented in child class by `Navya`")

    @classmethod
    @PlotEncapsulator
    def _plot_both_2D_data(cls, output_file_path: str, time_file_path: str):
        raise NotImplementedError("This function needs to be implemented in child class by `Navya`")

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

        layout = [
            [sg.Text('Plotter GUI', justification='center', size=(50, 1), font=("Helvetica 20 bold"))],
            [sg.Input(key='-FILE1-', visible=False, enable_events=True), sg.FileBrowse(button_text="File1 Browse", key="File1 Browse"),
            sg.Input(key='-FILE2-', visible=False, enable_events=True), sg.FileBrowse(button_text="File2 Browse", key="File2 Browse"),
            sg.Input(key='-FILE3-', visible=False, enable_events=True), sg.FileBrowse(button_text="File3 Browse", key="File3 Browse"),
            sg.Input(key='-FILE4-', visible=False, enable_events=True), sg.FileBrowse(button_text="EXE Browse", key="EXE Browse"),
            sg.Button(button_text="Refresh", key="-REFRESH-")],
            [sg.TabGroup([[sg.Tab('Plot 1', plot1_layout), sg.Tab('Plot 2', plot2_layout),
                                                         sg.Tab('Plot 3', plot3_layout),]])],
            [sg.Text('Logs', font=("Helvetica 15 bold"), justification='center', size=(50, 1))],
            [sg.Output(size=(114, 5), key="-output-")]

        ]

        self._rendered_layout = layout
        return self._rendered_layout

    @property
    def window(self):
        if self._window:
            return self._window
        else:
            self._window = sg.Window(size=self._window_size, **self._extra_argument, 
                layout=self._rendered_layout if self._rendered_layout else self._create_layout())

            return self._window

    def _draw_plots(self):

        fig1 = self._plot_first_2D_data("./.tmp/output.dat", self._second_input_path)
        fig2 = self._plot_second_2D_data("./.tmp/output.dat", self._second_input_path)
        fig3 = self._plot_both_2D_data("./.tmp/output.dat", self._second_input_path)
        self._draw_plot_with_toolbar(self.window['fig_plot_1'].TKCanvas, fig1, self.window['controls_plot_1'].TKCanvas)
        self._draw_plot_with_toolbar(self.window['fig_plot_2'].TKCanvas, fig2, self.window['controls_plot_2'].TKCanvas)
        self._draw_plot_with_toolbar(self.window['fig_plot_3'].TKCanvas, fig3, self.window['controls_plot_3'].TKCanvas)

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

    @property
    def is_processing(self):
        return self._is_any_thread_running()

    def freeze_buttons(self):
        self.window["File1 Browse"].update(disabled=True)
        self.window["File2 Browse"].update(disabled=True)
        self.window["File3 Browse"].update(disabled=True)
        self.window["EXE Browse"].update(disabled=True)
        self.window["-REFRESH-"].update(disabled=True)

    def unfreeze_buttons(self):
        self.window["File1 Browse"].update(disabled=False)
        self.window["File2 Browse"].update(disabled=False)
        self.window["File3 Browse"].update(disabled=False)
        self.window["EXE Browse"].update(disabled=False)
        self.window["-REFRESH-"].update(disabled=False)

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
            new_path = "./.tmp/{}".format(ext)
            shutil.copy(path, new_path)
            self._first_input_path = new_path

    @second_input_path.setter
    def second_input_path(self, path):
        if path:
            ext = os.path.basename(path)
            new_path = "./.tmp/{}".format(ext)
            shutil.copy(path, new_path)
            self._second_input_path = new_path

    @third_input_path.setter
    def third_input_path(self, path):
        if path:
            ext = os.path.basename(path)
            new_path = "./.tmp/{}".format(ext)
            shutil.copy(path, new_path)
            self._third_input_path = new_path

    @exe_file_path.setter
    def exe_file_path(self, path):
        if path:
            ext = os.path.basename(path)
            new_path = "./.tmp/{}".format(ext)
            shutil.copy(path, new_path)
            self._exe_file_path = new_path

    


