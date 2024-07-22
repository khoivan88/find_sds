import sys, os
sys.path.append(os.path.realpath('find_sds'))

import re
import pytest
from find_sds.find_sds import extract_download_url_from_fisher, \
                                    extract_download_url_from_chemicalsafety, \
                                    extract_download_url_from_fluorochem, \
                                    extract_download_url_from_chemblink, \
                                    extract_download_url_from_vwr, \
                                    extract_download_url_from_tci


def mock_raise_exception():
    # return pytest.raises(RuntimeError)
    raise RuntimeError()

@pytest.mark.xfail    # Fisher source might change leading to slightly different URL
@pytest.mark.parametrize(
    "cas_nr, expect", [
        ('623-51-8', (
            'Fisher',
            'https://www.fishersci.com/store/msds?partNumber=AAA1432106&productDescription=ethyl-mercaptoacet-g&vendorId=VN00024248&keyword=true&countryCode=US&language=en'
            )
        ),
        ('28697-53-2', (
            'Fisher',
            'https://www.fishersci.com/store/msds?partNumber=AC161450250&productDescription=d-arabinose-pa-gr&vendorId=VN00032119&keyword=true&countryCode=US&language=en'
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
            # 'ChemicalSafety',
            # 'http://sds.chemicalsafety.com/sds/pda/msds/getpdf.ashx?action=msdsdocument&auth=200C200C200C200C2008207A200D2078200C200C200C200C200C200C200C200C200C2008&param1=ZmRwLjFfNzM2MzAwMDNORQ==&unique='
            # 'Ambeed, Inc.', 'https://file.ambeed.com/static/upload/prosds/am/306/SDS-A305712.pdf',
            'Tokyo Chemical Industry Co., Ltd.', 'https://www.tcichemicals.com/US/en/sds/T0211_US_EN.pdf'
            )
        ),
        ('28697-53-2', (
            # 'ChemicalSafety',
            # 'http://sds.chemicalsafety.com/sds/pda/msds/getpdf.ashx?action=msdsdocument&auth=200C200C200C200C2008207A200D2078200C200C200C200C200C200C200C200C200C2008&param1=ZmRwLjFfMTQ2NzY2MDNORQ==&unique='
            # 'ChemScene LLC', 'https://file.ambeed.com/static/upload/prosds/am/178/SDS-A177089.pdf',
            'Ambeed, Inc.', 'https://file.ambeed.com/static/upload/prosds/am/178/SDS-A177089.pdf',
            )
        ),
        ('1450-76-6', (
            # 'ChemicalSafety',
            # 'http://sds.chemicalsafety.com/sds/pda/msds/getpdf.ashx?action=msdsdocument&auth=200C200C200C200C2008207A200D2078200C200C200C200C200C200C200C200C200C2008&param1=ZmRwLjFfODA5NTg4MDNORQ==&unique='
            # 'Ambeed, Inc.', 'https://file.chemscene.com/pdf/UsaMSDS/MSDSUSACS-W002624.pdf',
            'COMBI-BLOCKS', 'https://www.combi-blocks.com/msds/ST-9753.pdf'
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
        ('110489-05-9', None)
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
            'https://7128445.app.netsuite.com/core/media/media.nl?id=3356442&c=7128445&h=_v0Kc3ryqhf0PELFoYMezAkGMM5n8jmJXkNJjwa0JFQ7TLqt&_xt=.pdf'
            )
        ),
        ('1450-76-6', (
            'Fluorochem',
            'https://7128445.app.netsuite.com/core/media/media.nl?id=3274568&c=7128445&h=JZhDK4ckHBy0gdR1VbKyhzkmtZYBQzSKpmFRM33N7hUNvc4D&_xt=.pdf'
            )
        ),
        ('491588-98-8', (
            'Fluorochem',
            'https://7128445.app.netsuite.com/core/media/media.nl?id=3440879&c=7128445&h=PP8rxC0xkIl2R9G77mZWbuoWcmp39xUlKf5lVWxrDQl8brqz&_xt=.pdf'
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
            # 'https://www.chemblink.com/MSDS/MSDSFiles/67-68-5_Alfa-Aesar.pdf'
            'https://www.chemblink.com/MSDS/MSDSFiles/67-68-5Alfa-Aesar.pdf'
            )
        ),
        ('64-19-7', (
            'Alfa-Aesar',
            # 'https://www.chemblink.com/MSDS/MSDSFiles/64-19-7_Alfa-Aesar.pdf'
            'https://www.chemblink.com/MSDS/MSDSFiles/64-19-7Alfa-Aesar.pdf'
            )
        ),
        ('1450-76-6', (
            'Sigma-Aldrich',
            # 'https://www.chemblink.com/MSDS/MSDSFiles/1450-76-6_Sigma-Aldrich.pdf'
            'https://www.chemblink.com/MSDS/MSDSFiles/1450-76-6Sigma-Aldrich.pdf'
            )
        ),
        ('681128-50-7', (
            'Matrix',
            # 'https://www.chemblink.com/MSDS/MSDSFiles/681128-50-7_Matrix.pdf'
            'https://www.chemblink.com/MSDS/MSDSFiles/681128-50-7Matrix.pdf'
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


@pytest.mark.xfail    # source might change leading to slightly different URL
@pytest.mark.parametrize(
    "cas_nr, expect", [
        # ('67-68-5', (
        #     'TCI America',
        #     'https://us.vwr.com/assetsvc/asset/en_US/id/17035574/contents'
        #     )
        # ),
        ('64-19-7', (
            # 'Acros Organics',
            'Thermo Scientific',
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
    monkeypatch.setattr('find_sds.find_sds.requests.Session', mock_raise_exception)
    result = extract_download_url_from_vwr(cas_nr)
    assert result == expect


@pytest.mark.xfail    # source might change leading to slightly different URL
@pytest.mark.parametrize(
    "cas_nr, expect", [
        ('67-68-5', (
            'TCI',
            'https://www.tcichemicals.com/US/en/sds/D5293_US_EN.pdf'
            )
        ),
        ('64-19-7', (
            'TCI',
            'https://www.tcichemicals.com/US/en/sds/A3377_US_EN.pdf'
            )
        ),
        ('1450-76-6', (
            'TCI',
            'https://www.tcichemicals.com/US/en/sds/H1378_US_EN.pdf'
            )
        ),
        ('885051-07-0', (
            'TCI',
            'https://www.tcichemicals.com/US/en/sds/B3296_US_EN.pdf'
            )
        ),
        ('623-51-8', (
            'TCI',
            'https://www.tcichemicals.com/US/en/sds/T0211_US_EN.pdf'
            )
        ),
        ('128-50-7', (
            None,
            None
            )
        ),
        ('41931-18-4', (
            None,
            None
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
def test_extract_url_from_tci(cas_nr, expect):
    source, url = extract_download_url_from_tci(cas_nr) or (None, None)
    assert (source, url) == expect


@pytest.mark.parametrize(
    "cas_nr, expect", [
        ('623-51-8', None)
    ]
)
def test_extract_url_from_tci_with_exception(monkeypatch, cas_nr, expect):
    monkeypatch.setattr('find_sds.find_sds.requests.Session', mock_raise_exception)
    result = extract_download_url_from_tci(cas_nr)
    assert result == expect
