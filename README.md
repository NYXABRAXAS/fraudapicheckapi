# Fraud Detection API

Real-time fraud scoring API for banking LOS integrations using FastAPI, PostgreSQL, Redis, and a configurable rule engine. The service is structured for microservice deployment and future ML augmentation.

## Architecture

```text
LOS / Channel App
        |
        v
 FastAPI API Layer
        |
        v
 FraudScoringService
        |
        +--> RuleEngine (JSON-configured modular rules)
        +--> Repositories (PostgreSQL)
        +--> Cache / Rate Limiter (Redis)
        +--> Audit Trail (fraud_history)
        +--> EventPublisher (Kafka-ready stub)
```

### Layers

- `app/api`: REST endpoints and request orchestration
- `app/services`: fraud scoring, audit logging, event publishing
- `app/services/rules`: modular fraud rules with weighted contributions
- `app/repositories`: data access layer
- `app/models`: persistence models
- `app/core`: config, security, cache, logging
- `app/middleware`: Redis-backed API rate limiting

## Features

- JWT-protected `POST /fraud-check`
- Rule-based explainable fraud scoring normalized to `0-100`
- Risk tiers: `LOW`, `MEDIUM`, `HIGH`
- Decisioning: `APPROVE`, `REVIEW`, `REJECT`
- Audit history with rule explanations
- JSON-based rule configuration in [app/core/rules.json](C:/Users/Lokesh/Desktop/fraudapi/app/core/rules.json)
- Redis-backed rate limiting with in-memory fallback for local/test resilience
- Kafka-ready publisher abstraction for future event streaming
- Clean schema and indexes for low-latency lookups

## Fraud Rules Included

- Duplicate PAN detection
- Duplicate mobile detection
- Velocity check across recent applications
- IP anomaly detection
- Temporary or synthetic email pattern risk
- Income inconsistency heuristic
- Device fingerprint placeholder logic

## Database Schema

Core tables:

- `users`: API users / analysts / system accounts
- `applications`: applicant submissions from LOS
- `fraud_history`: final scores, flags, explanations, decisions
- `device_logs`: reusable device telemetry

Detailed SQL is available at [scripts/schema.sql](C:/Users/Lokesh/Desktop/fraudapi/scripts/schema.sql).

## Run Instructions

### 1. Start infrastructure

```powershell
Copy-Item .env.example .env
docker compose up -d postgres redis
```

Optional Kafka:

```powershell
docker compose --profile kafka up -d kafka
```

### 2. Install dependencies

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Start the API

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

On startup the service creates tables and seeds a default admin user:

- Username: `admin`
- Password: `admin123`

Change this immediately in non-local environments.

If you are on Python `3.14`, this project already uses the newer `psycopg` driver to avoid `psycopg2` build issues.

## API Usage

### Get JWT token

```powershell
$tokenResponse = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/auth/token" -ContentType "application/x-www-form-urlencoded" -Body "username=admin&password=admin123"
$tokenResponse.access_token
```

### Fraud check request

```powershell
$token = "<PASTE_TOKEN>"
$body = @{
  customer_id = "LOS-90001"
  name = "Rahul Verma"
  pan = "ABCDE1234F"
  mobile = "9876543210"
  email = "rahul@mailinator.com"
  ip_address = "203.0.113.25"
  income = 3200000
  timestamp = "2026-04-24T09:30:00Z"
  device_fingerprint = "dfp-ios-001"
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri "http://localhost:8000/fraud-check" `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body $body
```

### Example response

```json
{
  "fraud_score": 73.53,
  "risk_level": "HIGH",
  "flags": [
    "PAN already used in previous applications",
    "Email pattern indicates temporary or synthetic identity risk",
    "Declared income is inconsistent with applicant profile heuristics"
  ],
  "decision": "REJECT",
  "explanations": [
    {
      "rule": "duplicate_pan",
      "triggered": true,
      "score": 30,
      "reason": "PAN already used in previous applications",
      "metadata": {
        "existing_applications": 2
      }
    }
  ]
}
```

## Performance and Security Notes

- Indexes target PAN, mobile, IP, customer, and device lookups to keep scoring fast.
- Logs avoid raw PAN/mobile exposure and persist only a hashed note token for correlation.
- Input validation is enforced with Pydantic.
- JWT secures operational endpoints.
- Rule configuration is externalized for safer tuning without code changes.
- The service is ML-ready because rules, scoring, persistence, and event publishing are decoupled.

## Testing

```powershell
pytest
```

Included tests:

- Unit tests for core rules
- API integration test for `/fraud-check`

## Future ML Extension Path

- Publish final decisions and features to Kafka for model training pipelines
- Add feature store reads before scoring
- Run hybrid scoring: `rules_score + ml_probability`
- Store model version and feature snapshot in `fraud_history`
