from database import get_connection
from app import mcp

from validation import (
    validate_booking_exists,
    validate_requested_amount,
    validate_flight_eligible_for_compensation,
)

from authorization import authorize_customer_service


@mcp.tool()
def submit_compensation_request(
    employee_id: int,
    booking_id: int,
    requested_amount: float,
    reason: str,
) -> dict:
    """
    Submit a new compensation request for a passenger.
    Only Customer Service employees are allowed to create requests.
    """

    # -----------------------------
    # Authorization
    # -----------------------------
    auth = authorize_customer_service(employee_id)

    if not auth["authorized"]:
        return auth

    # -----------------------------
    # Validation
    # -----------------------------
    booking_validation = validate_booking_exists(booking_id)

    if not booking_validation["valid"]:
        return booking_validation

    amount_validation = validate_requested_amount(requested_amount)

    if not amount_validation["valid"]:
        return amount_validation

    eligibility_validation = validate_flight_eligible_for_compensation(
        booking_id
    )

    if not eligibility_validation["valid"]:
        return eligibility_validation

    # -----------------------------
    # Insert Request
    # -----------------------------
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO CompensationRequests
        (
            booking_id,
            requested_amount,
            reason,
            status,
            approved_by,
            created_at
        )
        VALUES
        (
            ?, ?, ?, 'Pending', NULL, DATE('now')
        )
        """,
        (
            booking_id,
            requested_amount,
            reason,
        ),
    )

    connection.commit()

    request_id = cursor.lastrowid

    connection.close()

    return {
        "success": True,
        "request_id": request_id,
        "booking_id": booking_id,
        "status": "Pending",
        "message": "Compensation request submitted successfully."
    }