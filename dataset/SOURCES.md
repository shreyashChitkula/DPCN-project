# Group 30 — Data sources

This document records the sources used for our Assignment 2 dataset and network files. The institutions are BARC Mumbai, IGCAR Kalpakkam, RRCAT Indore and NISER Bhubaneswar. The publication window is 2016–2026, with 2026 covering the records available at collection time.

Scopus supplies the publication records and citation counts. HBNI and institutional pages establish the faculty cohort and support author identification. SCImago and ICORE supply venue rankings. OpenAlex supplies citation links and institutional affiliations used in the connectivity analysis. These sources have different roles; the processing rules are explained in `DECISIONS.md`.

## 1. Publication records: Scopus

**Website:** [Scopus](https://www.scopus.com/)

A separate CSV was downloaded for each institution after searching for the institute and applying the 2016–2026 publication-year filter.

| Original export | Records |
|---|---:|
| `BARC_2016-2026.csv` | 19,314 |
| `IGCAR_2016-2026.csv` | 4,681 |
| `RRCAT_2016-2026.csv` | 2,491 |
| `NISER_2016-2026.csv` | 5,624 |
| **Total** | **32,110** |

The exports contain titles, publication years, document types, source titles, ISSNs, DOIs, EIDs, author names, Scopus Author IDs, affiliations, author-specific affiliations, references and the Scopus `Cited by` count. Conference fields include the meeting name, date and location where supplied by Scopus.

The `citations` column uses the count in the original Scopus export. It is not replaced by an OpenAlex count.

## 2. Faculty roster and academic profiles

### Homi Bhabha National Institute

The official HBNI faculty directory supplies the common roster for all four institutions:

- [HBNI faculty directory](http://www.hbni.ac.in/facultym5.html)
- [Directory data feed](http://www.hbni.ac.in/facultylistdisplay.json)
- [Academic profile data](http://www.hbni.ac.in/facultylist.json)
- [Faculty publication page](http://www.hbni.ac.in/facultyp5.html)
- [Faculty publication data](http://www.hbni.ac.in/facultypub.json)
- [Profile page](http://www.hbni.ac.in/profile3.html)

The underlying directory data was used rather than extracting only the entries visible in the page's scrolling table. HBNI faculty identifiers, names, constituent institution, designation, discipline and available division fields were retained.

The four-institution subset contains 774 roster entries: BARC 493, IGCAR 95, RRCAT 62 and NISER 124. HBNI publication lists provide an additional check where a listed publication can be matched to a Scopus record.

### Institutional directories and publications

| Source | Use |
|---|---|
| [NISER faculty directory](https://www.niser.ac.in/people/fac) and linked personal profiles | Names, schools, name variants and publication bibliographies used in identity reconciliation |
| [IGCAR HBNI faculty page](https://www.igcar.gov.in/hbni.html) | Supporting check of the institution's HBNI faculty information |
| [RRCAT HBNI faculty research profiles](https://www.rrcat.gov.in/hrd/hbni/HBNI_RRCAT_Faulty_Profile_v1.pdf) | Supporting names and publication evidence from an official institutional document |

The NISER directory was collected by school: [Biological Sciences](https://www.niser.ac.in/people/fac/sbs), [Computer Sciences](https://www.niser.ac.in/people/fac/scos), [Chemical Sciences](https://www.niser.ac.in/people/fac/scs), [Earth and Planetary Sciences](https://www.niser.ac.in/people/fac/seps), [Humanities and Social Sciences](https://www.niser.ac.in/people/fac/shss), [Mathematical Sciences](https://www.niser.ac.in/people/fac/sms) and [Physical Sciences](https://www.niser.ac.in/people/fac/sps). Collecting a directory page did not itself make every person on it eligible: the HBNI cohort and publication rules still applied.

### HBNI academic reports

Faculty-lists were taken from HBNI academic report pdfs for 2016–17, 2017–18, 2020–21, 2021–22, 2022–23, 2023–24 and 2024–25. The issuing institution is [HBNI](http://www.hbni.ac.in/). The saved files are named `HBNI_Faculty_List_<academic-year>.pdf`; These were not uploaded as the submission guidelines did not mention for sources of data to be uploaded.

These lists provide dated evidence that a person appeared on an academic faculty list. The matching records retain the PDF name and page number. They do not provide appointment start and end dates.

## 3. Journal rankings: SCImago

**Publisher of the ranking:** [SCImago Journal & Country Rank](https://www.scimagojr.com/journalrank.php)

The published annual `SJR Best Quartile` was used for the paper's publication year. The working table covers 2016–2025 and contains journal source IDs, titles, ISSNs, source types and best quartiles.

The annual data were obtained through the [sjrdata repository](https://github.com/ikashnitsky/sjrdata), which distributes SCImago data. The source artifact was `data-raw/sjr-journal/sjr_journals-2026.parquet`; its filename refers to the data release, not to a completed 2026 publication-year ranking. Our retained 2016–2025 subset is `supplementary/sources/scimago_annual_official_2016_2025.csv.gz`.

A separate copy of the 2025 edition, obtained through the [Academic Venues dataset](https://www.kaggle.com/datasets/krishnaaigen/academic-venues), was used for comparison. The saved validation records report agreement for all 32,193 source IDs in that 2025 comparison. The mirror is the acquisition route; SCImago remains the ranking authority.

Journal names and ISSNs in the publication records come from Scopus. Every journal website was not individually scraped. A journal's presence in the dataset is therefore traceable to its Scopus record, while its quartile is traceable to the annual SCImago table.

## 4. Conference names and rankings

**Ranking source:** [ICORE Conference Portal, 2026 edition](https://portal.core.edu.au/conf-ranks/?search=&by=all&source=ICORE2026&sort=atitle&order=asc)

Conference names were taken first from the original Scopus conference fields. Where supplementary DOI-linked meeting information was available, it was taken from [Crossref](https://www.crossref.org/) through the [Crossref REST API](https://api.crossref.org/works). A work record is retrieved by appending its DOI to that API URL.

The saved ICORE table is `core_portal_ranked_venues.csv`. 26 supported A*/A/B/C assignments were used, established through DOI-linked meeting evidence or reviewed conference names. The saved edition is ICORE2026; it is not a historical series of conference rankings.

We checked full meeting names as well as acronyms. Proceedings series such as *AIP Conference Proceedings* or *Journal of Physics: Conference Series* do not identify a particular conference and were not given a conference grade on their own. A blank grade means that no supported grade was assigned from the selected evidence; it does not imply that a meeting is poor quality.

## 5. Citation links, institutional partners and research topics: OpenAlex

**Source:** [OpenAlex](https://openalex.org/) and its [Works API](https://api.openalex.org/works)

OpenAlex records were joined to the Scopus corpus through normalized DOIs. We used work IDs, `referenced_works`, authorship institutions, institution country codes, publication years and topic identifiers. The saved API responses and collection audits are the evidence behind these fields.

| Institution | OpenAlex identifier |
|---|---|
| BARC | [I1329621470](https://openalex.org/I1329621470) |
| IGCAR | [I2802630050](https://openalex.org/I2802630050) |
| RRCAT | [I1289303365](https://openalex.org/I1289303365) |
| NISER | [I163389970](https://openalex.org/I163389970) |
| HBNI, used to recognise the shared umbrella affiliation | [I200207707](https://openalex.org/I200207707) |

The collection has three parts:

1. **Publication and authorship records.** Saved OpenAlex works supply DOI-to-work links, references and institutional affiliations.
2. **Indian citation collection.** Incoming citation queries were saved in batches. Outgoing collection was completed for 15,576 matched source works, with additional affiliation checks from saved records.
3. **Institutional topic comparison.** Complete paginated primary-topic group results were collected for 811 institution IDs, covering OpenAlex core works dated 1 January 2016 through 21 October 2026. These support the 1,308 institution–partner Jaccard comparisons in the wider project analysis. Topic IDs are OpenAlex's classifications; the Jaccard values are the calculations done from those sets.

OpenAlex citation links are used for network edges and Indian citation evidence. They are kept separate from the Scopus global citation totals in the main CSV. Collection windows and country/affiliation evidence are retained so that each measure can be interpreted in the context of its source.

## 6. Supporting sources consulted during development

The [BARC gazetted employee list](https://www.barc.gov.in/rti/gz.html), [BARC non-gazetted employee list](https://www.barc.gov.in/rti/ngz.html) and [ORCID public employment API](https://pub.orcid.org/v3.0/) were also consulted. These supported earlier affiliation screening. Employee status or an ORCID employment entry alone was not accepted as proof of HBNI faculty status; the final faculty selection follows the HBNI–Scopus procedure in `DECISIONS.md`.

Alternative ranking sources were examined but did not supply values to the submitted rank fields. These included an [external SCImago indicators panel](https://github.com/Michael-E-Rose/SCImagoJournalRankIndicators) and [Publication Forum/JUFO data](https://jufo-rest.csc.fi/v1.1/massa.json.zip). The former did not reproduce the annual best-quartile values adequately; the latter uses a different conference-ranking scale. They were not substituted for SCImago quartiles or ICORE grades.

## 7. Source traceability

The main CSV's DOI links identify the underlying publications. The working data retain additional EIDs, Scopus Author IDs, source filenames, original row identifiers, matching decisions and source checksums. Network evidence retains the corresponding paper and institution identifiers.

The uploaded CSVs contain the prescribed columns. 