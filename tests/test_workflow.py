import sqlite3
import sys
from pathlib import Path

import pytest

PROJECT_DIR = Path(__file__).parent.parent
APP_DIR = PROJECT_DIR / "app"
DB_PATH = PROJECT_DIR / "data" / "operations.db"

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from actions import (
    approve_proposal,
    execute_unassigned_booking_proposal,
)
from proposals import create_all_proposals


@pytest.fixture
def prepared_database():
    setup_script = PROJECT_DIR / "setup.py"

    import subprocess

    subprocess.run(
        [sys.executable, str(setup_script)],
        check=True,
        cwd=PROJECT_DIR,
    )

    create_all_proposals()

    yield DB_PATH


def fetch_one(query, parameters=()):
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    row = connection.execute(query, parameters).fetchone()
    connection.close()
    return row


def test_unapproved_proposal_cannot_execute(prepared_database):
    with pytest.raises(ValueError, match="not approved"):
        execute_unassigned_booking_proposal(
            proposal_id=1,
            new_route_id=2,
        )

    booking = fetch_one(
        "SELECT route_id FROM bookings WHERE id = 6"
    )

    assert booking["route_id"] is None


def test_approved_proposal_executes_once(prepared_database):
    approve_proposal(
        proposal_id=1,
        approved_by="test_reviewer",
    )

    result = execute_unassigned_booking_proposal(
        proposal_id=1,
        new_route_id=2,
    )

    assert result["success"] is True
    assert result["affected_rows"] == 1
    assert result["booking_id"] == 6
    assert result["new_route_id"] == 2

    booking = fetch_one(
        "SELECT route_id FROM bookings WHERE id = 6"
    )

    assert booking["route_id"] == 2


def test_audit_log_is_created(prepared_database):
    approve_proposal(
        proposal_id=1,
        approved_by="test_reviewer",
    )

    execute_unassigned_booking_proposal(
        proposal_id=1,
        new_route_id=2,
    )

    audit = fetch_one(
        """
        SELECT proposal_id, action, affected_rows
        FROM audit_log
        WHERE proposal_id = 1
        """
    )

    assert audit["proposal_id"] == 1
    assert audit["action"] == "assign_booking_to_route"
    assert audit["affected_rows"] == 1


def test_same_proposal_cannot_execute_twice(prepared_database):
    approve_proposal(
        proposal_id=1,
        approved_by="test_reviewer",
    )

    execute_unassigned_booking_proposal(
        proposal_id=1,
        new_route_id=2,
    )

    with pytest.raises(ValueError, match="not approved"):
        execute_unassigned_booking_proposal(
            proposal_id=1,
            new_route_id=2,
        )


def test_wrong_route_date_is_rejected(prepared_database):
    connection = sqlite3.connect(DB_PATH)

    connection.execute(
        """
        INSERT INTO routes
        (id, route_date, employee_id, status)
        VALUES (3, '2026-10-13', 1, 'planned')
        """
    )

    connection.commit()
    connection.close()

    approve_proposal(
        proposal_id=1,
        approved_by="test_reviewer",
    )

    with pytest.raises(ValueError, match="date"):
        execute_unassigned_booking_proposal(
            proposal_id=1,
            new_route_id=3,
        )

    booking = fetch_one(
        "SELECT route_id FROM bookings WHERE id = 6"
    )

    assert booking["route_id"] is None