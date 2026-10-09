import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "operations.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def find_unassigned_bookings():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            b.id AS booking_id,
            c.name AS customer_name,
            b.scheduled_date,
            b.start_time,
            b.end_time,
            b.status
        FROM bookings AS b
        JOIN customers AS c
            ON c.id = b.customer_id
        WHERE b.route_id IS NULL
          AND b.status = 'confirmed'
        ORDER BY b.scheduled_date, b.start_time
        """
    ).fetchall()

    connection.close()
    return [dict(row) for row in rows]


def find_overlapping_bookings():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            first_booking.id AS first_booking_id,
            second_booking.id AS second_booking_id,
            first_booking.route_id,
            first_booking.start_time AS first_start,
            first_booking.end_time AS first_end,
            second_booking.start_time AS second_start,
            second_booking.end_time AS second_end
        FROM bookings AS first_booking
        JOIN bookings AS second_booking
            ON first_booking.route_id = second_booking.route_id
           AND first_booking.id < second_booking.id
           AND first_booking.scheduled_date = second_booking.scheduled_date
           AND first_booking.start_time < second_booking.end_time
           AND second_booking.start_time < first_booking.end_time
        WHERE first_booking.status = 'confirmed'
          AND second_booking.status = 'confirmed'
        ORDER BY first_booking.route_id, first_booking.start_time
        """
    ).fetchall()

    connection.close()
    return [dict(row) for row in rows]


def find_out_of_hours_bookings():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            b.id AS booking_id,
            b.route_id,
            e.name AS employee_name,
            b.start_time,
            b.end_time,
            e.working_day_start,
            e.working_day_end
        FROM bookings AS b
        JOIN routes AS r
            ON r.id = b.route_id
        JOIN employees AS e
            ON e.id = r.employee_id
        WHERE b.status = 'confirmed'
          AND (
              b.start_time < e.working_day_start
              OR b.end_time > e.working_day_end
          )
        ORDER BY b.route_id, b.start_time
        """
    ).fetchall()

    connection.close()
    return [dict(row) for row in rows]


if __name__ == "__main__":
    print("Unassigned bookings:")
    for row in find_unassigned_bookings():
        print(row)

    print("\nOverlapping bookings:")
    for row in find_overlapping_bookings():
        print(row)

    print("\nOut-of-hours bookings:")
    for row in find_out_of_hours_bookings():
        print(row)