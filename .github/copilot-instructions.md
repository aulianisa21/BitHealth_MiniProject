## Repository-specific instructions for AI coding agents

These notes help an AI editing agent be immediately productive in this small FastAPI + LangChain repo.

- Project layout: single-file service in `main.py`. Key responsibilities live there: FastAPI app, Pydantic models, LangChain prompt/LLM wiring, and endpoints (`/` and `/recommend`).

- Primary integration points to inspect before edits:
  - `from dotenv import load_dotenv` — environment variables are expected; prefer `.env` for secrets.
  - `ChatGoogleGenerativeAI` (from `langchain_google_genai`) and `PromptTemplate` (from `langchain_core.prompts`) — LLM interface and prompt construction.
  - `chain = prompt | llm | StrOutputParser()` and `await chain.ainvoke(input_data)` — the code composes a LangChain pipeline and calls it asynchronously. Preserve async usage when modifying.

- Endpoint behavior to preserve:
  - POST `/recommend` takes `PatientInput` (gender, age, symptoms: list[str]) and returns `DepartmentOutput` with a single string field `recommended_department`.
  - The prompt enforces a strict output contract: "Tolong berikan hanya 'Nama departemen'... Jangan berikan penjelasan atau kalimat tambahan." Do not add surrounding text or explanations in responses unless you also update the API contract and tests.

- Sensitive data & environment:
  - `load_dotenv()` is called but `main.py` currently sets `GOOGLE_API_KEY` inline. Do NOT hardcode API keys — prefer `.env` and the `GOOGLE_API_KEY` env var. If you must change code, replace the inline assignment with safe-reading logic and add `.env` to `.gitignore`.

- Running & local development:
  - Run server locally with: `uvicorn main:app --reload` (file-level app is `app` in `main.py`).
  - Tests or integration checks should use `fastapi.testclient.TestClient` to exercise `/recommend` without starting uvicorn.

- Common edits an agent may perform:
  - Update or refine the `prompt_template_text` in `main.py` to change triage rules — keep the single-line output contract in sync with `DepartmentOutput`.
  - Swap LLM model by editing `ChatGoogleGenerativeAI(model="...")` — ensure downstream behavior still returns a plain department name.
  - Add logging around `chain.ainvoke(...)` and sanitise outputs (strip/regex) but do not add extra user-visible text to the API response.

- Dependencies to check when editing or running:
  - `fastapi`, `uvicorn`, `python-dotenv`, `pydantic`, and the LangChain packages used in `main.py` (imports shown above). If adding CI or tests, add a `requirements.txt` or `pyproject.toml` listing these.

- Examples from the codebase:
  - Prompt composition: `prompt = PromptTemplate.from_template(prompt_template_text)`
  - Chain composition: `chain = prompt | llm | StrOutputParser()`
  - Async invocation: `recommendation = await chain.ainvoke(input_data)`

- When modifying behavior, update two places together:
  1. `prompt_template_text` (intent/constraints), and
  2. the `DepartmentOutput` Pydantic model (response contract) and any tests.

If anything here is unclear or you want more examples (tests, CI config, or a corrected `.env`-safe refactor for `main.py`), tell me which area to expand and I will update this file.
