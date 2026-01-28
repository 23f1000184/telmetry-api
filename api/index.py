import os
import json
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import JSONResponse

app = FastAPI()

# ✅ Enable CORS correctly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(BASE_DIR, "q-vercel-latency.json")


class RequestBody(BaseModel):
    regions: list[str]
    threshold_ms: int


@app.post("/api")
def analyze(body: RequestBody):

    with open(DATA_FILE) as f:
        telemetry = json.load(f)

    output = {}

    for region in body.regions:
        rows = [r for r in telemetry if r["region"] == region]

        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime_pct"] for r in rows]

        output[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": int(sum(x > body.threshold_ms for x in latencies)),
        }

    # ✅ Force header in POST response
    return JSONResponse(
        content=output,
        headers={"Access-Control-Allow-Origin": "*"}
    )
