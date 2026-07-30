# EgyptAir MCP Server

## Overview

This project was developed as part of the Autonomous Agents – MCP Server Lab.

Our goal is to build a secure Model Context Protocol (MCP) server that allows an AI assistant to safely interact with EgyptAir's internal operational data without giving the language model direct access to the production database.

Instead of exposing SQL queries or shell commands, the server provides a carefully designed set of business tools that perform validated and authorized operations.

---

# Company

**EgyptAir** is Egypt's national airline.

The company handles thousands of passenger bookings every day. Flight delays and cancellations often lead to customer compensation requests that must be reviewed by customer service employees and supervisors.

The objective of this project is to build an AI assistant that helps employees manage these operations safely through MCP.

---

# Problem Statement

Without MCP, an LLM could generate arbitrary SQL queries directly against the production database, creating several risks:

- Invalid SQL queries
- Unauthorized data modification
- Prompt injection attacks
- Poor auditing
- Difficult monitoring

Instead, this project exposes a small number of business operations through an MCP Server.

---

# Project Structure

```
EgyptAir-MCP-Server/

│
├── db/
│   ├── schema.sql
│   ├── seed.sql
│   ├── create_db.py
│   ├── database.db
│   ├── erd.mmd
│   └── erd.png
│
├── mcp_server/
│   ├── app.py
│   ├── server.py
│   ├── database.py
│   ├── config.py
│   ├── authorization.py
│   ├── validation.py
│   └── tools/
│
├── agent/
│
└── README.md
```

---

# Database

SQLite was selected as the database engine because it is lightweight, portable, and easy to demonstrate during development.

The database contains the following entities:

- Employees
- Flights
- Passengers
- Bookings
- CompensationRequests
- Policies
- Reports

The complete Entity Relationship Diagram is available inside:

```
db/erd.png
```

---

# Current MCP Tools

| Tool | Type | Purpose |
|------|------|---------|
| get_flight_status | Read | Retrieve flight status |
| get_booking_details | Read | Retrieve booking information |
| get_compensation_policy | Read | Read compensation policy |
| submit_compensation_request | Write | Create a new compensation request |
| approve_compensation | Write | Approve or reject compensation |
| generate_disruption_report | Read | Generate disruption report |
| draft_passenger_email | Read | Draft passenger email |

---

# Defensive Tool Design

Write tools are designed using secure business operations instead of exposing SQL.

Security measures include:

- Parameterized SQL queries
- Server-side validation
- Authorization checks
- Business rule validation
- Structured responses

---

# Validation

Validation is performed independently from the MCP input schema.

Examples include:

- Booking exists
- Flight is eligible for compensation
- Requested amount is within allowed limits

---

# Authorization

Only authorized employees can execute sensitive write operations.

Example:

- Customer Service → Submit compensation requests
- Supervisor / Manager → Approve compensation requests

---

# Current Progress

The following components have been completed:

- Project planning
- Company selection
- Problem definition
- Database schema
- Seed data
- SQLite database
- ERD
- MCP Server initialization
- Database connection layer
- Configuration module
- Validation module
- Authorization module
- Initial MCP tools

---

# Remaining Work

The following protocol features are currently under development:

- Capability Negotiation
- Notifications
- Resources
- Prompts
- Elicitation
- Sampling
- Progress Tracking
- Streamable HTTP Transport
- Agent Integration
- Final Demonstration

---

# Technologies

- Python
- SQLite
- FastMCP
- Model Context Protocol (MCP)
- LangChain (planned)
- JSON Schema

---

# Team

- Marwan Ahmed
- Ahmed Ashraf
- Youssef Hatem

---

> **Note:** This README represents the current development stage. Additional protocol features will be added as implementation progresses.