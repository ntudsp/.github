import argparse, os, glob
import pandas as pd

#------------------------------ Define argument parser ------------------------------#

parser = argparse.ArgumentParser(description='Prints DSPLAB publication list in markdown/html format.')

# nargs: '?' = any number of arguments including 0, '*' = any number of arguments at least 1, N = exactly N arguments
parser.add_argument('publication_csv_fpath', metavar = 'PATH_TO_PUBLICATION_CSV', nargs = '?', default = 'publication_list.csv', 
                    help='The path to the publication CSV file (containing all relevant columns for printing the GitHub home page). Default: publication_list.csv.')
parser.add_argument('-c','--collapsible',dest='collapsible', metavar='C', type = int, nargs='+', default = 0, choices = [0,1,2,3,4],
                    help='Depth of headers to make collapsible. Enter 0 for non-collapsible headers at all levels (ignored if other numbers are entered for this flag). Enter one or more values in {1,2,3,4} for collapsible headers for all level {1,2,3,4} headings. Default: 0.')
parser.add_argument('-i','--introduction-fpath',dest='introduction_fpath', metavar='I', nargs='?', default = 'publication_list_introduction.txt',
                    help='The path to a file containing text to print in between the first level-1 header and the remainder of the document. Enter an empty string ("") to print nothing. Default: publication_list_introduction.txt.')
parser.add_argument('-o','--output-fpath',dest='output_fpath',metavar='S',nargs='?',default='publication_list.txt',
                    help=f'The directory to save the output home page to (in Markdown). Default: publication_list.txt') # Consider changing default to {os.path.join("profile","README.md")} to match github.
parser.add_argument('-t','--toggle-state',dest='toggle_state', metavar='T', type = int, nargs='?', default = 0, choices = [0,1],
                    help='Whether to toggle headers (if collapsible) as collapsed or open by default. This flag is only valid if the -c flag is non-zero. Enter 0 for collapsed by default, or 1 for open by default. Default: 0.')
parser.add_argument('-v','--verbose',dest='verbose', metavar='V', type = int, nargs='?', default = 1, choices = [0,1],
                    help='Verbosity of output. Enter 1 to print output of file, or 0 to print nothing. Default: 1.')

args = parser.parse_args()

if isinstance(args.collapsible, int): # Force parsed "collapsible" arguments into a list.
    args.collapsible = [args.collapsible]
elif args.collapsible == None:
    args.collapsible = [0]

#------------------------------ Generate citation list ------------------------------#

df = pd.read_csv(args.publication_csv_fpath)

## SORT EXCEL COLUMNS
sort_list = ['level-1','level-2','level-3','level-4','year','month','date']
sort_order = [True, True, True, True, False, False, False]
df.sort_values(sort_list, ascending = sort_order, ignore_index = True, inplace = True)

## DEFINE FUNCTION TO PRINT INDIVIDUAL LINES
def print_citation_list(df_citations,
                        url_keys = ['manuscript', 'code', 'code-1', 'code-2',
                                    'dataset', 'dataset-1', 'dataset-2', 'video', 'demo',
                                    'demo-1','demo-2', 'demo-3', 'map', 'gui',
                                    'gui-demo-1', 'gui-demo-2', 'slides', 'poster'],
                        verbose = 0):
    '''
    For each row in df_citations, print all the titles/authors in one line,
    and the urls in url_keys in another line, in order of key appearance.
    
    ======
    Inputs
    ======
    df_citations : pd.DataFrame
        Dataframe with at least the following keys:
        - visible : 1 or 0 depending on whether the citation should be printed for that row
        - title : title of publication
        - author-first : name of first author in (first, last) format
        - multiple-authors : 1 or 0 depending on whether there were multiple authors for the listed publication
        - year : year of publication
        - pub-name : journal/conference that publication was made in
        - all keys in url_keys
    url_keys : list of str
        list of strings corresponding to the keys where urls are located (if any)
        urls will be added to the output string if the value corresponding to the key is not nan
    verbose : bool
        If True, also prints the output. If False, prints nothing.
    
    ======
    Output
    ======
    s : str
        The string corresponding to the citations generated by df_citations.
        print(s) will print the string nicely.
    '''
    citation_str = ""
    df_citations = df_citations[df_citations['visible'] == 1] # Print only citations meant to be visible
    for idx, row in df_citations.iterrows():
        line_1 = f"- {row['title']} ({row['author-first']}{' et al.' if row['multiple-authors'] else ''}, {row['year']})\n" # First line of citation
        line_2 = f"  - {row['pub-name']} " # Indented second line of citation
        if verbose:
            print(line_1, end="")
            print(line_2, end="")
        citation_str += line_1
        citation_str += line_2
        for url_key in url_keys:
            if type(row[url_key]) is str:
                url_str = f"[[{url_key}]]({row[url_key]}) " # String of URLS after indented second line of citation
                if verbose: print(url_str, end="")
                citation_str += url_str
        if verbose: print()
        citation_str += f"\n"
    if verbose: print()
    citation_str += f"\n"
    return citation_str

## ADD LINES CORRESPONDING TO CITATIONS TO A STRING
s = ""
for l1idx, l1str in enumerate(df['level-1'].dropna().unique()):
    # PRINT LEVEL 1 HEADERS
    if 1 in args.collapsible:
        s += f"<details{' open' if args.toggle_state else ''}>\n\n"
        s += f"<summary><h1>{l1str}</h1></summary>\n\n"
    else:
        s += f"# {l1str}\n\n"

    # PRINT INTRODUCTION TO FIRST LEVEL 1 HEADER
    if l1idx == 0 and args.introduction_fpath:
        with open(args.introduction_fpath) as fh:
            s += fh.read()

    dfl1 = df[df['level-1'] == l1str]
    if dfl1['level-2'].isna().all():
        s += print_citation_list(dfl1)

    for l2str in dfl1['level-2'].dropna().unique():
        # PRINT LEVEL 2 HEADERS
        if 2 in args.collapsible:
            s += f"<details{' open' if args.toggle_state else ''}>\n\n"
            s += f"<summary><h2>{l2str}</h2></summary>\n\n"
        else:
            s += f"## {l2str}\n\n"

        # GET AND PRINT STUFF AT @ BELOW LEVEL 2
        dfl2 = dfl1[dfl1['level-2'] == l2str]
        if dfl2['level-3'].isna().all():
            s += print_citation_list(dfl2)
        for l3str in dfl2['level-3'].dropna().unique():
            # PRINT LEVEL 3 HEADERS
            if 3 in args.collapsible:
                s += f"<details{' open' if args.toggle_state else ''}>\n\n"
                s += f"<summary><h3>{l3str}</h3></summary>\n\n"
            else:
                s += f"### {l3str}\n\n"

            # GET AND PRINT STUFF AT @ BELOW LEVEL 3
            dfl3 = dfl2[dfl2['level-3'] == l3str]
            if dfl3['level-4'].isna().all():
                s += print_citation_list(dfl3)
            for l4str in dfl3['level-4'].dropna().unique():
                # PRINT LEVEL 4 HEADERS
                if 4 in args.collapsible:
                    s += f"<details{' open' if args.toggle_state else ''}>\n\n"
                    s += f"<summary><h4>{l4str}</h4></summary>\n\n"
                else:
                    s += f"#### {l4str}\n\n"
                
                # GET AND PRINT STUFF AT LEVEL 4 (NO MORE LEVELS BELOW)
                s += print_citation_list(dfl4) 

                if 4 in args.collapsible:
                    s += f'</details>\n\n'
            if 3 in args.collapsible:
                s += f'</details>\n\n'
        if 2 in args.collapsible:
            s += f'</details>\n\n'
    if 1 in args.collapsible:
        s += f'</details>\n\n'
         
## PRINT STRING IF VERBOSE
if args.verbose: print(s)

## SAVE STRING TO FILE
output_dir, _ = os.path.split(args.output_fpath)
if len(output_dir) > 1 and (not os.path.exists(output_dir)): os.makedirs(output_dir)

with open(args.output_fpath,'w') as fh:
    fh.writelines(s)
