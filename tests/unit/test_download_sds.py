import sys, os
sys.path.append(os.path.realpath('find_sds'))

import re
import pytest
from unittest.mock import patch
from find_sds.find_sds import download_sds, download_sds_tci


def mock_raise_exception():
    # return pytest.raises(RuntimeError)
    raise RuntimeError()


@pytest.mark.parametrize(
    "cas_nr, expect", [
        ('885051-07-0', ('885051-07-0', True, 'TCI')),
        ('64-19-7', ('64-19-7', True, 'TCI')),
        ('67-68-5', ('67-68-5', True, 'TCI')),
        ('128-50-7', ('128-50-7', False, None)),
        ('41931-18-4', ('41931-18-4', False, None)),
    ]
)
def test_download_sds_tci(tmpdir, monkeypatch, cas_nr, expect):
    '''Test download_sds() WITHOUT existing mol files'''

    '''Changing the value of 'debug' variable to True for extra info'''
    monkeypatch.setattr("find_sds.find_sds.debug", True)

    result = download_sds_tci(cas_nr, download_path=tmpdir)  
    assert result == expect


@pytest.mark.parametrize(
    "cas_nr, expect", [
        ('623-51-8', ('623-51-8', True, 'Fisher')),
        ('28697-53-2', ('28697-53-2', True, 'Fisher')),
        ('1450-76-6', ('1450-76-6', True, 'ChemicalSafety')),
        ('00000-00-0', ('00000-00-0', False, None)),
    ]
)
def test_download_sds_without_existing_files(tmpdir, monkeypatch, cas_nr, expect):
    '''Test download_sds() WITHOUT existing mol files'''

    '''Changing the value of 'debug' variable to True for extra info'''
    monkeypatch.setattr("find_sds.find_sds.debug", True)

    result = download_sds(cas_nr, download_path=tmpdir)  
    assert result == expect


@pytest.mark.parametrize(
    "cas_nr, expect", [
        ('623-51-8', ('623-51-8', True, None)),
        ('28697-53-2', ('28697-53-2', True, None)),
        ('1450-76-6', ('1450-76-6', True, None)),
        ('00000-00-0', ('00000-00-0', False, None)),
    ]
)
def test_download_sds_with_existing_files(tmpdir, monkeypatch, cas_nr, expect):
    '''Test download_sds() WITH existing mol files'''

    '''Changing the value of 'debug' variable to True for extra info'''
    monkeypatch.setattr("find_sds.find_sds.debug", True)

    '''Run the download once to simulate existing file'''
    download_sds(cas_nr, download_path=tmpdir)

    result = download_sds(cas_nr, download_path=tmpdir)  
    assert result == expect


@pytest.mark.parametrize(
    "cas_nr, expect", [
        ('623-51-8', ('623-51-8', False, None)),
    ]
)
def test_download_sds_with_error(tmpdir, monkeypatch, cas_nr, expect):
    '''Test download_sds() WITHOUT existing mol files'''

    '''Changing the value of 'debug' variable to True for extra info'''
    monkeypatch.setattr("find_sds.find_sds.debug", True)

    monkeypatch.setattr('find_sds.find_sds.extract_download_url_from_fisher', mock_raise_exception)
    
    result = download_sds(cas_nr, download_path=tmpdir) 
    assert result == expect
