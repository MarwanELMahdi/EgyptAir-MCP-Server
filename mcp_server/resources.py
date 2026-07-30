from app import mcp
from database import get_connection
import json

@mcp.resource("sql://policies")
def Fetch_resources() -> str:
    """Read-only resource for getting policy table."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
           """
           SELECT
               p.policy_id , p.title , p.content
           FROM Policies 
           """
       )
    policies = cursor.fetchall()
    connection.close()

    if not policies:
        return json.dumps({"found": False, "message": "No policies found."})

    return json.dumps(policies, indent=2)