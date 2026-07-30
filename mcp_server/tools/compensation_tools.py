from database import get_connection
from app import mcp
from authorization import authorize_manager
from notifications import notify_tools_changed
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

from fastmcp import Context
@mcp.tool()
async def approve_compensation(
    employee_id: int,
    request_id: int,
     ctx: Context,
) -> dict:
    """
    Approve or reject a compensation request.
    Only managers can perform this action.
    """

    # -----------------------------
    # Authorization
    # -----------------------------
    auth = authorize_manager(employee_id)

    if not auth["authorized"]:
        return auth

    connection = get_connection()
    cursor = connection.cursor()

    # -----------------------------
    # Check request exists
    # -----------------------------
    cursor.execute(
        """
        SELECT
            status,
            requested_amount,
            booking_id
        FROM CompensationRequests
        WHERE request_id = ?
        """,
        (request_id,)
    )

    request = cursor.fetchone()

    if request is None:
        connection.close()

        return {
            "success": False,
            "message": "Compensation request not found."
        }

    # -----------------------------
    # Must be pending
    # -----------------------------
    if request["status"] != "Pending":  
        confirmation = await ctx.elicit(
        message=f"""
        Are you sure you want to approve this compensation request?

Request ID:
{request_id}

Booking ID:
{request["booking_id"]}

Requested Amount:
${request["requested_amount"]}
""",
        response_type=bool,
    )


    if confirmation.action != "accept":

        connection.close()

        return {
            "success": False,
            "message": "Operation cancelled by user."
        }


    approve = confirmation.data
        
        
        

    ##################################################################
    #
    # MCP ELICITATION GOES HERE
    #
    # Ask:
    #
    # Approve compensation request?
    #
    # Amount:
    # Booking:
    #
    ##################################################################

    new_status = "Approved" if approve else "Rejected"

    cursor.execute(
        """
        UPDATE CompensationRequests
        SET
            status = ?,
            approved_by = ?
        WHERE request_id = ?
        """,
        (
            new_status,
            employee_id,
            request_id,
        ),
    )

    connection.commit()
    await notify_tools_changed(ctx)
    connection.close()

    ##################################################################
    #
    # MCP tools/list_changed notification goes here
    #
    ##################################################################

    return {
        "success": True,
        "request_id": request_id,
        "status": new_status,
        "approved_by": employee_id,
        "message": f"Request {new_status.lower()} successfully."
    }