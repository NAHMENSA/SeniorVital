"""Microservicio de autenticación y perfiles de usuario.

Gestiona el registro, inicio de sesión, actualización de perfiles
y vinculación entre seniors y cuidadores mediante JWT y bcrypt.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import asyncpg
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
from contextlib import asynccontextmanager
from passlib.hash import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta, date

from seniorvital_shared import get_pool, HealthProfile, init_pool, close_pool, init_db

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALG = "HS256"
ACCESS_EXPIRY = timedelta(minutes=15)
REFRESH_EXPIRY = timedelta(days=30)

security = HTTPBearer()


def create_access_token(user_id: str) -> str:
    """Genera un token JWT de acceso corto (15 min).

    :param user_id: Identificador único del usuario.
    :return: Token JWT codificado.
    """
    payload = {"sub": user_id, "type": "access", "exp": datetime.utcnow() + ACCESS_EXPIRY}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def create_refresh_token(user_id: str) -> str:
    """Genera un token JWT de refresco largo (30 días).

    :param user_id: Identificador único del usuario.
    :return: Token JWT codificado.
    """
    payload = {"sub": user_id, "type": "refresh", "exp": datetime.utcnow() + REFRESH_EXPIRY}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verifica y decodifica un token JWT.

    :param credentials: Credenciales Bearer extraídas del header.
    :raises HTTPException 401: Si el token es inválido o expiró.
    :return: Payload decodificado del token.
    """
    try:
        return jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALG])
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc



async def get_current_user(payload: dict = Depends(verify_token)) -> dict:
    """Obtiene el usuario autenticado desde la base de datos.

    :param payload: Payload del JWT con el campo 'sub' como ID.
    :raises HTTPException 404: Si el usuario no existe.
    :return: Diccionario con los datos del usuario.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", int(payload["sub"]))
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        return dict(row)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida del servicio: inicializa y cierra el pool de conexiones.

    Crea todas las tablas requeridas si no existen, garantizando que el
    esquema de base de datos coincida con lo que los endpoints esperan.
    """
    await init_pool(owner="auth")
    await init_db()
    yield
    await close_pool(owner="auth")


app = FastAPI(
    title="Auth Profile Service",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"},
    )


class RegisterRequest(BaseModel):
    """Datos necesarios para registrar un nuevo usuario."""
    email: EmailStr
    password: str
    role: str = "senior"
    profile: Optional[dict] = None
    nombre_senior: Optional[str] = None
    nombre_cuidador: Optional[str] = None
    health_profile: Optional[dict] = None


class LoginRequest(BaseModel):
    """Credenciales para iniciar sesión."""
    email: EmailStr
    password: str


class ProfileUpdate(BaseModel):
    """Datos para actualizar el perfil de salud."""
    profile: dict
    health_profile: Optional[dict] = None
    preferences: Optional[dict] = None


class RefreshRequest(BaseModel):
    """Solicitud para refrescar un token de acceso."""
    refresh_token: str


class LinkCaregiverRequest(BaseModel):
    """Email del cuidador a vincular con un senior."""
    caregiver_email: EmailStr


class AdminRoutineOverride(BaseModel):
    """Anulación manual de rutina por administrador."""
    custom_routine_override: Optional[dict] = None


@app.post("/auth/register")
async def register(req: RegisterRequest):
    """Registra un nuevo usuario en el sistema.

    Valida el rol, el perfil de salud y hashea la contraseña con bcrypt.

    :param req: Datos de registro (email, password, role, profile opcional).
    :raises HTTPException 400: Si el rol no es válido o el email ya existe.
    :return: ID, email y rol del usuario creado.
    """
    if req.role not in ("senior", "caregiver", "admin"):
        raise HTTPException(status_code=400, detail="Rol no permitido")
    hp = req.health_profile or req.profile
    if hp:
        HealthProfile(**hp)
    if req.role == "senior" and not req.nombre_senior:
        raise HTTPException(status_code=400, detail="nombre_senior requerido para senior")
    if req.role == "caregiver" and not req.nombre_cuidador:
        raise HTTPException(status_code=400, detail="nombre_cuidador requerido para caregiver")
    pool = await get_pool()
    async with pool.acquire() as conn:
        existing = await conn.fetchrow("SELECT id FROM users WHERE email = $1", req.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email ya registrado")
        hashed = bcrypt.hash(req.password)
        row = await conn.fetchrow(
            """INSERT INTO users (email, role, profile, health_profile, password, nombre_senior, nombre_cuidador)
               VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id""",
            req.email,
            req.role,
            json.dumps(hp or {}),
            json.dumps(hp or {}),
            hashed,
            req.nombre_senior,
            req.nombre_cuidador,
        )
    return {"id": str(row["id"]), "email": req.email, "role": req.role,
            "nombre_senior": req.nombre_senior, "nombre_cuidador": req.nombre_cuidador}


@app.post("/auth/login")
async def login(req: LoginRequest):
    """Autentica un usuario y devuelve un par de tokens JWT (access + refresh).

    :param req: Credenciales (email y password).
    :raises HTTPException 401: Si las credenciales son inválidas.
    :return: Token de acceso y token de refresco.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE email = $1", req.email)
        if not row:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        try:
            password_valid = bcrypt.verify(req.password, row["password"])
        except Exception:
            password_valid = False
        if not password_valid:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        user_id = str(row["id"])
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }


@app.post("/auth/refresh")
async def refresh(req: RefreshRequest):
    """Refresca un token de acceso usando un refresh token válido.

    :param req: Refresh token.
    :raises HTTPException 401: Si el refresh token es inválido o expiró.
    :return: Nuevo par de tokens (access + refresh).
    """
    try:
        payload = jwt.decode(req.refresh_token, JWT_SECRET, algorithms=[JWT_ALG])
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid refresh token") from exc

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Token is not a refresh token")

    user_id = payload["sub"]
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@app.get("/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    """Obtiene el perfil del usuario autenticado.

    :param user: Usuario autenticado (inyectado por dependencia).
    :return: Datos del perfil del usuario.
    """
    return {
        "id": str(user["id"]),
        "email": user["email"],
        "role": user["role"],
        "profile": user.get("profile"),
        "health_profile": user.get("health_profile"),
        "nombre_senior": user.get("nombre_senior"),
        "nombre_cuidador": user.get("nombre_cuidador"),
        "is_active": user.get("is_active", True),
        "created_at": str(user["created_at"]) if user.get("created_at") else None,
        "updated_at": str(user["updated_at"]) if user.get("updated_at") else None,
        "custom_routine_override": user.get("custom_routine_override"),
        "linked_senior_id": str(user["linked_senior_id"]) if user.get("linked_senior_id") else None,
        "preferences": user.get("preferences"),
    }


@app.put("/auth/profile")
async def update_profile(req: ProfileUpdate, user: dict = Depends(get_current_user)):
    """Actualiza el perfil de salud del usuario autenticado.

    Solo seniors y administradores pueden actualizar su perfil.

    :param req: Nuevo perfil de salud.
    :param user: Usuario autenticado.
    :raises HTTPException 403: Si el rol no tiene permisos.
    :return: Confirmación de actualización.
    """
    if user["role"] not in ("senior", "admin"):
        raise HTTPException(status_code=403, detail="Only senior or admin can update profile")
    hp = req.health_profile or req.profile
    HealthProfile(**hp)
    pool = await get_pool()
    async with pool.acquire() as conn:
        update_fields = {"profile": json.dumps(hp), "health_profile": json.dumps(hp)}
        if req.preferences is not None:
            update_fields["preferences"] = json.dumps(req.preferences)
        set_clause = ", ".join(f"{k} = ${i+1}" for i, k in enumerate(update_fields))
        values = list(update_fields.values()) + [user["id"]]
        await conn.execute(
            f"UPDATE users SET {set_clause} WHERE id = ${len(update_fields)+1}",
            *values,
        )
    return {"detail": "Profile updated"}


@app.post("/auth/link-caregiver")
async def link_caregiver(req: LinkCaregiverRequest, user: dict = Depends(get_current_user)):
    """Vincula un cuidador a un senior autenticado.

    :param req: Email del cuidador a vincular.
    :param user: Senior autenticado.
    :raises HTTPException 403: Si el usuario no es senior.
    :raises HTTPException 404: Si el cuidador no existe.
    :raises HTTPException 400: Si ya hay 3 cuidadores o el cuidador ya está vinculado.
    :return: Confirmación de vinculación.
    """
    if user["role"] != "senior":
        raise HTTPException(status_code=403, detail="Only seniors can link caregivers")
    pool = await get_pool()
    async with pool.acquire() as conn:
        caregiver = await conn.fetchrow(
            "SELECT id FROM users WHERE email = $1 AND role = 'caregiver'", req.caregiver_email
        )
        if not caregiver:
            raise HTTPException(status_code=404, detail="Caregiver not found")
        linked_count = await conn.fetchval(
            "SELECT COUNT(*) FROM users WHERE linked_senior_id = $1 AND role = 'caregiver'",
            user["id"],
        )
        if linked_count >= 3:
            raise HTTPException(status_code=400, detail="Senior already linked to max 3 caregivers")
        existing_link = await conn.fetchval(
            "SELECT linked_senior_id FROM users WHERE id = $1", caregiver["id"]
        )
        if existing_link:
            raise HTTPException(status_code=400, detail="Caregiver already linked to a senior")
        await conn.execute(
            "UPDATE users SET linked_senior_id = $1 WHERE id = $2",
            user["id"],
            caregiver["id"],
        )
    return {"detail": "Caregiver linked successfully"}


class LinkSeniorRequest(BaseModel):
    """Email del senior a vincular con un cuidador."""
    senior_email: EmailStr


@app.get("/caregiver/seniors")
async def get_caregiver_seniors(user: dict = Depends(get_current_user)):
    """Obtiene la lista de seniors vinculados al cuidador autenticado.

    :param user: Cuidador autenticado.
    :raises HTTPException 403: Si el usuario no es cuidador.
    :return: Lista de seniors vinculados con su información básica.
    """
    if user["role"] != "caregiver":
        raise HTTPException(status_code=403, detail="Only caregivers can view linked seniors")
    pool = await get_pool()
    async with pool.acquire() as conn:
        seniors = await conn.fetch(
            """SELECT u.id, u.email, u.nombre_senior, u.profile, u.health_profile
               FROM users u
               WHERE u.id = $1 AND u.role = 'senior'""",
            user.get("linked_senior_id"),
        )
        return [
            {
                "id": str(s["id"]),
                "email": s["email"],
                "senior_name": s.get("nombre_senior"),
                "senior_user_id": str(s["id"]),
            }
            for s in seniors
        ]


@app.post("/caregiver/link")
async def caregiver_link_senior(req: LinkSeniorRequest, user: dict = Depends(get_current_user)):
    """Vincula un senior a un cuidador autenticado.

    :param req: Email del senior a vincular.
    :param user: Cuidador autenticado.
    :raises HTTPException 403: Si el usuario no es cuidador.
    :raises HTTPException 404: Si el senior no existe.
    :raises HTTPException 400: Si el senior ya tiene 3 cuidadores o el cuidador ya está vinculado.
    :return: Confirmación de vinculación.
    """
    if user["role"] != "caregiver":
        raise HTTPException(status_code=403, detail="Only caregivers can link seniors")
    pool = await get_pool()
    async with pool.acquire() as conn:
        senior = await conn.fetchrow(
            "SELECT id FROM users WHERE email = $1 AND role = 'senior'", req.senior_email
        )
        if not senior:
            raise HTTPException(status_code=404, detail="Senior not found")
        # Verificar si el cuidador ya está vinculado a otro senior
        if user.get("linked_senior_id"):
            raise HTTPException(status_code=400, detail="Caregiver already linked to a senior")
        # Verificar si el senior ya tiene 3 cuidadores
        linked_count = await conn.fetchval(
            "SELECT COUNT(*) FROM users WHERE linked_senior_id = $1 AND role = 'caregiver'",
            senior["id"],
        )
        if linked_count >= 3:
            raise HTTPException(status_code=400, detail="Senior already has max 3 caregivers")
        # Vincular el cuidador al senior
        await conn.execute(
            "UPDATE users SET linked_senior_id = $1 WHERE id = $2",
            senior["id"],
            user["id"],
        )
    return {"detail": "Senior linked successfully"}


@app.get("/caregiver/alerts")
async def get_caregiver_alerts(user: dict = Depends(get_current_user)):
    """Obtiene las alertas de los seniors vinculados al cuidador autenticado.

    Incluye alertas de fatiga alta, inactividad y otros eventos.

    :param user: Cuidador autenticado.
    :raises HTTPException 403: Si el usuario no es cuidador.
    :return: Lista de alertas ordenadas por fecha descendente.
    """
    if user["role"] != "caregiver":
        raise HTTPException(status_code=403, detail="Only caregivers can view alerts")
    
    senior_id = user.get("linked_senior_id")
    if not senior_id:
        return []
    
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Obtener nombre del senior
        senior = await conn.fetchrow(
            "SELECT nombre_senior FROM users WHERE id = $1",
            senior_id
        )
        senior_name = senior["nombre_senior"] if senior else "Paciente"
        
        # Obtener alertas de fatiga alta (RPE >= 8) de los últimos 7 días
        alerts = []
        fatigue_records = await conn.fetch(
            """SELECT t.id, t.rpe, t.completed_at, t.exercise_id
               FROM tracking t
               WHERE t.user_id = $1 
               AND t.rpe >= 8
               AND t.completed_at >= NOW() - INTERVAL '7 days'
               ORDER BY t.completed_at DESC
               LIMIT 10""",
            senior_id
        )
        
        for record in fatigue_records:
            alerts.append({
                "id": f"fatigue-{record['id']}",
                "type": "fatigue",
                "severity": "high" if record["rpe"] >= 9 else "medium",
                "title": f"Fatiga alta detectada (RPE: {record['rpe']})",
                "message": f"El paciente reportó un nivel de esfuerzo de {record['rpe']}/10. Verifica su bienestar.",
                "senior_name": senior_name,
                "senior_id": str(senior_id),
                "created_at": record["completed_at"].isoformat(),
                "read": False
            })
        
        # Obtener alertas de inactividad (sin actividad en los últimos 3 días)
        last_activity = await conn.fetchval(
            """SELECT MAX(completed_at)
               FROM tracking
               WHERE user_id = $1""",
            senior_id
        )
        
        if last_activity:
            # Manejar compatibilidad de zonas horarias
            now = datetime.utcnow()
            # Si last_activity tiene zona horaria, convertirla a naive
            if hasattr(last_activity, 'tzinfo') and last_activity.tzinfo is not None:
                last_activity = last_activity.replace(tzinfo=None)
            
            days_inactive = (now - last_activity).days
            if days_inactive >= 3:
                severity = "high" if days_inactive >= 7 else "medium" if days_inactive >= 5 else "low"
                alerts.append({
                    "id": f"inactivity-{senior_id}",
                    "type": "inactivity",
                    "severity": severity,
                    "title": f"Inactividad detectada ({days_inactive} días)",
                    "message": f"El paciente no ha registrado actividad desde hace {days_inactive} días. Contacta para verificar su estado.",
                    "senior_name": senior_name,
                    "senior_id": str(senior_id),
                    "created_at": last_activity.isoformat(),
                    "read": False
                })
        
        # Ordenar por fecha descendente
        alerts.sort(key=lambda x: x["created_at"], reverse=True)
        
        return alerts


@app.get("/caregiver/reports")
async def get_caregiver_reports(user: dict = Depends(get_current_user)):
    """Obtiene los reportes de progreso de los seniors vinculados al cuidador autenticado.

    :param user: Cuidador autenticado.
    :raises HTTPException 403: Si el usuario no es cuidador.
    :return: Lista de reportes de los últimos 30 días.
    """
    if user["role"] != "caregiver":
        raise HTTPException(status_code=403, detail="Only caregivers can view reports")
    
    senior_id = user.get("linked_senior_id")
    if not senior_id:
        return []
    
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Obtener nombre del senior
        senior = await conn.fetchrow(
            "SELECT nombre_senior FROM users WHERE id = $1",
            senior_id
        )
        senior_name = senior["nombre_senior"] if senior else "Paciente"
        
        # Obtener estadísticas de los últimos 30 días
        period_start = datetime.utcnow() - timedelta(days=30)
        period_end = datetime.utcnow()
        
        # Total de sesiones completadas
        sessions_completed = await conn.fetchval(
            """SELECT COUNT(DISTINCT completed_at::date)
               FROM tracking
               WHERE user_id = $1
               AND completed_at >= $2""",
            senior_id,
            period_start
        )
        
        # RPE promedio
        avg_rpe = await conn.fetchval(
            """SELECT AVG(rpe)
               FROM tracking
               WHERE user_id = $1
               AND completed_at >= $2
               AND rpe IS NOT NULL""",
            senior_id,
            period_start
        )
        
        # Racha actual
        today = date.today()
        streak_days = 0
        check = today
        while True:
            day_count = await conn.fetchval(
                "SELECT COUNT(*) FROM tracking WHERE user_id = $1 AND completed_at::date = $2",
                senior_id,
                check
            )
            if day_count and day_count > 0:
                streak_days += 1
                check -= timedelta(days=1)
            else:
                break
        
        # Generar recomendaciones basadas en los datos
        recommendations = []
        if sessions_completed and sessions_completed < 10:
            recommendations.append("Intenta aumentar la frecuencia de ejercicios a 3-4 veces por semana.")
        if avg_rpe and avg_rpe > 7:
            recommendations.append("El esfuerzo promedio es alto. Considera reducir la intensidad.")
        if streak_days < 3:
            recommendations.append("Mantén una rutina consistente para mejores resultados.")
        if not recommendations:
            recommendations.append("¡Excelente progreso! Continúa con la rutina actual.")
        
        report = {
            "id": f"report-{senior_id}-{period_start.strftime('%Y%m%d')}",
            "senior_id": str(senior_id),
            "senior_name": senior_name,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "sessions_completed": sessions_completed or 0,
            "avg_rpe": round(avg_rpe, 1) if avg_rpe else 0,
            "streak_days": streak_days,
            "recommendations": recommendations,
            "created_at": period_end.isoformat()
        }
        
        return [report]


@app.get("/caregiver/senior/{senior_id}/progress")
async def get_caregiver_senior_progress(senior_id: str, user: dict = Depends(get_current_user)):
    """Obtiene el progreso detallado de un senior específico vinculado al cuidador.

    :param senior_id: ID del senior.
    :param user: Cuidador autenticado.
    :raises HTTPException 403: Si el usuario no es cuidador o el senior no está vinculado.
    :return: Progreso detallado del senior.
    """
    if user["role"] != "caregiver":
        raise HTTPException(status_code=403, detail="Only caregivers can view senior progress")
    
    # Verificar que el senior está vinculado al cuidador
    if user.get("linked_senior_id") != int(senior_id):
        raise HTTPException(status_code=403, detail="Senior not linked to this caregiver")
    
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Obtener nombre del senior
        senior = await conn.fetchrow(
            "SELECT nombre_senior FROM users WHERE id = $1",
            int(senior_id)
        )
        senior_name = senior["nombre_senior"] if senior else "Paciente"
        
        # Obtener progreso (similar a /dashboard/progress)
        week_ago = date.today() - timedelta(days=7)
        rows = await conn.fetch(
            """SELECT completed_at::date as day, SUM(reps) as total_reps,
                AVG(rpe) as avg_rpe
                FROM tracking
                WHERE user_id = $1 AND completed_at >= $2
                GROUP BY completed_at::date
                ORDER BY day""",
            int(senior_id),
            week_ago,
        )
        
        calendar = {}
        rpe_trend = []
        for r in rows:
            day_str = r["day"].isoformat()
            avg_rpe = round(float(r["avg_rpe"]), 1) if r["avg_rpe"] else 0
            calendar[day_str] = {"completed": True, "rpe_avg": avg_rpe}
            rpe_trend.append({"date": day_str, "avg_rpe": avg_rpe})
        
        today = date.today()
        streak_days = 0
        check = today
        while True:
            day_rows = await conn.fetchval(
                "SELECT COUNT(*) FROM tracking WHERE user_id = $1 AND completed_at::date = $2",
                int(senior_id),
                check,
            )
            if day_rows and day_rows > 0:
                streak_days += 1
                check -= timedelta(days=1)
            else:
                break
        
        total_sessions = await conn.fetchval(
            "SELECT COUNT(DISTINCT completed_at::date) FROM tracking WHERE user_id = $1 AND completed_at >= $2",
            int(senior_id),
            week_ago,
        )
        
        progress = {
            "sessions_this_week": total_sessions or 0,
            "current_streak": streak_days,
            "total_sessions": total_sessions or 0,
            "rpe_trend": rpe_trend,
            "calendar": calendar,
        }
        
        return {
            "senior_name": senior_name,
            "progress": progress
        }


@app.get("/admin/users")
async def get_admin_users(user: dict = Depends(get_current_user)):
    """Obtiene la lista de usuarios seniors con información de riesgo para el panel de administración.

    :param user: Usuario autenticado (debe ser admin).
    :raises HTTPException 403: Si el usuario no es administrador.
    :return: Lista de pacientes seniors con métricas de riesgo.
    """
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view all users")
    pool = await get_pool()
    async with pool.acquire() as conn:
        seniors = await conn.fetch(
            "SELECT u.id, u.email, u.nombre_senior, u.health_profile, u.created_at "
            "FROM users u WHERE u.role = 'senior' ORDER BY u.nombre_senior"
        )
        result = []
        for s in seniors:
            health = s.get("health_profile")
            if isinstance(health, str):
                try:
                    health = json.loads(health)
                except (json.JSONDecodeError, TypeError):
                    health = {}
            elif health is None:
                health = {}

            total_sessions = await conn.fetchval(
                "SELECT COUNT(*) FROM tracking WHERE user_id = $1", s["id"]
            )
            last_session = await conn.fetchval(
                "SELECT MAX(completed_at) FROM tracking WHERE user_id = $1", s["id"]
            )
            avg_rpe = await conn.fetchval(
                "SELECT AVG(rpe) FROM tracking WHERE user_id = $1 AND rpe IS NOT NULL", s["id"]
            )

            if avg_rpe is None:
                rpe_trend = "stable"
            elif avg_rpe >= 8:
                rpe_trend = "declining"
            elif avg_rpe >= 5:
                rpe_trend = "stable"
            else:
                rpe_trend = "improving"

            if avg_rpe is None:
                risk = "green"
            elif avg_rpe >= 8.5:
                risk = "red"
            elif avg_rpe >= 6.5:
                risk = "amber"
            else:
                risk = "green"

            result.append({
                "id": str(s["id"]),
                "nombre_senior": s.get("nombre_senior"),
                "email": s["email"],
                "risk": risk,
                "last_session": last_session.isoformat() if last_session else None,
                "streak": 0,
                "rpe_trend": rpe_trend,
                "total_sessions": total_sessions or 0,
            })
        return result


@app.put("/admin/users/{user_id}/routine-override")
async def admin_routine_override(user_id: str, req: AdminRoutineOverride, user: dict = Depends(get_current_user)):
    """Actualiza la anulación de rutina de un usuario (solo admin).

    :param user_id: ID del usuario a modificar.
    :param req: Nueva anulación de rutina.
    :param user: Usuario autenticado (debe ser admin).
    :raises HTTPException 403: Si el usuario no es administrador.
    :raises HTTPException 404: Si el usuario objetivo no existe.
    :return: Confirmación de actualización.
    """
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can set routine overrides")
    pool = await get_pool()
    async with pool.acquire() as conn:
        existing = await conn.fetchrow("SELECT id FROM users WHERE id = $1", int(user_id))
        if not existing:
            raise HTTPException(status_code=404, detail="User not found")

        await conn.execute(
            "INSERT INTO admin_logs (admin_user_id, action, target_user_id, details) VALUES ($1, $2, $3, $4)",
            user["id"],
            "routine_override",
            int(user_id),
            json.dumps(req.custom_routine_override or {}),
        )

        if req.custom_routine_override is not None:
            await conn.execute(
                "UPDATE users SET custom_routine_override = $1 WHERE id = $2",
                json.dumps(req.custom_routine_override),
                int(user_id),
            )
        return {"detail": "Routine override updated"}
