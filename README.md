[![Python 3](https://pyup.io/repos/github/khoivan88/find_sds/python-3-shield.svg)](https://pyup.io/repos/github/khoivan88/find_sds/)
[![Updates](https://pyup.io/repos/github/khoivan88/find_sds/shield.svg)](https://pyup.io/repos/github/khoivan88/find_sds/)
[![codecov](https://codecov.io/gh/khoivan88/find_sds/branch/master/graph/badge.svg)](https://codecov.io/gh/khoivan88/find_sds)
[![python version](https://img.shields.io/badge/python-v3.6%2B-blue)]()
[![tested platforms](https://img.shields.io/badge/tested%20platform-win%20%7C%20osx%20%7C%20ubuntu-lightgrey)]()

# FIND MISSING SAFETY DATA SHEET (SDS) 

This program is designed to find and download safety data sheet of chemical using CAS number.

<br/>


## CONTENTS

- [FIND MISSING SAFETY DATA SHEET (SDS)](#find-missing-safety-data-sheet-sds)
  - [CONTENTS](#contents)
  - [DETAILS](#details)
  - [REQUIREMENTS](#requirements)
  - [USAGE](#usage)
  - [VERSIONS](#versions)


## DETAILS
- Provided with a list of CAS numbers, this program searches and downloads safety
data sheet (SDS) into a designated folder. If a download folder is not provided,
SDS will be downloaded into folder 'SDS' inside folder `find_sds`.
- This program uses **multithreading** to speed up the download process. By default,
ten threads are used but it can be changed depends on running computer.
- Downloaded SDS are saved as '<CAS_Number>-SDS.pdf'



## REQUIREMENTS

- Python 3+
- [Dependencies](requirements.txt)

<br/>

## USAGE

1. Clone this repository:
   
   ```bash
   $ git clone https://github.com/khoivan88/find_sds.git    #if you have git
   # if you don't have git, you can download the zip file then unzip
   ```

2. Change into the directory of the program:
   
   ```bash
   $ cd find_sds
   ```

3. (Optional): create virtual environment for python to install dependency:
   Note: you can change `find_sds_venv` to another name if desired.

   ```bash
   $ python3 -m venv find_sds_venv   # Create virtual environment
   $ source find_sds_venv/bin/activate    # Activate the virtual environment on Linux
   # find_sds_venv/Scripts/activate    # Activate the virtual environment on Windows
   ```

4. Install python dependencies:
   
   ```bash
   $ pip install -r requirements.txt
   ```

5. Example usage:
   
   ```bash
   $ python3
   ```

   ```python
   >>> from find_sds.find_sds import find_sds
   >>> cas_list = ['141-78-6', '110-82-7', '67-63-0', '75-09-2', '109-89-7',
   ...     '872-50-4', '68-12-2', '96-47-9', '111-66-0', '110-54-3',
   ...     '00000-0-0',    # invalid CAS number, or unknow CAS
   ... ]
   >>> download_path = 'SDS'
   >>> find_sds(cas_list=cas_list, download_path=download_path, pool_size=10)
   Downloading missing SDS files. Please wait!
   
   Searching for 96-47-9-SDS.pdf ...
   
   Searching for 110-82-7-SDS.pdf ...

   Searching for 141-78-6-SDS.pdf ...

   Searching for 872-50-4-SDS.pdf ...

   Searching for 00000-0-0-SDS.pdf ...

   Searching for 111-66-0-SDS.pdf ...

   Searching for 110-54-3-SDS.pdf ...

   Searching for 75-09-2-SDS.pdf ...

   Searching for 68-12-2-SDS.pdf ...

   Searching for 67-63-0-SDS.pdf ...

   Searching for 109-89-7-SDS.pdf ...

   Still missing SDS:
   {'00000-0-0'}

   Summary:
           1 SDS files are missing.
           10 SDS files downloaded.


   (Optional): you can turn on debug mode (more error printing during search) using the following command:
   python find_sds/find_sds.py  --debug

   >>>
   ```

<br/>


## VERSIONS
See [here](VERSION.md) for the most up-to-date
