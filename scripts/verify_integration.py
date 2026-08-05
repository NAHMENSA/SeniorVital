"""Verify frontend-backend integration."""
import httpx

BASE = "http://localhost:8000"

print("=== Integration Verification ===\n")

# 1. Frontend served
r = httpx.get(f"{BASE}/", timeout=5)
print(f"[1] Frontend HTML: status={r.status_code} size={len(r.text)}b seniorvital={'SeniorVital' in r.text}")

# 2. SPA route fallback
r = httpx.get(f"{BASE}/habits", timeout=5)
print(f"[2] SPA route /habits: status={r.status_code} root={'root' in r.text}")

# 3. SPA route /progress
r = httpx.get(f"{BASE}/progress", timeout=5)
print(f"[3] SPA route /progress: status={r.status_code} root={'root' in r.text}")

# 4. SPA route /admin
r = httpx.get(f"{BASE}/admin", timeout=5)
print(f"[4] SPA route /admin: status={r.status_code} root={'root' in r.text}")

# 5. CSS asset
r = httpx.get(f"{BASE}/assets/index-ad04ce5b.css", timeout=5)
print(f"[5] CSS asset: status={r.status_code} size={len(r.text)}b")

# 6. JS asset
r = httpx.get(f"{BASE}/assets/index-5b3c4525.js", timeout=5)
print(f"[6] JS asset: status={r.status_code} size={len(r.text)}b")

# 7. API proxy POST (login)
r = httpx.post(f"{BASE}/auth/login", json={"email":"ollama_test@test.com","password":"test123"}, timeout=5)
has_token = "access_token" in r.json()
print(f"[7] API POST /auth/login: status={r.status_code} token={has_token}")

# 8. API proxy GET (catalog)
r = httpx.get(f"{BASE}/catalog/exercises", timeout=5)
print(f"[8] API GET /catalog/exercises: status={r.status_code} count={len(r.json())}")

# 9. API proxy GET (routines)
r = httpx.get(f"{BASE}/routines/today?user_id=nonexistent", timeout=5)
print(f"[9] API GET /routines/today: status={r.status_code}")

# 10. Docs still accessible
r = httpx.get(f"{BASE}/docs", timeout=5)
print(f"[10] Docs: status={r.status_code}")

# 11. Register + Login full flow via gateway
r = httpx.post(f"{BASE}/auth/register", json={"email":"final@test.com","password":"test123","role":"senior"}, timeout=5)
print(f"[11] Register via gateway: status={r.status_code} id={r.json().get('id','N/A')[:8] if r.status_code==200 else 'N/A'}")

r = httpx.post(f"{BASE}/auth/login", json={"email":"final@test.com","password":"test123"}, timeout=5)
print(f"[12] Login via gateway: status={r.status_code} token={'access_token' in r.json()}")

print("\n=== Summary ===")
