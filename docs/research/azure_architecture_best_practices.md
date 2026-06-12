# Azure Generative AI - Viralliset Arkkitehtuurisuositukset

Etsin tietoa suoraan **Azure Architecture Centerin** ja **Microsoftin virallisista referenssiarkkitehtuureista** GenAI- ja multi-agent -toteutuksiin. Tässä on tiivistelmä siitä, miten Microsoft suosittelee tuotantotason tekoälysovellusten (kuten meidän Information Digestin) rakentamista:

## 1. Arkkitehtuurin Kerrokset (Core Layers)
Microsoft suosittelee vahvasti tekoälysovellusten hajauttamista seuraaviin kerroksiin:
- **Käyttöliittymä ja API-hallinta:** Älä koskaan altista AI-rajapintoja suoraan verkkoon. Käytä **Azure API Management (APIM)** -palvelua throttlaukseen ja autentikointiin. Edessä voi olla *Azure Front Door* tai *Application Gateway* palomuurilla (WAF).
- **Sovelluskerros (Integration):** Erota bisneslogiikka tekoälymalleista. Käytä modulaariseen orkestrointiin (esim. meidän tiedonhakijat) **Azure Container Apps** tai **Azure Functions** -palveluita.
- **Data ja RAG-kerros:** Käytä **Azure AI Search** -palvelua vektorointiin ja hybridihakuun, sekä *Azure Data Lakea* tai *Fabriccia* pitkäaikaiseen tallennukseen.
- **Tekoälykerros:** Kaikki mallit hallitaan keskitetysti **Azure AI Foundryn** kautta (Azure OpenAI Service).

## 2. Tietoturva (Security - Non-Negotiable)
Microsoftin referenssiarkkitehtuureissa nämä ovat pakollisia tuotannossa:
- **Verkkoeristys:** Kaikki palvelut (AI, Search, Storage) on kytketty toisiinsa **Private Endpoints** -yhteyksillä. Julkinen internet-yhteys on suljettu.
- **Identiteetti:** Ei API-avaimia! Koko putki käyttää **Managed Identities** -toiminnallisuutta (`DefaultAzureCredential`).
- **Hallinta:** Käytetään Azure Policyjä valvomaan, että data pysyy tietyllä maantieteellisellä alueella (GDPR).

## 3. Strategiset Suositukset
- **RAG > Fine-Tuning:** Microsoft linjaa erittäin selvästi, että yritysdatan hyödyntämisessä RAG on turvallisempi, halvempi ja helpommin hallittava lähestymistapa kuin mallien hienosäätö. Fine-tuningia tulisi käyttää vain "viimeisenä oljenkortena" erikoistuneen sävyn tai ohjelmointikielen opettamiseen.
- **Stateless Inference:** Käsittele LLM-malleja "tilattomina" moottoreina. Älä luota mallin "muistiin", vaan injektoi kaikki tarvittava konteksti sisään joka kerta RAGin avulla. Tämä on juuri sitä, mitä me teemme `SequentialBuilderilla` siirtämällä JSON-tilaa agentilta toiselle!
- **Modulaarinen arkkitehtuuri:** Monimutkaiset prosessit tulee hajauttaa pieniin osiin (Esim. *Extraction* -> *Context Building* -> *Response Construction*).

## Mitä tämä tarkoittaa meille?
Meidän `the_plan.md` on jo uskomattoman linjassa näiden virallisten suositusten kanssa:
1. Meillä on modulaarinen arkkitehtuuri (erilliset Extractor ja Synthesizer agentit).
2. Meillä on Stateless Inference -logiikka, jossa tilatieto siirtyy tiukkana Pydantic JSON:ina.
3. Arkkitehti-agenttimme skill-tiedosto vaatii jo nyt `DefaultAzureCredential` -käyttöä.

**Ainoa ero** on se, että emme pystytä Hackathonissa täyttä VNet/Private Endpoint -infrastruktuuria, sillä teemme ohjelmistolähtöistä proof-of-conceptia emmekä verkkoarkkitehtuuria. Voimme kuitenkin mainita demossamme, että *tuotantoversiossa järjestelmä kääritään Azure APIM ja Private Endpoints -suojaan* Architecture Centerin mukaisesti!
