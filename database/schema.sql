-- EdgeHealth Guardian Network — Database Schema (PostgreSQL)
-- Note: raw biometric streams stay on-device. This DB stores only
-- derived summaries, predictions, alerts, and metadata synced from
-- the edge hub for the caregiver dashboard.

CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name       VARCHAR(120) NOT NULL,
    role            VARCHAR(20) NOT NULL CHECK (role IN ('patient','caregiver','clinician','admin')),
    email           VARCHAR(160) UNIQUE NOT NULL,
    phone           VARCHAR(30),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE devices (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_type     VARCHAR(20) NOT NULL CHECK (device_type IN ('wearable','hub')),
    device_serial   VARCHAR(80) UNIQUE NOT NULL,
    firmware_version VARCHAR(20),
    last_seen_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE health_records (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recorded_at     TIMESTAMPTZ NOT NULL,
    heart_rate_avg  NUMERIC(5,2),
    spo2_avg        NUMERIC(5,2),
    resp_rate_avg   NUMERIC(5,2),
    tremor_score    NUMERIC(5,2),
    activity_level  NUMERIC(5,2),
    sleep_stage     VARCHAR(20),
    data_quality    NUMERIC(3,2),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE digital_twin (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    baseline_hr     NUMERIC(5,2),
    baseline_spo2   NUMERIC(5,2),
    baseline_resp   NUMERIC(5,2),
    baseline_tremor NUMERIC(5,2),
    twin_state      JSONB NOT NULL,      -- rolling state-space model parameters
    last_updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    twin_version    INT NOT NULL DEFAULT 1
);

CREATE TABLE predictions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    predicted_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    condition       VARCHAR(60) NOT NULL,      -- e.g. 'respiratory_distress','fall_risk','cardiac_abnormality'
    risk_score      NUMERIC(5,2) NOT NULL CHECK (risk_score BETWEEN 0 AND 100),
    horizon_hours   NUMERIC(4,1) NOT NULL,
    contributing_agents JSONB,               -- which agents voted and their individual scores
    explanation     TEXT
);

CREATE TABLE alerts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    prediction_id   UUID REFERENCES predictions(id),
    tier            VARCHAR(10) NOT NULL CHECK (tier IN ('low','medium','high','critical')),
    channel         VARCHAR(20) NOT NULL CHECK (channel IN ('dashboard','push','sms','ble_mesh','emergency_call')),
    message         TEXT NOT NULL,
    acknowledged_at TIMESTAMPTZ,
    escalated       BOOLEAN NOT NULL DEFAULT false,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE agents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(40) NOT NULL UNIQUE,   -- sensor, validation, prediction, risk_assessment, medical_knowledge, alert, emergency, digital_twin
    description     TEXT,
    version         VARCHAR(20)
);

CREATE TABLE reports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    generated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    period_start    DATE NOT NULL,
    period_end      DATE NOT NULL,
    summary         TEXT,
    file_url        TEXT
);

CREATE INDEX idx_health_records_patient_time ON health_records (patient_id, recorded_at DESC);
CREATE INDEX idx_predictions_patient_time ON predictions (patient_id, predicted_at DESC);
CREATE INDEX idx_alerts_patient_time ON alerts (patient_id, created_at DESC);
