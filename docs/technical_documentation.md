# Technical Documentation
This is the technical documentation for the Library Metadata Harvester.

[Database](#databasepy) <br>
[API and Web Scraping information](#api-and-web-scraping-function-parameter-information) <br>
[Google API](#googleapipy) <br>
[Harvard API](#harvardapipy) <br>
[Library of Congress API](#locapipy) <br>
[Open Library API](#openlibraryapipy) <br>
[Web Scraper](#webscraperpy) <br>
[Z3950](#z3950py) <br>
[Call Number Validation](#callnumbervalidationpy) <br>
[Configuration](#configpy) <br>
[Main Program](#lmhpy)




## Database.py
### Example Code
```c
database = Database(database_name="your_database.db")
```
| argument       | value                                |
|----------------|--------------------------------------|
| database_name  | name of database in .db format       |

### Methods

* **.open_connection(*self*)** <br>
Opens the connection to the database.


* **.close_connection(*self*)** <br>
Closes the connection to the database.

* **.create_table(*self*)** <br>
Creates a table in the database with columns *isbn*, *ocn*, *lccn*, *lccn_source*.

* **.insert(*self*, *isbn*, *ocn*, *lccn*, *lccn_source*, *is_isbn*)** <br>
Inserts an ISBN or OCN into that database along with the associated metadata. If no value is available, an empty string ("") is used.
    ```c
    database.insert(isbn="0192843845", ocn="73824832", lccn="GB 2403.3.B44 2010", lccn_source="Harvard", is_isbn=True)
    ```
    | parameter  | value               |
    |------------|---------------------|
    | isbn       | String: ISBN number |
    | ocn        | String: OCN number  |
    | lccn       | String: LCCN number |
    | lccn_source| String: LCCN source |
    | is_isbn    | Boolean             |

* **.is_in_database(*self*, *number*, *isbn_or_ocn*)** <br>
Checks if an ISBN or OCN is in the database. Returns True or False.
    ```c
    database.is_in_database(number="73824832", isbn_or_ocn="OCN")
    ```
    | parameter    | value                    |
    |--------------|--------------------------|
    | number       | String: ISBN/OCN number  |
    | isbn_or_ocn  | String: "ISBN" or "OCN"  |

* **.get_metadata(*self*, *number*, *type*)** <br>
Returns the associated metadata for a given ISBN or OCN.
    ```c
    database.get_metadata(number="0192843845", type=0)

    returns ["0192843845", "73824832", ("GB 2403.3.B44 2010", "Harvard")]
    ```
    | parameter    | value                    |
    |--------------|--------------------------|
    | number       | String: ISBN/OCN number  |
    | isbn_or_ocn  | 0:ISBN, 1:OCN            |

* **.clear_db(*self*)** <br>
Deletes all data inside the database. As an alternative, you can &delete the database file and a new one will be created when you run the LMH.

* **.view_table_contents(*self*)** <br>
Prints all of the rows in the database to standard output.
>[!NOTE]
>
>.view_table_contents() method is used for testing purposes. The use of this function, depending on how large your database is, could take a long time to print all of the rows.

## API and Web Scraping function parameter information

The APIs and web scraping files contain functions to parse and retrieve data. The parameters for these functions can be found below.

### Parse data function parameters:
   
| parameter          | value                    |
|--------------------|--------------------------|
| entry              | Dictionary: Dictionary of metadata for given number. {"isbn":value, "oclc":value, "lccn":value, "source":value}  |
| number             | String: ISBN or OCLC number  |
| retrieval_settings | Dictionary: Settings for what metadata the user wants to obtain. {"retrieve_isbn":Boolean, "retrieve_oclc":Boolean, "retrieve_lccn":Boolean}  |
| is_oclc            |  Boolean            |
| is_isbn            |  Boolean            |
| library            | String: library name|

### Retrieve data function parameters:

| parameter | value           |
|-----------|-----------------|
| number    | String: ISBN or OCN number |
| looking_for_status | Boolean: used to check API connection |
| is_oclc | Boolean      |
|is_isbn  | Boolean      |

## googleAPI.py

Refer to the user guide for information on how to set up the [Google Books API](https://developers.google.com/books/docs/v1/getting_started) with the Library Metadata Harvester.

### Functions

* **parse_google_data(*entry*, *number*, *retrieval_settings*, *is_oclc*, *is_isbn*)** <br>
Obtains the ISBN or OCLC(OCN) from the response of the API and adds it to the entry variable.
    
    

* **retrieve_data_from_google(*number*, *looking_for_status*, *is_oclc*, *is_isbn*)** <br>
Constructs url for the Google Books API using an ISBN or OCLC(OCN) number and returns response data.

## harvardAPI.py

More information on the Harvard API can be found [here](https://library.harvard.edu/services-tools/harvard-library-apis-datasets)

### Functions

* **parse_harvard_data(*entry*, *number*, *retrieval_settings*)** <br>
Obtains the LCCN and OCLC metadata for a given ISBN and adds them to the entry variable.

* **rertrieve_data_from_harvard(*isbn*, *looking_for_status*)** <br>
Contructs url for the Harvard API using an ISBN and returns the response data.

## locAPI.py

More information on the Library of Congress API can be found [here](https://www.loc.gov/apis/)

### Functions

* **parse_loc_data(*entry*, *number*, *retrieval_settings*, *is_oclc*)** <br>
Obtains the LCCN and OCLC metadata for a given ISBN and adds them to the entry variable.

* **retrieve_data_from_loc(*number*, *looking_for_status*)** <br>
Constructs the url for the Library of Congress API and returns the response data.

## openLibraryAPI.py
More information on the Open Library API can be found [here](https://openlibrary.org/dev/docs/api/books)

### Functions

* **parse_open_library_data(*entry*, *number*, *retrieval_settings*, *is_oclc*, *is_isbn*)** <br>
Obtains the LCCN and OCLC/ISBN metadata for a given ISBN/OCN(OCLC) and adds them to the entry variable.

* **retrieve_data_from_loc(*number*, *looking_for_status*)** <br>
Constructs the url for the Open Library API and returns the response data.


## webScraper.py

Generic web scraper for Blacklight catalogs. Information on how to add websites can be found in the user documentation.

### Functions

* **extract_highlighted_items(*html_content*)** <br>
Extracts the document ids from the html of the webpage.

* **read_html_file(*file_path*)** <br>
Returns the html content from the file path proveded.

* **download_webpage(*url*, *file_path*)** <br>
Downloads the html of the url provided and writes it to the file path provided.

* **extract_lccn_numbers(*file_path*)** <br>
Extracts and returns the LCCN numbers from the html of the webpage that is found at the file path provided.

* **extract_oclc_numbers(*file_path*)** <br>
Extracts and returns the OCLC numbers from the html of the webpage that is found at the file path provided.

* **parse_data(*entry*, *number*, *retrieval_settings*, *library*)** <br>
Obtains the OCLC and LCCN for a given ISBN and updates the enrtry variable with them.

## z3950.py

Refer to the user documentation for information on how to set up Z39.50 and YAZ Client with the Library Metadata Harvester.

* **parse_text_marc(*text_marc*)** <br>
Takes in the MARC record as input and returns the OCLC and LCCN.

* **run_yaz_client(*isbn*, *target_string*)** <br>
Runs the yaz client for a given ISBN and returns its MARC record.

* **parse_data(*entry*, *number*, *retrieval_settings*, *library*)** <br>
Obtains the OCLC and LCC for a given ISBN and updates the entry variable.

## callNumberValidation.py

* **validate_lc_call_number(*call_number*)** <br>
Simple regular expression to make sure given LCCN is not a Control Number.

## config.py

### config.json format:
{<br>
            "google_api_key": "YOUR_GOOGLE_API_KEY", # String for API key<br>
            "search_timeout": 10,  # Default search timeout in seconds<br>
            "retrieve_isbn": True,<br>
            "retrieve_oclc": True,<br>
            "retrieve_lccn": True,<br>
            "appearance_mode": "Dark",<br>
            "yaz_client_path": "", # path to yaz client<br>
            "z3950_sources": 
            {"name (Yale)": "url (z3950.library.yale.edu:7090/voyager)"},<br>
            "web_scraping_sources": {name, base_url, query_url},<br>
            "ordered_sources": [] # order of sources to be searched<br>
        }

Configuration settings for the Library Metadata Harvester are stored in a JSON file named "config.json".

* **load_config()** <br>
Loads the config file. If the file is not found, it creates a config file with default settings.

* **save_config(*new_config*)** <br>
Saves the config file. Used after configuration settings have been updated.

* **set_search_timeout(*config*, *search_timeout*)** <br>
Updates the the search timeout settings in the config file.

* **set_google_key(*config*, *google_key*)** <br>
Updates the the Google Books API key in the config file.

* **set_isbn_retrieval(*config*, *isbn_retrieval*)** <br>
Updates the the ISBN retrieval settings in the config file.

* **set_oclc_retrieval(*config*, *oclc_retrieval*)** <br>
Updates the the OCLC retrieval settings in the config file.

* **set_lccn_retrieval(*config*, *lccn_retrieval*)** <br>
Updates the the LCCN retrieval settings in the config file.

* **set_appearence_mode(*config*, *appearence_mode*)** <br>
Updates the the appearence mode settings in the config file.

* **add_z3950_source(*config*, *source_name*, *source_link*)** <br>
Adds a source to the Z39.50 sources in the config file.

* **remove_z3950_source(*config*, *source*)** <br>
Removes a source from the Z39.50 sources in the config file.

* **add_web_scraping_source(*config*, *source_name*, *query_url*, *base_url*)** <br>
Adds a source to the web scraping sources in the config file.

* **remove_web_scraping_source(*config*, *source*)** <br>
Removes a source from the web scraping sources in the config file.

* **save_source_configuration(*config*, *sources*)** <br>
Saves the updated order of the sources in the config file.

* **append_source(*config*, *source*)** <br>
Adds a source to the ordered sources list in the config file.

* **remove_source(*config*, *source*)** <br>
Removes a source from the ordered sources list in the config file.

## lmh.py

* **read_input_file(*file_path*)** <br>
Accepts the path of a file as input and returns a list of its contents.

* **write_to_output(*metadata*, *output_file*)** <br>
Writes all metadata to an output file.

* **create_window_and_move_to_center()** <br>
Creates the main window for the LMH GUI and centers it on the screen.

* **change_appearance_mode(*new_appearance_mode*)** <br>
Updates the appearance mode of the GUI to be light or dark.

* **change_isbn_retrieval()** <br>
Change the ISBN retrieval switch to "on" or "off".

* **set_isbn_retrieval(*boolean*)** <br>
Set the ISBN retrieval setting to True or False in the config file.

* **change_oclc_retrieval()** <br>
Change the OCLC retrieval switch to "on" or "off".

* **set_oclc_retrieval(*boolean*)** <br>
Set the OCLC retrieval setting to True or False in the config file.

* **change_lccn_retrieval()** <br>
Change the LCCN retrieval switch to "on" or "off".

* **set_lccn_retrieval(*boolean*)** <br>
Set the LCCN retrieval setting to True or False in the config file.

* **open_z3950_config()** <br>
Opens the configuration window for adding and removing Z39.50 sources.

* **create_config_window()** <br>
Creates a configuration window.

* **remove_z3950_source()** <br>
Removes the Z39.50 source that is selected.

* **add_z3950_source()** <br>
Adds a Z39.50 source.

* **open_web_scraping_config()** <br>
Opens the configuration window for adding and removing web scraping sources.

* **remove_web_scraping_source()** <br>
Removes the web scraping source that is selected.

* **add_webscraping_source()** <br>
Adds a web scraping source.

* **change_google_key()** <br>
Opens an input dialog to allow the user to change their Google Books API key.

* **set_google_key(*key*)** <br>
Sets the Google Books API key in the config file to a new value.

* **change_timeout_value()** <br>
Opens a input dialog to allow user to change the timeout value.

* **set_timeout_value(*timeout_value*)** <br>
Changes the timeout value in the config file.

* **change_input_type_isbn()** <br>
Changes the input radio button to be ISBN.

* **change_input_type_oclc()** <br>
Changes the input radio button to be OCLC.

* **choose_file()** <br>
Uses file dialog to allow user to select the input file.

* **move_source_up()** <br>
Moves the selected source up in the sources listbox.

* **move_source_down** <br>
Moves the selected source down in the sources listbox.

* **append_to_log(*text*)** <br>
Appends text to log file.

* **start_search()** <br>
Initiates the running of the Library Metadata Harvester.

* **check_thread_status(*thread*)** <br>
Disables functionality while the LMH is running.

* **search()** <br>
Main run function for searching sources.

* **check_status(*dont_use_api*, *ordered_sources*, *number*, *is_isbn*, *is_oclc*)** <br>
Checks if selected APIs are online and that the sources are available for the configuration the user chose.

* **stop_search()** <br>
Stops running the Library Metadata Harvester.

* **create_progress_window()** <br>
Creates a CustomTkinter window for the progress.

