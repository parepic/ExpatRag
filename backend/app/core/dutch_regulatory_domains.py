"""Official Dutch government and regulatory domains used to scope web search.

These lists are passed to Tavily as ``include_domains`` so the web search agent only
returns results from authoritative sources instead of blogs, forums and relocation
agencies that often carry outdated or plainly wrong rules.

Notes:
    - Tavily caps ``include_domains`` at 300 entries; keep the combined list under that.
    - Entries are registrable domains without scheme or ``www``. Tavily matches
      subdomains too, so ``ilent.nl`` also covers ``english.ilent.nl``.
    - Individual ministries are not listed separately: they all publish under
      ``rijksoverheid.nl`` (Dutch) and ``government.nl`` (English).
"""

# --- Central government portals & official publications ---------------------
_GOVERNMENT_PORTALS = [
    "rijksoverheid.nl",           # Central government, all ministries (NL)
    "government.nl",              # Central government, all ministries (EN)
    "overheid.nl",                # Government information portal (incl. wetten.overheid.nl)
    "mijnoverheid.nl",            # Personal government portal
    "officielebekendmakingen.nl", # Official gazette / legal publications
    "tweedekamer.nl",             # House of Representatives
    "eerstekamer.nl",             # Senate
    "netherlandsworldwide.nl",    # Consular services & embassies (EN)
    "nederlandwereldwijd.nl",     # Consular services & embassies (NL)
    "denederlandsegrondwet.nl",   # Constitution & parliamentary documentation
]

# --- Immigration, residence & integration -----------------------------------
_IMMIGRATION = [
    "ind.nl",              # Immigration and Naturalisation Service
    "inburgeren.nl",       # Civic integration
    "naarnederland.nl",    # Civic integration exam taken abroad
    "coa.nl",               # Central Agency for the Reception of Asylum Seekers
    "vluchtelingenwerk.nl", # Dutch Council for Refugees (government-funded NGO)
]

# --- Tax & customs ----------------------------------------------------------
_TAX = [
    "belastingdienst.nl",  # Tax and Customs Administration
    "toeslagen.nl",        # Allowances / benefits (zorgtoeslag, huurtoeslag)
    "douane.nl",           # Customs
]

# --- Work, benefits, pensions & social security -----------------------------
_WORK_AND_SOCIAL = [
    "uwv.nl",                   # Employee Insurance Agency
    "werk.nl",                  # UWV job portal
    "svb.nl",                   # Social Insurance Bank (AOW, child benefit)
    "nlarbeidsinspectie.nl",    # Netherlands Labour Authority
    "mijnpensioenoverzicht.nl", # National pension overview
    "arboportaal.nl",           # Working conditions portal (Ministry of SZW)
]

# --- Business & entrepreneurship --------------------------------------------
_BUSINESS = [
    "kvk.nl",             # Chamber of Commerce
    "rvo.nl",             # Netherlands Enterprise Agency
    "ondernemersplein.nl", # Business information portal (NL)
    "business.gov.nl",    # Business information portal (EN)
]

# --- Education & diploma recognition ----------------------------------------
_EDUCATION = [
    "duo.nl",                # Education Executive Agency (student finance, diplomas)
    "nuffic.nl",             # Internationalisation in education, credential evaluation
    "onderwijsinspectie.nl", # Inspectorate of Education
]

# --- Health, care & insurance -----------------------------------------------
_HEALTH = [
    "rivm.nl",                    # National Institute for Public Health
    "zorginstituutnederland.nl",  # National Health Care Institute (basic package)
    "nza.nl",                     # Dutch Healthcare Authority
    "igj.nl",                     # Health and Youth Care Inspectorate
    "cak.nl",                     # Central Administration Office (care contributions)
    "ciz.nl",                     # Care Needs Assessment Centre
    "zorgverzekeringslijn.nl",    # Official health insurance help line
    "bigregister.nl",             # BIG register of healthcare professionals
    "ggd.nl",                     # Municipal public health services
]

# --- Financial & market regulators ------------------------------------------
_FINANCIAL_REGULATORS = [
    "dnb.nl",                # De Nederlandsche Bank (central bank, prudential supervisor)
    "afm.nl",                # Authority for the Financial Markets
    "acm.nl",                # Authority for Consumers and Markets
    "consuwijzer.nl",        # ACM consumer information desk
    "kifid.nl",              # Financial Services Complaints Institute
    "kansspelautoriteit.nl", # Netherlands Gambling Authority
]

# --- Justice, law enforcement & legal aid -----------------------------------
_JUSTICE = [
    "rechtspraak.nl",        # The Judiciary / case law
    "juridischloket.nl",     # Legal Services Counter (free legal advice)
    "rvr.org",               # Legal Aid Board (Raad voor Rechtsbijstand)
    "rechtsbijstand.nl",     # Subsidised legal aid information
    "om.nl",                 # Public Prosecution Service
    "politie.nl",            # National Police
    "cjib.nl",               # Central Judicial Collection Agency (fines)
    "justis.nl",             # Screening authority (VOG / certificate of conduct)
    "nationaleombudsman.nl", # National Ombudsman
    "slachtofferhulp.nl",    # Victim Support Netherlands
]

# --- Privacy & digital ------------------------------------------------------
_PRIVACY_AND_DIGITAL = [
    "autoriteitpersoonsgegevens.nl", # Dutch Data Protection Authority
    "digid.nl",                      # DigiD digital identity
    "ncsc.nl",                       # National Cyber Security Centre
    "rdi.nl",                        # Digital Infrastructure Inspectorate (ex-Agentschap Telecom)
]

# --- Housing, land & living environment -------------------------------------
_HOUSING_AND_ENVIRONMENT = [
    "huurcommissie.nl",   # Rent Tribunal (rent disputes, rent caps)
    "kadaster.nl",        # Land Registry
    "rijkswaterstaat.nl", # Infrastructure and water management
    "ilent.nl",           # Human Environment and Transport Inspectorate
    "autoriteitnvs.nl",   # Authority for Nuclear Safety and Radiation Protection
    "anvs.nl",            # ANVS (alternate domain)
]

# --- Transport & vehicles ---------------------------------------------------
_TRANSPORT = [
    "rdw.nl",  # Vehicle Authority (registration, import, APK)
    "cbr.nl",  # Driving Licence Authority (exams, licence exchange)
]

# --- Food, product & consumer safety ----------------------------------------
_SAFETY = [
    "nvwa.nl",            # Food and Consumer Product Safety Authority
    "voedingscentrum.nl", # Netherlands Nutrition Centre
]

# --- Statistics -------------------------------------------------------------
_STATISTICS = [
    "cbs.nl",  # Statistics Netherlands
]

# --- Municipalities ---------------------------------------------------------
# Registration (BRP/BSN), parking permits, waste rules and local taxes are all
# municipal, so the largest municipalities are included for local questions.
_MUNICIPALITIES = [
    "amsterdam.nl",
    "rotterdam.nl",
    "denhaag.nl",
    "utrecht.nl",
    "eindhoven.nl",
    "groningen.nl",
    "tilburg.nl",
    "almere.nl",
    "breda.nl",
    "nijmegen.nl",
    "haarlem.nl",
    "arnhem.nl",
    "amersfoort.nl",
    "maastricht.nl",
    "leiden.nl",
    "delft.nl",
    "enschede.nl",
    "zwolle.nl",
    "apeldoorn.nl",
    "dordrecht.nl",
    "s-hertogenbosch.nl",
    "wageningen.nl",
    "hilversum.nl",
    "zoetermeer.nl",
]

#: Every official Dutch government / regulatory domain, deduplicated and ordered.
DUTCH_REGULATORY_DOMAINS: list[str] = [
    *_GOVERNMENT_PORTALS,
    *_IMMIGRATION,
    *_TAX,
    *_WORK_AND_SOCIAL,
    *_BUSINESS,
    *_EDUCATION,
    *_HEALTH,
    *_FINANCIAL_REGULATORS,
    *_JUSTICE,
    *_PRIVACY_AND_DIGITAL,
    *_HOUSING_AND_ENVIRONMENT,
    *_TRANSPORT,
    *_SAFETY,
    *_STATISTICS,
    *_MUNICIPALITIES,
]

#: EU-level sources that govern residence, coordination of social security and
#: recognition of qualifications for EU nationals living in the Netherlands.
EU_OFFICIAL_DOMAINS: list[str] = [
    "europa.eu",  # All EU institutions, incl. eur-lex, EURES and Your Europe subdomains
]

#: The list handed to Tavily as ``include_domains``.
WEB_SEARCH_INCLUDE_DOMAINS: list[str] = [
    *DUTCH_REGULATORY_DOMAINS,
    *EU_OFFICIAL_DOMAINS,
]
