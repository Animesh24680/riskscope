import numpy as np
from app.database import SessionLocal, Prediction
from sqlalchemy import func


def compute_psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
    eps = 1e-6
    expected_perc = np.histogram(expected, bins=bins, range=(0, 1))[0] / len(expected)
    actual_perc = np.histogram(actual, bins=bins, range=(0, 1))[0] / len(actual)
    expected_perc = np.clip(expected_perc, eps, 1)
    actual_perc = np.clip(actual_perc, eps, 1)
    psi = np.sum((actual_perc - expected_perc) * np.log(actual_perc / expected_perc))
    return round(float(psi), 4)


def detect_drift(window: int = 100, baseline_size: int = 500) -> dict:
    db = SessionLocal()
    try:
        total = db.query(Prediction).count()
        if total < baseline_size + window:
            return {
                "drift_detected": False,
                "psi": 0.0,
                "message": f"Insufficient data ({total} records, need {baseline_size + window})",
                "total_predictions": total,
            }

        all_records = (
            db.query(Prediction.risk_probability, Prediction.is_delinquent)
            .order_by(Prediction.created_at.asc())
            .all()
        )

        baseline_probs = np.array([r.risk_probability for r in all_records[:-window]])
        window_probs = np.array([r.risk_probability for r in all_records[-window:]])

        psi = compute_psi(baseline_probs, window_probs)

        baseline_dq = np.mean([r.is_delinquent for r in all_records[:-window]])
        window_dq = np.mean([r.is_delinquent for r in all_records[-window:]])

        drift_detected = psi > 0.1 or abs(window_dq - baseline_dq) > 0.1

        return {
            "drift_detected": drift_detected,
            "psi": psi,
            "baseline_mean_risk": round(float(np.mean(baseline_probs)), 4),
            "window_mean_risk": round(float(np.mean(window_probs)), 4),
            "baseline_delinquency_rate": round(float(baseline_dq), 4),
            "window_delinquency_rate": round(float(window_dq), 4),
            "message": "Drift detected" if drift_detected else "No significant drift",
            "total_predictions": total,
        }
    finally:
        db.close()
