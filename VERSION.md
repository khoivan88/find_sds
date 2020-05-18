# DETAILS

## Version 0.9.0 (2020-05-18)

- Feat: Add [TCI](https://www.tcichemicals.com/) as another source for SDS
- Feat: Add tests for TCI

## Version 0.8.0 (2020-05-10)

- Feat: Add [VWR](https://us.vwr.com/store/search/searchMSDS.jsp) as another source for SDS
- Feat: Add tests for VWR
- Feat: Remove TCI because of its new website

## Version 0.7.0 (2020-04-02)

- Feat: Add [ChemBlink](https://www.chemblink.com) as another source for SDS
- Feat: Add tests for ChemBlink

## Version 0.6 (2020-02-12)

- Add [TCI](https://www.tcichemicals.com/en/us/) as another source for SDS
- Code clean up
- Add tests for SDS downloading functions

## Version 0.5

- Incorporate result from Fluorochem
- Fixing bug with existing default_safety_sheet_url and default_safety_sheet_mime
by setting them to NULL

## Version 0.4

- Testing using cheminfo.org/webservices by extracting catalog number from [Fluorochem](http://www.fluorochem.co.uk/)

## Version 0.3

- Refractor extracting url download into its own method
- Added extracting url download from [Chemicalsafety](https://chemicalsafety.com/sds-search/)

## Version 0.2

- Switch to extracting data from [Fisher Scientific](https://www.fishersci.com/us/en/catalog/search/sdshome.html) because Chemexper has limited requests
