"""Quick integration checks."""
import httpx

BASE = "http://localhost:8000"

print("=== Quick Integration Check ===")

r = httpx.get(f"{BASE}/", timeout=5)
print(f"[1] Frontend HTML: {r.status_code} size={len(r.text)}b")

r = httpx.get(f"{BASE}/habits", timeout=5)
print(f"[2] SPA route /habits: {r.status_code} ok={'root' in r.text}")

r = httpx.get(f"{BASE}/progress", timeout=5)
print(f"[3] SPA route /progress: {r.status_code} ok={'root' in r.text}")

r = httpx.get(f"{BASE}/assets/index-ad04ce5b.css", timeout=5)
print(f"[4] CSS asset: {r.status_code} size={len(r.text)}b")

r = httpx.post(f"{BASE}/auth/register", json={"email":"newquick@test.com","password":"test123","role":"senior"}, timeout=5)
uid = r.json().get("id","N/A")[:8] if r.status_code == 200 else str(r.json())
print(f"[5] Register via gateway: {r.status_code} id={uid}")

r = httpx.post(f"{BASE}/auth/login", json={"email":"newquick@test.com","password":"test123"}, timeout=5)
data = r.json()
print(f"[6] Login via gateway: {r.status_code} token={'access_token' in data}")

r = httpx.get(f"{BASE}/catalog/exercises", timeout=5)
print(f"[7] API proxy GET: {r.status_code} count={len(r.json())}")

r = httpx.get(f"{BASE}/docs", timeout=5)
print(f"[8] Docs: {r.status_code}")

r = httpx.post(f"{BASE}/auth/login", json={"email":"newquick@test.com","password":"test123"}, timeout=5)
token = r.json().get("access_token", "")
r = httpx.get(f"{BASE}/auth/me", headers={"Authorization": f"Bearer {token}"}, timeout=5)
print(f"[9] GET /auth/me: {r.status_code} email={r.json().get('email','N/A')}")

print("=== Done ===")
