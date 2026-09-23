---
name: rds-oss-advisor
description: Advisor for Amazon RDS open-source engines (MySQL, MariaDB, PostgreSQL) focusing on optimization, proxy evaluation, and lifecycle management.
---

# RDS OSS Advisor (MySQL, MariaDB, PostgreSQL)

This skill provides expert guidance for Amazon RDS open-source engines. It is designed to be executed by the `AgentOrchestrator` using the Perceive-Plan-Act-Evaluate architecture to ensure production-ready database configurations.

## Agentic Workflow

The agent follows the **Perceive-Plan-Act-Evaluate** cycle across three distinct phases:

### Phase 1: Diagnosis (Perceive)
**Goal:** Gather the current state of the RDS environment and identify the user's specific objective.
- **Perceive:** Analyze existing instance configurations, engine versions, connection metrics (via CloudWatch/Performance Insights), and current cost structures.
- **Identify Target:** Determine if the focus is on Instance Creation, Upgrade Planning, Commitment Pricing, Proxy Evaluation, or Blue/Green Deployment.
- **Constraint Mapping:** Identify version compatibility, regional availability, and security requirements (encryption, VPC).

### Phase 2: Analysis (Plan)
**Goal:** Develop a tailored strategy based on the diagnosed state.
- **Plan:**
    - **For Creation:** Map requirements to best-practice defaults (Multi-AZ, Performance Insights, Secrets Manager).
    - **For Upgrades:** Enumerate target versions and generate a pre-flight checklist.
    - **For Proxy:** Analyze connection pinning risks and utilization patterns to determine if RDS Proxy provides value.
    - **For Pricing:** Model RI vs. Savings Plan scenarios for the specific workload.
    - **For Blue/Green:** Perform DDL compatibility analysis to ensure low-downtime transitions.

### Phase 3: Implementation & Reporting (Act & Evaluate)
**Goal:** Execute the plan or provide the final advisory report.
- **Act:**
    - **Automated Execution:** For *Instance Creation*, generate and execute the `create-db-instance` call using the AWS MCP server or AWS CLI.
    - **Advisory Output:** For *Upgrades, Pricing, and Switchovers*, provide a detailed report including cost estimates, precheck findings, and the exact CLI commands required.
- **Evaluate:** 
    - Verify that the proposed configuration adheres to production best practices.
    - Ensure all "Advisory Only" operations have a clear "User Confirmation" gate.
    - Validate that the output is scoped strictly to MySQL, MariaDB, and PostgreSQL.

## Tech Stack Integration

The agent leverages the following stack for execution and reporting:
- **Execution:** AWS MCP Server / AWS CLI.
- **Reporting:** Findings are formatted for delivery via **Astro**-based dashboards or emailed via **Resend** if requested.
- **Infrastructure:** Deployment scripts may be hosted on **Cloudflare Pages/Functions** for self-service advisor interfaces.
- **Validation:** Use **TypeScript/Node.js** for pre-flight check scripts and **Python** for cost modeling calculations.

## Decision Guide

| Area | Action Type | Key Focus |
| :--- | :--- | :--- |
| **Instance Creation** | Execute | Production defaults, Multi-AZ, Encryption, Secrets Manager |
| **Upgrade Planning** | Advisory | Version targets, Live prechecks, Regression flagging |
| **Commitment Pricing** | Advisory | RI vs. Database Savings Plans, Workload steadiness |
| **RDS Proxy** | Advisory | Connection utilization, Pinning risks, Lambda scaling |
| **Blue/Green** | Advisory | DDL compatibility, Low-downtime major upgrades |

**Scope Note:** This skill is strictly for RDS open-source engines. For Aurora, use `amazon-aurora`. For Oracle, SQL Server, or Db2, use the respective engine-specific skills.
