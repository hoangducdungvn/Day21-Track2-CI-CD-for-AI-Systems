from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
import joblib
import os

app = FastAPI()

GCS_BUCKET = os.environ.get("GCS_BUCKET", "my-mlops-lab-bucket")
GCS_MODEL_KEY = "models/latest/model.pkl"
MODEL_PATH = os.path.expanduser("~/models/model.pkl")


def download_model():
    """
    Tai file model.pkl tu S3 ve may khi server khoi dong.
    """
    if not os.path.exists(os.path.dirname(MODEL_PATH)):
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    
    # Kiem tra xem da co model chua, neu co thi bo qua de test cuc bo
    # Trong moi truong that tren VM, service se luon chay lai download nay.
    try:
        s3 = boto3.client('s3')
        s3.download_file(GCS_BUCKET, GCS_MODEL_KEY, MODEL_PATH)
        print("Model da duoc tai xuong tu AWS S3.")
    except Exception as e:
        print(f"Loi khi tai model tu S3: {e}")
        # Neu file da ton tai cuc bo thi bo qua loi (huu ich cho viec test tren may)
        if not os.path.exists(MODEL_PATH):
            raise e

download_model()
model = joblib.load(MODEL_PATH)


class PredictRequest(BaseModel):
    features: list[float]


@app.get("/health")
def health():
    """
    Endpoint kiem tra suc khoe server.
    """
    return {"status": "ok"}


@app.post("/predict")
def predict(req: PredictRequest):
    """
    Endpoint suy luan chinh.
    """
    if len(req.features) != 12:
        raise HTTPException(status_code=400, detail="Expected 12 features (wine quality)")
        
    pred = model.predict([req.features])[0]
    
    labels = {0: "thap", 1: "trung_binh", 2: "cao"}
    label = labels.get(int(pred), "unknown")
    
    return {"prediction": int(pred), "label": label}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
