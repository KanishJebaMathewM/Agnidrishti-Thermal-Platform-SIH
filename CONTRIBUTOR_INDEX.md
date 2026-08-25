# AGNIDRISHTI — Multi-Contributor Architecture & Team Workflow

> **Project:** AGNIDRISHTI — Thermal Anomaly Intelligence Platform  
> **Team Strategy:** 5 Independent Contributors / AI Agents  
> **Core Guarantee:** 100% Domain Isolation to prevent git conflicts.  

---

## 1. Zero-Conflict Architecture & Domain Ownership

To ensure 5 contributors can work concurrently without git merge conflicts, the codebase is split into 5 strictly decoupled domains.

| Contributor | Role & Domain | Assigned Git Branch | Document Link |
|---|---|---|---|
| **Contributor 1** | **Infrastructure, Database & FastAPI Core** (`backend/`, `db/`, `deployment/`, `scripts/`) | `feat/infra-backend` | [`CONTRIBUTOR_1_INFRA_AND_BACKEND.md`](file:///c:/Users/Admin/Desktop/Agnidrishti-Thermal-Platform-SIH-main/CONTRIBUTOR_1_INFRA_AND_BACKEND.md) |
| **Contributor 2** | **Data Ingestion & Processing Pipeline** (`workers/ingestion/`, `workers/preprocessing/`, `workers/enrichment/`, `data/`) | `feat/data-pipeline` | [`CONTRIBUTOR_2_DATA_PIPELINE.md`](file:///c:/Users/Admin/Desktop/Agnidrishti-Thermal-Platform-SIH-main/CONTRIBUTOR_2_DATA_PIPELINE.md) |
| **Contributor 3** | **ML Pipeline, Anomaly & Event Formation** (`ml/`, `workers/inference/`, `workers/events/`) | `feat/ml-pipeline` | [`CONTRIBUTOR_3_ML_PIPELINE.md`](file:///c:/Users/Admin/Desktop/Agnidrishti-Thermal-Platform-SIH-main/CONTRIBUTOR_3_ML_PIPELINE.md) |
| **Contributor 4** | **Frontend API Integration & UI State** (`frontend/`, `src/api/`, `src/hooks/`, `src/components/`, `src/pages/`) | `feat/frontend-integration` | [`CONTRIBUTOR_4_FRONTEND_INTEGRATION.md`](file:///c:/Users/Admin/Desktop/Agnidrishti-Thermal-Platform-SIH-main/CONTRIBUTOR_4_FRONTEND_INTEGRATION.md) |
| **Contributor 5** | **Jurisdiction Routing, Notifications & DevOps** (`backend/app/services/`, `workers/notifications/`, `deployment/`, `docs/`, `.github/`) | `feat/routing-notifications-devops` | [`CONTRIBUTOR_5_ROUTING_NOTIFICATIONS_AND_DEVOPS.md`](file:///c:/Users/Admin/Desktop/Agnidrishti-Thermal-Platform-SIH-main/CONTRIBUTOR_5_ROUTING_NOTIFICATIONS_AND_DEVOPS.md) |

---

## 2. Git Branching & Submission Rules

Every contributor (human or AI agent) **MUST** adhere to the following rules:

1. **Always Create a Feature Branch:**
   Before writing any code, check out your designated branch:
   ```bash
   git checkout -b <your-assigned-branch>
   ```

2. **Never Touch Other Domains:**
   Only modify files within your assigned domain. Do not edit files owned by another contributor unless explicitly listed in your plan step.

3. **Push to Your Feature Branch Only:**
   ```bash
   git add .
   git commit -m "feat: <description of work completed>"
   git push -u origin <your-assigned-branch>
   ```
   **Never push directly to `main`.**

---

## 3. How An AI Agent Should Execute A Plan

When an AI agent is assigned to one of the 5 roles:
1. Open the corresponding `CONTRIBUTOR_X_...md` document.
2. Run **Step 0** (git branch checkout and prerequisite code reading).
3. Follow the steps sequentially from **Step 1** to the final step.
4. Execute unit/integration tests for your module.
5. Push the feature branch to origin.

---

## 4. Master Reference Plan

For overall system architectural rationale and mathematical formulations, refer to the master plan:
- [`AGNIDRISHTI_PLAN.md`](file:///c:/Users/Admin/Desktop/Agnidrishti-Thermal-Platform-SIH-main/AGNIDRISHTI_PLAN.md)
