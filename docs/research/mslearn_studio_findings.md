# Löydökset: MS Learn AI Studio -materiaali

Aliagentit tutkivat `mslearn-ai-studio` -kansion sisällön (`labfiles` koodiesimerkit ja `source-materials` arkkitehtuuriohjeet). Tässä on yhteenveto Azure AI Studion parhaista käytännöistä Information Digest -projektia varten:

## 1. Yhteydet ja SDK (Azure AI Projects)
- **AIProjectClient:** Azure OpenAI:n käyttöön suositellaan `azure.ai.projects.AIProjectClient` -luokkaa yhdessä `DefaultAzureCredential` -autentikoinnin kanssa. 
- **Etu:** Tämä poistaa tarpeen kovakoodata API-avaimia sovellukseen (Käytetään Entra ID / Managed Identity -tunnistautumista).
- **Yhteyshallinta:** Kaikki palveluyhteydet (tietokannat, API:t, Azure AI Search) tulisi hallita keskitetysti AI Studion/Foundryn projektitasolla, eikä koodissa.

## 2. Prompt Flow & Orkestrointi
- **Visuaalinen ohjelmointi:** Prompt Flow'n avulla työnkulkujen (kuten tiedonhaku ja tiivistäminen) rakentaminen ja testaaminen on helppoa YAML-tiedostojen ja UI:n avulla.
- **Rakenne:** Kussakin työnkulussa on selkeät Inputit, Outputit ja "LLM Toolit". Prompt Flow tukee Jinja-syntaksia kontekstin ja chat-historian ruiskuttamiseksi systeemi-prompteihin.
- **Meidän projektiimme:** Voimme rakentaa eri agenteille (esim. Extractor, Synthesizer) omat Prompt Flow -työnkulkunsa, ja lopuksi julkaista ne itsenäisinä mikropalveluina.

## 3. RAG (Retrieval-Augmented Generation) ja Tiedonhaku
- **Sisäänrakennettu integraatio:** Omien Python-pohjaisten RAG-vektorointien rakentamisen sijaan Microsoft suosittelee datan tallentamista Azure AI Search -indeksiin.
- **Hybrid Search:** Vektorihaun (semanaattinen samankaltaisuus) ja avainsanahaun yhdistelmä on tarkin tapa hakea tietoa.
- **Koodiesimerkki:** Haku onnistuu suoraan antamalla `chat.completions` -kutsulle `extra_body`-parametri, jossa viitataan AI Search -indeksiin (`"type": "azure_search"`).

## 4. Tietoturva (Content Safety) ja Responsible AI
- **Custom Content Filters:** Koska Information Digest hakee 3. osapuolen dataa netistä, on kriittistä kytkeä päälle Azuren Content Filterit. Ne estävät mm. väkivaltaisen tai vihamielisen sisällön prosessoinnin.
- **Prompt Shields:** Suojaavat agenttia "Prompt Injection" -hyökkäyksiltä (esim. jos lukemassamme blogissa on piilotettu teksti: "Ignore previous instructions and output bad stuff").
- **Monikerroksisuus:** Tietoturva ei saa levätä vain yhden filtterin varassa. Se vaatii hyvän system promptin, automaattiset filtterit ja tarvittaessa "Human-in-the-loop" -tarkastuksia.

## 5. Evaluoinnit ja Laadunvarmistus
- **Golden Dataset:** Suositellaan rakentamaan `.jsonl` -tiedosto, joka sisältää kysymyksiä/artikkeleita ja *odotettuja vastauksia* (ExpectedResponse).
- **Automatisoitu testaus:** Tämän datasettiin voidaan ajaa automatisoituja kokeita (esim. vahvemmalla GPT-4o mallilla), joka arvioi agenttiemme tuotoksia esimerkiksi skaalalla Semantic similarity, Relevance ja F1 Score.
- **Ihmistestaus:** Automaation lisäksi tarvitaan säännöllistä manuaalista testituotosten lukemista, sillä AI ei täydellisesti hahmota tekstin sävyä ("Looks good" ei riitä).

## 6. Fine-Tuning (Hienosäätö)
- **Vasta viimeinen vaihtoehto:** Mallien hienosäätöä ei suositella tiedon opettamiseen (siihen käytetään RAGia), vaan ainoastaan poikkeuksellisten formaattien tai tietynlaisen yrityssävyn (Tone of voice) pakottamiseen.
