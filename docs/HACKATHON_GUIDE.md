# Microsoft Agents League Hackathon - Projektin Ohjenuora ja Arvostelurubriikki

Tämä dokumentti toimii projektinne punaisena lankana ja tarkistuslistana (checklist). Se on luotu [Agents League Hackathonin virallisten sääntöjen](http://aka.ms/AgentsLeagueRules) ja rekisteröintisivuston pohjalta. Voitte käyttää tätä rubriikkia iteratiivisesti projektin hiomiseen kohti täydellisyyttä.

---

## 1. Aikataulu ja Deadlinet

- **Rekisteröityminen päättyy:** 12. kesäkuuta 2026 klo 12.00 Tyynenmeren aikaa (PT).
- **Projektin palautus (Submission):** 14. kesäkuuta 2026 klo 23.59 Tyynenmeren aikaa (PT).

## 2. Valittavat Haasteet (Tracks)
Valitkaa vähintään yksi näistä, tai voitte osallistua kaikkiin:

1. **Creative Apps:** Rakenna innovatiivisia, luovia sovelluksia hyödyntäen tekoälyavusteista kehitystä (**GitHub Copilot**).
2. **Reasoning Agents:** Luo älykkäitä agentteja, jotka ratkaisevat monimutkaisia ongelmia monivaiheisen päättelyn avulla (**Microsoft Foundry**).
3. **Enterprise Agents:** Rakenna yrityskäyttöön valmiita agentteja **Microsoft 365 Copilotia** varten.

> [!TIP]
> Keskittykää alkuvaiheessa tarkasti yhteen haasteeseen ja siihen vaadittuun teknologiaan (GitHub Copilot, Foundry tai M365 Copilot), jotta arkkitehtuuri on selkeä ja ratkaisu on syvällinen.

---

## 3. Palautuksen Vaatimukset (Submission Checklist)

Projektinne palautukseen (Contest-sivuston "Projects"-välilehden kautta) **on pakollista** sisällyttää seuraavat asiat:

- [ ] **Toimiva agentti/projekti:** Vaadituilla työkaluilla rakennettu.
- [ ] **Demo-video:** Max 5 minuuttia, ladattuna YouTubeen tai Vimeoon. (Näyttää projektin toiminnassa. Älä käytä tekijänoikeusmateriaalia!). *Huom: Videon tekemisen, kuvaamisen ja editoinnin on oltava täysin omaa työtänne.*
- [ ] **Projektin kuvaus:** Mitä ominaisuuksia siinä on, mitä teknologioita käytettiin ja **minkä ongelman se ratkaisee**.
- [ ] **Julkinen GitHub-repo:** Sisältää projektin lähdekoodin.
- [ ] **Arkkitehtuurikaavio:** Havainnollistaa, miten ratkaisunne käyttää Microsoft Foundryä, M365 Copilotia ja/tai GitHub Copilotia.
- [ ] **Tiimitiedot:** Osallistujien Microsoft Learn -käyttäjänimet (jos tiimi).

---

## 4. Arvostelukriteerit (Iteratiivisen hionnan rubriikki)

Palkinnot (yhteensä $55,000 USD arvosta) jaetaan seuraavien kriteerien perusteella. Arvioikaa projektianne jokaisessa kehitysvaiheessa näitä kysymyksiä vasten:

### 1. Luotettavuus ja Turvallisuus (Reliability & Safety) — 20%
*Koodi ja mallit noudattavat kestäviä rakenteita ja välttävät ilmeiset sudenkuopat.*
- [ ] Käsitteleekö agentti virhetilanteet ja odottamattomat syötteet kaatumatta?
- [ ] Onko agenttiin rakennettu "kaiteet" (guardrails) estämään haitallinen tai ei-toivottu toiminta (hallusinaatiot, epäasiallinen sisältö, tietoturvariskit)?
- [ ] Toimiiko koodi sujuvasti kerta toisensa jälkeen?

### 2. Tarkkuus ja Relevanssi (Accuracy & Relevance) — 20%
*Projekti vastaa täysin valitun haasteen vaatimuksia.*
- [ ] Takaako ratkaisunne aidosti valitsemanne haasteen (esim. Enterprise Agent -ongelmanratkaisu)?
- [ ] Onko agentin antama tieto tai lopputulos täsmällistä ja käyttäjälle hyödyllistä?

### 3. Päättely ja Monivaiheinen ajattelu (Reasoning & Multi-step Thinking) — 20%
*Selkeä ongelmanratkaisulähestymistapa.*
- [ ] Näkyykö agentin toiminnassa looginen ketju (suunnittelu -> toiminta -> havainnointi -> reflektointi)?
- [ ] Kokeilkaa antaa agentille monimutkainen, useita työvaiheita vaativa tehtävä. Pystyykö se purkamaan sen palasiin ja ratkaisemaan askel kerrallaan?

### 4. Luovuus ja Alkuperäisyys (Creativity & Originality) — 15%
*Uudet ideat ja yllättävä, raikas toteutus.*
- [ ] Erottuuko ideanne tavanomaisista "chatboteista" tai yksinkertaisista skripteistä?
- [ ] Onko teknologiaa (kuten GitHub Copilot tai Foundry) käytetty jollakin uudella, kekseliäällä tavalla?

### 5. Käyttökokemus ja Esitys (User Experience & Presentation) — 15%
*Ratkaisu on selkeä, hiottu ja helposti demottavissa.*
- [ ] Onko käyttöliittymä (tai CLI/rajapinta) intuitiivinen, responsiivinen ja visuaalisesti miellyttävä?
- [ ] Onko GitHub-repositorion `README.md` ammattimainen, selkeästi formatoitu ja sisältääkö se helpot asennusohjeet?
- [ ] Ovatko arkkitehtuurikaavio ja projektin kuvaus visuaalisesti houkuttelevia ja helposti ymmärrettäviä?
- [ ] Kertooko 5 minuutin demo-video selkeän ja mukaansatempaavan tarinan projektin arvosta?

### 6. Yhteisön äänet (Community Vote) — 10%
*Discord-äänestyksen tulos ( [aka.ms/agentsleague/discord](https://aka.ms/agentsleague/discord) ).*
- [ ] Onko konseptinne sellainen, että sitä on helppo markkinoida muille kehittäjille Discordissa? (Tarttuva nimi, hieno demo, selkeä hyöty.)

---

## 5. Ehdotettu Työnkulku (Workflow)

1. **Suunnittelu ja Ideointi (Päivät 1-3):** 
   - Valitkaa trackki (Creative, Reasoning, Enterprise).
   - Piirtäkää alustava **arkkitehtuurikaavio**.
   - Käykää idea läpi arvioiden kohtia *Luovuus* ja *Tarkkuus*.
2. **Prototyypin Rakentaminen (Päivät 4-10):**
   - Keskittykää ydintoiminnallisuuteen (MVP) ja tekoälyn *päättelykyvyn* (Reasoning) rakentamiseen. 
   - Keskittykää *turvallisuuteen ja luotettavuuteen* heti alusta pitäen.
3. **Hiominen ja Käyttökokemus (Päivät 11-15):**
   - Viilatkaa *käyttökokemus (UX)* kuntoon. Jos teette verkkosovellusta, tehkää siitä visuaalisesti huippuluokkainen (Premium/WOW-efekti).
   - Lisätkää poikkeustenhallinta (error handling) lujuuden (*Reliability*) takaamiseksi.
4. **Dokumentointi ja Demo-video (Päivät 16-20):**
   - Siistikää koodi ja viimeistelkää GitHub-repo.
   - Nauhoittakaa max 5 min video. Käsikirjoittakaa se hyvin!
   - Viimeistelkää arkkitehtuurikaavio.
5. **Palautus (Submission):**
   - Palauttakaa projekti hyvissä ajoin ennen 14.6. deadlinea.

---

## 6. Hyödyllisiä Resursseja ja Linkkejä

Web-hakujen perusteella löysin teille erinomaisia resursseja projektin käynnistämisen avuksi:

1. **Virallinen GitHub-repositorio (Starter Kits):** 
   - [microsoft/agentsleague](https://github.com/microsoft/agentsleague)
   - *Täältä löydätte viralliset "Starter kitit", asennusohjeet ja esimerkkiprojektit jokaiselle kolmelle trackille! Tämä on ehdottomasti paras paikka aloittaa koodaaminen.*
2. **Yhteisö ja verkostoituminen:**
   - [Discord-yhteisö](https://aka.ms/agentsleague/discord)
   - *Discord on paikka, josta voitte löytää tiimiläisiä, kysyä teknisiä kysymyksiä ja myöhemmin kerätä ääniä (Community Vote -osuus).*
3. **Microsoft Reactor & Live Coding Battles:**
   - YouTube/Microsoft Reactor -kanavalla järjestetään live-koodaustaisteluita. Näistä voi hakea inspiraatiota ja nähdä edistyneitä tekniikoita livenä ammattilaisten tekemänä.
4. **Microsoft Learn & AI Skills Navigator:**
   - Etsikää oppimispolkuja spesifeihin teknologioihin (kuten *Microsoft Foundry* tai *M365 Copilot*), jotta saatte ohjelmointiin vankan pohjan.
