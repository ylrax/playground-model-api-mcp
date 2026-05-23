from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd

import joblib

import os
print(os.getcwd())

app = FastAPI()

model_path = os.path.join(os.path.dirname(__file__), '..', 'modeling', 'model.joblib')
model_saved = joblib.load(model_path)


class Data(BaseModel):
    age: int
    sleep: float

@app.get("/status")
def status():
    return {"status": 200}


@app.post("/")
async def pred_endpoint(item:Data):

    load_pred = model_saved.predict(pd.DataFrame([[item.age, item.sleep]], columns=["Age", "Sleep Duration"]))


    return {"prediction": int(load_pred[0])}
