\# Gold Adam Route Operations Copilot

\[!\[Live Demo](https://img.shields.io/badge/Live\_Demo-Streamlit-FF4B4B?logo=streamlit\&logoColor=white)](https://dhyeyproject.streamlit.app/)



\*\*Live demo:\*\* \[Route Operations Copilot](PASTE\_YOUR\_STREAMLIT\_URL\_HERE)

A portfolio prototype demonstrating safe, database-connected workflow automation for route operations.



\## What it does



This prototype demonstrates a controlled automation workflow for route operations:



1\. Detects unassigned bookings.

2\. Detects overlapping bookings.

3\. Detects bookings outside employee working hours.

4\. Creates structured agent proposals.

5\. Requires human approval before operational changes.

6\. Executes approved changes inside a database transaction.

7\. Checks that exactly one row was affected.

8\. Verifies the final database state.

9\. Records an audit log.



\## Architecture



```text

SQLite database

&#x20;       ↓

Deterministic SQL checks

&#x20;       ↓

Operational issue detected

&#x20;       ↓

Agent proposal created

&#x20;       ↓

Human approval

&#x20;       ↓

Current state revalidated

&#x20;       ↓

Transactional update

&#x20;       ↓

Affected-row verification

&#x20;       ↓

Audit log

```



The system separates detection, proposal, approval, execution, and auditing. An AI model can later interpret tasks and explain results, but it should not bypass these controls.



\## Why this matters



Many AI demos stop at generating an answer. This project focuses on the operational layer:



\- What data can the agent read?

\- What action can it propose?

\- Who approves the action?

\- What happens if the database changes before execution?

\- How do we ensure exactly one row is changed?

\- How do we make the action auditable?



This is the pattern needed when automation affects bookings, payments, customer communication, compliance reporting, or other systems people depend on.



\## Technology



\- Python

\- SQLite

\- SQL

\- Streamlit

\- Python virtual environment

\- Synthetic operational data



\## Run locally



```bash

python -m venv .venv

```



Windows PowerShell:



```powershell

.\\.venv\\Scripts\\Activate.ps1

pip install -r requirements.txt

python setup.py

python -m streamlit run app/dashboard.py

```



Open the local URL shown by Streamlit.



\## Safety design



The prototype separates:



```text

Detection -> Proposal -> Approval -> Execution -> Verification -> Audit

```



The write workflow:



\- Re-checks the current booking state.

\- Rejects already-assigned bookings.

\- Validates the target route.

\- Requires exactly one affected row.

\- Rolls back if validation fails.

\- Verifies the final state.

\- Writes an audit record.



\## Disclaimer



This project uses synthetic data and is not connected to Gold Adam or any production system. It is a portfolio demonstration of database-aware AI automation patterns.



\## Potential extensions



\- Route travel-time validation.

\- Human approval through a web interface.

\- MCP-compatible tools.

\- Payment reconciliation.

\- Compliance reporting.

\- LLM-based task interpretation.

\- Automated evaluation and monitoring.

