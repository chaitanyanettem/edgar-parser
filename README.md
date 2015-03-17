#EDGAR Parser

parser.py fetches the first available 13F-HR file for any given CIK. It is assumed that the given CIK is valid. (Although there *is* a validate function whose call has been commented out. So, if needed validation can be enabled)

I read the [EDGAR Form 13F XML Technical Specification](http://www.sec.gov/info/edgar/specifications/form13fxmltechspec1-1.zip) from the SEC's website before getting started. From there I understood that the full text submission is essentially a combination of the XML from the Primary Document and the Information Table with some accompanying meta data. I also noticed that the data about a given corporation's holdings is held entirely in the information table.

With these things in mind I designed a script which does the following:
- Fetches an atom feed of the 13F-HR submissions for a given CIK.
- Picks the first submission and constructs a link to the full txt submission.
- Fetches the txt submission and splits it into xml for the Primary Document and the Information Table
- Parses the XML and writes data to 2 separate csv files with the following fields respectively:

## Primary Document
| periodOfReport | tableEntryTotal |  tableValueTotal |
|----------------|-----------------|------------------|

## Information Table
| nameOfIssuer | titleOfClass | cusip | value | sshPrnamt | sshPrnamtType | putCall | investmentDiscretion | otherManager | Sole | Shared | None |
|--------------|--------------|-------|-------|-----------|---------------|---------|----------------------|--------------|------|--------|------|
