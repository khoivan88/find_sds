import sys, os
sys.path.append(os.path.realpath('find_sds'))

import re
from pathlib import Path
import pytest
from unittest.mock import patch
from find_sds.find_sds import find_sds


# def mock_raise_exception():
#     # return pytest.raises(RuntimeError)
#     raise RuntimeError()


# @pytest.mark.parametrize(
#     "cas_nr, expect", [
#         ('885051-07-0', ('885051-07-0', True, 'TCI')),
#         ('64-19-7', ('64-19-7', True, 'TCI')),
#         ('67-68-5', ('67-68-5', True, 'TCI')),
#         ('128-50-7', ('128-50-7', False, None)),
#         ('41931-18-4', ('41931-18-4', False, None)),
#     ]
# )
def test_find_sds(tmpdir, monkeypatch):
    '''Test find_sds() WITHOUT existing mol files'''
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
    ]

    '''Changing the value of 'debug' variable to True for extra info'''
    monkeypatch.setattr("find_sds.find_sds.debug", True)

    find_sds(cas_list, download_path=tmpdir)  
    for cas in cas_list:
        file = Path(tmpdir) / (cas + '-SDS.pdf')
        assert file.exists()
