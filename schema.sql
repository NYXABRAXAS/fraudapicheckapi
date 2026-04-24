CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'analyst',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS applications (
    id SERIAL PRIMARY KEY,
    customer_id VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    pan VARCHAR(20) NOT NULL,
    mobile VARCHAR(20) NOT NULL,
    email VARCHAR(255) NOT NULL,
    ip_address VARCHAR(64) NOT NULL,
    income DOUBLE PRECISION NOT NULL,
    submitted_at TIMESTAMP NOT NULL,
    device_fingerprint VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'RECEIVED',
    source_system VARCHAR(100) NOT NULL DEFAULT 'LOS',
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fraud_history (
    id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL,
    customer_id VARCHAR(100) NOT NULL,
    fraud_score DOUBLE PRECISION NOT NULL,
    risk_level VARCHAR(50) NOT NULL,
    decision VARCHAR(50) NOT NULL,
    flags JSONB NOT NULL DEFAULT '[]'::jsonb,
    explanation JSONB NOT NULL DEFAULT '[]'::jsonb,
    evaluated_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS device_logs (
    id SERIAL PRIMARY KEY,
    customer_id VARCHAR(100) NOT NULL,
    application_id INTEGER NOT NULL,
    device_fingerprint VARCHAR(255) NOT NULL,
    ip_address VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_applications_pan_created_at ON applications (pan, created_at);
CREATE INDEX IF NOT EXISTS ix_applications_mobile_created_at ON applications (mobile, created_at);
CREATE INDEX IF NOT EXISTS ix_applications_ip_created_at ON applications (ip_address, created_at);
CREATE INDEX IF NOT EXISTS ix_applications_customer_created_at ON applications (customer_id, created_at);
CREATE INDEX IF NOT EXISTS ix_fraud_history_customer_created_at ON fraud_history (customer_id, created_at);
CREATE INDEX IF NOT EXISTS ix_fraud_history_risk_level_created_at ON fraud_history (risk_level, created_at);
CREATE INDEX IF NOT EXISTS ix_device_logs_fingerprint_created_at ON device_logs (device_fingerprint, created_at);
CREATE INDEX IF NOT EXISTS ix_device_logs_customer_created_at ON device_logs (customer_id, created_at);
