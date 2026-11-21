# Group 30 — Data processing and author identification

The data collected covers publications from 2016–2026 associated with HBNI-listed faculty at BARC Mumbai, IGCAR Kalpakkam, RRCAT Indore and NISER Bhubaneswar. Scopus was used for publication metadata and citation counts, official faculty sources for the research cohort, and OpenAlex for citation and institutional links. `SOURCES.md` gives the source details.

The main processing decision was to separate three questions: whether a person appears on the official faculty roster, whether a Scopus Author ID belongs to that person, and whether that person is affiliated with the assigned institution on a particular paper. A match at one stage did not automatically answer the other two.

## 1. How authors on each paper were checked

### Reading the Scopus author records

The author names and their explicit identifiers were parsed from the original Scopus CSVs. The exports contain `Author full names`, `Author(s) ID`, abbreviated author names and `Authors with affiliations`. The parsed name–ID sequence was checked to be in agreement with the separate Author ID sequence before using it for faculty matching.

Names were standardized for comparison by removing honorifics and normalizing punctuation, spacing and case. We retained the source names for display and kept identifiers as the basis for joining records. A normalized name was a way to find candidates, not a replacement for an author identifier.

### Connecting a publication author to the faculty roster

Each candidate was compared with the official HBNI roster, including the person's institution. We then looked for that candidate's own affiliation in the paper's Scopus author-affiliation information. A matching institute elsewhere in a long coauthor list was not sufficient.

Two evidence routes were used:

- **Official publication evidence.** A publication on an HBNI or institutional faculty profile was matched to a Scopus paper using its bibliographic details, such as DOI or title and year. This supported the association between the roster person and the Scopus Author ID.
- **Name and paper-affiliation evidence.** When no independently matched bibliography was available, a unique qualifying Scopus ID could be selected using the name and repeated publication-affiliation evidence. An exact full-name-token candidate needed at least one directly affiliated paper with the required location support. The stricter exact-initial-token category needed at least three directly affiliated papers and three location-supported papers.

The selection gave precedence to a uniquely supported ID from the official-publication reconciliation. Otherwise, it required exactly one candidate meeting the relevant name-and-affiliation rule. The most prolific candidate was not selected merely because it had more papers.

After selecting an ID for a person, the person's affiliation was checked separately on every paper admitted through that identity. This avoids counting a paper from another institution just because its author later appears on the current roster.

For BARC, the assigned campus is Mumbai. We checked the faculty author's own BARC affiliation for Mumbai-area address evidence, including recognised variants such as Bombay, Trombay, Parel and Anushakti Nagar. An unrelated coauthor's Mumbai address, or the Mumbai address of HBNI alone, did not establish the faculty author's BARC campus.

This process selected 583 faculty from the 774-entry roster. Of the selected identities, 122 had official publication corroboration and 461 were selected through the unique name-and-publication-affiliation route. The evidence level was recorded rather than describing every identity as independently verified from a personal bibliography.

### What the `author` column represents

The main dataset preserves the paper's source author list, which can include students, external collaborators and other researchers as well as the matched faculty. We did not classify every person in that list as HBNI faculty. Faculty-level calculations and the faculty coauthorship network use the separately resolved HBNI–Scopus identities.

## 2. Authors with identical or similar names

Names alone were not used as unique keys. The working records distinguish the HBNI faculty identifier, Scopus Author ID, institution and paper-specific affiliation.

| Situation | Treatment |
|---|---|
| Two authors have the same displayed name but different Scopus IDs | Keep their records separate; compare each with the roster and affiliation evidence. |
| Several plausible Scopus IDs match one roster person | Keep the identity for review unless the stronger evidence establishes one selected ID. Do not automatically merge profiles. |
| One Scopus ID is selected for two roster people | Run a collision check. If exactly one has official-publication corroboration, retain that supported selection and return the other to review. Otherwise, leave the conflicting selections unresolved. |
| An abbreviated name corresponds to more than one author on the same paper | Do not assign its affiliation block arbitrarily to one of them. |
| A name differs only in punctuation, spacing, initials or a documented variant | Use normalization and the supporting bibliography/affiliation evidence to assess the candidate; do not treat spelling similarity alone as proof. |

In the retained roster, 191 people did not have a resolved unique identity: 124 had no qualifying unique ID, 65 had multiple supported candidates and two required collision review. They were not assigned individual publication statistics or faculty-network nodes. Their publications can still appear in the main dataset when another resolved faculty member provides a valid link to the same paper.

This preserves the distinction between “not linked in this dataset” and “has no publications.”

## 3. Faculty population and historical evidence

An included paper must fall within 2016–2026 and show the selected author's affiliation with the assigned institute. This provides a consistent cohort across the four institutions.

The available HBNI academic-report lists add dated supporting evidence. They cover 2016–17, 2017–18 and 2020–21 through 2024–25. A matching list entry is recorded with its report period and page. Where a person appears in both the 2017–18 and 2020–21 lists and has a 2019 paper with the required institute affiliation, the historical annotation records inferred continuity for 2019.

That annotation is an inference between documented observations, not an appointment date. Historical lists supplement the current-roster method; absence from an extracted list does not automatically exclude an otherwise supported current-roster publication. The study does not attempt to enumerate former faculty absent from the chosen roster.

## 4. Processing the publication dataset

### Import and standardization

The four original Scopus exports were preserved unchanged. We created a working table with the original file, row number, EID and a source-record hash. DOIs were normalized for matching by removing URL prefixes and comparing them in lowercase; the submission displays DOI URLs. ISSNs and venue titles were standardized for matching while retaining the original source values in the working records.

The 32,110 export rows contain 30,323 distinct Scopus EIDs. A paper can occur in more than one institution's export. Repeated EIDs were checked for metadata conflicts and the relationship between a paper and each assigned institution was kept.

### Faculty and institutional selection

The resolved faculty–paper links were joined to the source publication table. A paper entered an institution's cohort when at least one selected faculty member had the required author-specific affiliation. This produced 17,905 institution–paper rows before document-type screening.

### Publication types and subject scope

The original Scopus document type was used together with venue and conference information:

- Scopus conference papers were retained as conference records. A named meeting was used where available; otherwise the source title was retained as the display fallback.
- Articles, reviews, letters, notes, short surveys and data papers in named serial sources were retained as journal publications when there was no conflicting conference context. Letters and notes were included because they can report research findings.
- One record labelled Article had explicit conference information and was classified as a conference paper.
- Books, book chapters, editorials, errata and retracted records were excluded from this journal/conference research corpus.

The broad Science and Engineering scope follows the faculty disciplines recorded by HBNI. Medical and Health Sciences is included, which is relevant to nuclear medicine and related work at the assigned institutions. Discipline is used as a broad subject proxy; it is not presented as an independently checked paper-level classification.

The resulting dataset contains **17,328 institution–paper rows**, after 554 document-form exclusions and 23 held proceedings records:

| Institution | Included rows |
|---|---:|
| BARC | 10,247 |
| IGCAR | 2,020 |
| RRCAT | 1,120 |
| NISER | 3,941 |

### Duplicate handling and counting

The dataset's unit is an institution–paper record. A paper shared by BARC and IGCAR can therefore appear once for each institution without being an accidental duplicate.

For statistics, three duplicate institution–paper records with matching DOI, title and year were collapsed, giving 17,325 distinct institution–paper records. For the citation graph, papers were grouped by normalized DOI, with an EID-based node where DOI was absent. This gives 16,466 distinct paper nodes across the group. These totals answer different questions and are not interchangeable.

## 5. Venue ranks and citation counts

Journal quartiles were matched to the publication year in the annual SCImago tables. We first checked ISSNs and used the normalized journal title to resolve candidates. An unambiguous source match was required; a conflicting ISSN/title match was left unresolved. The value used is SCImago's published **Best Quartile**, rather than a quartile recalculated from broad subject areas.

The retained tables cover 2016–2025. A 2025 quartile was not labelled as a 2026 publication-year rank. Conference grades use the selected ICORE2026 edition and require a supported meeting identity. Acronym-only matches and ranks inherited from a parent conference by a co-located workshop were rejected.

The detailed working data retain journal quartiles and conference grades separately. A missing rank is left blank rather than assigned a guessed category.

The main `citations` field retains Scopus's exported global `Cited by` count. It counts citations to the publication across Scopus, not just citations from the four assigned institutions. OpenAlex citation links are a separate source for network construction; the two measures are not expected to be numerically identical.

## 6. Citation network and Indian citation flags

Scopus DOIs were joined to saved OpenAlex work records, directed reference links were extracted and were combined with the saved incoming-citation collection. Each edge means that the source paper cites the target paper. Repeated observations of the same directed paper pair were merged.

The submitted citation network is the induced graph of the selected Group 30 papers: both endpoints belong to the selected corpus. It contains **39,807 unique directed paper pairs**, expanded to **56,725 rows** for the source/target institution combinations. This expansion matters when a paper belongs to more than one assigned institution. The edge-list `year` is the source paper's Scopus publication year.

External Indian citation witnesses were collected separately for the paper-level flags and the wider citation-flow analysis. These use citing/cited works with Indian institutional evidence, excluding the focal institution and the shared HBNI umbrella affiliation when determining an external connection.

The flags have three interpretations:

| Value | Interpretation |
|---|---|
| `TRUE` | At least one qualifying citation link has a saved affiliation witness or an audited Indian-country/institution-filter result. |
| `FALSE` | No qualifying link was found within the completed source query and its recorded reference/affiliation evidence. An empty indexed reference list also supports an index-bounded negative under the adopted rule. |
| Blank | The available DOI, query or affiliation information is insufficient to decide. |

Thus, `FALSE` refers to the observed OpenAlex data and query window; it is not a claim about every citation in every index. Incoming queries are dated 13 October 2026 and outgoing collection 21 October 2026. These dates are kept distinct.

For outgoing collection, compact Indian-country queries were intersected with each source work's saved references. Work affiliated with another assigned institute or HBNI was checked further for an external Indian institution where saved authorship details were available. Records with potentially truncated authorship information or uncertain institutional countries were not automatically turned into negatives.

Papers without a DOI remain in the main dataset. They can be represented internally by EID, but do not create DOI-keyed citation edges. The graph's in-degree and PageRank measure citations within the selected corpus, separately from Scopus global citation counts.

## 7. Authorship network

The authorship graph uses the resolved faculty identities. For each retained paper, we gathered its supported faculty coauthors and generated every unordered pair. A paper with three eligible faculty produces three pair events. A paper with one eligible faculty contributes to that person's publication record but produces no pair edge.

The submitted file contains **9,113 coauthorship events** representing **2,356 distinct faculty pairs**. Authors are joined internally by their HBNI and Scopus identifiers; readable names are exported in `author_a` and `author_b`. A pair appearing on different papers is retained as separate paper-level events.

`inst_a` and `inst_b` identify the assigned institutions of the two resolved faculty members, allowing cross-institution pairs to be distinguished. All 583 resolved faculty are represented in the wider node table, including 67 isolates; an edge-only CSV cannot display an isolated node by itself. The wider analysis computes degree, betweenness and Louvain communities from this faculty graph.

## 8. Coauthor institutions and Indian connections

Institutional partners were extracted from DOI-matched OpenAlex authorship records and grouped using OpenAlex institution identifiers. This avoids treating minor display-name variations as different partners. The focal institution and the shared HBNI umbrella affiliation were excluded from the partner list for that focal institution.

`coauthor_institutes` contains the available other named institutions, which may include overseas institutions. For `indian_connections.csv`, we retain partners with country code `IN` and aggregate by focal institution and partner identifier:

- `shared_papers` is the number of distinct shared DOI-linked papers.
- `total_citations` is the sum of Scopus global citation counts on those shared papers, counting a shared DOI once per institution–partner pair.

`total_citations` is therefore a measure of the citation totals attached to joint publications. It is not the number of citations exchanged between the two institutions. A paper with several Indian partners contributes once to each relevant pair, so partner counts cannot be summed to obtain a unique-paper total.

The resulting file has **1,308 institution–partner rows**. These are the connections observed in the joined sources. Blank partner lists may mean that no other named institution was present in the saved affiliations, or that the DOI/affiliation information was insufficient; they are not universally interpreted as “no collaboration.”

## 9. Related analysis conventions

Faculty h-index is calculated over each person's eligible 2016–2026 institute-affiliated papers using their Scopus citation counts. It is labelled as a corpus h-index, rather than a career h-index. Department summaries use the official HBNI division where available and a labelled HBNI discipline fallback otherwise. Research-area counts can overlap when coauthors on the same paper belong to different disciplines.

For the wider project's topic comparison, Jaccard similarity is the number of shared OpenAlex primary-topic IDs divided by the number present in either institution's set. Both sides use the defined institution-wide OpenAlex core corpus from 1 January 2016 through 21 October 2026. This differs from the faculty-filtered Scopus population used for publication statistics.