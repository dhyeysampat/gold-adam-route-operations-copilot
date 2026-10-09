import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "operations.db"


def seed_database():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("PRAGMA foreign_keys = ON")

    customers = [
        (1, "Customer 1", "+358400000001", "Helsinki", 60.1699, 24.9384),
        (2, "Customer 2", "+358400000002", "Espoo", 60.2055, 24.6559),
        (3, "Customer 3", "+358400000003", "Vantaa", 60.2934, 25.0378),
        (4, "Customer 4", "+358400000004", "Helsinki", 60.1900, 24.9500),
        (5, "Customer 5", "+358400000005", "Kauniainen", 60.2120, 24.7280),
        (6, "Customer 6", "+358400000006", "Helsinki", 60.1700, 24.9700),
    ]

    employees = [
        (1, "Employee 1", "08:00", "16:00"),
        (2, "Employee 2", "09:00", "17:00"),
    ]

    routes = [
        (1, "2026-10-12", 1, "planned"),
        (2, "2026-10-12", 2, "planned"),
    ]

    bookings = [
        (1, 1, "2026-10-12", "09:00", "09:30", "confirmed", 1),
        (2, 2, "2026-10-12", "09:20", "09:50", "confirmed", 1),
        (3, 3, "2026-10-12", "11:00", "11:30", "confirmed", 1),
        (4, 4, "2026-10-12", "15:45", "16:15", "confirmed", 1),
        (5, 5, "2026-10-12", "10:00", "10:30", "confirmed", 2),
        (6, 6, "2026-10-12", "13:00", "13:30", "confirmed", None),
    ]

    route_stops = [
        (1, 1, 1, 1, "09:00"),
        (2, 1, 2, 2, "09:20"),
        (3, 1, 3, 3, "11:00"),
        (4, 1, 4, 4, "15:45"),
        (5, 2, 5, 1, "10:00"),
    ]

    cursor.executemany(
        """
        INSERT INTO customers
        (id, name, phone, address, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        customers,
    )

    cursor.executemany(
        """
        INSERT INTO employees
        (id, name, working_day_start, working_day_end)
        VALUES (?, ?, ?, ?)
        """,
        employees,
    )

    cursor.executemany(
        """
        INSERT INTO routes
        (id, route_date, employee_id, status)
        VALUES (?, ?, ?, ?)
        """,
        routes,
    )

    cursor.executemany(
        """
        INSERT INTO bookings
        (id, customer_id, scheduled_date, start_time, end_time, status, route_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        bookings,
    )

    cursor.executemany(
        """
        INSERT INTO route_stops
        (id, route_id, booking_id, sequence_number, planned_arrival)
        VALUES (?, ?, ?, ?, ?)
        """,
        route_stops,
    )

    connection.commit()
    connection.close()
    print("Synthetic data inserted successfully.")


if __name__ == "__main__":
    seed_database()