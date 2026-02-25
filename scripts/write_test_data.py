import os
import time
import random
from datetime import datetime, timezone

from influxdb_client import InfluxDBClient, Point, WritePrecision

INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "super-secret-admin-token")
INFLUX_ORG = os.getenv("INFLUX_ORG", "pmd-org")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "robot")


def main():
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = client.write_api()

    axes = ["J1", "J2", "J3", "J4", "J5", "J6"]

    print("Writing test telemetry to InfluxDB... Ctrl+C to stop.")
    while True:
        axis = random.choice(axes)
        position = random.uniform(-3.14, 3.14)
        velocity = random.uniform(-2.0, 2.0)
        torque = random.uniform(10.0, 120.0)

        point = (
            Point("telemetry")
            .tag("axis", axis)
            .field("position", float(position))
            .field("velocity", float(velocity))
            .field("torque", float(torque))
            .time(datetime.now(timezone.utc), WritePrecision.NS)
        )

        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
        time.sleep(1)


if __name__ == "__main__":
    main()