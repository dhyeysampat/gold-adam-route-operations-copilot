import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "operations.db"


def create_database():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.executescript(
        """
        DROP TABLE IF EXISTS audit_log;
        DROP TABLE IF EXISTS agent_proposals;
        DROP TABLE IF EXISTS route_stops;
        DROP TABLE IF EXISTS bookings;
        DROP TABLE IF EXISTS routes;
        DROP TABLE IF EXISTS employees;
        DROP TABLE IF EXISTS customers;

        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL
        );

        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            working_day_start TEXT NOT NULL,
            working_day_end TEXT NOT NULL
        );

        CREATE TABLE routes (
            id INTEGER PRIMARY KEY,
            route_date TEXT NOT NULL,
            employee_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        );

        CREATE TABLE bookings (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            scheduled_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            status TEXT NOT NULL,
            route_id INTEGER,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (route_id) REFERENCES routes(id)
        );

        CREATE TABLE route_stops (
            id INTEGER PRIMARY KEY,
            route_id INTEGER NOT NULL,
            booking_id INTEGER NOT NULL,
            sequence_number INTEGER NOT NULL,
            planned_arrival TEXT NOT NULL,
            FOREIGN KEY (route_id) REFERENCES routes(id),
            FOREIGN KEY (booking_id) REFERENCES bookings(id)
        );

        CREATE TABLE agent_proposals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            issue_type TEXT NOT NULL,
            explanation TEXT NOT NULL,
            proposed_action TEXT NOT NULL,
            evidence_json TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            approved_by TEXT
        );

        CREATE TABLE audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proposal_id INTEGER,
            action TEXT NOT NULL,
            affected_rows INTEGER NOT NULL,
            before_state TEXT,
            after_state TEXT,
            timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (proposal_id) REFERENCES agent_proposals(id)
        );
        """
    )

    connection.commit()
    connection.close()
    print(f"Database created at: {DB_PATH}")


if __name__ == "__main__":
    create_database()