# api_server.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal
import uvicorn

app = FastAPI(title="Health Prediction API")

class PatientInput(BaseModel):
    glucose: float
    haemoglobin: float
    cholesterol: float

class PredictionOutput(BaseModel):
    risk: Literal["Low", "Medium", "High"]
    message: str

@app.post("/predict", response_model=PredictionOutput)
def predict(input_data: PatientInput):
    score = 0

    if input_data.glucose > 140:
        score += 1
    if input_data.haemoglobin < 12:
        score += 1
    if input_data.cholesterol > 240:
        score += 1

    if score >= 2:
        risk = "High"
        message = "High risk of metabolic / cardiovascular issues based on current lab values."
    elif score == 1:
        risk = "Medium"
        message = "Moderate health risk detected; follow-up evaluation recommended."
    else:
        risk = "Low"
        message = "Low risk based on current lab values."

    return PredictionOutput(risk=risk, message=message)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)