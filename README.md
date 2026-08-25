# AGNIDRISHTI — Thermal Anomaly Intelligence Platform

AGNIDRISHTI is a physics-based thermal anomaly intelligence platform for satellite-driven detection, classification, baseline deviation monitoring, and agency alert routing across India.

## Features

- **National Overview:** Real-time satellite thermal event processing, anomaly escalation tracking, and suppression of expected industrial/seasonal sources.
- **Interactive Detection Map:** Spatial visualization of active thermal events across Indian states with classification indicators.
- **Thermal Source Registry:** Infrastructure inventory for registered industrial flares, brick kilns, power plants, and refineries.
- **Alerts & Agency Routing:** Automated notification routing to Fire Services, CPCB, Forest Department, and State Aggregation agencies.
- **Model Insights & Explainability:** Physics-based feature importance, confusion matrix analysis, and audit-ready classification metrics.
- **Historical & Seasonal Trends:** 30-day temporal trend breakdown and state-level anomaly rates.

## Team Contributor Plans & Workflows

To enable 5 contributors or AI agents to work concurrently without git merge conflicts, the project features 5 decoupled domain implementation plans:

| Contributor Plan | Domain & Scope | Branch |
|---|---|---|
| **Contributor 1** | [Infrastructure, Database & FastAPI Core](file:///c:/Users/Admin/Desktop/Agnidrishti-Thermal-Platform-SIH-main/CONTRIBUTOR_1_INFRA_AND_BACKEND.md) | `feat/infra-backend` |
| **Contributor 2** | [Data Ingestion & Processing Pipeline](file:///c:/Users/Admin/Desktop/Agnidrishti-Thermal-Platform-SIH-main/CONTRIBUTOR_2_DATA_PIPELINE.md) | `feat/data-pipeline` |
| **Contributor 3** | [ML Pipeline, Anomaly & Event Formation](file:///c:/Users/Admin/Desktop/Agnidrishti-Thermal-Platform-SIH-main/CONTRIBUTOR_3_ML_PIPELINE.md) | `feat/ml-pipeline` |
| **Contributor 4** | [Frontend API Integration & UI State](file:///c:/Users/Admin/Desktop/Agnidrishti-Thermal-Platform-SIH-main/CONTRIBUTOR_4_FRONTEND_INTEGRATION.md) | `feat/frontend-integration` |
| **Contributor 5** | [Jurisdiction Routing, Notifications & DevOps](file:///c:/Users/Admin/Desktop/Agnidrishti-Thermal-Platform-SIH-main/CONTRIBUTOR_5_ROUTING_NOTIFICATIONS_AND_DEVOPS.md) | `feat/routing-notifications-devops` |

For full details on git branching rules and domain boundaries, see the [Contributor Index](file:///c:/Users/Admin/Desktop/Agnidrishti-Thermal-Platform-SIH-main/CONTRIBUTOR_INDEX.md) and [Master Plan](file:///c:/Users/Admin/Desktop/Agnidrishti-Thermal-Platform-SIH-main/AGNIDRISHTI_PLAN.md).

## Getting Started

### Prerequisites

- Node.js (v18+ recommended)
- Python 3.11+
- Docker & Docker Compose

### Installation & Local Run

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start Development Server:**
   ```bash
   npm run dev
   ```

   Access the application at `http://localhost:5173`.

3. **Build for Production:**
   ```bash
   npm run build
   ```

