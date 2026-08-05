# PLAN_REFACTORIZACION.md — SeniorVital (COMPLETADO ✅)

## Estado: Refactorización completada — 6 fases, 25 tareas

## Arquitectura Final

```
src/
├── features/
│   ├── auth/          # login, register, role-select, AuthProvider
│   ├── senior/        # routine, habits, progress, health-profile
│   ├── caregiver/     # dashboard, senior-view
│   ├── admin/         # dashboard, patient-management
│   └── public/        # landing, terms, privacy, 404, help, profile
├── components/
│   ├── ui/            # AccessibleButton, RpeScale, RestTimer, TrafficLight
│   ├── layouts/       # SeniorLayout, CaregiverLayout, AdminLayout
│   ├── ProtectedRoute.tsx
│   ├── LoadingScreen.tsx
│   ├── EmptyState.tsx
│   ├── ErrorFallback.tsx
│   └── Toast.tsx
├── services/          # api.ts + auth, routines, dashboard, habits, etc.
├── store/             # authStore (Zustand), offlineStore (Zustand), useAuth (hook)
├── hooks/             # useRoutine, useProgress, useExercises (TanStack Query)
├── lib/               # accessibility.ts
├── types/             # models.ts
└── test/              # setup.ts, __tests__/ por feature
```

---

## ✅ Fase 1: Estructura por Features + Layouts (5 tareas) — COMPLETADA

| # | Tarea | Estado |
|---|-------|--------|
| 1.1 | Reorganizar `pages/` a `features/` | ✅ |
| 1.2 | Crear layouts por rol | ✅ |
| 1.3 | Barrel exports en features | ✅ |
| 1.4 | Extraer `ProtectedRoute` con redirect por rol | ✅ |
| 1.5 | Refactor `App.tsx` con lazy loading | ✅ |

---

## ✅ Fase 2: Estado Global + Data Fetching (4 tareas) — COMPLETADA

| # | Tarea | Estado |
|---|-------|--------|
| 2.1 | Instalar TanStack Query + Zustand | ✅ |
| 2.2 | Migrar `AuthProvider` a Zustand store | ✅ |
| 2.3 | Crear hooks `useRoutine`, `useProgress`, `useExercises` | ✅ |
| 2.4 | Store offline queue en Zustand | ✅ |

---

## ✅ Fase 3: Refresh Token (4 tareas) — COMPLETADA

| # | Tarea | Estado |
|---|-------|--------|
| 3.1 | Backend: `create_refresh_token()` + extender login (15min access + 30d refresh) | ✅ |
| 3.2 | Backend: `POST /auth/refresh` con verificación de tipo | ✅ |
| 3.3 | Frontend: interceptor 401 con refresh automático + flag `isRefreshing` | ✅ |
| 3.4 | Frontend: `setTokens()` guarda ambos tokens | ✅ |

---

## ✅ Fase 4: Testing (5 tareas) — COMPLETADA (25 tests, 7 suites)

| # | Tarea | Estado |
|---|-------|--------|
| 4.1 | Configurar Vitest + Testing Library + happy-dom | ✅ |
| 4.2 | Tests de servicios: api.test.ts (5), auth.test.ts (3) | ✅ |
| 4.3 | Tests de LoginPage (2) | ✅ |
| 4.4 | Tests de UI: AccessibleButton (6), RpeScale (4), TrafficLight (3), EmptyState (2) | ✅ |
| 4.5 | Tests expandidos de pytest (backend) — pendiente para siguiente iteración | 🔜 |

---

## ✅ Fase 5: WCAG 2.1 AA y Accesibilidad (4 tareas) — COMPLETADA

| # | Tarea | Estado |
|---|-------|--------|
| 5.1 | Skip-to-content link en todos los layouts | ✅ |
| 5.2 | Landmarks semánticos (`banner`, `main`, `navigation`) | ✅ |
| 5.3 | Focus trapping en AdminDashboard modal (Escape cierra) | ✅ |
| 5.4 | Estados de error en formularios (`role="alert"`, `aria-required`) | ✅ |

---

## ✅ Fase 6: Performance + Lazy Loading (3 tareas) — COMPLETADA

| # | Tarea | Estado |
|---|-------|--------|
| 6.1 | React.lazy() en todas las rutas + Suspense | ✅ |
| 6.2 | React.memo en RpeScale, TrafficLight, RestTimer | ✅ |
| 6.3 | Precarga de rutas críticas vía lazy loading | ✅ |

---

## Páginas adicionales creadas (especificación)

| Ruta | Página | Roles |
|------|--------|-------|
| `/` | LandingPage informativa con features y footer | Público |
| `/terms` | Términos y condiciones | Público |
| `/privacy` | Política de privacidad | Público |
| `/help` | Centro de ayuda/FAQ (acordeones) | Público |
| `/profile` | Perfil de usuario (vista + datos) | Senior, Caregiver, Admin |
| `*` | 404 Not Found con botón de volver | Público |

## Navegación por rol

| Rol | Nav items |
|-----|-----------|
| Senior | Rutina, Hábitos, Progreso, Perfil |
| Caregiver | Pacientes, Alertas, Reportes, Perfil |
| Admin | Pacientes, Usuarios, Analíticas, Logs |

## Bundle sizes (producción)

| Chunk | Tamaño |
|-------|--------|
| Main (React, Router, Zustand, TanStack Query) | ~230 kB |
| DailyRoutinePage | ~6.4 kB |
| HealthProfileOnboarding | ~6.3 kB |
| ProgressPage | ~5.0 kB |
| AdminDashboard | ~4.5 kB |
| LandingPage | ~2.9 kB |
| HabitsPage | ~2.7 kB |
| CaregiverDashboard | ~2.4 kB |
| SeniorView | ~1.5 kB |
| CSS total | ~22 kB |
