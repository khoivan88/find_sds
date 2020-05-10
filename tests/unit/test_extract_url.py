import sys, os
sys.path.append(os.path.realpath('find_sds'))

import re
import pytest
from find_sds.find_sds import extract_download_url_from_fisher, \
                                    extract_download_url_from_chemicalsafety, \
                                    extract_download_url_from_fluorochem, \
                                    extract_download_url_from_chemblink, \
                                    extract_download_url_from_vwr


def mock_raise_exception():
    # return pytest.raises(RuntimeError)
    raise RuntimeError()

@pytest.mark.xfail    # Fisher source might change leading to slightly different URL
@pytest.mark.parametrize(
    "cas_nr, expect", [
        ('623-51-8', (
            'Fisher',
            'https://www.fishersci.com/store/msds?partNumber=AC118675000&productDescription=ethyl-mercaptoacetate--acros-organicstrade&vendorId=VN00032119&keyword=true&countryCode=US&language=en'
            )
        ),
        ('28697-53-2', (
            'Fisher',
            'https://www.fishersci.com/store/msds?partNumber=S25650&productDescription=darabinose&vendorId=VN00115888&keyword=true&countryCode=US&language=en'
            )
        ),
        ('1450-76-6', (
            None,
            None
            )
        ),
        ('00000-00-0', (
            None,
            None
            )
        ),
    ]
)
def test_extract_url_from_fisher(cas_nr, expect):
    source, url = extract_download_url_from_fisher(cas_nr) or (None, None)
    assert (source, url) == expect


@pytest.mark.parametrize(
    "cas_nr, expect", [
        ('623-51-8', None)
    ]
)
def test_extract_url_from_fisher_with_exception(monkeypatch, cas_nr, expect):
    monkeypatch.setattr('find_sds.find_sds.requests.get', mock_raise_exception)
    result = extract_download_url_from_fisher(cas_nr)
    assert result == expect


@pytest.mark.parametrize(
    "cas_nr, expect", [
        ('623-51-8', (
            'ChemicalSafety',
            'http://sds.chemicalsafety.com/sds/pda/msds/getpdf.ashx?action=msdsdocument&auth=200C200C200C200C2008207A200D2078200C200C200C200C200C200C200C200C200C2008&param1=ZmRwLjFfNzM2MzAwMDNORQ==&unique='
            )
        ),
        ('28697-53-2', (
            'ChemicalSafety',
            'http://sds.chemicalsafety.com/sds/pda/msds/getpdf.ashx?action=msdsdocument&auth=200C200C200C200C2008207A200D2078200C200C200C200C200C200C200C200C200C2008&param1=ZmRwLjFfMjQ3MDYyMDNORQ==&unique='
            )
        ),
        ('1450-76-6', (
            'ChemicalSafety',
            'http://sds.chemicalsafety.com/sds/pda/msds/getpdf.ashx?action=msdsdocument&auth=200C200C200C200C2008207A200D2078200C200C200C200C200C200C200C200C200C2008&param1=ZmRwLjFfNTI5ODU1MDNORQ==&unique='
            )
        ),
        ('00000-00-0', (
            None,
            None
            )
        ),
    ]
)
def test_extract_url_from_chemicalsafety(cas_nr, expect):
    source, url = extract_download_url_from_chemicalsafety(cas_nr) or (None, None)
    # Chemicalsafety return url with changing `...&unique=some-number`.
    # Use regex to remove this number for consistent result
    url = re.sub(r'(?<=unique=).+$', '', url) if url else None
    assert (source, url) == expect


@pytest.mark.parametrize(
    "cas_nr, expect", [
        ('623-51-8', None)
    ]
)
def test_extract_url_from_chemicalsafety_with_exception(monkeypatch, cas_nr, expect):
    monkeypatch.setattr('find_sds.find_sds.requests.post', mock_raise_exception)
    result = extract_download_url_from_chemicalsafety(cas_nr)
    assert result == expect


@pytest.mark.parametrize(
    "cas_nr, expect", [
        ('623-51-8', (
            None,
            None
            )
        ),
        ('28697-53-2', (
            'Fluorochem',
            'https://www.cheminfo.org/webservices/msds?brand=fluorochem&catalog=237868&embed=true'
            )
        ),
        ('1450-76-6', (
            'Fluorochem',
            'https://www.cheminfo.org/webservices/msds?brand=fluorochem&catalog=219286&embed=true'
            )
        ),
        ('00000-00-0', (
            None,
            None
            )
        ),
    ]
)
def test_extract_url_from_fluorochem(cas_nr, expect):
    source, url = extract_download_url_from_fluorochem(cas_nr) or (None, None)
    assert (source, url) == expect


@pytest.mark.parametrize(
    "cas_nr, expect", [
        ('28697-53-2', None)
    ]
)
def test_extract_url_from_fluorochem_with_exception(monkeypatch, cas_nr, expect):
    monkeypatch.setattr('find_sds.find_sds.requests.post', mock_raise_exception)
    result = extract_download_url_from_fluorochem(cas_nr)
    assert result == expect


@pytest.mark.parametrize(
    "cas_nr, expect", [
        ('67-68-5', (
            'Alfa-Aesar',
            'https://www.chemblink.com/MSDS/MSDSFiles/67-68-5_Alfa-Aesar.pdf'
            )
        ),
        ('64-19-7', (
            'Alfa-Aesar',
            'https://www.chemblink.com/MSDS/MSDSFiles/64-19-7_Alfa-Aesar.pdf'
            )
        ),
        ('1450-76-6', (
            'Sigma-Aldrich',
            'https://www.chemblink.com/MSDS/MSDSFiles/1450-76-6_Sigma-Aldrich.pdf'
            )
        ),
        ('681128-50-7', (
            'Matrix',
            'https://www.chemblink.com/MSDS/MSDSFiles/681128-50-7_Matrix.pdf'
            )
        ),
        ('00000-00-0', (
            None,
            None
            )
        ),
    ]
)
def test_extract_url_from_chemblink(cas_nr, expect):
    source, url = extract_download_url_from_chemblink(cas_nr) or (None, None)
    assert (source, url) == expect


@pytest.mark.parametrize(
    "cas_nr, expect", [
        ('623-51-8', None)
    ]
)
def test_extract_url_from_chemblink_with_exception(monkeypatch, cas_nr, expect):
    monkeypatch.setattr('find_sds.find_sds.requests.get', mock_raise_exception)
    result = extract_download_url_from_chemblink(cas_nr)
    assert result == expect


@pytest.mark.parametrize(
    "cas_nr, expect", [
        # ('67-68-5', (
        #     'TCI America',
        #     'https://us.vwr.com/assetsvc/asset/en_US/id/17035574/contents'
        #     )
        # ),
        ('64-19-7', (
            'Acros Organics',
            'https://us.vwr.com/assetsvc/asset/en_US/id/17991993/contents'
            )
        ),
        ('1450-76-6', (
            'TCI America',
            'https://us.vwr.com/assetsvc/asset/en_US/id/16979825/contents'
            )
        ),
        ('885051-07-0', (
            'TCI America',
            'https://us.vwr.com/assetsvc/asset/en_US/id/18065210/contents'
            )
        ),
        ('623-51-8', (
            'TCI America',
            'https://us.vwr.com/assetsvc/asset/en_US/id/16825892/contents'
            )
        ),
        ('681128-50-7', (
            None,
            None
            )
        ),
        ('00000-00-0', (
            None,
            None
            )
        ),
    ]
)
def test_extract_url_from_vwr(cas_nr, expect):
    source, url = extract_download_url_from_vwr(cas_nr) or (None, None)
    assert (source, url) == expect


@pytest.mark.parametrize(
    "cas_nr, expect", [
        ('623-51-8', None)
    ]
)
def test_extract_url_from_vwr_with_exception(monkeypatch, cas_nr, expect):
    monkeypatch.setattr('find_sds.find_sds.requests.session', mock_raise_exception)
    result = extract_download_url_from_vwr(cas_nr)
    assert result == expect
