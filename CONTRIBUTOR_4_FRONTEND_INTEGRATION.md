# CONTRIBUTOR 4 — Frontend API Integration & UI State Management

> **Branch name to create:** `feat/frontend-integration`  
> **Your domain:** `frontend/`, `src/api/`, `src/hooks/`, `src/components/`, `src/pages/`, `frontend/tests/`  
> **Do NOT touch:** `backend/`, `workers/`, `ml/`, `db/migrations/`  
> **Push rule:** Always push to `feat/frontend-integration`. Never push to `main`.  

---

## Who you are

You are connecting the AGNIDRISHTI visual user interface to the backend services.
You own:

- The HTTP API client layer connecting React to FastAPI endpoints
- Custom React hooks for data fetching, caching, loading states, and error handling
- Replacing mock data with live API endpoints while preserving fallback capability
- Updating map visualizations (MapLibre GL / deck.gl / Leaflet) with real event coordinates
- Connecting human-in-the-loop verification actions (Confirm, False Alarm, Reclassify)
- Adding data freshness indicators and error boundaries across all pages
- Unit and component tests for the frontend

---

## Repository context

**AGNIDRISHTI** is a physics-based thermal anomaly intelligence platform for satellite-driven detection, classification, baseline deviation monitoring, and agency alert routing across India.

The frontend is built with:
- **React 18 + TypeScript + Vite**
- **Tailwind CSS**
- **Lucide React** (icons)
- **Leaflet / React-Leaflet** (spatial map rendering)
- **Recharts** (charts & trend analysis)
- **React Router v6**

The data contracts are defined in `src/data/mockData.ts`. Study this file — it specifies the TypeScript interfaces for `ThermalEvent`, `ThermalSource`, `AlertRoute`, `DashboardSummary`, and `ModelInsights`.

---

## Step 0 — First actions (do these before anything else)

```bash
git checkout -b feat/frontend-integration
```

Then read these files before writing any code:

1. `src/data/mockData.ts` — The TypeScript interfaces represent the exact schema returned by the backend API.
2. `src/App.tsx` — Routing layout and top-level navigation.
3. `CONTRIBUTOR_1_INFRA_AND_BACKEND.md` — Section 4 (FastAPI application routes and endpoint contracts).
4. `AGNIDRISHTI_PLAN.md` — Section 6 (Phase 1 — Freeze and Connect Existing Frontend).

---

## Step 1 — API Client Layer Setup

Create `src/api/client.ts` to provide a unified HTTP client with configurable base URL and fallback support.

```typescript
// src/api/client.ts

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const USE_MOCK_FALLBACK = import.meta.env.VITE_USE_MOCK_FALLBACK === 'true';

export async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
  
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API Error ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    if (USE_MOCK_FALLBACK) {
      console.warn(`[API Client] Endpoint ${endpoint} failed. Falling back to mock mode.`, error);
      throw error; // Let custom hooks catch and fallback to mockData
    }
    throw error;
  }
}
```

Create environment template file `.env.example` inside `frontend/` or root:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCK_FALLBACK=true
```

---

## Step 2 — API Domain Modules

Create structured API wrappers under `src/api/`:

### 2.1 `src/api/dashboardApi.ts`

```typescript
import { fetchApi } from './client';
import { mockDashboardSummary, mockThermalEvents } from '../data/mockData';

export async function getDashboardSummary() {
  try {
    return await fetchApi<typeof mockDashboardSummary>('/dashboard/summary');
  } catch (err) {
    return mockDashboardSummary; // Fallback during initial dev
  }
}

export async function getMapEvents() {
  try {
    return await fetchApi<{ events: typeof mockThermalEvents }>('/dashboard/map');
  } catch (err) {
    return { events: mockThermalEvents };
  }
}

export async function getDashboardTrends() {
  return await fetchApi<{ points: any[] }>('/dashboard/trends');
}
```

### 2.2 `src/api/eventsApi.ts`

```typescript
import { fetchApi } from './client';
import { ThermalEvent, mockThermalEvents } from '../data/mockData';

export interface EventFilterParams {
  page?: number;
  limit?: number;
  state?: string;
  classification?: string;
  status?: string;
  anomaly_only?: boolean;
}

export async function getEvents(params?: EventFilterParams) {
  const query = new URLSearchParams();
  if (params?.page) query.append('page', params.page.toString());
  if (params?.limit) query.append('limit', params.limit.toString());
  if (params?.state) query.append('state', params.state);
  if (params?.classification) query.append('classification', params.classification);
  if (params?.status) query.append('status', params.status);
  if (params?.anomaly_only) query.append('anomaly_only', 'true');

  try {
    return await fetchApi<{ items: ThermalEvent[]; total: number; page: number; pages: number }>(
      `/events?${query.toString()}`
    );
  } catch (err) {
    return { items: mockThermalEvents, total: mockThermalEvents.length, page: 1, pages: 1 };
  }
}

export async function getEventById(id: string): Promise<ThermalEvent> {
  try {
    return await fetchApi<ThermalEvent>(`/events/${id}`);
  } catch (err) {
    const found = mockThermalEvents.find((e) => e.id === id);
    if (!found) throw new Error(`Event ${id} not found`);
    return found;
  }
}

export async function confirmEvent(id: string, reviewer: string, comment: string) {
  return await fetchApi(`/events/${id}/confirm`, {
    method: 'POST',
    body: JSON.stringify({ reviewer, comment }),
  });
}

export async function markFalseAlarm(id: string, reviewer: string, comment: string) {
  return await fetchApi(`/events/${id}/false-alarm`, {
    method: 'POST',
    body: JSON.stringify({ reviewer, comment }),
  });
}

export async function reclassifyEvent(id: string, newClassification: string, reviewer: string, comment: string) {
  return await fetchApi(`/events/${id}/reclassify`, {
    method: 'POST',
    body: JSON.stringify({ new_classification: newClassification, reviewer, comment }),
  });
}
```

### 2.3 `src/api/sourcesApi.ts` & `src/api/authoritiesApi.ts`

Create:
- `src/api/sourcesApi.ts`: `getSources()`, `getSourceById(id)`, `getSourceHistory(id)`
- `src/api/authoritiesApi.ts`: `getAuthorities()`, `resolveRouting(lat, lon, classification)`

---

## Step 3 — Custom Data Hooks

Create React custom hooks under `src/hooks/` to handle loading, error, polling, and refetch states cleanly.

### 3.1 `src/hooks/useDashboardData.ts`

```typescript
import { useState, useEffect } from 'react';
import { getDashboardSummary } from '../api/dashboardApi';

export function useDashboardData() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastSync, setLastSync] = useState<Date>(new Date());

  const refetch = async () => {
    setLoading(true);
    try {
      const res = await getDashboardSummary();
      setData(res);
      setLastSync(new Date());
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch dashboard summary');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refetch();
    // Poll every 60 seconds
    const interval = setInterval(refetch, 60000);
    return () => clearInterval(interval);
  }, []);

  return { data, loading, error, lastSync, refetch };
}
```

### 3.2 `src/hooks/useEventsList.ts`

```typescript
import { useState, useEffect } from 'react';
import { getEvents, EventFilterParams } from '../api/eventsApi';
import { ThermalEvent } from '../data/mockData';

export function useEventsList(initialParams?: EventFilterParams) {
  const [events, setEvents] = useState<ThermalEvent[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [params, setParams] = useState<EventFilterParams>(initialParams || {});

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    getEvents(params)
      .then((res) => {
        if (isMounted) {
          setEvents(res.items);
          setTotal(res.total);
          setError(null);
        }
      })
      .catch((err) => {
        if (isMounted) setError(err.message);
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [JSON.stringify(params)]);

  return { events, total, loading, error, params, setParams };
}
```

---

## Step 4 — Page Component Integration

Connect existing pages to live hooks:

### 4.1 `src/pages/Overview.tsx`
- Replace direct `mockData` references with `useDashboardData()`
- Render loading spinner skeleton while `loading` is true
- Render error alert banner if `error` is present
- Add live data timestamp badge: `Last sync ${formatDistanceToNow(lastSync)} ago`

### 4.2 `src/pages/Events.tsx`
- Connect search box, state dropdown, and classification filter to `useEventsList()`
- Pass filtered events array to `src/components/IndiaMap.tsx` and list view

### 4.3 `src/components/EventDetail.tsx`
- Connect verification action buttons:
  - **Confirm Event** button calls `confirmEvent(event.id, "Operator", comment)`
  - **Mark False Alarm** calls `markFalseAlarm(...)`
  - **Reclassify** triggers dropdown modal and calls `reclassifyEvent(...)`

### 4.4 `src/pages/Alerts.tsx`
- Connect routing resolution lookup form to `resolveRouting(lat, lon, classification)`
- Render routing agency breakdown dynamically based on PostGIS authority response

---

## Step 5 — UI Polishing & Error Boundaries

1. Create `src/components/shared/ErrorBoundary.tsx` to prevent component crashes from taking down the app shell.
2. Add empty state components when search/filter returns zero events.
3. Update `TopNav.tsx` live status badge to reflect actual API connectivity state (`Live` vs `Offline / Demo Mode`).

---

## Step 6 — Frontend Tests

Create unit and component tests in `frontend/tests/`:

1. `tests/apiClient.test.ts`: Test `fetchApi` handling 200 OK responses and 500 error scenarios.
2. `tests/useEventsList.test.tsx`: Test filtering params triggering re-fetch.
3. `tests/EventDetailModal.test.tsx`: Test clicking confirm button calls the API handler.

Run tests using Vite / Vitest / Jest:
```bash
npm run test
```

---

## Step 7 — Push

```bash
git add .
git commit -m "feat: frontend API integration layer, custom hooks, live map rendering, and human verification actions"
git push -u origin feat/frontend-integration
```

---

## Files you will create or modify

```text
frontend/
  .env.example                               (new)
  tests/
    apiClient.test.ts                        (new)
    useEventsList.test.tsx                   (new)
    EventDetailModal.test.tsx                (new)
src/
  api/
    client.ts                                (new)
    dashboardApi.ts                          (new)
    eventsApi.ts                             (new)
    sourcesApi.ts                            (new)
    authoritiesApi.ts                        (new)
  hooks/
    useDashboardData.ts                      (new)
    useEventsList.ts                         (new)
    useEventDetail.ts                        (new)
    useSourcesList.ts                        (new)
  components/
    shared/
      ErrorBoundary.tsx                      (new)
      LoadingSkeleton.tsx                    (new)
      EmptyState.tsx                         (new)
    TopNav.tsx                               (modify)
    IndiaMap.tsx                             (modify)
    EventDetail.tsx                          (modify)
  pages/
    Overview.tsx                             (modify)
    Events.tsx                               (modify)
    Registry.tsx                             (modify)
    Alerts.tsx                               (modify)
    Trends.tsx                               (modify)
    DataSources.tsx                          (modify)
    ModelInsights.tsx                        (modify)
```

---

## Key rules for this contributor

1. **Preserve existing UI contracts.** The visual design in `src/pages/` is approved. Do not alter styling or layout unless adding a missing backend field.
2. **Always support graceful fallback.** If backend endpoints return an error or are unreachable, catch errors gracefully and display user-friendly warnings or mock fallbacks during development.
3. **Keep state management predictable.** Use clean custom hooks for data fetching. Do not put global `fetch()` calls directly inside JSX render functions.
4. **Coordinate UI modals with backend status.** Disable action buttons while async requests are pending to prevent double-submission.
