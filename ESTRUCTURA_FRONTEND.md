# Estructura del Frontend — SeniorVital

> Aplicación SPA de gestión de bienestar para adultos mayores. Construida con **React 18**, **Vite 4**, **Tailwind CSS 3.3** (tema Material Design 3), **react-router-dom v6** e iconos **Material Symbols**. Consume las APIs REST del backend SeniorVital (gateway en puerto 8000) y se comunica opcionalmente con **Ollama** para generación de rutinas con IA. Diseño mobile-first con navegación inferior en móvil y sidebar en escritorio.

---

## Árbol de Directorios (primer y segundo nivel)

```
seniorvital-frontend/
├── index.html
├── package.json
├── package-lock.json
├── postcss.config.js
├── tailwind.config.js
├── vite.config.js
├── dist/
│   ├── index.html
│   └── assets/
│       ├── index-5b3c4525.js
│       └── index-b4028b0b.css
└── src/
    ├── main.jsx
    ├── App.jsx
    ├── index.css
    ├── components/
    │   ├── TopAppBar.jsx
    │   ├── BottomNavBar.jsx
    │   └── AdminSidebar.jsx
    └── pages/
        ├── Home.jsx
        ├── Habits.jsx
        ├── Video.jsx
        ├── Progress.jsx
        └── AdminDashboard.jsx
```

---

## 1. Raíz del proyecto — `seniorvital-frontend/`

**Funcionalidad:** Contiene la configuración global del build tooling, las dependencias, los estilos base y el punto de entrada HTML. Es el directorio raíz desde el que se ejecutan todos los comandos (`npm run dev`, `npm run build`).

**Uso y aplicabilidad:** Capa de infraestructura y tooling. No contiene lógica de negocio. Cada archivo aquí define cómo se compila, empaqueta o sirve la aplicación.

### Archivos

#### `index.html`
- **Funcionalidad:** Punto de entrada HTML. Lenguaje `es`. Incluye Google Fonts (**Lexend** pesos 400, 600, 700), Google Material Symbols Outlined, y un favicon SVG inline del emoji 👵. El body tiene clases Tailwind `bg-background text-on-background min-h-screen`. El div `#root` recibe la app React renderizada por `src/main.jsx`.
- **Conexiones:** Importa `/src/main.jsx` como módulo ES. Es procesado por Vite durante desarrollo y build.

#### `package.json`
- **Funcionalidad:** Define metadatos del proyecto (`name: "seniorvital-frontend"`, `version: "1.0.0"`, `type: "module"`), scripts (`dev`, `build`, `preview`), y dependencias:
  - **Producción:** `react@^18.2.0`, `react-dom@^18.2.0`, `react-router-dom@^6.11.2`.
  - **Desarrollo:** `@vitejs/plugin-react`, `tailwindcss`, `postcss`, `autoprefixer`, `vite`, `@types/react`, `@types/react-dom`.
- **Conexiones:** `npm install` descarga todas las dependencias aquí listadas. Los scripts `dev`/`build` ejecutan Vite.

#### `package-lock.json`
- **Funcionalidad:** Lockfile generado automáticamente por npm. Bloquea versiones exactas de todas las dependencias transitivas.
- **Conexiones:** No se modifica manualmente. Generado por `npm install`.

#### `postcss.config.js`
- **Funcionalidad:** Configura PostCSS con dos plugins: `tailwindcss` y `autoprefixer`.
- **Conexiones:** Vite invoca PostCSS automáticamente durante el build. Tailwind procesa las directivas `@tailwind` en `src/index.css`.

#### `tailwind.config.js`
- **Funcionalidad:** Configuración completa del tema Tailwind. Define:
  - **Content paths:** `./index.html`, `./src/**/*.{js,ts,jsx,tsx}`
  - **Paleta de colores personalizada (57 tokens):** Sigue el sistema Material Design 3 con colores `primary` (#041627, azul marino oscuro), `secondary` (#9f4021, naranja óxido), `tertiary` (#001a07, verde oscuro), `error`, `surface` y sus variantes (container, fixed, dim, bright, inverse).
  - **Espaciado semántico:** `stack-md: 24px`, `stack-sm: 12px`, `touch-target-min: 48px`, `gutter: 24px`, `margin-mobile: 20px`, `margin-desktop: 64px`.
  - **Border radius:** `lg: 0.5rem`, `xl: 0.75rem`, `full: 9999px`.
  - **Font family:** `lexend: ["Lexend", "sans-serif"]`.
- **Conexiones:** Todos los componentes y pages usan estas clases de utilidad Tailwind.

#### `vite.config.js`
- **Funcionalidad:** Configura Vite con el plugin `@vitejs/plugin-react` para transformación JSX.
- **Conexiones:** Integra React con Vite (Fast Refresh en desarrollo, optimización de build en producción).

#### `dist/`
- **Funcionalidad:** Directorio de salida del build de producción (`npm run build`). Contiene `index.html`, `assets/index-*.js` y `assets/index-*.css` minificados y hasheados.
- **Conexiones:** Generado por Vite. Servible estáticamente desde cualquier servidor web o CDN.

---

## 2. `src/`

**Funcionalidad:** Contiene todo el código fuente de la aplicación: el punto de entrada React, el enrutador, los estilos globales, los componentes reutilizables y las páginas que conforman la UI.

**Uso y aplicabilidad:** Capa de presentación y lógica de UI. Organizado en `components/` (piezas reutilizables) y `pages/` (vistas completas asociadas a rutas).

### Archivos raíz

#### `src/main.jsx`
- **Funcionalidad:** Punto de entrada de React. Monta la aplicación en `#root` usando `ReactDOM.createRoot`. Renderiza `<App />` envuelto en `<React.StrictMode>`.
- **Conexiones:** Importa `App` desde `./App.jsx` y los estilos globales desde `./index.css`. Es referenciado por `index.html`.

#### `src/App.jsx`
- **Funcionalidad:** Componente raíz de la aplicación. Define el sistema de enrutamiento con `BrowserRouter` de react-router-dom. Declara 5 rutas:
  | Ruta | Componente | Descripción |
  |------|-----------|-------------|
  | `/` | `Home` | Página principal con generación de rutina IA |
  | `/habits` | `Habits` | Seguimiento de hábitos diarios |
  | `/video` | `Video` | Catálogo de videos de ejercicio |
  | `/progress` | `Progress` | Calendario de progreso |
  | `/admin` | `AdminDashboard` | Panel de administración clínica |
  Renderiza un `<Routes>` con 5 `<Route>` anidados.
- **Conexiones:** Importa los 5 componentes de `pages/`. Si se añaden nuevas rutas, se declaran aquí. Es el componente articulador de toda la navegación.

#### `src/index.css`
- **Funcionalidad:** Estilos globales. Contiene las directivas `@tailwind base`, `@tailwind components`, `@tailwind utilities`. Define:
  - Fuente base: `font-family: 'Lexend', sans-serif`.
  - Altura mínima: `100vh` / `100dvh`.
  - Sin tap highlight en móvil: `-webkit-tap-highlight-color: transparent`.
  - Estilo base de Material Symbols: `font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24`.
  - Clase `.fill`: activa el relleno del icono (`'FILL' 1`).
- **Conexiones:** Importado por `main.jsx`. Afecta globalmente a todos los componentes. La clase `.fill` es usada por `BottomNavBar.jsx` para el icono activo.

---

## 3. `src/components/`

**Funcionalidad:** Componentes React reutilizables que aparecen en múltiples páginas o proveen estructura de layout común.

**Uso y aplicabilidad:** Capa de UI compartida. Cada componente es independiente y recibe sus datos via props.

### Archivos

#### `src/components/TopAppBar.jsx`
- **Funcionalidad:** Barra superior fija (`top-0`, `z-50`) con altura `min-h-[72px]` y borde inferior. Recibe dos props:
  - `title` (string, default `"SeniorVital"`): texto del título renderizado con `font-headline-lg text-headline-lg text-secondary font-extrabold`.
  - `showBack` (boolean, default `false`): si es `true`, muestra un botón de flecha hacia atrás que ejecuta `useNavigate().go(-1)`. Si es `false`, muestra un icono de menú hamburguesa no interactivo.
  - Lado derecho: un div spacer de balance.
- **Conexiones:** Usa `useNavigate` de `react-router-dom`. Importado por las páginas que necesitan navegación superior. Recibe props desde cada página.

#### `src/components/BottomNavBar.jsx`
- **Funcionalidad:** Barra de navegación inferior fija para móvil. Oculto en `md:` y superior (`hidden md:hidden`). Contiene 4 enlaces:
  | Ruta | Icono Material | Etiqueta |
  |------|---------------|----------|
  | `/` | `home` | Inicio |
  | `/habits` | `rebase_edit` | Hábitos |
  | `/video` | `play_circle` | Vídeo |
  | `/progress` | `insights` | Progreso |
  Cada elemento mide `min-w-[64px] min-h-[64px]` con `rounded-xl`. El enlace activo (detectado via `useLocation()`) obtiene `bg-secondary-container text-on-secondary-container font-bold` y el icono con clase `.fill`.
- **Conexiones:** Usa `Link` y `useLocation` de `react-router-dom`. Se renderiza en las páginas que no son `/admin`. El estado activo se calcula comparando `location.pathname` con la ruta de cada ítem.

#### `src/components/AdminSidebar.jsx`
- **Funcionalidad:** Sidebar de administración para escritorio. Visible solo en `md:` y superior (`hidden md:flex`). Fijo a la izquierda (`w-64`, altura completa, `z-40`). Contiene:
  - **Header:** Logotipo "SeniorVital" + subtítulo "Panel de Administrador".
  - **Navegación:**
    - `/admin` → "Panel Clínico" (icono `dashboard`). Activo si `location.pathname === "/admin"` (fondo `bg-primary-container`).
    - `/` → "Vista Móvil (Demo)" (icono `phone_iphone`).
  - **Footer:** `/` → "Cerrar Sesión" (icono `logout`).
  - Usa `Link` de react-router-dom.
- **Conexiones:** Usa `useLocation` y `Link` de `react-router-dom`. Renderizado únicamente por `AdminDashboard.jsx`. Los colores del sidebar usan las variables `bg-surface-container-high`, `text-primary`, `bg-primary-container`, etc.

---

## 4. `src/pages/`

**Funcionalidad:** Componentes que representan vistas completas de la aplicación, cada uno asociado a una ruta en `App.jsx`. Contienen la lógica de UI, estado local y datos mockeados.

**Uso y aplicabilidad:** Capa de vistas. Cada página es autocontenida: maneja su propio estado con hooks de React (`useState`, `useEffect`) y renderiza componentes compartidos (`TopAppBar`, `BottomNavBar`, `AdminSidebar`).

### Archivos

#### `src/pages/Home.jsx`
- **Funcionalidad:** Página principal ("Mi Rutina con IA"). Estado:
  - `btnState`: `"idle" | "generating" | "ready"` — controla el botón principal de generación de rutina.
  - `showRoutine`: boolean — muestra/oculta la tarjeta de rutina.
  - **Flujo:** Click en "Generar Mi Rutina" → estado `"generating"` con spinner → 1.5s después → estado `"ready"` + tarjeta de rutina visible → 2.5s después → reset a `"idle"`.
  - **Botón principal:** 3 estados visuales:
    - `idle`: `smart_toy` icon, `bg-secondary text-on-secondary`.
    - `generating`: spinner rotando (`refresh` con animación CSS), deshabilitado.
    - `ready`: `check_circle` icon, `bg-tertiary-fixed text-on-tertiary-fixed`.
  - **Tarjeta de rutina** (`max-w-3xl`): 3 actividades con texto personalizado (simulado):
    - Mañana (icono `sunny`): "8 min de estiramientos sentados en silla y respiración profunda."
    - Tarde (icono `directions_walk`): "Caminata suave de 15 minutos en el jardín de la residencia."
    - Hidratación (icono `water_drop`): "Beber 2 vasos extras de agua antes de la cena."
  - Cuando la rutina está oculta, los mismos ítems aparecen con texto genérico y `opacity-70`.
  - Incluye cita motivacional y enlace a `/admin`.
  - Renderiza `TopAppBar` (sin back) y `BottomNavBar`.
- **Conexiones:** No realiza llamadas API reales — el flujo de IA es simulado con `setTimeout`. Renderiza `TopAppBar` y `BottomNavBar`. Los datos de rutina son strings hardcodeados. En una versión futura, el botón debería llamar a `POST /routines/generate` del backend.

#### `src/pages/Habits.jsx`
- **Funcionalidad:** Página de seguimiento de hábitos diarios. Estado:
  - `water` (number, default 4): contador de vasos de agua.
  - `walking` (number, default 15): minutos de caminata.
  - `medsTaken` (`null | true | false`): estado de medicación.
  - **Targetas de hábitos** en grid de 2 columnas:
    1. **Agua** (icono `water_drop`): botones +1/-1 con valor numérico centrado.
    2. **Caminata** (icono `directions_walk`): botones +5/-5, mismo layout.
    3. **Medicación** (icono `medication`, `md:col-span-2`): botones "Sí" / "No". 
       - "Sí" seleccionado: `bg-secondary text-on-secondary`.
       - "No" seleccionado: `bg-error text-on-error`.
  - **Mensaje empático** al pie:
    - Si `medsTaken === true && water >= 6 && walking >= 20`: "¡Impresionante! Has completado todos tus objetivos de hoy."
    - Caso contrario: "¡Lo estás haciendo genial hoy!" + "Cada pequeño paso cuenta para tu bienestar."
  - Renderiza `TopAppBar` (sin back) y `BottomNavBar`.
- **Conexiones:** Estado puramente local. No persiste datos. Renderiza componentes compartidos. En producción, debería sincronizar con `POST /tracking/record` o endpoints de hábitos.

#### `src/pages/Video.jsx`
- **Funcionalidad:** Página de catálogo de videos de ejercicio con reproductor simulado. Estado:
  - `activeVideo`: índice del video activo (0-3).
  - `isPlaying`: boolean.
  - `progress`: 0-100, simulado con `setInterval` de 500ms que incrementa en 1.
  - **PLAYLIST hardcodeada** (4 videos con thumbnails de Google):
    1. "Estiramientos Suaves de Mañana" (10 min)
    2. "Recetas Saludables para el Corazón" (15 min)
    3. "Respiración de Relajación" (8 min)
    4. "Básicos del Cuidado Articular" (12 min)
  - **Reproductor** (`aspect-video`): 
    - Thumbnail con overlay: cuando suena, `opacity-30 scale-105 blur-[2px]`.
    - Overlay de reproducción: título + barras de audio animadas.
    - Botón circular play/pause (`w-20 h-20`).
    - Barra de progreso inferior (full-width, `h-2`).
  - **Detalles:** título, badge de duración, descripción.
  - **Lista "Más Vídeos para Ti":** grid de 2 columnas con thumbnails, título truncado, descripción (`line-clamp-1`), badge de duración.
  - Renderiza `TopAppBar` (sin back) y `BottomNavBar`.
- **Conexiones:** No consume API real. Los thumbnails son URLs de Google (`https://www.gstatic.com/...`). En producción llamaría a `GET /catalog/exercises` del backend. El reproductor real debería reemplazar la simulación con un `<video>` HTML5 o YouTube embed.

#### `src/pages/Progress.jsx`
- **Funcionalidad:** Página de calendario de progreso mensual. Datos hardcodeados:
  - `MONTHS_DATA`: Octubre, Noviembre, Diciembre 2023. Octubre tiene 7 días de datos de ejemplo.
  - Estado: `monthIndex` (0-2), `selectedDay` (default 7).
  - **Calendario UI**:
    - Navegación mensual con flechas `chevron_left`/`chevron_right`.
    - Días de la semana: L, M, M, J, V, S, D.
    - Offset de inicio para alinear con el día de la semana correcto.
    - **Celdas de día** (`aspect-square`, `min-h-[64px]`):
      - Hoy: borde `border-primary` con fondo `bg-primary-fixed` y barra inferior de acento.
      - Días con datos: punto indicador coloreado.
      - Sin datos: `opacity-40 cursor-not-allowed`.
      - Seleccionado: `ring-4 ring-secondary/55`.
      - Todos los objetivos cumplidos: `bg-tertiary-fixed/30`.
    - **Leyenda:** punto verde = "Completado", barra naranja = "Hoy".
  - **Desglose del día** (3-columnas): agua (vasos), caminata (min), medicación (Tomada/No Tomada/Pendiente).
  - Renderiza `TopAppBar` (sin back) y `BottomNavBar`.
- **Conexiones:** Datos hardcodeados. Sin llamadas API. Renderiza componentes compartidos. En producción consumiría `GET /dashboard/progress/{user_id}` del backend.

#### `src/pages/AdminDashboard.jsx`
- **Funcionalidad:** Panel de administración clínica para escritorio. Datos hardcodeados:
  - `RESIDENTS_DATA`: 8 residentes con:
    - `stable` (3): Eleanor Rigby, Robert Jenkins, John Lennon
    - `observation` (2): Arthur Pendelton, Paul McCartney
    - `review` (1): Martha Stewart
    - `offline` (2): Gladys Cooper, Ringo Starr
  - Estado: `searchQuery`, `statusFilter` (`all|stable|observation|review|offline`), `currentPage` (paginación, 5 por página).
  - **Header:** "Seguimiento Clínico" + descripción del panel.
  - **Búsqueda:** Input de texto con icono `search`, filtra por nombre o unidad.
  - **Filtro de estado:** `<select>` dropdown.
  - **KPIs** (3-columnas):
    1. "Total Monitoreados" → 8.
    2. "Activos Hoy (24h)" → 6 (todos excepto offline).
    3. "Atención Sugerida" → 3 (review + observation), con acento visual.
  - **Tabla clínica** (`min-w-[700px]`):
    - Columnas: Nombre, Habitación/Unidad, Última Sincronización, Patrón de Estado, Acciones.
    - Badges de estado con puntos de color:
      - `stable`: verde, badge con borde verde.
      - `observation`: ámbar, badge neutral.
      - `review`: naranja, badge naranja + borde izquierdo naranja en la fila.
      - `offline`: gris, badge gris.
    - Filas en observación: fondo tintado claro.
    - Botón de acción: `chevron_right` → muestra `alert()` con el nombre del residente.
    - Estado vacío: "No se encontraron residentes..."
  - **Paginación:** 5 por página, botones anterior/siguiente.
  - No renderiza `BottomNavBar` (usa `AdminSidebar` en su lugar).
- **Conexiones:** Renderiza `AdminSidebar` en lugar de `BottomNavBar`. Datos hardcodeados. En producción consumiría `GET /dashboard/progress/{user_id}`, `GET /dashboard/insights/{user_id}`, y endpoints de administración. La tabla clínica se integraría con `GET /admin/residents` hipotético.
