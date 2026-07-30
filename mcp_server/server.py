from app import mcp

# Register all tools
import tools.flight_tools
import tools.booking_tools

if __name__ == "__main__":
    mcp.run()