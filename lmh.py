from app.apis import harvardAPI, openLibraryAPI, locAPI, googleAPI, z3950, webScraper
from app.database.LMH_database import Database
from app import config, logs
from tkinter import filedialog
from CTkListbox import *
from CTkToolTip import *
from CTkMessagebox import *
import customtkinter
import threading
import csv

ui_map = {}
stop_search_flag = False
ui_has_been_disabled = False


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
                entry.get('lccn', ''),
                entry.get('source', '')
            ]
            writer.writerow(row)

    append_to_log(f"Output file {output_file} has been generated.")


def create_window_and_move_to_center():
    root = customtkinter.CTk()
    root.title("Library Metadata Harvester")
    # Set window size
    window_width = 675
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


def open_z3950_config():
    config_file = config.load_config()

    z3950_config_window = create_config_window()
    z3950_config_window.grid_rowconfigure((0, 3), weight=1)
    z3950_config_window.grid_columnconfigure((0, 3), weight=1)
    ui_map['z3950_config_window'] = z3950_config_window

    frame = customtkinter.CTkFrame(master=z3950_config_window)
    frame.grid(column=1, row=1, pady=10, sticky="nsew")

    z3950_sources_label = customtkinter.CTkLabel(master=frame, text="Z39.50 Sources")
    z3950_sources_label.grid(column=1, row=1, padx=25, pady=0, sticky="nsew")

    z3950_sources_list_box = CTkListbox(master=frame, multiple_selection=True, height=220)
    for key, value in config_file["z3950_sources"].items():
        z3950_sources_list_box.insert("END", key)
    z3950_sources_list_box.grid(column=1, row=2, padx=20, pady=(0, 10), sticky="nsew")
    ui_map['z3950_sources_list_box'] = z3950_sources_list_box

    add_source_button = customtkinter.CTkButton(master=z3950_config_window, text="Add Source", width=50,
                                                command=add_z3950_source)
    add_source_button.grid(column=2, row=1, padx=10, pady=(60, 10), sticky="new")

    source_name_field = customtkinter.CTkEntry(master=z3950_config_window, placeholder_text="Enter Source Name")
    source_name_field.grid(column=2, row=1, padx=20, pady=(100, 20), sticky="new")
    ui_map["source_name_field"] = source_name_field

    source_link_field = customtkinter.CTkEntry(master=z3950_config_window, placeholder_text="Enter Source Link")
    source_link_field.grid(column=2, row=1, padx=20, pady=(140, 20), sticky="new")
    ui_map["source_link_field"] = source_link_field

    remove_source_button = customtkinter.CTkButton(master=z3950_config_window, text="Remove Source", width=50,
                                                   command=remove_z3950_source)
    remove_source_button.grid(column=2, row=1, padx=10, pady=(10, 70), sticky="sew")


def create_config_window():
    z3950_config_window = customtkinter.CTkToplevel()
    z3950_config_window.title("Source Settings")
    # Set window size
    window_width = 420
    window_height = 325
    # Get screen width and height
    screen_width = z3950_config_window.winfo_screenwidth()
    screen_height = z3950_config_window.winfo_screenheight()
    # Calculate window position
    x_coordinate = (screen_width - window_width) // 2
    y_coordinate = (screen_height - window_height) // 2
    # Move window to calculated position
    z3950_config_window.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
    z3950_config_window.resizable(False, False)
    # Parent the window to the root window
    z3950_config_window.transient(ui_map['root'])
    return z3950_config_window


def remove_z3950_source():
    z3950_sources_list_box = ui_map['z3950_sources_list_box']
    if len(z3950_sources_list_box.curselection()) == 0:
        CTkMessagebox(title="Error", message="You must select an element to remove.",
                      icon="cancel")
        return
    if len(z3950_sources_list_box.curselection()) > 1:
        CTkMessagebox(title="Error", message="You can only remove one element at a time.", icon="cancel")
        return

    config_file = config.load_config()

    priorities = z3950_sources_list_box.curselection()
    all_sources = [z3950_sources_list_box.get(i) for i in range(z3950_sources_list_box.size())]
    selected_source = [all_sources[index] for index in priorities]
    config.remove_z3950_source(config_file, selected_source[0])
    if config_file["ordered_sources"]:
        config.remove_source(config_file, str(selected_source[0]) + " (Z39.50)")

    z3950_sources_list_box.delete(z3950_sources_list_box.curselection()[0])

    source_order = [ui_map['sources_list_box'].get(i) for i in range(ui_map['sources_list_box'].size())]

    for index, source in enumerate(source_order):
        if source == str(selected_source[0]) + " (Z39.50)":
            ui_map['sources_list_box'].delete(index)


def add_z3950_source():
    if ui_map['source_name_field'].get() is None or ui_map['source_name_field'].get() == '':
        CTkMessagebox(title="Error", message="You must specify a source name if you wish to add a source.",
                      icon="cancel")
        return
    if ui_map['source_link_field'].get() is None or ui_map['source_link_field'].get() == '':
        CTkMessagebox(title="Error", message="You must specify a source link if you wish to add a source.",
                      icon="cancel")
        return

    config_file = config.load_config()

    config.add_z3950_source(config_file, ui_map['source_name_field'].get(), ui_map['source_link_field'].get())
    if config_file["ordered_sources"]:
        config.append_source(config_file, ui_map['source_name_field'].get() + " (Z39.50)")

    ui_map['sources_list_box'].insert("END", ui_map['source_name_field'].get() + " (Z39.50)")
    ui_map['z3950_sources_list_box'].insert("END", ui_map['source_name_field'].get())


def open_web_scraping_config():
    config_file = config.load_config()

    web_scraping_config_window = create_config_window()
    web_scraping_config_window.grid_rowconfigure((0, 3), weight=1)
    web_scraping_config_window.grid_columnconfigure((0, 3), weight=1)
    ui_map['web_scraping_config_window'] = web_scraping_config_window

    frame = customtkinter.CTkFrame(master=web_scraping_config_window)
    frame.grid(column=1, row=1, pady=10, sticky="nsew")

    web_scraping_sources_label = customtkinter.CTkLabel(master=frame, text="Web Scraping Sources")
    web_scraping_sources_label.grid(column=1, row=1, padx=25, pady=0, sticky="nsew")

    web_scraping_sources_list_box = CTkListbox(master=frame, multiple_selection=True, height=220)
    for key, value in config_file["web_scraping_sources"].items():
        web_scraping_sources_list_box.insert("END", key)
    web_scraping_sources_list_box.grid(column=1, row=2, padx=20, pady=(0, 10), sticky="nsew")
    ui_map['web_scraping_sources_list_box'] = web_scraping_sources_list_box

    add_source_button = customtkinter.CTkButton(master=web_scraping_config_window, text="Add Source", width=50,
                                                command=add_web_scraping_source)
    add_source_button.grid(column=2, row=1, padx=10, pady=(40, 10), sticky="new")

    web_source_name_field = customtkinter.CTkEntry(master=web_scraping_config_window, placeholder_text="Enter "
                                                                                                       "Source Name")
    web_source_name_field.grid(column=2, row=1, padx=20, pady=(80, 20), sticky="new")
    ui_map["web_source_name_field"] = web_source_name_field

    source_query_url_field = customtkinter.CTkEntry(master=web_scraping_config_window, placeholder_text="Enter "
                                                                                                        "Query URL")
    source_query_url_field.grid(column=2, row=1, padx=20, pady=(120, 20), sticky="new")
    ui_map["source_query_url_field"] = source_query_url_field

    source_base_url_field = customtkinter.CTkEntry(master=web_scraping_config_window, placeholder_text="Enter Base URL")
    source_base_url_field.grid(column=2, row=1, padx=20, pady=(160, 20), sticky="new")
    ui_map["source_base_url_field"] = source_base_url_field

    remove_source_button = customtkinter.CTkButton(master=web_scraping_config_window, text="Remove Source", width=50,
                                                   command=remove_web_scraping_source)
    remove_source_button.grid(column=2, row=1, padx=10, pady=(10, 50), sticky="sew")


def remove_web_scraping_source():
    web_scraping_sources_list_box = ui_map['web_scraping_sources_list_box']
    if len(web_scraping_sources_list_box.curselection()) == 0:
        CTkMessagebox(title="Error", message="You must select an element to remove.",
                      icon="cancel")
        return
    if len(web_scraping_sources_list_box.curselection()) > 1:
        CTkMessagebox(title="Error", message="You can only remove one element at a time.", icon="cancel")
        return

    config_file = config.load_config()

    priorities = web_scraping_sources_list_box.curselection()
    all_sources = [web_scraping_sources_list_box.get(i) for i in range(web_scraping_sources_list_box.size())]
    selected_source = [all_sources[index] for index in priorities]
    config.remove_web_scraping_source(config_file, selected_source[0])
    if config_file["ordered_sources"]:
        config.remove_source(config_file, str(selected_source[0]) + " (Web)")

    web_scraping_sources_list_box.delete(web_scraping_sources_list_box.curselection()[0])

    source_order = [ui_map['sources_list_box'].get(i) for i in range(ui_map['sources_list_box'].size())]

    for index, source in enumerate(source_order):
        if source == str(selected_source[0]) + " (Web)":
            ui_map['sources_list_box'].delete(index)


def add_web_scraping_source():
    if ui_map['web_source_name_field'].get() is None or ui_map['web_source_name_field'].get() == '':
        CTkMessagebox(title="Error", message="You must specify a source name if you wish to add a source.",
                      icon="cancel")
        return
    if ui_map['source_query_url_field'].get() is None or ui_map['source_query_url_field'].get() == '':
        CTkMessagebox(title="Error", message="You must specify a query URL if you wish to add a source.",
                      icon="cancel")
        return
    if ui_map['source_base_url_field'].get() is None or ui_map['source_base_url_field'].get() == '':
        CTkMessagebox(title="Error", message="You must specify a base URL if you wish to add a source.",
                      icon="cancel")
        return

    config_file = config.load_config()

    config.add_web_scraping_source(config_file, ui_map['web_source_name_field'].get(),
                                   ui_map['source_query_url_field'].get(), ui_map['source_base_url_field'].get())
    if config_file["ordered_sources"]:
        config.append_source(config_file, ui_map['web_source_name_field'].get() + " (Web)")

    ui_map['sources_list_box'].insert("END", ui_map['web_source_name_field'].get() + " (Web)")
    ui_map['web_scraping_sources_list_box'].insert("END", ui_map['web_source_name_field'].get())


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
        text="Type in your new timeout value in seconds. \nWarning! This will overwrite your previous timeout value!",
        title="Change Timeout Value")
    timeout_value = timeout_value_window.get_input()
    if timeout_value is not None and timeout_value != '':
        set_timeout_value(timeout_value)


def set_timeout_value(timeout_value):
    try:
        if int(timeout_value) < 0:
            CTkMessagebox(title="Error",
                          message="Timeout value cannot be a negative number.\nPlease provide a positive number when "
                                  "trying to change timeout value.",
                          icon="cancel")
            return

        config_file = config.load_config()
        config.set_search_timeout(config_file, int(timeout_value))
        ui_map['timeout_button'].configure(
            text="Change Timeout Value (" + str(config_file["search_timeout"]) + " secs)")
        CTkMessagebox(title="Info", message=f"Source timeout is now set to {timeout_value} seconds.")
    except ValueError:
        CTkMessagebox(title="Error",
                      message="Timeout value must be a number.\nPlease provide a positive number when trying to "
                              "change timeout value.",
                      icon="cancel")
        return


def change_yaz_client_path():
    config_file = config.load_config()
    yaz_client_path = filedialog.askopenfilename()
    if yaz_client_path != "":
        config.set_yaz_client_path(config_file, yaz_client_path)
        CTkMessagebox(title="Info", message=f"Yaz client path is now set to {yaz_client_path}.")
        ui_map['yaz_client_tooltip'].configure(message=f"Change the path of the YAZ Client.\n "
                                                       f"Currently the yaz client path is set"
                                                       f" to:\n {yaz_client_path}")


def change_input_type_isbn():
    ui_map['oclc_radio_button'].deselect()
    ui_map['input_type'] = "isbn"


def change_input_type_oclc():
    ui_map['isbn_radio_button'].deselect()
    ui_map['input_type'] = "oclc"


def choose_file():
    file_path = filedialog.askopenfilename()
    file_path_label = ui_map.get('file_path')
    if file_path:
        file_path_label.configure(text=file_path)
    else:
        file_path_label.configure(text='')


def move_source_up():
    sources_list_box = ui_map['sources_list_box']
    if len(sources_list_box.curselection()) == 0:
        CTkMessagebox(title="Error", message="You must select an element to move.", icon="cancel")
        return
    if len(sources_list_box.curselection()) > 1:
        CTkMessagebox(title="Error", message="You can only move one element at a time.", icon="cancel")
        return
    if sources_list_box.curselection() is not None:
        for index in sources_list_box.curselection():
            sources_list_box.move_up(index)


def move_source_down():
    sources_list_box = ui_map['sources_list_box']
    if len(sources_list_box.curselection()) == 0:
        CTkMessagebox(title="Error", message="You must select an element to move.", icon="cancel")
        return
    if len(sources_list_box.curselection()) > 1:
        CTkMessagebox(title="Error", message="You can only move one element at a time.", icon="cancel")
        return
    if sources_list_box.curselection() is not None:
        for index in sources_list_box.curselection():
            sources_list_box.move_down(index)


def save_order():
    config_file = config.load_config()

    sources_list_box = ui_map['sources_list_box']
    source_order = [sources_list_box.get(i) for i in range(sources_list_box.size())]

    config.save_source_configuration(config_file, source_order)
    CTkMessagebox(title="Info", message="Source order has now been saved.")


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
                                message="You have not specified an output file so no output will be generated, "
                                        "but the data will still be entered into the database. Do you still "
                                        "want to proceed?",
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
    global ui_has_been_disabled
    global stop_search_flag
    if thread.is_alive():
        if not ui_has_been_disabled:
            ui_has_been_disabled = True
            ui_map['appearance_mode_option_menu'].configure(state="disabled")
            ui_map['isbn_radio_button'].configure(state="disabled")
            ui_map['oclc_radio_button'].configure(state="disabled")
            ui_map['choose_file_button'].configure(state="disabled")
            ui_map['output_file_field'].configure(state="disabled")
            ui_map['save_order_button'].configure(state="disabled")
            ui_map['retrieve_isbn_switch'].configure(state="disabled")
            ui_map['retrieve_oclc_switch'].configure(state="disabled")
            ui_map['retrieve_lccn_switch'].configure(state="disabled")
            ui_map['timeout_button'].configure(state="disabled")
            ui_map['google_key_button'].configure(state="disabled")
            ui_map['yaz_client_button'].configure(state="disabled")
            ui_map['z3950_button'].configure(state="disabled")
            ui_map['web_scraping_button'].configure(state="disabled")
            ui_map['start_button'].configure(state="disabled")
        ui_map['root'].after(200, check_thread_status, thread)
    else:
        has_been_disabled = False
        stop_search_flag = False
        ui_map['appearance_mode_option_menu'].configure(state="normal")
        ui_map['isbn_radio_button'].configure(state="normal")
        ui_map['oclc_radio_button'].configure(state="normal")
        ui_map['choose_file_button'].configure(state="normal")
        ui_map['output_file_field'].configure(state="normal")
        ui_map['save_order_button'].configure(state="normal")
        ui_map['retrieve_isbn_switch'].configure(state="normal")
        ui_map['retrieve_oclc_switch'].configure(state="normal")
        ui_map['retrieve_lccn_switch'].configure(state="normal")
        ui_map['timeout_button'].configure(state="normal")
        ui_map['google_key_button'].configure(state="normal")
        ui_map['yaz_client_button'].configure(state="normal")
        ui_map['z3950_button'].configure(state="normal")
        ui_map['web_scraping_button'].configure(state="normal")
        ui_map['start_button'].configure(state="normal")
    return


def search():
    config_file = config.load_config()

    db_manager = Database('LMH_database.db')

    retrieval_settings = {}
    dont_use_api = {"dont_continue_search": False, "dont_use_harvard": False, "dont_use_openlibrary": False,
                    "dont_use_loc": False, "dont_use_google": False, "dont_use_z3950": False}
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

    try:
        if ui_map['z3950_config_window']:
            ui_map['z3950_config_window'].destroy()
    except KeyError as e:
        logs.log_info("No Z39.50 config window to close.")

    try:
        if ui_map['web_scraping_config_window']:
            ui_map['web_scraping_config_window'].destroy()
    except KeyError as e:
        logs.log_info("No web scraping config window to close.")

    input_data = read_input_file(ui_map['file_path'].cget('text'))

    # Check which type of input data we have
    if ui_map["input_type"] == "isbn":
        is_isbn = True
        append_to_log("Assuming list contains ISBN values.")
        if (retrieval_settings['retrieve_isbn'] and not retrieval_settings['retrieve_oclc'] and not
        retrieval_settings['retrieve_lccn']):
            message = CTkMessagebox(title="Warning",
                                    message="You currently only have retrieval for ISBNs selected while also inputting "
                                            "a list of ISBNs. Do you still want to proceed?",
                                    icon="warning", option_1="Yes", option_2="No")
            if message.get() == "No":
                return
    elif ui_map["input_type"] == "oclc":
        is_oclc = True
        append_to_log("Assuming list contains OCLC values.")
        if (not retrieval_settings['retrieve_isbn'] and retrieval_settings['retrieve_oclc'] and not
        retrieval_settings['retrieve_lccn']):
            message = CTkMessagebox(title="Warning",
                                    message="You currently only have retrieval for OCLC values selected while also "
                                            "inputting a list of OCLC values. Do you still want to proceed?",
                                    icon="warning", option_1="Yes", option_2="No")
            if message.get() == "No":
                return

    progress_window = create_progress_window()
    progress_window.grid_rowconfigure((0, 4), weight=1)
    progress_window.grid_columnconfigure((0, 2), weight=1)

    logs_label = customtkinter.CTkLabel(master=progress_window, text="Please wait while the search process is "
                                                                     "running. \nThis might take several minutes.")
    logs_label.grid(column=1, row=1, padx=25, pady=(0, 10), sticky="nsew")

    progress_bar = customtkinter.CTkProgressBar(master=progress_window, orientation="horizontal")
    progress_bar.grid(column=1, row=2, padx=20, pady=10, sticky="nsew")
    progress_bar.set(0)

    stop_button = customtkinter.CTkButton(progress_window, text="Stop Search", width=125, command=stop_search)
    stop_button.grid(column=1, row=3, padx=20, pady=10)
    ui_map['stop_button'] = stop_button

    # Initialize metadata list
    metadata = []

    # Define the ordered sources based on source priorities
    sources_list_box = ui_map['sources_list_box']
    priorities = sources_list_box.curselection()
    source_order = [sources_list_box.get(i) for i in range(sources_list_box.size())]
    ordered_sources = [source_order[index] for index in priorities]

    config.save_source_configuration(config_file, source_order)

    dont_use_api = check_status(dont_use_api, ordered_sources, input_data[0], is_isbn, is_oclc)

    if dont_use_api["dont_continue_search"]:
        progress_window.destroy()
        append_to_log("Search process has been cancelled.")
        return

    for index, number in enumerate(input_data):

        if stop_search_flag is True:
            append_to_log("Process is being manually stopped... Please wait... Last Processed value was: " + number)
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
                        'lccn': database_entry[2][0][0],
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
                        'lccn': database_entry[2][0][0],
                        'source': database_entry[2][0][1]
                    })

        # Skip this iteration of the loop if all the data has been retrieved from the database or if we
        # said we didn't want it
        if (((entry.get('isbn') and entry.get('isbn') != '') or not retrieval_settings['retrieve_isbn']) and
                ((entry.get('oclc') and entry.get('oclc') != '') or not retrieval_settings['retrieve_oclc']) and
                ((entry.get('lccn') and entry.get('lccn') != '') or not retrieval_settings['retrieve_lccn'])):
            # Append the entry to metadata
            metadata.append(entry)
            # Update the progress bar
            progress_bar.set((index + 1) / len(input_data))
            continue

        # Check sources in the specified priority order
        for source in ordered_sources:

            # Check if Harvard is the next source
            if source == 'Harvard (API)' and not dont_use_api["dont_use_harvard"]:
                entry = harvardAPI.parse_harvard_data(entry, number, retrieval_settings)

            # Check if OpenLibrary is the next source
            elif source == 'Open Library (API)' and not dont_use_api["dont_use_openlibrary"]:
                entry = openLibraryAPI.parse_open_library_data(entry, number, retrieval_settings, is_oclc, is_isbn)

            # Check if LOC is the next source
            elif source == 'LOC (API)' and not dont_use_api["dont_use_loc"]:
                entry = locAPI.parse_loc_data(entry, number, retrieval_settings, is_oclc)

            # Check if Google Books is the next source
            elif source == 'Google Books (API)' and not dont_use_api["dont_use_google"]:
                entry = googleAPI.parse_google_data(entry, number, retrieval_settings, is_oclc, is_isbn)

            # Check if a Z39.50 is the next source
            elif source.split("(")[0].strip() in config_file["z3950_sources"] and not dont_use_api["dont_use_z3950"]:
                entry = z3950.parse_data(entry, number, retrieval_settings, source.split("(")[0].strip())

            # Check if a Web Scraping is the next source
            elif source.split("(")[0].strip() in config_file["web_scraping_sources"]:
                entry = webScraper.parse_data(entry, number, retrieval_settings, source.split("(")[0].strip())

            # Break out of the loop if data has been retrieved for the current source excluding stuff we said we
            # didn't want
            if (((entry.get('isbn') and entry.get('isbn') != '') or not retrieval_settings['retrieve_isbn']) and
                    ((entry.get('oclc') and entry.get('oclc') != '') or not retrieval_settings['retrieve_oclc']) and
                    ((entry.get('lccn') and entry.get('lccn') != '') or not retrieval_settings['retrieve_lccn'])):
                break

        db_manager.insert(entry.get('isbn', ''), entry.get('oclc', ''), entry.get('lccn', ''),
                          entry.get('source', ''), is_isbn)

        # Append the entry to metadata
        metadata.append(entry)

        # Update the progress bar
        progress_bar.set((index + 1) / len(input_data))

    if ui_map['output_file_field'].get() is not None and ui_map['output_file_field'].get() != '':
        # Write metadata to output file
        write_to_output(metadata, ui_map['output_file_field'].get())

    global ui_has_been_disabled
    ui_has_been_disabled = False

    progress_window.destroy()

    CTkMessagebox(title="Process Complete", message="Process is complete.", icon="check")


def check_status(dont_use_api, ordered_sources, number, is_isbn, is_oclc):
    append_to_log("Performing API status checks:")

    config_file = config.load_config()

    # Check sources in the specified priority order
    for source in ordered_sources:

        if dont_use_api["dont_continue_search"]:
            return dont_use_api

        # Check if Harvard is the next source
        if source == 'Harvard (API)':
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
        elif source == 'Open Library (API)':
            if openLibraryAPI.retrieve_data_from_open_library(number, True, is_oclc, is_isbn) == 200:
                append_to_log("Open Library: Online")
            else:
                append_to_log("Open Library: Offline")
                dont_use_api["dont_use_openlibrary"] = True

        # Check if LOC is the next source
        elif source == 'LOC (API)':
            if locAPI.retrieve_data_from_loc(number, True) == 200:
                append_to_log("Library of Congress: Online")
            else:
                append_to_log("Library of Congress: Offline")
                dont_use_api["dont_use_loc"] = True

        # Check if Google Books is the next source
        elif source == 'Google Books (API)':
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

        elif source.split("(")[0].strip() in config_file["z3950_sources"] and not dont_use_api["dont_use_z3950"]:
            if not is_isbn:
                message = CTkMessagebox(title="Warning",
                                        message="Z39.50 requires ISBN values as input. Currently you have input "
                                                "oclc values. Would you like to proceed without using any Z39.50 "
                                                "sources?",
                                        icon="warning", option_1="Yes", option_2="No")
                if message.get() == "No":
                    dont_use_api["dont_continue_search"] = True
                    continue
                elif message.get() == "Yes":
                    dont_use_api["dont_use_z3950"] = True
                    continue
            if config_file["yaz_client_path"] == "":
                message = CTkMessagebox(title="Warning",
                                        message="Currently no path has been given for the Yaz Client which is required "
                                                "to use any Z39.50 sources. Would you like to proceed without using "
                                                "any Z39.50 sources?",
                                        icon="warning", option_1="Yes", option_2="No")
                if message.get() == "No":
                    dont_use_api["dont_continue_search"] = True
                    continue
                elif message.get() == "Yes":
                    dont_use_api["dont_use_z3950"] = True
                    continue

    return dont_use_api


def stop_search():
    global stop_search_flag
    stop_search_flag = True
    ui_map['stop_button'].configure(state="disabled")


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
    config_file = config.load_config()

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

    start_button = customtkinter.CTkButton(sidebar_frame, text="Start Search", command=start_search)
    start_button.grid(row=1, column=0, padx=20, pady=10)
    ui_map['start_button'] = start_button

    ui_map['input_type'] = None

    isbn_radio_button = customtkinter.CTkRadioButton(master=sidebar_frame, text="ISBN", command=change_input_type_isbn)
    isbn_radio_button.grid(row=2, column=0, padx=(40, 10), pady=(5, 0), sticky="w")
    ui_map['isbn_radio_button'] = isbn_radio_button

    oclc_radio_button = customtkinter.CTkRadioButton(master=sidebar_frame, text="OCN", command=change_input_type_oclc)
    oclc_radio_button.grid(row=2, column=0, padx=(10, 0), pady=(5, 0), sticky="e")
    ui_map['oclc_radio_button'] = oclc_radio_button

    choose_file_button = customtkinter.CTkButton(master=sidebar_frame, text="Choose File", command=choose_file)
    choose_file_button.grid(row=3, column=0, padx=20, pady=(20, 5))
    ui_map['choose_file_button'] = choose_file_button

    file_path_label = customtkinter.CTkLabel(sidebar_frame, text="Input File Path:")
    file_path_label.grid(row=4, column=0, padx=20, pady=(5, 0), sticky="sw")

    file_path = customtkinter.CTkLabel(master=sidebar_frame, text='', width=200, wraplength=200,
                                       fg_color=("white", "gray25"))
    file_path.grid(row=5, column=0, padx=20, pady=(0, 10))
    ui_map['file_path'] = file_path

    output_file_field = customtkinter.CTkEntry(master=sidebar_frame, placeholder_text="Enter Output File")
    output_file_field.grid(row=6, column=0, padx=20, pady=20, sticky="nsew")
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
    tabview.tab("Settings").grid_rowconfigure(0, weight=1)

    logs_label = customtkinter.CTkLabel(root, text="Search Information:")
    logs_label.grid(row=1, column=1, padx=25, pady=(10, 0), sticky="sw")

    logs_textbox = customtkinter.CTkTextbox(root, width=400, state="disabled")
    logs_textbox.grid(row=2, column=1, padx=(20, 0), pady=(0, 10), sticky="nsew")
    ui_map['logs_textbox'] = logs_textbox

    sources_list_box = CTkListbox(tabview.tab("Sources"), multiple_selection=True, height=220)
    if config_file["ordered_sources"]:
        for item in config_file["ordered_sources"]:
            sources_list_box.insert("END", item)
    else:
        for item in ["Harvard (API)", "Open Library (API)", "LOC (API)", "Google Books (API)"]:
            sources_list_box.insert("END", item)
        for item in config_file["z3950_sources"]:
            sources_list_box.insert("END", item + " (Z39.50)")
        for item in config_file["web_scraping_sources"]:
            sources_list_box.insert("END", item + " (Web)")
    sources_list_box.grid(row=0, column=0, padx=(60, 10), pady=10)
    ui_map['sources_list_box'] = sources_list_box

    save_order_button = customtkinter.CTkButton(tabview.tab("Sources"), width=30, text="Save Order", command=save_order)
    save_order_button.grid(row=0, column=1, padx=10, sticky="e")
    ui_map['save_order_button'] = save_order_button

    CTkToolTip(save_order_button, border_width=1, message="Saves the current source order.\n"
                                                          "This is also automatically done\n"
                                                          "whenever a search is performed.")

    move_up_button = customtkinter.CTkButton(tabview.tab("Sources"), width=30, text="▲", command=move_source_up)
    move_up_button.grid(row=0, column=1, padx=(0, 100), pady=(95, 0), sticky="nw")
    ui_map['move_up'] = move_up_button

    CTkToolTip(move_up_button, border_width=1, message="Move source up")

    move_down_button = customtkinter.CTkButton(tabview.tab("Sources"), width=30, text="▼", command=move_source_down)
    move_down_button.grid(row=0, column=1, padx=(0, 100), pady=(135, 0), sticky="nw")
    ui_map['move_down'] = move_down_button

    CTkToolTip(move_down_button, border_width=1, message="Move source down")

    settings_frame = customtkinter.CTkScrollableFrame(tabview.tab("Settings"))
    settings_frame.grid(row=0, column=0, padx=10, sticky="nsew")
    settings_frame.grid_columnconfigure(0, weight=1)

    retrieve_isbn_switch = customtkinter.CTkSwitch(settings_frame, text="Retrieve ISBN",
                                                   command=change_isbn_retrieval)
    retrieve_isbn_switch.grid(row=0, column=0, padx=10, pady=5)
    ui_map['retrieve_isbn_switch'] = retrieve_isbn_switch

    CTkToolTip(retrieve_isbn_switch, border_width=1, message="Disable/Enable ISBN "
                                                             "retrieval\nwhen the "
                                                             "input file is OCNs")

    retrieve_oclc_switch = customtkinter.CTkSwitch(settings_frame, text="Retrieve OCN",
                                                   command=change_oclc_retrieval)
    retrieve_oclc_switch.grid(row=1, column=0, padx=10, pady=5)
    ui_map['retrieve_oclc_switch'] = retrieve_oclc_switch

    CTkToolTip(retrieve_oclc_switch, border_width=1, message="Disable/Enable OCN "
                                                             "retrieval\nwhen the "
                                                             "input file is ISBNs")

    retrieve_lccn_switch = customtkinter.CTkSwitch(settings_frame, text="Retrieve LCCN",
                                                   command=change_lccn_retrieval)
    retrieve_lccn_switch.grid(row=2, column=0, padx=10, pady=5)
    ui_map['retrieve_lccn_switch'] = retrieve_lccn_switch

    CTkToolTip(retrieve_lccn_switch, border_width=1, message="Disable LCCN "
                                                             "retrieval\nwhen the "
                                                             "input file is either\n"
                                                             "OCNs or ISBNs")

    timeout_button = customtkinter.CTkButton(settings_frame, text="Change Timeout Value", width=50,
                                             command=change_timeout_value)
    timeout_button.grid(row=3, column=0, padx=10, pady=(10, 5))
    ui_map['timeout_button'] = timeout_button

    CTkToolTip(timeout_button, border_width=1, message="Timeout value (in seconds) and is\n"
                                                       "on a per value basis per each\n"
                                                       "selected source.")

    google_key_button = customtkinter.CTkButton(settings_frame, text="Change Google API Key", width=50,
                                                command=change_google_key)
    google_key_button.grid(row=4, column=0, padx=10, pady=5)
    ui_map['google_key_button'] = google_key_button

    yaz_client_button = customtkinter.CTkButton(settings_frame, text="Change YAZ Client Path", width=50,
                                                command=change_yaz_client_path)
    yaz_client_button.grid(row=5, column=0, padx=10, pady=5)
    ui_map['yaz_client_button'] = yaz_client_button

    yaz_client_path = config_file["yaz_client_path"]
    yaz_client_tooltip = CTkToolTip(yaz_client_button, border_width=1, message=f"Change the path of the YAZ Client.\n "
                                                                               f"Currently the yaz client path is set"
                                                                               f" to:\n {yaz_client_path}")
    ui_map['yaz_client_tooltip'] = yaz_client_tooltip

    z3950_button = customtkinter.CTkButton(settings_frame, text="Change Z39.50 Settings", width=50,
                                           command=open_z3950_config)
    z3950_button.grid(row=6, column=0, padx=10, pady=5)
    ui_map['z3950_button'] = z3950_button

    web_scraping_button = customtkinter.CTkButton(settings_frame, text="Change Web Scraping Settings",
                                                  width=50,
                                                  command=open_web_scraping_config)
    web_scraping_button.grid(row=7, column=0, padx=10, pady=5)
    ui_map['web_scraping_button'] = web_scraping_button

    # Set default values

    appearance_mode_option_menu.set(config_file["appearance_mode"])
    change_appearance_mode(config_file["appearance_mode"])

    timeout_button.configure(text="Change Timeout Value (" + str(config_file["search_timeout"]) + " secs)")

    ui_map['isbn_radio_button'].select()
    ui_map['input_type'] = "isbn"

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
