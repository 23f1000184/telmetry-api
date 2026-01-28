import os
import json
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# ✅ Perfect CORS (Fixes Access-Control-Allow-Origin issue)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],   # includes OPTIONS + POST
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(BASE_DIR, "q-vercel-latency.json")


class RequestBody(BaseModel):
    regions: list[str]
    threshold_ms: int


# ✅ Handle browser preflight request
@app.options("/api")
def options_api():
    return {}


@app.post("/api")
def analyze(body: RequestBody):

    # Load telemetry file
    with open(DATA_FILE) as f:
        telemetry = json.load(f)

    output = {}

    for region in body.regions:
        rows = [r for r in telemetry if r["region"] == region]

        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime_pct"] for r in rows]

        avg_latency = float(np.mean(latencies))
        p95_latency = float(np.percentile(latencies, 95))
        avg_uptime = float(np.mean(uptimes))
        breaches = int(sum(x > body.threshold_ms for x in latencies))

        output[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches,
        }

    return output