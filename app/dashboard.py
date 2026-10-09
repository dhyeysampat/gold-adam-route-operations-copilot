import sys
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent
DB_PATH = PROJECT_DIR / "data" / "operations.db"

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


def ensure_database_exists():
    if not DB_PATH.exists():
        from data.create_database import create_database
        from data.seed_database import seed_database

        create_database()
        seed_database()


ensure_database_exists()

from actions import (
    approve_proposal,
    execute_unassigned_booking_proposal,
)
from checks import (
    find_out_of_hours_bookings,
    find_overlapping_bookings,
    find_unassigned_bookings,
)
from proposals import create_all_proposals, list_proposals


st.set_page_config(
    page_title="Route Operations Copilot",
    page_icon="🛣️",
    layout="wide",
)

st.title("Route Operations Copilot")
st.caption("Synthetic data demonstration for controlled AI automation")

st.warning(
    "This is a portfolio prototype using synthetic data. "
    "It is not connected to Gold Adam systems."
)


def display_issue_counts():
    unassigned = find_unassigned_bookings()
    overlapping = find_overlapping_bookings()
    out_of_hours = find_out_of_hours_bookings()

    st.header("Operational issues")

    metric_1, metric_2, metric_3 = st.columns(3)

    metric_1.metric("Unassigned bookings", len(unassigned))
    metric_2.metric("Overlapping bookings", len(overlapping))
    metric_3.metric("Out-of-hours bookings", len(out_of_hours))

    return unassigned, overlapping, out_of_hours


def display_issues(unassigned, overlapping, out_of_hours):
    tab_1, tab_2, tab_3 = st.tabs(
        [
            "Unassigned bookings",
            "Overlapping bookings",
            "Out-of-hours bookings",
        ]
    )

    with tab_1:
        if unassigned:
            st.dataframe(unassigned, use_container_width=True)

            if st.button(
                "Create proposals for unassigned bookings",
                key="create_proposals",
            ):
                proposal_ids = create_all_proposals()
                st.success(f"Created proposal IDs: {proposal_ids}")
                st.rerun()
        else:
            st.success("No unassigned bookings found.")

    with tab_2:
        if overlapping:
            st.dataframe(overlapping, use_container_width=True)
        else:
            st.success("No overlapping bookings found.")

    with tab_3:
        if out_of_hours:
            st.dataframe(out_of_hours, use_container_width=True)
        else:
            st.success("No out-of-hours bookings found.")


def display_proposals():
    st.header("Agent proposals")

    proposals = list_proposals()

    if not proposals:
        st.info("No proposals have been created yet.")
        return

    st.dataframe(proposals, use_container_width=True)

    pending_proposals = [
        proposal
        for proposal in proposals
        if proposal["status"] == "pending"
    ]

    approved_proposals = [
        proposal
        for proposal in proposals
        if proposal["status"] == "approved"
    ]

    if pending_proposals:
        st.subheader("Approval required")

        for proposal in pending_proposals:
            st.write(f"Proposal {proposal['id']}")
            st.write(proposal["explanation"])
            st.write(f"Suggested action: {proposal['proposed_action']}")

            if st.button(
                f"Approve proposal {proposal['id']}",
                key=f"approve_{proposal['id']}",
            ):
                try:
                    approve_proposal(
                        proposal_id=proposal["id"],
                        approved_by="dashboard_reviewer",
                    )
                    st.success(
                        f"Proposal {proposal['id']} approved."
                    )
                    st.rerun()
                except Exception as error:
                    st.error(str(error))

    if approved_proposals:
        st.subheader("Approved actions")

        for proposal in approved_proposals:
            st.write(f"Proposal {proposal['id']}")
            st.write(proposal["explanation"])

            route_id = st.selectbox(
                "Select target route",
                options=[1, 2],
                key=f"route_{proposal['id']}",
            )

            if st.button(
                f"Execute proposal {proposal['id']}",
                key=f"execute_{proposal['id']}",
            ):
                try:
                    result = execute_unassigned_booking_proposal(
                        proposal_id=proposal["id"],
                        new_route_id=route_id,
                    )

                    st.success(
                        "Action executed successfully. "
                        f"Affected rows: {result['affected_rows']}"
                    )
                    st.json(result)
                    st.rerun()

                except Exception as error:
                    st.error(str(error))


unassigned, overlapping, out_of_hours = display_issue_counts()

display_issues(
    unassigned,
    overlapping,
    out_of_hours,
)

display_proposals()