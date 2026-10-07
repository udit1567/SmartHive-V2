"""Dev-only: seed 100 realistic sensor rows for one user.

Usage (from backend/, venv active):

    python seed_data.py uditmaurya2003@gmail.com

Pin layout (matches firmwared-hardware/esp32-environ.ino):
    D1 = temperature (C)        ~26.2
    D2 = humidity (%)           ~55, peaks near 77
    D3 = MQ-135 raw ADC         air-quality raw (0-4095)
    D4 = MQ-135 air quality %   AQI level 0-100
    D5 = MQ-135 voltage (V)
    D6 = MQ-2 raw ADC           gas/smoke raw (0-4095)
    D7 = MQ-2 gas %             0-100
    D8 = MQ-2 voltage (V)
"""

import math
import random
import sys
from datetime import timedelta

from app import create_app
from app.extensions import db
from app.models import Data, User, get_ist_time

ADC_MAX = 4095.0
ADC_VREF = 3.3
N = 100
INTERVAL_MIN = 10          # one reading every 10 minutes
SEED = 42


def adc_from_percent(pct):
    return int(round(pct / 100.0 * ADC_MAX))


def voltage_from_adc(adc):
    return round(adc / ADC_MAX * ADC_VREF, 3)


def main():
    if len(sys.argv) != 2:
        print("Usage: python seed_data.py <email>")
        raise SystemExit(1)

    email = sys.argv[1]
    random.seed(SEED)

    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"No user with email {email!r}")
            raise SystemExit(1)

        now = get_ist_time()
        rows = []

        for i in range(N):
            # oldest first; last row is the most recent
            ts = now - timedelta(minutes=INTERVAL_MIN * (N - 1 - i))

            # daily cycle (0..1) so temp/humidity drift believably
            phase = (i / N) * 2 * math.pi

            # D1 temperature: centred on 26.2, gentle swing + noise
            temp = 26.2 + 0.9 * math.sin(phase) + random.uniform(-0.4, 0.4)

            # D2 humidity: ~55 average, inversely tied to temp, peaks ~77
            humidity = 61 - 7 * math.sin(phase) + random.uniform(-3, 3)
            if random.random() < 0.08:          # occasional humid spike
                humidity += random.uniform(8, 16)
            humidity = max(42, min(77, humidity))

            # D3/D4/D5 MQ-135 air quality: mostly GOOD/MODERATE
            aqi_pct = 22 + 8 * math.sin(phase + 1) + random.uniform(-4, 6)
            aqi_pct = max(8, min(72, aqi_pct))
            mq135_raw = adc_from_percent(aqi_pct)
            mq135_v = voltage_from_adc(mq135_raw)

            # D6/D7/D8 MQ-2 gas/smoke: low, lightly correlated with AQI
            gas_pct = 15 + 0.5 * (aqi_pct - 22) + random.uniform(-3, 5)
            gas_pct = max(5, min(60, gas_pct))
            mq2_raw = adc_from_percent(gas_pct)
            mq2_v = voltage_from_adc(mq2_raw)

            rows.append(
                Data(
                    timestamp=ts,
                    D1=round(temp, 2),
                    D2=round(humidity, 1),
                    D3=float(mq135_raw),
                    D4=round(aqi_pct, 1),
                    D5=mq135_v,
                    D6=float(mq2_raw),
                    D7=round(gas_pct, 1),
                    D8=mq2_v,
                    user_id=user.id,
                )
            )

        db.session.bulk_save_objects(rows)
        db.session.commit()

        print(f"Inserted {len(rows)} rows for {user.email} (id={user.id}).")
        last = rows[-1]
        print(
            "Latest -> D1 %.2fC  D2 %.1f%%  D4 AQI %.1f%%  D7 gas %.1f%%"
            % (last.D1, last.D2, last.D4, last.D7)
        )


if __name__ == "__main__":
    main()
