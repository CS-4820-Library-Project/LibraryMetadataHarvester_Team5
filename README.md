# Library Metadata Harvester

The Library Metadata Harvester (LMH) project accepts a list of either International Standard
Book Numbers (ISBNs) or Online Computer Library Center (OCLC) Control Numbers (aka
OCNs) to perform a priority search of the internet sources for related metadata. The retrieved
metadata is stored in an SQLite database and output as a tab-delimited file. The internet
sources include a variety of Application Programming Interfaces (APIs), Blacklight-based
library catalogues, and WorldCat-based library catalogues. LMH also uses Z39.50 for
searching through databases over a TCP/IP network.
It also has an optional web-scraping that could be set up.