# EgyptAir MCP Server

## Overview

This project was developed as part of the Autonomous Agents – MCP Server Lab.

Our goal is to build a secure Model Context Protocol (MCP) server that allows an AI assistant to safely interact with EgyptAir's internal operational data without giving the language model direct access to the production database.

Instead of exposing SQL queries or shell commands, the server provides carefully designed business tools that perform validated and authorized operations.

The MCP server acts as a secure layer between the AI assistant and the database.

Architecture:
LLM
|
▼
MCP Client
|
▼
EgyptAir MCP Server
|
▼
SQLite Database
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

Instead of giving the LLM direct database access, this project exposes controlled business operations through an MCP Server.

The server handles:

- Authentication
- Authorization
- Validation
- Business rules
- Database operations

---

# Project Structure


EgyptAir-MCP-Server/

│
├── db/
│ ├── schema.sql
│ ├── seed.sql
│ ├── create_db.py
│ ├── database.db
│ ├── erd.mmd
│ └── erd.png
│
├── mcp_server/
│ ├── app.py
│ ├── server.py
│ ├── database.py
│ ├── config.py
│ ├── authorization.py
│ ├── validation.py
│ ├── notifications.py
│ └── tools/
│
├── agent/
│
└── README.md


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


db/erd.png


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

# Tool Classification

## Read Tools

Read tools only retrieve information and do not modify database state.

Examples:

- get_flight_status
- get_booking_details
- get_compensation_policy
- generate_disruption_report
- draft_passenger_email

---

## Write Tools

Write tools modify database information and require additional protection.

Examples:

- submit_compensation_request
- approve_compensation

---

# Defensive Tool Design

Write tools are designed using secure business operations instead of exposing SQL queries to the LLM.

Security measures include:

- Parameterized SQL queries
- Server-side validation
- Authorization checks
- Business rule validation
- Structured responses

The LLM only interacts with predefined MCP tools and never executes raw SQL commands.

---

# Validation

Validation is performed independently from MCP input schemas.

Examples:

- Verify booking exists
- Verify flight is eligible for compensation
- Verify requested amount is valid
- Verify compensation request exists
- Verify request is still pending before approval

---

# Authorization

Only authorized employees can execute sensitive write operations.

Example:

- Customer Service → Submit compensation requests
- Supervisor / Manager → Approve compensation requests

Authorization is performed inside the MCP tool handler before any database modification.

---

# Implemented Issue: Secure Compensation Approval Workflow

## Issue

The `approve_compensation` tool was a high-risk write operation because it directly modified compensation requests.

The missing requirements were:

- Human confirmation before approval
- MCP notification after state changes
- Protection against accidental database updates

---

# Solution 1: MCP Elicitation

## Problem

Before implementation, the approval process updated the database immediately after authorization checks.

This could allow accidental approval of compensation requests.

---

## Implementation

MCP Elicitation was added before the database update.

The workflow became:


Manager
|
approve_compensation()
|
Authorization Check
|
Request Validation
|
MCP Elicitation
|
User Confirmation
|
Database Update


The server asks the user for confirmation:

Example:


Are you sure you want to approve this compensation request?

Request ID: 8

Amount: $350


If the user confirms:

- Status becomes Approved
- approved_by is stored

If the user rejects:

- The operation is cancelled
- No database modification occurs

This ensures sensitive operations require explicit human approval.

---

# Solution 2: MCP tools/list_changed Notification

## Problem

After changing compensation status, connected clients needed a way to know that the server state had changed.

---

## Implementation

After successful compensation processing, the server sends:


notifications/tools/list_changed


This allows MCP clients to refresh their available information and stay synchronized with server changes.

---

# Implemented Issue: MCP Progress Tracking

## Problem

The `generate_disruption_report` tool performs multiple database operations and may take time.

Previously, the client had no information about the current execution state.

---

## Solution

MCP progress notifications were added.

The report generation now provides updates:


10% Starting report generation

30% Counting delayed flights

60% Counting cancelled flights

90% Calculating statistics

100% Report completed


After reaching 100%, the server returns the final report:

Contains:

- Delayed flights
- Cancelled flights
- Average delay
- Affected passengers

This improves user experience during long-running operations.

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
- Secure compensation approval workflow
- MCP Elicitation
- MCP tools/list_changed notification
- MCP Progress Tracking

---

# Remaining Work

The following protocol features are still under development:

- Capability Negotiation
- Resources
- Prompts
- Sampling
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

> **Note:** This README represents the current development stage. Additional protocol features will be added as 