# MS Learn Koodireferenssit – Information Digest

Tämä raportti on koottu map-reduce-menetelmällä kolmelta eri aliagentilta, jotka tutkivat `mslearn-ai-agents`, `mslearn-ai-studio` ja `mslearn-genaiops` -koodivarastot (erityisesti niiden harjoituskansiot). Löydökset on jaoteltu projektisuunnitelman (`the_plan.md`) arkkitehtuurikomponenttien mukaisesti. Olen lisäksi varmistanut hakujen kattavuuden manuaalisilla läpikäynneillä.

## 1. Datan Hakijat -> MCP Palvelimet (Model Context Protocol)

Aliagentit löysivät laajoja ja hyödyllisiä esimerkkejä MCP:n hyödyntämisestä. 

**Parhaat koodireferenssit (`mslearn-ai-agents`):**
- `Labfiles/03-mcp-integration/Python/agent.py`, `client.py` ja `server.py` antavat meille suoraan valmiin pohjan MCP-palvelimen ja -asiakkaan rakentamiseen (esim. blogi- ja YouTube-datan lukemiseksi).
- Työkalujen yhdistäminen agenttiin löytyy tiedostosta: `Labfiles/03c-use-agent-tools-with-mcp/Python/client.py`.

## 2. Tekoälyorkestrointi (Microsoft Agent Framework)

Orkestroinnin osalta löysimme sekä etsimämme `SequentialBuilderin` että esimerkkejä puhtaasta `azure.ai.projects` -SDK:n käytöstä.

**Multi-agent orkestrointi (`mslearn-ai-agents`):**
- **SequentialBuilder:** Koodiesimerkki löytyy tiedostosta `Labfiles/05-agent-orchestration/Python/agents.py` (esim. putken rakentaminen: `workflow = SequentialBuilder(participants=[summarizer, classifier, action]).build()`). Tätä voimme suoraan hyödyntää Fan-In/Fan-Out -toteutuksessamme.
- **GroupChatBuilder:** Monimutkaisempien keskustelujen mallinnus löytyy tiedostosta `Labfiles/05-agent-orchestration/Python/agents_groupchat.py`.

**AI Agent Service (`mslearn-genaiops`):**
- Perustason agentin luonti ja `PromptAgentDefinition` löytyvät tiedostosta `src/agents/trail_guide_agent/trail_guide_agent.py`.

**Pydantic Validointi:**
- Repositorioissa käytetään vain Pydanticin perusteita (esim. `from pydantic import Field` tiedostossa `Labfiles/07-agent-framework/python/agent-framework.py`), joten joudumme todennäköisesti kirjoittamaan validointimallit tiukemmiksi itse suunnitelmamme mukaan. Laajempaa mallipohjaista tiedonjäsentelyä (BaseModel) ei harjoituksissa ole käytetty.

## 3. Output & Integraatio (Teams)

Projektisuunnitelman mukainen automaattinen Teams-viestintä löytyy suoraan `mslearn-ai-agents` -harjoituksista.

**Teams Bot/Webhook -integraatio (`mslearn-ai-agents`):**
- `Labfiles/05a-m365-teams-integration/Python/m365_teams_lab.py` sisältää bot-manifestipohjat (`"bots": [{"botId": "${{BOT_ID}}"}]`), Azure Bot Servicen asetusohjeet ja webhook-viittaukset. Voimme hyödyntää tätä "Master Synthesizerin" julkaisuputkessa.

## 4. GenAIOps ja Tuotantovalmius

Tämä on kriittinen osuus Hackathonissa menestymiseen. Löysimme todella hyvät mallit OpenTelemetrylle ja evaluoinnille.

**OpenTelemetry (Azure Monitor) (`mslearn-genaiops`):**
- GenAIOps-kansiossa seuranta on pitkälle automatisoitu. `src/tests/run_monitoring.py` hyödyntää funktiota `azure.monitor.opentelemetry.configure_azure_monitor` ja OpenAI:n instrumentointia varten `opentelemetry.instrumentation.openai_v2.OpenAIInstrumentor`. 
- Lisäksi `mslearn-ai-agents` -repositorion `requirements.txt` -tiedostot suosittelevat `opentelemetry-semantic-conventions-ai` -kirjaston käyttöä.

**Content Filters:**
- Yksikään agentti tai tarkennettu hakuni ei löytänyt kooditason määrittelyitä Content Safety -suodattimille. Tämä vahvistaa sen, että sisällönsuodattimet kytketään pääsääntöisesti päälle suoraan Azure AI Foundry -portaalista koodin sijaan näissä malleissa.

**Golden Dataset Evaluointi (LLM-as-a-judge):**
- **Evaluointiskripti (`mslearn-genaiops`):** `src/evaluators/evaluate_agent.py` sisältää täydellisen pilvievaluointiskriptin, joka käyttää GPT-malleja (esim. gpt-4) tuomarina (LLM-as-a-judge). 
- **Esimerkit datasta:** Löysimme kaksi loistavaa esimerkkirakennetta `.jsonl`-tiedostoille. `data/trail_guide_evaluation_dataset.jsonl` (`query`, `response`, `ground_truth`) ja `mslearn-ai-studio` -reposta `labfiles/model-eval/travel_evaluation_data.jsonl` (`Question`, `ExpectedResponse`). Näistä pystymme suoraan kopioimaan mallin oman agenttiemme suorituskyvyn varmistavaan jsonl-testisettiin.

---

### Loppupäätelmä
Kaikki projektisuunnitelmamme osa-alueet löytyvät valmiina pohjina lukuun ottamatta laajaa Pydantic-validointia ja ohjelmallista Content Filter -määrittelyä, jotka meidän tulee soveltaa itse. Tämä tekee hackathonin rakennusvaiheesta huomattavasti nopeamman.
