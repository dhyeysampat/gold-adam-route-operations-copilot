import json
import sqlite3
from pathlib import Path

from checks import (
    find_out_of_hours_bookings,
    find_unassigned_bookings,
    find_overlapping_bookings,
)

DB_PATH = Path(__file__).parent.parent / "data" / "operations.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_unassigned_booking_proposal(booking):
    connection = get_connection()

    explanation = (
        f"Booking {booking['booking_id']} for {booking['customer_name']} "
        f"is confirmed for {booking['scheduled_date']} from "
        f"{booking['start_time']} to {booking['end_time']}, but it has no route."
    )

    proposed_action = (
        f"Review available routes and assign booking "
        f"{booking['booking_id']} to a suitable route."
    )

    cursor = connection.execute(
        """
        INSERT INTO agent_proposals
        (issue_type, explanation, proposed_action, evidence_json, status)
        VALUES (?, ?, ?, ?, 'pending')
        """,
        (
            "unassigned_booking",
            explanation,
            proposed_action,
            json.dumps(booking),
        ),
    )

    connection.commit()
    proposal_id = cursor.lastrowid
    connection.close()

    return proposal_id


def create_all_proposals():
    proposal_ids = []

    for booking in find_unassigned_bookings():
        proposal_ids.append(create_unassigned_booking_proposal(booking))

    return proposal_ids


def list_proposals():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            id,
            issue_type,
            explanation,
            proposed_action,
            status,
            created_at,
            approved_by
        FROM agent_proposals
        ORDER BY id
        """
    ).fetchall()

    connection.close()
    return [dict(row) for row in rows]


if __name__ == "__main__":
    proposal_ids = create_all_proposals()
    print(f"Created proposal IDs: {proposal_ids}")

    print("\nCurrent proposals:")
    for proposal in list_proposals():
        print(proposal)