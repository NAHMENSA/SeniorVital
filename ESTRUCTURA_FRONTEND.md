# Estructura del Frontend — SeniorVital

> SPA de gestión de bienestar para adultos mayores construida con **TypeScript 5.3**, **React 18**, **Vite 4**, **Tailwind CSS 3.3**, **react-router-dom v6**, **Zustand** (estado), **@tanstack/react-query** (servidor de datos), **react-hook-form + zod** (formularios), **recharts** (gráficas) y **localforage** (persistencia offline). Consume las APIs REST del backend SeniorVital a través del gateway en el puerto 8000 (proxy de Vite en desarrollo). La generación de rutinas con IA (Ollama) se recibe por **SSE streaming**. Diseño mobile-first con layouts por rol: senior, cuidador y admin.

---

## Árbol de Directorios

```
seniorvital/frontend/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── index.css
    ├── vite-env.d.ts
    ├── components/
    │   ├── EmptyState.tsx
    │   ├── ErrorFallback.tsx
    │   ├── LoadingScreen.tsx
    │   ├── ProtectedRoute.tsx
    │   ├── Toast.tsx
    │   ├── index.ts
    │   ├── layouts/
    │   │   ├── AdminLayout.tsx
    │   │   ├── CaregiverLayout.tsx
    │   │   ├── SeniorLayout.tsx
    │   │   └── index.ts
    │   └── ui/
    │       ├── AccessibleButton.tsx
    │       ├── HamburgerMenu.tsx / .module.css
    │       ├── RestTimer.tsx
    │       ├── RpeScale.tsx / .module.css
    │       ├── TrafficLight.tsx
    │       └── index.ts
    ├── contexts/
    │   └── AuthProvider.tsx
    ├── features/
    │   ├── public/   (LandingPage, TermsPage, PrivacyPage, HelpPage, ProfilePage, NotFoundPage)
    │   ├── auth/     (RoleSelectPage, LoginPage, RegisterPage)
    │   ├── senior/   (DailyRoutinePage, HabitsPage, ProgressPage, HealthProfileOnboarding)
    │   ├── caregiver/ (CaregiverDashboard, CaregiverAlertsPage, CaregiverReportsPage, SeniorView)
    │   └── admin/    (AdminDashboard)
    ├── hooks/
    │   ├── useRoutine.ts
    │   ├── useProgress.ts
    │   ├── useExercises.ts
    │   ├── useMediaQuery.ts
    │   ├── useEscapeKey.ts
    │   ├── useClickOutside.ts
    │   └── index.ts
    ├── lib/
    │   └── accessibility.ts
    ├── services/
    │   ├── api.ts
    │   ├── auth.ts
    │   ├── routines.ts
    │   ├── habits.ts
    │   ├── exercises.ts
    │   ├── dashboard.ts
    │   ├── caregiver.ts
    │   └── admin.ts
    ├── store/
    │   ├── authStore.ts
    │   ├── offlineStore.ts
    │   └── useAuth.ts
    ├── test/
    │   └── setup.ts
    └── types/
        └── models.ts
```

---

## 1. Raíz — `frontend/`

**Funcionalidad:** Configuración de tooling, dependencias, estilos base y punto de entrada HTML. Todos los comandos se ejecutan aquí (`npm run dev`, `npm run build`, `npm test`).

### `index.html`
- Entrada HTML en español (`lang="es"`). Carga Google Fonts **Lexend** (400, 600, 700) y Material Symbols Outlined. Body con clases `bg-background text-on-background min-h-screen` y div `#root`.

### `package.json`
- `name: "seniorvital-frontend"`, `type: "module"`, `scripts`: `dev`, `build`, `preview`, `test` (`vitest run`), `test:watch`.
- **Dependencias:** `react@^18.2`, `react-dom@^18.2`, `react-router-dom@^6.11`, `zustand@^5`, `@tanstack/react-query@^5.101`, `react-hook-form@^7.78`, `@hookform/resolvers@^5.4`, `zod@^4.4`, `recharts@^3.8`, `localforage@^1.10`, `typescript@5.3`.
- **devDependencies:** `vite@^4.3`, `vitest@^4.1`, `@vitejs/plugin-react`, `tailwindcss@^3.3`, `postcss`, `autoprefixer`, `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event`, `happy-dom`, tipos de React.

### `vite.config.ts`
- Plugin React + alias `@` → `./src`.
- **Config de test (Vitest):** `environment: 'happy-dom'`, `setupFiles: ['./src/test/setup.ts']`, `globals: true`.
- **Proxy de desarrollo (5173 → gateway 8000):** `/auth`, `/caregiver`, `/admin`, `/catalog`, `/tracking`, `/dashboard`, `/habits`, `/notify`, `/storage`, y `/routines` con `proxyTimeout`/`timeout: 600000` (600s) para acomodar la generación lenta de rutinas por Ollama.

### `tailwind.config.js`
- Paleta **Material Design 3** (tokens `primary`, `secondary`, `tertiary`, `error`, `surface` con variantes container/fixed/dim/bright/inverse), espaciado semántico (`stack-md`, `touch-target-min`, `gutter`), radio `lg/xl/full` y font `lexend`.

---

## 2. Punto de entrada y enrutado

### `src/index.css`
- Estilos globales **orientados a adultos mayores**: directivas `@tailwind base/components/utilities`, fuente base 20px (`html { font-size: 125% }`), tamaño de texto `clamp(1.25rem → 1.5rem)`, touch targets ≥ 56px, anillo de foco visible reforzado (`:focus-visible`, WCAG 2.4.7) y utilidad `.sr-only`.

### `src/main.tsx`
- `ReactDOM.createRoot` sobre `#root`, renderiza `<App />` en `<React.StrictMode>`, importa `index.css`.

### `src/App.tsx`
- Provee `QueryClient` (retry 1, sin refetch al enfocar ventana, `staleTime` 5 min) → `Router` → `AuthProvider` → `Routes`.
- **Carga diferida (lazy) + `Suspense`** con `LoadingScreen` como fallback para las páginas de features.
- **`RoleRouter`:** según `useAuth().user`, redirige al home de cada rol: senior → `/routine`, caregiver → `/caregiver`, admin → `/admin`.

Tabla de rutas:

| Ruta | Rol | Componente |
|------|-----|-----------|
| `/` | público | `LandingPage` |
| `/register`, `/login` | público | `RegisterPage`, `LoginPage` |
| `/terms`, `/privacy`, `/help` | público | `TermsPage`, `PrivacyPage`, `HelpPage` |
| `/profile` | todos (protegida) | `ProfilePage` |
| `/onboarding/health-profile` | protegida sin layout | `HealthProfileOnboarding` |
| `/routine`, `/habits`, `/progress` | senior | `DailyRoutinePage`, `HabitsPage`, `ProgressPage` |
| `/caregiver`, `/caregiver/alerts`, `/caregiver/reports` | caregiver | `CaregiverDashboard`, `CaregiverAlertsPage`, `CaregiverReportsPage` |
| `/caregiver/senior/:seniorId` | caregiver | `SeniorView` |
| `/admin` | admin | `AdminDashboard` |
| `*` | — | `NotFoundPage` |

- Las rutas de rol usan `ProtectedRoute requiredRole="..."`; las públicas sin protección quedan abiertas.

---

## 3. Estado global — `src/store/`

### `authStore.ts`
- Store Zustand persistente de autenticación: `user`, `loading`, acciones `login`, `register`, `logout`, `updateUser`. Guarda/restaura sesión desde localStorage.

### `useAuth.ts`
- Hook de conveniencia sobre el store: expone `isSenior`, `isCaregiver`, `isAdmin` (derivados de `user.role`) y `displayName` (prioriza `nombre_senior`, luego `nombre_cuidador`, luego `email`).

### `offlineStore.ts`
- Cola offline (Zustand) para reintentar peticiones de hábitos/tracking cuando no hay conexión. Se procesa con `processOfflineQueue()` de `services/api.ts`.

---

## 4. Capa de servicios — `src/services/`

- **`api.ts`** — Cliente HTTP base con token JWT:
  - Guarda `sv_token` y `sv_refresh_token` en localStorage.
  - Inyecta `Authorization: Bearer` excepto en `/auth/login`, `/auth/register`, `/auth/refresh`.
  - **Auto-refresh:** en un 401 no público, intenta refrescar una sola vez (con protección `isRefreshing`/`refreshPromise` para evitar llamadas concurrentes); si falla, limpia sesión y dispara el evento `sv:unauthorized`.
  - `ApiError` con `status` + mensaje extraído de `detail` de FastAPI.
  - Cola offline: `addToOfflineQueue`, `processOfflineQueue`, `getOfflineQueueSize`.
- **`auth.ts`** — login, register, refresh, logout.
- **`routines.ts`** — genera rutinas por **SSE streaming** (`generateRoutineStream`), obtiene la rutina del día, etc.
- **`habits.ts`** — registro/consulta de hábitos diarios (agua, sueño).
- **`exercises.ts`** — catálogo de ejercicios.
- **`dashboard.ts`** — progreso, racha, tendencia RPE, insights del agente.
- **`caregiver.ts`** — enlace senior-cuidador, alertas (fatiga/inactividad), reportes semanales.
- **`admin.ts`** — lista de pacientes con semáforo de riesgo.

---

## 5. Hooks — `src/hooks/`

| Hook | Uso |
|------|-----|
| `useRoutine` | Estado y generación de la rutina diaria (incluye streaming SSE) |
| `useProgress` | Datos de progreso/analítica |
| `useExercises` | Catálogo de ejercicios |
| `useMediaQuery` | Breakpoints responsive vía matchMedia |
| `useEscapeKey` | Cierra modales/menús con tecla Escape |
| `useClickOutside` | Cierra menús/desplegables al hacer clic fuera |

---

## 6. Utilidades de accesibilidad — `src/lib/accessibility.ts`

- `announce(message)` — anuncia mensajes a lectores de pantalla (WCAG 2.1 AA, `aria-live="polite"`).
- `vibrate(pattern)` — vibración háptica para confirmar acciones (si `navigator.vibrate` existe).
- `getRpeEmoji(rpe)` — mapa RPE 1–10 → emoji + etiqueta (es) + clases de color (verde→rojo). Fallback al nivel 5.

---

## 7. Tipos — `src/types/models.ts`

Tipos centrales compartidos por todo el frontend:

- **Enums/tipos unión:** `Role`, `FitnessLevel`, `Goal`, `MedicalRestriction`, `Equipment`, `InsightType`, `AlertType`, `AlertSeverity`, `RiskTrafficLight`.
- **Auth/User:** `User`, `RegisterPayload`, `LoginPayload`, `AuthResponse`, `RoutineOverride`.
- **Rutina:** `RoutineExercise`, `DailyRoutine` (con `generated_by?: 'ollama' | 'fallback'`, `llm_available`, `llm_model`, `llm_error`), `WorkoutSet`, `TrackEntryPayload`.
- **Dashboard:** `ProgressData`, `AgentInsight`.
- **Hábitos:** `DailyHabits`.
- **Cuidador:** `CaregiverLink`, `CaregiverAlert`, `CaregiverReport`, `SeniorProgressResponse`.
- **Admin:** `AdminPatient` (semáforo `risk` green/amber/red, tendencia RPE).

---

## 8. Componentes — `src/components/`

### Compartidos (raíz)
- **`ProtectedRoute`** — guard de rutas: verifica sesión y rol (`requiredRole`); si no hay usuario redirige a `/`; opción `useLayout={false}` para rutas sin layout.
- **`LoadingScreen`** — splash de carga (usado por `Suspense`).
- **`ErrorFallback`** — error boundary para fallos de render.
- **`EmptyState`** — estado vacío reutilizable para listas/paneles.
- **`Toast`** — notificaciones transitorias.

### `layouts/`
- **`SeniorLayout`**, **`CaregiverLayout`**, **`AdminLayout`** — estructuras de navegación por rol (navbar inferior en móvil, sidebar en escritorio, botón de menú hamburguesa).

### `ui/` (componentes de accesibilidad y dominio)
- **`AccessibleButton`** — botón con anuncios de screen reader y vibración.
- **`RpeScale`** — selector de esfuerzo percibido 1–10 (con `RpeScale.module.css`).
- **`RestTimer`** — cronómetro de descanso entre series (reiniciado y verificado previamente).
- **`TrafficLight`** — semáforo de riesgo (verde/ámbar/rojo) para el panel clínico.
- **`HamburgerMenu`** — menú móvil animado (`HamburgerMenu.module.css`).

### `contexts/AuthProvider.tsx`
- Provee el estado de sesión a toda la app: restaura la sesión al cargar, expone logout global y escucha el evento `sv:unauthorized`.

---

## 9. Features — `src/features/` (páginas por dominio)

- **`public/`** — `LandingPage`, `TermsPage`, `PrivacyPage`, `HelpPage`, `ProfilePage`, `NotFoundPage`.
- **`auth/`** — `RoleSelectPage` (elección senior/cuidador/admin), `LoginPage`, `RegisterPage`.
- **`senior/`** — `DailyRoutinePage` (generación de rutina con IA; muestra el origen `generated_by` — Ollama o plantilla de respaldo — y usa el `RestTimer`), `HabitsPage` (agua y sueño, con registro offline), `ProgressPage` (gráficas recharts y calendario), `HealthProfileOnboarding` (formulario react-hook-form + zod del perfil de salud).
- **`caregiver/`** — `CaregiverDashboard`, `CaregiverAlertsPage`, `CaregiverReportsPage`, `SeniorView` (vista de un senior enlazado).
- **`admin/`** — `AdminDashboard` (panel clínico con semáforo de riesgo, KPIs y tabla de pacientes).

---

## 10. Tests del frontend (`src/**/__tests__` + `src/test/setup.ts`)

- Configurado en `vite.config.ts` con **Vitest + happy-dom**.
- `src/test/setup.ts` — setup global (`@testing-library/jest-dom`, mocks de APIs del navegador).
- Cobertura actual: `components/ui` (AccessibleButton, RpeScale, TrafficLight), `EmptyState`, `features/auth/LoginPage`, `features/senior/HabitsPage`, `services` (api, auth).

> Nota: el comando `npm test` presenta un error ambiental de binding nativo de Vitest 4 (@rolldown) en este equipo; el build (`npm run build`) y el type-check sí pasan. Ejecutar `npm run build` para validar el frontend.
