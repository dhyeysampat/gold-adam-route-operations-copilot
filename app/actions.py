import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "operations.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def approve_proposal(proposal_id, approved_by):
    connection = get_connection()

    cursor = connection.execute(
        """
        UPDATE agent_proposals
        SET status = 'approved',
            approved_by = ?
        WHERE id = ?
          AND status = 'pending'
        """,
        (approved_by, proposal_id),
    )

    if cursor.rowcount != 1:
        connection.rollback()
        connection.close()
        raise ValueError(
            f"Proposal {proposal_id} was not pending or does not exist."
        )

    connection.commit()
    connection.close()

    return True


def execute_unassigned_booking_proposal(proposal_id, new_route_id):
    connection = get_connection()

    try:
        proposal = connection.execute(
            """
            SELECT *
            FROM agent_proposals
            WHERE id = ?
              AND issue_type = 'unassigned_booking'
              AND status = 'approved'
            """,
            (proposal_id,),
        ).fetchone()

        if proposal is None:
            raise ValueError(
                "The proposal does not exist or is not approved."
            )

        evidence = json.loads(proposal["evidence_json"])
        booking_id = evidence["booking_id"]

        booking_before = connection.execute(
            """
            SELECT id, route_id, status
            FROM bookings
            WHERE id = ?
            """,
            (booking_id,),
        ).fetchone()

        if booking_before is None:
            raise ValueError(f"Booking {booking_id} does not exist.")

        if booking_before["route_id"] is not None:
            raise ValueError(
                f"Booking {booking_id} is already assigned to a route."
            )

        route = connection.execute(
            """
            SELECT id, route_date, status
            FROM routes
            WHERE id = ?
            """,
            (new_route_id,),
        ).fetchone()

        if route is None:
            raise ValueError(f"Route {new_route_id} does not exist.")

        if route["route_date"] != evidence["scheduled_date"]:
            raise ValueError("The route date does not match the booking date.")

        if route["status"] != "planned":
            raise ValueError("Only planned routes can receive new bookings.")

        connection.execute("BEGIN")

        update_cursor = connection.execute(
            """
            UPDATE bookings
            SET route_id = ?
            WHERE id = ?
              AND route_id IS NULL
              AND status = 'confirmed'
            """,
            (new_route_id, booking_id),
        )

        if update_cursor.rowcount != 1:
            raise RuntimeError(
                f"Expected to update 1 booking, updated "
                f"{update_cursor.rowcount}."
            )

        booking_after = connection.execute(
            """
            SELECT id, route_id, status
            FROM bookings
            WHERE id = ?
            """,
            (booking_id,),
        ).fetchone()

        if booking_after["route_id"] != new_route_id:
            raise RuntimeError("Post-update verification failed.")

        connection.execute(
            """
            UPDATE agent_proposals
            SET status = 'executed'
            WHERE id = ?
              AND status = 'approved'
            """,
            (proposal_id,),
        )

        connection.execute(
            """
            INSERT INTO audit_log
            (proposal_id, action, affected_rows, before_state, after_state)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                proposal_id,
                "assign_booking_to_route",
                update_cursor.rowcount,
                json.dumps(dict(booking_before)),
                json.dumps(dict(booking_after)),
            ),
        )

        connection.commit()

        return {
            "success": True,
            "proposal_id": proposal_id,
            "booking_id": booking_id,
            "new_route_id": new_route_id,
            "affected_rows": update_cursor.rowcount,
            "before": dict(booking_before),
            "after": dict(booking_after),
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    proposal_id = 1
    new_route_id = 2

    approve_proposal(proposal_id, "demo_reviewer")

    result = execute_unassigned_booking_proposal(
        proposal_id,
        new_route_id,
    )

    print(result)