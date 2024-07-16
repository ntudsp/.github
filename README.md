# citation-list-dsplab

This is a repository used to dynamically generate the DSPLAB Github home page based on publication data given in the `publication_list.csv` file.

## Getting started

To update the text for the home page, first update `publication_list.csv` with any additional rows corresponding to new publications.

Then, run the `print_citation_list.py` script from Python to generate the new text file to upload to the Github home page (`publication_list.txt`).

The script can be run from a terminal by entering the command

    python print_citation_list.py
  
This requires pandas to be installed, which you may do so by running this line first:

    pip install pandas

## Details of `print_citation_list.py` script

Actually, the `print_citation_list.py` script contains an argument parser that allows you to make minor adjustments to how the section headers are displayed and formatted. However, just running the command `python print_citation_list.py` still works and it gives the formatting that was used before 13 July 2024.

As of 16 July 2024, the command used to generate the live version on the home page is:

    python print_citation_list.py -c 2 3 4 -t 0
	
which makes level 2, 3, and 4 headers collapsible on the home page by clicking on them, and leaves the headers open (and not collapsed) by default. For more detailed information on the script, you can run this line on the terminal:

    python print_citation_list.py --help
