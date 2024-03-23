from app.apis import harvardAPI, openLibraryAPI, locAPI, googleAPI
from app.database.LMH_database import Database
from app import config
from tkinter import filedialog
from CTkListbox import *
from CTkMessagebox import *
import customtkinter
import threading
import csv

ui_map = {}
stop_search_flag = False


def read_input_file(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file, delimiter='\t')  # Adjust delimiter based on the actual file format
        input_data = [row[0] for row in reader]  # Assuming the data is in the first column of the file
    return input_data


def write_to_output(metadata, output_file):
    header = ['ISBN', 'OCLC', 'LCCN', 'LCCN-Source']

    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='\t')
        writer.writerow(header)

        for entry in metadata:
            row = [
                entry.get('isbn', ''),
                entry.get('oclc', ''),
                entry.get('lcc', ''),
                entry.get('source', '')
            ]
            writer.writerow(row)

    append_to_log(f"Output file {output_file} has been generated.")


def create_window_and_move_to_center():
    root = customtkinter.CTk()
    root.title("Library Metadata Harvester")
    # Set window size
    window_width = 680
    window_height = 580
    # Get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    # Calculate window position
    x_coordinate = (screen_width - window_width) // 2
    y_coordinate = (screen_height - window_height) // 2
    # Move window to calculated position
    root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
    root.resizable(False, False)
    return root


def change_appearance_mode(new_appearance_mode):
    config_file = config.load_config()
    config.set_appearance_mode(config_file, new_appearance_mode)
    customtkinter.set_appearance_mode(new_appearance_mode)
    sources_list_box = ui_map['sources_list_box']
    sources_list_box.configure(text_color=customtkinter.ThemeManager.theme["CTkLabel"]["text_color"])
    sources_list_box.configure(fg_color=customtkinter.ThemeManager.theme["CTkLabel"]["fg_color"])


def change_isbn_retrieval():
    retrieve_isbn_switch = ui_map['retrieve_isbn_switch']
    if retrieve_isbn_switch.get() == 0:
        set_isbn_retrieval(False)
    else:
        set_isbn_retrieval(True)


def set_isbn_retrieval(boolean):
    config_file = config.load_config()
    config.set_isbn_retrieval(config_file, boolean)


def change_oclc_retrieval():
    retrieve_oclc_switch = ui_map['retrieve_oclc_switch']
    if retrieve_oclc_switch.get() == 0:
        set_oclc_retrieval(False)
    else:
        set_oclc_retrieval(True)


def set_oclc_retrieval(boolean):
    config_file = config.load_config()
    config.set_oclc_retrieval(config_file, boolean)


def change_lccn_retrieval():
    retrieve_lccn_switch = ui_map['retrieve_lccn_switch']
    if retrieve_lccn_switch.get() == 0:
        set_lccn_retrieval(False)
    else:
        set_lccn_retrieval(True)


def set_lccn_retrieval(boolean):
    config_file = config.load_config()
    config.set_lccn_retrieval(config_file, boolean)


def change_google_key():
    google_key_window = customtkinter.CTkInputDialog(
        text="Type in your new Google Books API key. \nWarning! This will overwrite your previous key!",
        title="Change Google Books API Key")
    key = google_key_window.get_input()
    if key is not None and key != '':
        set_google_key(key)


def set_google_key(key):
    config_file = config.load_config()
    config.set_google_key(config_file, key)
    CTkMessagebox(title="Info", message=f"Google Books API key is now set to: {key}")


def change_timeout_value():
    timeout_value_window = customtkinter.CTkInputDialog(
        text="Type in your new timeout value. \nWarning! This will overwrite your previous timeout value!",
        title="Change Timeout Value")
    timeout_value = timeout_value_window.get_input()
    if timeout_value is not None and timeout_value != '':
        set_timeout_value(timeout_value)


def set_timeout_value(timeout_value):
    try:
        if int(timeout_value) < 0:
            CTkMessagebox(title="Error",
                          message="Timeout value cannot be a negative number. \nPlease provide a positive number when "
                                  "trying to change timeout value.",
                          icon="cancel")
            return

        config_file = config.load_config()
        config.set_search_timeout(config_file, int(timeout_value))
        CTkMessagebox(title="Info", message=f"API timeout is now set to {timeout_value}.")
    except ValueError:
        CTkMessagebox(title="Error",
                      message="Timeout value must be a number. \nPlease provide a positive number when trying to "
                              "change timeout value.",
                      icon="cancel")
        return


def choose_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    file_path_label = ui_map.get('file_path')
    if file_path:
        file_path_label.configure(text=file_path)
    else:
        file_path_label.configure(text='')


def move_source_up():
    sources_list_box = ui_map['sources_list_box']
    if len(sources_list_box.curselection()) != 1:
        CTkMessagebox(title="Error", message="You can only move one element at a time.", icon="cancel")
        return
    if sources_list_box.curselection() is not None:
        for index in sources_list_box.curselection():
            sources_list_box.move_up(index)


def move_source_down():
    sources_list_box = ui_map['sources_list_box']
    if len(sources_list_box.curselection()) != 1:
        CTkMessagebox(title="Error", message="You can only move one element at a time.", icon="cancel")
        return
    if sources_list_box.curselection() is not None:
        for index in sources_list_box.curselection():
            sources_list_box.move_down(index)


def append_to_log(text):
    ui_map['logs_textbox'].configure(state="normal")
    ui_map['logs_textbox'].insert("end", text + '\n')
    ui_map['logs_textbox'].configure(state="disabled")


def start_search():
    if ui_map['file_path'].cget('text') is None or ui_map['file_path'].cget('text') == '':
        CTkMessagebox(title="Error", message="You must select a input file.", icon="cancel")
        return
    if ui_map['sources_list_box'].get() is None:
        CTkMessagebox(title="Error", message="You must select at least one source from the list of sources.",
                      icon="cancel")
        return
    if (ui_map['retrieve_isbn_switch'].get() == 0 and ui_map['retrieve_oclc_switch'].get() == 0 and
            ui_map['retrieve_lccn_switch'].get() == 0):
        CTkMessagebox(title="Error",
                      message="You must select at least one type of metadata to retrieve from the settings menu.",
                      icon="cancel")
        return

    if ui_map['output_file_field'].get() is None or ui_map['output_file_field'].get() == '':
        message = CTkMessagebox(title="Question",
                                message="You have not specified an output file so no output will be generated. Do you "
                                        "still want to proceed?",
                                icon="question", option_1="Yes", option_2="No")
        if message.get() == "No":
            return

    ui_map['logs_textbox'].configure(state="normal")
    ui_map['logs_textbox'].delete(0.0, "end")
    ui_map['logs_textbox'].configure(state="disabled")

    thread = threading.Thread(target=search)
    thread.start()
    check_thread_status(thread)


def check_thread_status(thread):
    global stop_search_flag
    if thread.is_alive():
        ui_map['appearance_mode_option_menu'].configure(state="disabled")
        ui_map['choose_file_button'].configure(state="disabled")
        ui_map['output_file_field'].configure(state="disabled")
        ui_map['retrieve_isbn_switch'].configure(state="disabled")
        ui_map['retrieve_oclc_switch'].configure(state="disabled")
        ui_map['retrieve_lccn_switch'].configure(state="disabled")
        ui_map['timeout_button'].configure(state="disabled")
        ui_map['google_key_button'].configure(state="disabled")
        ui_map['start_button'].configure(state="disabled")
        if not stop_search_flag:
            ui_map['stop_button'].configure(state="normal")
        ui_map['root'].after(200, check_thread_status, thread)
    else:
        stop_search_flag = False
        ui_map['appearance_mode_option_menu'].configure(state="normal")
        ui_map['choose_file_button'].configure(state="normal")
        ui_map['output_file_field'].configure(state="normal")
        ui_map['retrieve_isbn_switch'].configure(state="normal")
        ui_map['retrieve_oclc_switch'].configure(state="normal")
        ui_map['retrieve_lccn_switch'].configure(state="normal")
        ui_map['timeout_button'].configure(state="normal")
        ui_map['google_key_button'].configure(state="normal")
        ui_map['start_button'].configure(state="normal")
        ui_map['stop_button'].configure(state="disabled")
    return


def search():
    db_manager = Database('LMH_database.db')

    retrieval_settings = {}
    dont_use_api = {"dont_continue_search": False, "dont_use_harvard": False, "dont_use_openlibrary": False, "dont_use_loc": False, "dont_use_google": False}
    is_isbn = False
    is_oclc = False
    global stop_search_flag

    if ui_map['retrieve_isbn_switch'].get() == 1:
        retrieval_settings['retrieve_isbn'] = True
    else:
        retrieval_settings['retrieve_isbn'] = False
    if ui_map['retrieve_oclc_switch'].get() == 1:
        retrieval_settings['retrieve_oclc'] = True
    else:
        retrieval_settings['retrieve_oclc'] = False
    if ui_map['retrieve_lccn_switch'].get() == 1:
        retrieval_settings['retrieve_lccn'] = True
    else:
        retrieval_settings['retrieve_lccn'] = False

    input_data = read_input_file(ui_map['file_path'].cget('text'))

    # Check which type of input data we have
    if len(input_data[0]) >= 10:
        is_isbn = True
        append_to_log("Assuming list contains ISBN values.")
        if retrieval_settings['retrieve_isbn'] and not retrieval_settings['retrieve_oclc'] and not retrieval_settings['retrieve_lccn']:
            message = CTkMessagebox(title="Warning",
                                    message="You currently only have retrieval for isbns selected while also inputting "
                                            "a list of isbns. Do you still want to proceed?",
                                    icon="warning", option_1="Yes", option_2="No")
            if message.get() == "No":
                return
    elif len(input_data[0]) <= 9:
        is_oclc = True
        append_to_log("Assuming list contains OCLC values.")
        if not retrieval_settings['retrieve_isbn'] and retrieval_settings['retrieve_oclc'] and not retrieval_settings['retrieve_lccn']:
            message = CTkMessagebox(title="Warning",
                                    message="You currently only have retrieval for oclc values selected while also "
                                            "inputting a list of oclc values. Do you still want to proceed?",
                                    icon="warning", option_1="Yes", option_2="No")
            if message.get() == "No":
                return

    progress_window = create_progress_window()
    progress_window.grid_rowconfigure((0, 3), weight=1)
    progress_window.grid_columnconfigure((0, 2), weight=1)

    logs_label = customtkinter.CTkLabel(master=progress_window, text="Please wait while the search process is "
                                                                     "running. \nThis might take several minutes.")
    logs_label.grid(column=1, row=1, padx=25, pady=(0, 10), sticky="nsew")

    progress_bar = customtkinter.CTkProgressBar(master=progress_window, orientation="horizontal")
    progress_bar.grid(column=1, row=2, padx=20, pady=10, sticky="nsew")
    progress_bar.set(0)

    # Initialize metadata list
    metadata = []

    # Define the ordered sources based on source priorities
    sources_list_box = ui_map['sources_list_box']
    priorities = sources_list_box.curselection()
    source_order = [sources_list_box.get(i) for i in range(sources_list_box.size())]
    ordered_sources = [source_order[index] for index in priorities]

    dont_use_api = check_status(dont_use_api, ordered_sources, input_data[0], is_isbn, is_oclc)

    if dont_use_api["dont_continue_search"]:
        progress_window.destroy()
        append_to_log("Search process has been cancelled.")
        return

    for index, number in enumerate(input_data):

        if stop_search_flag is True:
            break

        if is_isbn:
            entry = {'isbn': number}
            if db_manager.is_in_database(number, "ISBN"):
                database_entry = db_manager.get_metadata(number, 0)

                if retrieval_settings['retrieve_oclc']:
                    entry.update({
                        'oclc': database_entry[1]
                    })
                if retrieval_settings['retrieve_lccn']:
                    entry.update({
                        'lcc': database_entry[2][0][0],
                        'source': database_entry[2][0][1]
                    })

        if is_oclc:
            entry = {'oclc': number}
            if db_manager.is_in_database(number, "OCN"):
                database_entry = db_manager.get_metadata(number, 1)

                if retrieval_settings['retrieve_isbn']:
                    entry.update({
                        'isbn': database_entry[0]
                    })
                if retrieval_settings['retrieve_lccn']:
                    entry.update({
                        'lcc': database_entry[2][0][0],
                        'source': database_entry[2][0][1]
                    })

        # Skip this iteration of the loop if all the data has been retrieved from the database or if we
        # said we didn't want it
        if (((entry.get('isbn') and entry.get('isbn') != '') or not retrieval_settings['retrieve_isbn']) and
                ((entry.get('oclc') and entry.get('oclc') != '') or not retrieval_settings['retrieve_oclc']) and
                ((entry.get('lcc') and entry.get('lcc') != '') or not retrieval_settings['retrieve_lccn'])):
            # Append the entry to metadata
            metadata.append(entry)
            # Update the progress bar
            progress_bar.set((index + 1) / len(input_data))
            continue

        # Check sources in the specified priority order
        for source in ordered_sources:

            # Check if Harvard is the next source
            if source == 'Harvard' and not dont_use_api["dont_use_harvard"]:
                entry = harvardAPI.parse_harvard_data(entry, number, retrieval_settings)

            # Check if OpenLibrary is the next source
            elif source == 'Open Library' and not dont_use_api["dont_use_openlibrary"]:
                entry = openLibraryAPI.parse_open_library_data(entry, number, retrieval_settings, is_oclc, is_isbn)

            # Check if LOC is the next source
            elif source == 'Library of Congress' and not dont_use_api["dont_use_loc"]:
                entry = locAPI.parse_loc_data(entry, number, retrieval_settings, is_oclc)

            # Check if Google Books is the next source
            elif source == 'Google Books' and not dont_use_api["dont_use_google"]:
                entry = googleAPI.parse_google_data(entry, number, retrieval_settings, is_oclc, is_isbn)

            # Break out of the loop if data has been retrieved for the current source excluding stuff we said we
            # didn't want
            if (((entry.get('isbn') and entry.get('isbn') != '') or not retrieval_settings['retrieve_isbn']) and
                    ((entry.get('oclc') and entry.get('oclc') != '') or not retrieval_settings['retrieve_oclc']) and
                    ((entry.get('lcc') and entry.get('lcc') != '') or not retrieval_settings['retrieve_lccn'])):
                break

        db_manager.insert(entry.get('isbn', ''), entry.get('oclc', ''), entry.get('lcc', ''),
                          entry.get('source', ''))

        # Append the entry to metadata
        metadata.append(entry)

        # Update the progress bar
        progress_bar.set((index + 1) / len(input_data))

    if ui_map['output_file_field'].get() is not None and ui_map['output_file_field'].get() != '':
        # Write metadata to output file
        write_to_output(metadata, ui_map['output_file_field'].get())

    progress_window.destroy()

    CTkMessagebox(title="Process Complete", message="Process is complete.", icon="check")


def check_status(dont_use_api, ordered_sources, number, is_isbn, is_oclc):
    append_to_log("Performing API status checks:")

    # Check sources in the specified priority order
    for source in ordered_sources:

        if dont_use_api["dont_continue_search"]:
            return dont_use_api

        # Check if Harvard is the next source
        if source == 'Harvard':
            if not is_isbn:
                message = CTkMessagebox(title="Warning",
                                        message="Harvard API requires ISBN values as input. Currently you have input "
                                                "oclc values. Would you like to proceed without using the Harvard API?",
                                        icon="warning", option_1="Yes", option_2="No")
                if message.get() == "No":
                    dont_use_api["dont_continue_search"] = True
                    continue
                elif message.get() == "Yes":
                    dont_use_api["dont_use_harvard"] = True
                    continue
            if harvardAPI.retrieve_data_from_harvard(number, True) == 200:
                append_to_log("Harvard: Online")
            else:
                append_to_log("Harvard: Offline")
                dont_use_api["dont_use_harvard"] = True

        # Check if OpenLibrary is the next source
        elif source == 'Open Library':
            if openLibraryAPI.retrieve_data_from_open_library(number, True, is_oclc, is_isbn) == 200:
                append_to_log("Open Library: Online")
            else:
                append_to_log("Open Library: Offline")
                dont_use_api["dont_use_openlibrary"] = True

        # Check if LOC is the next source
        elif source == 'Library of Congress':
            if locAPI.retrieve_data_from_loc(number, True) == 200:
                append_to_log("Library of Congress: Online")
            else:
                append_to_log("Library of Congress: Offline")
                dont_use_api["dont_use_loc"] = True

        # Check if Google Books is the next source
        elif source == 'Google Books':
            config_file = config.load_config()
            if config_file["google_api_key"] == "YOUR_GOOGLE_API_KEY":
                message = CTkMessagebox(title="Warning",
                                        message="Google Books API requires the user to have a valid Google API key "
                                                "saved using the settings menu. Would you like to proceed without "
                                                "using the Google Books API?",
                                        icon="warning", option_1="Yes", option_2="No")
                if message.get() == "No":
                    dont_use_api["dont_continue_search"] = True
                    continue
                elif message.get() == "Yes":
                    dont_use_api["dont_use_google"] = True
                    continue
            if googleAPI.retrieve_data_from_google(number, True, is_oclc, is_isbn) == 200:
                append_to_log("Google Books: Online")
            else:
                append_to_log("Google Books: Offline")
                dont_use_api["dont_use_google"] = True

    return dont_use_api


def stop_search():
    global stop_search_flag
    stop_search_flag = True
    ui_map['stop_button'].configure(state="disabled")
    append_to_log("Process is being forcefully stopped... Please wait...")


def create_progress_window():
    progress_window = customtkinter.CTkToplevel()
    progress_window.title("Library Metadata Harvester - Progress")
    # Set window size
    window_width = 420
    window_height = 145
    # Get screen width and height
    screen_width = progress_window.winfo_screenwidth()
    screen_height = progress_window.winfo_screenheight()
    # Calculate window position
    x_coordinate = (screen_width - window_width) // 2
    y_coordinate = (screen_height - window_height) // 2
    # Move window to calculated position
    progress_window.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
    progress_window.resizable(False, False)
    # Disable closing the window (the user can still technically close the window by stopping the search)
    # Without this we get errors whenever we try to update a progress bar that no longer exists
    progress_window.protocol("WM_DELETE_WINDOW", disable_closing)
    # Parent the window to the root window
    progress_window.transient(ui_map['root'])
    return progress_window


def disable_closing():
    pass


def main():
    root = create_window_and_move_to_center()
    ui_map['root'] = root

    root.grid_rowconfigure(0, weight=1)

    # Create sidebar frame with widgets
    sidebar_frame = customtkinter.CTkFrame(root, width=140, corner_radius=0)
    sidebar_frame.grid(row=0, column=0, rowspan=6, sticky="nsew")
    sidebar_frame.grid_rowconfigure(7, weight=1)

    logo_label = customtkinter.CTkLabel(sidebar_frame, text="Library Metadata Harvester",
                                        font=customtkinter.CTkFont(size=15, weight="bold"))
    logo_label.grid(row=0, column=0, padx=10, pady=(20, 10))

    start_button = customtkinter.CTkButton(sidebar_frame, text="Start Search", width=50, command=start_search)
    start_button.grid(row=1, column=0, padx=20, pady=10, sticky="w")
    ui_map['start_button'] = start_button

    stop_button = customtkinter.CTkButton(sidebar_frame, text="Stop Search", width=50, state="disabled",
                                          command=stop_search)
    stop_button.grid(row=1, column=0, padx=20, pady=10, sticky="e")
    ui_map['stop_button'] = stop_button

    choose_file_button = customtkinter.CTkButton(master=sidebar_frame, text="Choose File", command=choose_file)
    choose_file_button.grid(row=2, column=0, padx=20, pady=(20, 5))
    ui_map['choose_file_button'] = choose_file_button

    file_path_label = customtkinter.CTkLabel(sidebar_frame, text="Input File Path:")
    file_path_label.grid(row=3, column=0, padx=20, pady=(5, 0), sticky="sw")

    file_path = customtkinter.CTkLabel(master=sidebar_frame, text='', width=200, wraplength=200,
                                       fg_color=("white", "gray25"))
    file_path.grid(row=4, column=0, padx=20, pady=(0, 10))
    ui_map['file_path'] = file_path

    output_file_field = customtkinter.CTkEntry(master=sidebar_frame, placeholder_text="Enter Output File")
    output_file_field.grid(row=5, column=0, padx=20, pady=20, sticky="nsew")
    ui_map['output_file_field'] = output_file_field

    appearance_mode_label = customtkinter.CTkLabel(sidebar_frame, text="Appearance Mode:", anchor="w")
    appearance_mode_label.grid(row=8, column=0, padx=20, pady=(10, 0))

    appearance_mode_option_menu = customtkinter.CTkOptionMenu(sidebar_frame, values=["Light", "Dark"],
                                                              command=change_appearance_mode)
    appearance_mode_option_menu.grid(row=9, column=0, padx=20, pady=(0, 10))
    ui_map['appearance_mode_option_menu'] = appearance_mode_option_menu

    # Create tabview with widgets
    tabview = customtkinter.CTkTabview(root, width=400)
    tabview.grid(row=0, column=1, padx=(20, 0), pady=(10, 0), sticky="nsew")
    tabview.add("Sources")
    tabview.add("Settings")
    tabview.tab("Sources").grid_columnconfigure(0, weight=1)
    tabview.tab("Settings").grid_columnconfigure(0, weight=1)

    logs_label = customtkinter.CTkLabel(root, text="Logs:")
    logs_label.grid(row=1, column=1, padx=25, pady=(10, 0), sticky="sw")

    logs_textbox = customtkinter.CTkTextbox(root, width=400, state="disabled")
    logs_textbox.grid(row=2, column=1, padx=(20, 0), pady=(0, 10), sticky="nsew")
    ui_map['logs_textbox'] = logs_textbox

    sources_list_box = CTkListbox(tabview.tab("Sources"), multiple_selection=True, height=220)
    for item in ["Harvard", "Open Library", "Library of Congress", "Google Books", "Z39.50"]:
        sources_list_box.insert("END", item)
    sources_list_box.grid(row=0, column=0, padx=(60, 10), pady=10)
    ui_map['sources_list_box'] = sources_list_box

    move_up_button = customtkinter.CTkButton(tabview.tab("Sources"), width=30, text="▲", command=move_source_up)
    move_up_button.grid(row=0, column=1, padx=(0, 100), pady=(90, 0), sticky="nw")
    ui_map['move_up'] = move_up_button

    move_down_button = customtkinter.CTkButton(tabview.tab("Sources"), width=30, text="▼", command=move_source_down)
    move_down_button.grid(row=0, column=1, padx=(0, 100), pady=(130, 0), sticky="nw")
    ui_map['move_down'] = move_down_button

    retrieve_isbn_switch = customtkinter.CTkSwitch(tabview.tab("Settings"), text="Retrieve ISBN",
                                                   command=change_isbn_retrieval)
    retrieve_isbn_switch.grid(row=0, column=0, padx=10, pady=5)
    ui_map['retrieve_isbn_switch'] = retrieve_isbn_switch

    retrieve_oclc_switch = customtkinter.CTkSwitch(tabview.tab("Settings"), text="Retrieve OCLC",
                                                   command=change_oclc_retrieval)
    retrieve_oclc_switch.grid(row=1, column=0, padx=10, pady=5)
    ui_map['retrieve_oclc_switch'] = retrieve_oclc_switch

    retrieve_lccn_switch = customtkinter.CTkSwitch(tabview.tab("Settings"), text="Retrieve LCCN",
                                                   command=change_lccn_retrieval)
    retrieve_lccn_switch.grid(row=2, column=0, padx=10, pady=5)
    ui_map['retrieve_lccn_switch'] = retrieve_lccn_switch

    timeout_button = customtkinter.CTkButton(tabview.tab("Settings"), text="Change Timeout Value", width=50,
                                             command=change_timeout_value)
    timeout_button.grid(row=3, column=0, padx=10, pady=(10, 5))
    ui_map['timeout_button'] = timeout_button

    google_key_button = customtkinter.CTkButton(tabview.tab("Settings"), text="Change Google API Key", width=50,
                                                command=change_google_key)
    google_key_button.grid(row=4, column=0, padx=10, pady=5)
    ui_map['google_key_button'] = google_key_button

    # Set default values
    config_file = config.load_config()

    appearance_mode_option_menu.set(config_file["appearance_mode"])
    change_appearance_mode(config_file["appearance_mode"])

    if not config_file["retrieve_isbn"]:
        retrieve_isbn_switch.deselect()
    else:
        retrieve_isbn_switch.select()

    if not config_file["retrieve_oclc"]:
        retrieve_oclc_switch.deselect()
    else:
        retrieve_oclc_switch.select()

    if not config_file["retrieve_lccn"]:
        retrieve_lccn_switch.deselect()
    else:
        retrieve_lccn_switch.select()

    root.mainloop()


if __name__ == "__main__":
    main()
