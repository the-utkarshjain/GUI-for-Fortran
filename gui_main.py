from gui_func import GUIMain


if __name__ == "__main__":

    GUI = GUIMain(window_size=(800, 700), title="GUI", auto_size_buttons=False, 
            auto_size_text=False, finalize=True, element_justification='center')

    while True:
        event, values = GUI.window.read(timeout=50)

        if event == GUI.WIN_CLOSED:
            break
        elif event == "-FILE1-":
            values[event] = None if values[event] is "" else values[event]
            print(f"File 1 path set to {values[event]}")
            GUI.first_input_path = values[event]

        elif event == "-FILE2-":
            values[event] = None if values[event] is "" else values[event]
            print(f"File 2 path set to {values[event]}")
            GUI.second_input_path = values[event]

        elif event == "-FILE3-":
            values[event] = None if values[event] is "" else values[event]
            print(f"File 3 path set to {values[event]}")
            GUI.third_input_path = values[event]

        elif event == "-FILE4-":
            values[event] = None if values[event] is "" else values[event]
            print(f"EXE file path set to {values[event]}")
            GUI.exe_file_path = values[event]

        elif event == "-REFRESH-":
            GUI.refresh()

        if GUI.is_processing:
            GUI.PopupAnimated(GUI.DEFAULT_BASE64_LOADING_GIF, background_color='green', transparent_color='green')
            GUI.freeze_buttons()
        else:
            GUI.PopupAnimated(None)
            GUI.unfreeze_buttons()
    

    GUI.window.close()