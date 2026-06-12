# Löydökset: MS Learn GenAIOps -materiaali

Aliagentit tutkivat `mslearn-genaiops` -kansion sisällön (`src`, `infra`, `experiments` ja arkkitehtuuriohjeet). Tässä on yhteenveto parhaista käytännöistä "LLMOps" ja "GenAIOps" -maailmassa, joita voimme soveltaa Information Digest -projektiimme:

## 1. GenAIOps Elinkaari & Arkkitehtuuri
- **Promptit koodina:** GenAIOps-ajattelussa agenttien ohjeistukset ja promptit käsitellään tuotantokoodina. Kaikki muutokset (esim. promptin viilaus tai lämpötilan vaihto) testataan erillisissä Git-haaroissa. Vain yksi muuttuja muutetaan kerrallaan, jotta muutoksen aito vaikutus laatuun voidaan mitata.
- **Työkalupino:** Kehitys ja hallinta tapahtuu *Azure AI Foundryssä*, CI/CD-automaatio *GitHub Actionseilla* ja seuranta *Azure Monitorilla*.

## 2. Automatisoitu Evaluointi (LLM-as-a-Judge)
- **Kultainen Datasetti:** Järjestelmän pohjalle rakennetaan `jsonl`-tiedosto, joka sisältää testitapauksia: `query` (syöte), `response` (vastaus) ja `ground_truth` (fakta). Setin tulee sisältää sekä peruskysymyksiä että vaikeita "edge case" -tilanteita.
- **Tuomarimalli:** Vahva malli (esim. GPT-4o) arvioi agenttiemme tuotoksia numeerisesti (1-5). Tärkeimpiä mittareita:
  - *Intent Resolution:* Ratkaisiko agentti käyttäjän todellisen ongelman?
  - *Relevance:* Pysyikö agentti tiukasti asiassa?
  - *Groundedness:* Ovatko faktat oikein ja lähteisiin perustuvia?
- **Laatuportit (Quality Gates):** MS Learnin esimerkeissä evaluointi on automatisoitu! GitHub Actions ajaa testit jokaisen Pull Requestin kohdalla. Jos uusi agenttiversio saa huonot pisteet (esim. alle 3/5), yhdistäminen (merge) estetään ja tulokset tulostetaan suoraan GitHub-kommentiksi kehittäjille.

## 3. Monitorointi ja Telemetria (Observability)
- **Hajautettu Jäljitys (Distributed Tracing):** Pelkät tekstilokit eivät riitä. Projektissa suositellaan `OpenTelemetry` -kirjastoa (`opentelemetry-instrumentation-openai-v2`). Agenttien työnkulut kääritään hierarkkisiin "spaneihin", jolloin lokipalvelusta näkee visuaalisesti graafina, kauanko tietyn työkalun (esim. MCP-fetcherin) kutsu kesti ja mihin koodi kaatui.
- **Kustannus- ja viivemittarit:** Telemetrian tärkeimmät mittarit ovat TTFT (Time-to-first-token), kokonaiskesto sekä Token-kulutus (prompt + completion tokens). Token-seuranta on ainoa tapa hallita pilvikuluja luotettavasti.
- **A/B-testaus tuotannossa:** Lokeihin injektoidaan tieto siitä, mitä prompt-versiota ajettiin (esim. `v1` vs `v2`). Näin nähdään nopeasti, paransiko monimutkaisempi ja kalliimpi prompti tulosta riittävästi oikeuttaakseen tuplaantuneen token-kulutuksen.

---

## 🎯 Suositukset Information Digest -projektiin

Näiden huipputason DevOps-käytäntöjen pohjalta suosittelen kolmea lisäystä projektiimme:

1. **Evaluointisetti:** Luodaan heti alussa pieni "Golden dataset" muutamalla teknologia-artikkelilla ja niiden toivotuilla tiivistelmillä. Voimme vertailla agenttiemme tuotoksia niihin.
2. **Telemetria:** Asennetaan `OpenTelemetry` heti alussa. Näin näemme kojelaudalta tarkasti, kuinka paljon Azuren tokeneita "Raw -> Silver -> Gold" -myllymme tosiasiallisesti polttaa viikossa!
3. **CI/CD GitHub Actionsilla:** Kirjoitetaan pieni skripti, joka evaluoi agenttiemme suorituskyvyn automaattisesti Azure AI Foundryn tuomarimallin avulla.
