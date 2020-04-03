# import sys
# print(sys.path)

# #!/usr/bin/python

"""
Author: Khoi Van, 2020

This program is designed to find and download safety data sheet (SDS)
using multithreading
"""


import json
import os
import re
import sys
import traceback
from functools import partial
from multiprocessing import Pool
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import requests
from bs4 import BeautifulSoup

debug = False
# print out extra info in debug mode in case SDS is not found
if len(sys.argv) == 2 and sys.argv[1] in ['--debug=True', '--debug=true', '--debug', '-d']:
    debug = True


def find_sds(cas_list: List[str], download_path: str = None, pool_size: int = 10) -> None:
    """Find safety data sheet (SDS) for list of CAS numbers
    
    Parameters
    ----------
    cas_list : List[str]
        List of CAS numbers
    download_path : str, optional
        the path for downloaded file, 
        by default None. If so, SDS will be downloaded into folder 'SDS' 
            inside folder containing the python file
    pool_size : int, optional
        the number of multithread that are running simultaneously, 
        by default 10
    
    Returns
    -------
    None:
        Summary of result is print to screen
    """

    global debug

    # If the list of CAS is empty, exit the program
    if not cas_list:
        print('List of CAS numbers is empty!')
        exit(0)

    # # print out extra info in debug mode in case SDS is not found
    # if len(sys.argv) == 2 and sys.argv[1] in ['--debug=True', '--debug=true', '--debug', '-d']:
    #     debug = True
    # print('debug value: {}'.format(debug))

    # Set download_path to 'SDS' folder inside the parent folder of python file
    if not download_path:
        download_path = Path(__file__).resolve().parent / 'SDS'

    # Get the set of CAS for molecule missing sds:
    to_be_downloaded = set(cas_list)

    # Step 1: downloading sds file
    # Check if download path directory exists. If not, create it
    # https://stackoverflow.com/questions/12517451/automatically-creating-directories-with-file-output
    # https://docs.python.org/3/library/os.html#os.makedirs
    os.makedirs(download_path, exist_ok=True)

    print('Downloading missing SDS files. Please wait!')
    
    download_result = []
    # # Using multithreading
    try:
        with Pool(pool_size) as p:
            download_result = p.map(partial(
                                        download_sds,
                                        download_path=download_path),
                                    to_be_downloaded)
        
    except Exception as error:
        # if debug:
        traceback_str = ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__))
        print(traceback_str)


    # Step 2: print out summary
    finally:
        # Sometimes Pool worker return 'None', remove 'None' as the following
        # print(download_result)
        download_result = [x for x in download_result if x]

        missing_sds = set()
        updated_sds = set()

        for cas_nr, sds_existed, sds_source in download_result:
            if sds_existed:
                updated_sds.add(cas_nr)
            else:
                missing_sds.add(cas_nr)
        
        if missing_sds:
            print('\nStill missing SDS:\n{}'.format(missing_sds))
        
        print('\nSummary: ')
        print('\t{} SDS files are missing.'.format(len(missing_sds)))
        print('\t{} SDS files downloaded.'.format(len(updated_sds)))

        # Advice user about turning on debug mode for more error printing
        if not debug:
            print('\n\n(Optional): you can turn on debug mode (more error printing during search) using the following command:')
            print('python find_sds/find_sds.py  --debug\n')


def download_sds(cas_nr: str, download_path: str) -> Tuple[str, bool, Optional[str]]:
    """Download SDS from variety of sources

    Parameters
    ----------
    cas_nr : str
        The CAS number of the molecule of interest
    download_path : str
        The path to download folder

    Returns
    -------
    Tuple[str, bool, Optional[str]]
        - str: CAS number of the input chemical
        - bool: True if SDS file downloaded or exists
        - Optional[str]: the name of the SDS source or None
    """

    global debug
    '''This function is used to extract a single sds file
    See here for more info: http://stackabuse.com/download-files-with-python/'''

    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}

    # Set initial return value for if SDS is downloaded (or existed)
    downloaded = False

    file_name = cas_nr + '-SDS.pdf'
    download_file = Path(download_path) / file_name
    # Check if the file not exists and download
    # check file exists: https://stackoverflow.com/questions/82831/how-do-i-check-whether-a-file-exists
    if download_file.exists():
        # print('{} already downloaded'.format(file_name))
        # print('.', end='')
        downloaded = True
        return cas_nr, downloaded, None

    else:
        print('\nSearching for {} ...'.format(file_name))
        try:
            # print('CAS {} ...'.format(file_name))
            sds_source, full_url = extract_download_url_from_fisher(cas_nr) or (None, None)
            if full_url is None:    # extract with chemblink
                sds_source, full_url = extract_download_url_from_chemblink(cas_nr) or (None, None)
            if full_url is None:    # extract with chemicalsafety
                sds_source, full_url = extract_download_url_from_chemicalsafety(cas_nr) or (None, None)
            if full_url is None:    # extract with fluorochem
                sds_source, full_url = extract_download_url_from_fluorochem(cas_nr) or (None, None)
            # print('full url is: {}'.format(full_url))
            if full_url:    # extract with chemicalsafety
                r = requests.get(full_url, headers=headers, timeout=20)
                # Check to see if give OK status (200) and not redirect
                if r.status_code == 200 and len(r.history) == 0:
                    # print('\nDownloading {} ...'.format(file_name))
                    open(download_file, 'wb').write(r.content)
                    # print()
                    # return (0, sds_source)
                    downloaded = True
                    return (cas_nr, downloaded, sds_source)

            else:
                return download_sds_tci(cas_nr, download_path)
                # return 1

        except Exception as error:
            if debug:
                traceback_str = ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__))
                print(traceback_str)
            return (cas_nr, downloaded, None)


def extract_download_url_from_fisher(cas_nr: str) -> Optional[Tuple[str, str]]:
    """Search for url to download SDS for chemical with cas_nr
    from https://www.fishersci.com

    Parameters
    ----------
    cas_nr : str
        CAS# for chemical of interest

    Returns
    -------
    Optional[Tuple[str, str]]
        Tuple[str, str]:
            the name of the SDS source
            the URL from Fisher for SDS file
        None: if URL cannot be found
    """

    global debug

    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}

    # get url from Fisher to get url to download sds file
    extract_info_url = 'https://www.fishersci.com/us/en/catalog/search/sds'
    payload = {
        'selectLang': 'EN',
        'msdsKeyword': cas_nr}

    if debug:
        print('Searching on https://www.fishersci.com/us/en/catalog/search/sdshome.html')

    try:
        r = requests.get(extract_info_url, headers=headers, timeout=10, params=payload)
        # Check to see if give OK status (200) and not redirect
        if r.status_code == 200 and len(r.history) == 0:
            # BeautifulSoup ref: https://www.digitalocean.com/community/tutorials/how-to-scrape-web-pages-with-beautiful-soup-and-python-3
            # Using BeautifulSoup to scrap text
            html = BeautifulSoup(r.text, 'html.parser')
            # The list of found sds is in class 'catalog_num', with each item in class 'catlog_items'
            # cat_no_list = html.find(class_='catalog_num')    # This is to find all of the sds

            # Check if there is error message. Fisher automatically does a close search with error message
            error_message = html.find(class_='errormessage search_results_error_message')
            cat_no_list = html.find(class_='catlog_items')    # This will find the first sds
            
            if (not error_message) and cat_no_list:
                cat_no_items = cat_no_list.find_all('a')   #
                # download info
                rel_download_url = cat_no_items[0].get('href')
                catalogID = cat_no_items[0].contents[0]
                full_url = 'https://www.fishersci.com' + rel_download_url
                # print(f'rel_download_url is {rel_download_url}')
                return 'Fisher', full_url

    except Exception as error:
        # print('.', end='')
        if debug:
            traceback_str = ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__))
            print(traceback_str)
        # return None


def extract_download_url_from_chemblink(cas_nr: str) -> Optional[Tuple[str, str]]:
    """Search for url to download SDS for chemical with cas_nr
    from https://www.chemblink.com/
    
    Parameters
    ----------
    cas_nr : str
        CAS# for chemical of interest
    
    Returns
    -------
    Optional[Tuple[str, str]]
        Tuple[str, str]:
            the name of the SDS source
            the URL from Fisher for SDS file
        None: if URL cannot be found

    Examples
    --------
    >>> print(extract_download_url_from_chemblink(cas_nr='681128-50-7'))
    ('Matrix', 'https://www.chemblink.com/MSDS/MSDSFiles/681128-50-7_Matrix.pdf')
    """
    
    global debug

    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }

    # get url from chemicalsafety.com to get url to download sds file
    extract_info_url = f'https://www.chemblink.com/MSDS/{cas_nr}_MSDS.htm'

    if debug:
        print('Searching on https://www.chemblink.com')

    try:
        r1 = requests.get(extract_info_url, headers=headers, timeout=20)
        # print(r1)
    
        # Check to see if give OK status (200) and not redirect
        if r1.status_code == 200 and len(r1.history) == 0:
            soup = BeautifulSoup(r1.text, 'html.parser')
            if soup:
                # Find all <a> tags with content "View / download", example: https://www.chemblink.com/MSDS/64-19-7_MSDS.htm
                # Example of a correct <a> tag for SDS download: '<a href="/MSDS/MSDSFiles/64-19-7_Alfa-Aesar.pdf" class="blue" onclick="blur()" target="_blank">View / download</a>'
                a_tags = soup.find_all('a', string=re.compile(r'View / download'))
                if a_tags:
                    domain = 'https://www.chemblink.com'
                    sds_link = a_tags[0]['href']
                    # Get source name from sds_link, example of sds_link href: '/MSDS/MSDSFiles/64-19-7_Alfa-Aesar.pdf'
                    source = re.search(r'\S+_(\S*)\.pdf', sds_link).group(1)
                    full_url = f'{domain}{sds_link}'
                    return source, full_url

    except Exception as error:
        # print('.', end='')
        if debug:
            traceback_str = ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__))
            print(traceback_str)
        # return None


def extract_download_url_from_chemicalsafety(cas_nr: str) -> Optional[Tuple[str, str]]:
    """Search for url to download SDS for chemical with cas_nr
    from https://chemicalsafety.com/sds-search/
    
    Parameters
    ----------
    cas_nr : str
        CAS# for chemical of interest
    
    Returns
    -------
    Optional[Tuple[str, str]]
        Tuple[str, str]:
            the name of the SDS source
            the URL from Fisher for SDS file
        None: if URL cannot be found
    """

    global debug

    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
        'accept-encoding': 'gzip, deflate, br',
        'content-type': 'application/json'}
    # get url from chemicalsafety.com to get url to download sds file
    extract_info_url = 'https://chemicalsafety.com/sds1/retriever.php'
    form1 = {
        "action": "search", 
        "p1": "MSMSDS.COMMON|",
        "p2": "MSMSDS.MANUFACT|", 
        "p3": "MSCHEM.CAS|" + cas_nr,
        "hostName": "chemicalsafety.com", 
        "isContains": "0"
        }

    if debug:
        print('Searching on https://chemicalsafety.com/sds-search/')

    try:
        r1 = requests.post(extract_info_url, headers=headers, 
                data=json.dumps(form1), timeout=20)
        # Check to see if give OK status (200) and not redirect
        if r1.status_code == 200 and len(r1.history) == 0:
            id_list = r1.json()['rows']
            msds_id = ''
            for item in id_list:
                if item[3] == cas_nr:
                    msds_id = item[0]
                    break
            if msds_id != '':
                form2 = {"action": "msdsdetail",
                        "p1": msds_id,
                        "p2": "",
                        "p3": "",
                        "isContains": ""}
                r2 = requests.post(extract_info_url, headers=headers, 
                        data=json.dumps(form2), timeout=20)
                result = r2.json()['rows'][0]
                #Confirm the msds_id and cas_nr:
                if msds_id == result[0] and cas_nr == result[3]:
                    sds_pdf_file = result[10].rstrip(',')
                    form3 = {"action":"getpdfurl","p1":sds_pdf_file,"p2":"","p3":"","isContains":""}
                    r3 = requests.post(extract_info_url, headers=headers, data=json.dumps(form3), timeout=20)
                    #Get the url
                    # Translate curl to python https://curl.trillworks.com/
                    # urllib.parse doc: https://docs.python.org/3.6/library/urllib.parse.html
                    full_url = r3.json()['url']
                    return 'ChemicalSafety', full_url
    except Exception as error:
        # print('.', end='')
        if debug:
            traceback_str = ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__))
            print(traceback_str)
        # return None


def extract_download_url_from_fluorochem(cas_nr: str) -> Optional[Tuple[str, str]]:
    """Search for url to download SDS for chemical with cas_nr
    from http://www.fluorochem.co.uk/
        
    Parameters
    ----------
    cas_nr : str
        CAS# for chemical of interest
    
    Returns
    -------
    Optional[Tuple[str, str]]
        Tuple[str, str]:
            the name of the SDS source
            the URL from Fisher for SDS file
        None: if URL cannot be found
    """

    global debug

    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
        'Content-Type': 'application/json', }

    url = 'http://www.fluorochem.co.uk/Products/Search'
    payload = {
        "lstSearchType": "C",
        "txtSearchText": cas_nr,
        "showPrices": 'false',
        "showStructures": 'false',
        "groupFilters": []}

    if debug:
        print('Searching on http://www.fluorochem.co.uk')

    try:
        r = requests.post(url, headers=headers, timeout=20, data=json.dumps(payload))
        # No need to check if requests give OK status (200) and not redirect because
        # fluorochem return code 200 without redirect with error

        # BeautifulSoup ref: https://www.digitalocean.com/community/tutorials/how-to-scrape-web-pages-with-beautiful-soup-and-python-3
        # Using BeautifulSoup to scrap text
        html = BeautifulSoup(r.text, 'html.parser')
        if html:
            result = html.find_all('td')
            if result:
                # info = [item.contents[0] for item in result]
                # cat_no_1 = info[0]
                # cas = info[2]
                cat_no_2 = html.find(class_='textLink prodDetailLink').get('prodcode')
                # confirming cas# and catalog number
                # if cas == cas_nr and cat_no_1 == cat_no_2:
                # download info
                download_url = 'https://www.cheminfo.org/webservices/msds?brand=fluorochem&catalog={}&embed=true'
                full_url = download_url.format(cat_no_2)
                return 'Fluorochem', full_url
    except Exception as error:
        #     print('.', end='')
        if debug:
            traceback_str = ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__))
            print(traceback_str)
        # return None


def download_sds_tci(cas_nr: str, download_path: str) -> Tuple[str, bool, Optional[str]]:
    """Download SDS from TCI Chemicals (www.tcichemicals.com)

    Parameters
    ----------
    cas_nr : str
        The CAS number of the molecule of interest
    download_path : str
        The path to download folder

    Returns
    -------
    Tuple[str, bool, Optional[str]]
        - str: CAS number of the input chemical
        - bool: True if SDS file downloaded or exists
        - str: the name of the SDS source or None
    """
    '''Note: this function cannot be combined with download_sds() because 
    downloading SDS from TCI requires session and cookies'''

    global debug

    if debug:
        print('Searching on https://www.tcichemicals.com/en/us/')


    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}

    adv_search_url = 'https://www.tcichemicals.com/eshop/en/us/catalog/list/search?searchCasNo={}&mode=1'.format(cas_nr)
    
    # Set initial return value for if SDS is downloaded (or existed)
    downloaded = False

    file_name = cas_nr + '-SDS.pdf'
    download_file = Path(download_path) / file_name

    try:
        get_id = requests.get(adv_search_url, headers=headers, timeout=10)

        if get_id.status_code == 200 and len(get_id.history) == 0:
            # get_id.text
            html = BeautifulSoup(get_id.text, 'html.parser')
    #         print(html.prettify())

            hit_count = html.find(class_='search-sum').text
    #         hit_count

            # Check to make sure that there is at least 1 hit
            if hit_count:
                '''
                The first hit ('cart') have the unique ID in <form> (<form id='cart1_0'>) tag. 
                Use this info to find the first "cart".
                '''
                # Find the first hit using the <form> with unique 'id'
                first_hit_form = html.find('form', id='cart1_0')

                # The info for this form is the <table> right above the first hit <form>
                first_hit_info = first_hit_form.find_previous_sibling('table', class_='comp-tbl')
    #             print(first_hit_info.prettify())

                ''' Find the CAS# for the first hit
                Right above the <form> tag is the chemical info. The html that show CAS#:
                    <th class="comp-th">
                        <span>CAS RN</span>
                    </th>
                    <td class="comp-td" colspan="2">
                        <span>885051-07-0</span>
                    </td>
                Search for the returned_cas to match with the given CAS#
                '''
                returned_cas = first_hit_info.find('span', string='CAS RN').parent.find_next_sibling().span.text
    #             print(returned_cas)

                # Confirm the first hit has the same CAS# as search chemical
                if returned_cas == cas_nr:
                    '''The first <form> order box, have id='cart1_0'. 
                    Inside this <form> has <input> with id='commodityCode' and value gives the TCI product number.
                    Exammple:
                        <form action="/eshop/en/us/catalog/list" enctype="application/x-www-form-urlencoded" id="cart1_0" method="post" name="cart1_0" onsubmit="return false;">
                            ...
                            <input id="commodityCode" name="commodityCode" type="hidden" value="B3296"/>
                            ...
                        </form>
                    Get this TCI product number as follow:
                    '''
    #                 tci_id = html.find('form', id='cart1_0').find('input', id='commodityCode').get('value')
                    tci_id = first_hit_form.find('input', id='commodityCode').get('value')
    #                 print(tci_id)

                    # Check if TCI product number is found:
                    if tci_id:
                        sds_url = 'https://www.tcichemicals.com/eshop/en/us/commodity/{}/'.format(tci_id)
                        '''For some reason, TCI does not allow using sds_url2 directly, that is why this code 
                        go to the detail page of the chemical (sds_url) and then use Session() to go to the 
                        SDS download page (sds_url2)'''
                        with requests.Session() as s:
                            sds = s.get(sds_url, headers=headers, timeout=15)
                            if sds.status_code == 200 and len(sds.history) == 0:
                                sds_url2 = 'https://www.tcichemicals.com/eshop/en/us/catalog/detail/msds/en/{}/'.format(tci_id)
                                sds2 = s.get(sds_url2, headers=headers, timeout=15)
                                if sds2.status_code == 200:
                                    open(download_file, 'wb').write(sds2.content)
                                    downloaded = True
                                    return (cas_nr, downloaded, 'TCI')
    
    except Exception as error:
        if debug:
            traceback_str = ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__))
            print(traceback_str)
        return (cas_nr, downloaded, None)


if __name__ == '__main__':
    cas_list = [
        '141-78-6',
        '110-82-7',
        '67-63-0',
        '75-09-2',
        '109-89-7',
        '872-50-4',
        '68-12-2',
        '96-47-9',
        '111-66-0',
        '110-54-3',
        '00000-0-0',
    ]
    download_path = 'SDS'
    find_sds(cas_list=cas_list, download_path=download_path, pool_size=10)

    # find_sds(cas_list=cas_list, pool_size=10)
