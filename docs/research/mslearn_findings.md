# Löydökset: MS Learn AI Agents -materiaali

Aliagentit kävivät läpi MS Learn -materiaalin (`source-materials` ja `Labfiles` -kansiot) etsien parhaita käytäntöjä ja koodimalleja meidän Information Digest -projektiimme. Tässä on yhteenveto tärkeimmistä löydöksistä:

## 1. Arkkitehtuuriset Konseptit (Source Materials)

- **Multi-Agent Orkestrointi:**
  - *Sequential Orchestration:* Datan vienti putken läpi asiantuntija-agentilta toiselle (esim. Tiedonhakija -> Tiivistäjä -> Muotoilija). Tämä vastaa täydellisesti meidän "Raw -> Silver -> Gold" -visiotamme.
  - *Concurrent (Fan-Out/Fan-In):* Tehtävien rinnakkainen ajo. Voimme analysoida (Fan-Out) esimerkiksi 10 artikkelia rinnakkain Silver-agenteilla ja yhdistää ne lopuksi yhdeksi uutiskirjeeksi (Fan-In).
  - *Group Chat:* Agenttien välinen vapaampi keskustelu (esim. Maker/Checker -asetelma).
- **Knowledge Base (Foundry IQ):** Omien monimutkaisten RAG-putkien sijaan Microsoft suosittelee domain-kohtaisten Foundry IQ -tietokantojen käyttöä.
- **Dynaamiset työkalut ja MCP:** Työkalut kannattaa irrottaa MCP-palvelimiksi (Model Context Protocol), jotta niitä voidaan kutsua dynaamisesti ja päivittää ilman, että itse agentin koodiin kosketaan.
- **Prompt Engineering ja Työkalut:** Työkalujen määrittelyssä tulee käyttää Pydanticin `Annotated` ja `Field` -määrityksiä erittäin yksityiskohtaisesti. LLM käyttää näitä kuvauksia suoraan promptina päätellessään, mitä työkalua pitää käyttää.

## 2. Koodiesimerkit ja SDK-toteutukset (Labfiles)

Koodiesimerkeistä paljastui, että MS käyttää kahta päälähestymistapaa agenttien ohjelmoinnissa:

### Tapa A: Azure AI Projects SDK (`azure.ai.projects`)
Matalamman tason kirjasto, joka muistuttaa perinteistä OpenAI API:a.
- **Agentin luonti:** `AIProjectClient.agents.create_version(..., tools=[...])`
- **MCP Työkalut:** Määritellään `MCPTool`-luokalla. Palvelimen kutsut vaativat koodissa nimenomaisen hyväksymisluupin (`mcp_approval_request` -> `McpApprovalResponse`).
- **Strukturoitu Data:** Tehdään puhtailla JSON-skeemoilla (`FunctionTool`).

### Tapa B: Microsoft Agent Framework (`agent_framework`)
Korkeamman tason orkestrointikirjasto, joka on tehty nimenomaan multi-agent -työnkulkuihin.
- **Orkestrointi:** Tarjoaa valmiit luokat kuten `SequentialBuilder` ja `GroupChatBuilder`, jotka tekevät agenttien ketjuttamisesta todella helppoa.
- **Esimerkki:**
  ```python
  workflow = SequentialBuilder().participants([summarizer, classifier]).build()
  async for event in workflow.run_stream("User prompt"):
      # Handle events
  ```
- **Työkalut:** Käyttää `@tool`-dekoraattoreita ja Pydantic-validointia.

---

## 🎯 Johtopäätökset Information Digest -projektiin

Näiden löydösten perusteella meidän alkuperäinen suunnitelmamme saa kaksi isoa vahvistusta ja päivitystä:

1. **Valitsemme SDK:ksi `agent_framework`:** Sen tarjoama `SequentialBuilder` on kuin tehty meidän arkkitehtuuriimme. Ketjutamme agentit muotoon: `Extractor Agent` -> `Silver Validator Agent` -> `Master Synthesizer`.
2. **Käytämme Fan-Out / Fan-In -mallia:** Jotta emme tee koodista hidasta, ajamme Raw -> Silver -vaiheen rinnakkain usealla dokumentilla yhtä aikaa (Fan-Out) ja syötämme tulokset "Fan-In" -tyyppisesti Master Synthesizerille, joka rakentaa lopullisen Markdownin.
3. **Pydantic pysyy mukana:** Vaikka luovuimme `Pydantic AI` -kirjastosta orkestraattorina, Microsoftin uusi `agent_framework` nojaa vahvasti Pydanticiin (`Annotated` ja `Field`) työkalujen ja strukturoidun datan validoinnissa. Alkuperäinen vahvuutemme JSON-validoinnissa ei siis katoa mihinkään!
