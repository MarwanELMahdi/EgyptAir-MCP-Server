from database import get_connection
from app import mcp


@mcp.tool()
def get_flight_status(flight_number: str) -> dict:
    """
    Retrieve the current status and schedule of a flight using its flight number.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            flight_number,
            origin,
            destination,
            departure_time,
            arrival_time,
            status,
            delay_minutes
        FROM Flights
        WHERE flight_number = ?
        """,
        (flight_number,),
    )

    flight = cursor.fetchone()

    connection.close()

    if flight is None:
        return {
            "found": False,
            "message": "Flight not found."
        }

    return {
        "found": True,
        "flight_number": flight["flight_number"],
        "origin": flight["origin"],
        "destination": flight["destination"],
        "departure_time": flight["departure_time"],
        "arrival_time": flight["arrival_time"],
        "status": flight["status"],
        "delay_minutes": flight["delay_minutes"],
    }