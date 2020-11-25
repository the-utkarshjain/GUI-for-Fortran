import PySimpleGUI as sg
from copy import deepcopy


class GUIVariableSetter(object):

    def __init__(self, variable_name):
        self.variable_name = variable_name
        self.variable_status = {x: None for x in variable_name}
        self.selected_color = ('red', 'white')

        self.layout = [
            [sg.Column(layout=[[sg.Text("Variable Settings", font=("Helvetica", 16))]], element_justification="center", expand_x=True)],
            [sg.Column(layout = [[sg.Text(var_name, pad=(6, 5), font=("Helvetica 10 bold"))] for var_name in variable_name]),
            sg.VSeparator(),
            sg.Column(layout = [[sg.Button("Determined", key="determined_{}".format(var_name)), sg.Button("Initial Guess", key="guess_{}".format(var_name)), sg.In(key="value_{}".format(var_name), visible=False, size=(8, 1), enable_events=True)] for var_name in variable_name])],
            [sg.Column(layout=[[sg.Button("Submit", key="exit", pad=(2, 2))]], expand_x=True, element_justification="center")]
        ]

        self.window = sg.Window(title="Variable Setter", layout=self.layout, use_default_focus=False)

    def run(self):
        while True:
            event, values = self.window.read()
            if event in [sg.WINDOW_CLOSED, "exit"]:
                if None in self.variable_status.values():
                    sg.popup_error("You have to supply input for every variable")
                    continue
                break
            else:
                prefix, base = event.split("_")
                if prefix == "value":
                    try:
                        self.variable_status[base] = float(values[event])
                    except ValueError:
                        sg.popup_error("Oops!, values should be float, not letters")
                    continue
                self.window["determined_{}".format(base)].update(button_color=sg.theme_button_color())
                self.window["guess_{}".format(base)].update(button_color=sg.theme_button_color())
                self.window[event].update(button_color=self.selected_color)
                if "guess" in event:
                    self.window["value_{}".format(base)].update(visible=True)
                else:
                    self.window["value_{}".format(base)].update(visible=False)
                    self.variable_status[base] = "determined"

        self.window.close()
        return self.variable_status
    
class GUILimitSetter(object):

    def __init__(self, variable_dict):
        variable_name = variable_dict.keys()

        self.variable_state = deepcopy(variable_dict)
        self.layout = [
            [sg.Column(layout=[[sg.Text("Bound Settings", font=("Helvetica", 16))]], element_justification="center", expand_x=True)],
            [sg.Column(layout = [[sg.Text("", pad=(7, 5), font=("Helvetica 8 bold"))]] + [[sg.Text(var_name, pad=(4, 4), font=("Helvetica 8 bold"))] for var_name in variable_name]),
            sg.VSeparator(),
            sg.Column(layout = [[sg.Text("Lower Bound  ", pad=(6, 5), font=("Helvetica 8 bold")), sg.Text("Upper Bound  ", pad=(6, 5), font=("Helvetica 8 bold"))]] + [[sg.In(default_text=variable_dict[var_name]["lower"], key="lower_{}".format(var_name), enable_events=True, size=(13, 1)), sg.In(default_text=variable_dict[var_name]["upper"], key="upper_{}".format(var_name), size=(13, 1), enable_events=True)] for var_name in variable_name])],
            [sg.Column(layout=[[sg.Button("Submit", key="exit", pad=(2, 2))]], expand_x=True, element_justification="center")]
        ]

        self.window = sg.Window(title="Bound Setter", layout=self.layout, use_default_focus=False)

    def run(self):

        while True:
            events, values = self.window.read()
            if events in [sg.WINDOW_CLOSED, "exit"]:
                for key in self.variable_state:
                    if self.variable_state[key]["lower"] is None or self.variable_state[key]["upper"] is None:
                        sg.popup_error("You have to supply input for every variable")
                    continue
                break
            else:
                prefix, base = events.split("_")
                if prefix == "lower":
                    try:
                        self.variable_state[base]["lower"] = str(float(values[events]))
                    except ValueError:
                        sg.popup_error("Oops!, values should be float, not letters")
                    continue
                if prefix == "upper":
                    try:
                        self.variable_state[base]["upper"] = str(float(values[events]))
                    except ValueError:
                        sg.popup_error("Oops!, values should be float, not letters")
                    continue

        self.window.close()
        return self.variable_state