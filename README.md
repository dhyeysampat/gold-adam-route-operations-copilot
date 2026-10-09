\# Gold Adam Route Operations Copilot



A portfolio prototype demonstrating safe, database-connected workflow automation for route operations.



\## What it does



The application:



\- Detects unassigned bookings.

\- Detects overlapping bookings.

\- Detects bookings outside employee working hours.

\- Creates structured agent proposals.

\- Requires approval before operational changes.

\- Executes approved changes inside a database transaction.

\- Checks the affected row count.

\- Verifies the updated state.

\- Records an audit log.



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

