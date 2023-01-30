import uvicorn as uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date
import pulp

app = FastAPI()


class DailyDecision(BaseModel):
    water_sold: float
    electricity_sold: float
    hydrogen_produced: float
    profit: float


class DailyData(BaseModel):
    water_quantity: float
    electricity_quantity: float
    electricity_price_sale: float
    hydrogen_price_sale: float
    water_price_sale: float
    dailyDecision: DailyDecision



dataBase = {}


@app.post("/create-daily-data/{data_id}")
def create_daily_data(data_id: int, daily_data: DailyData):
    daily_data_id = data_id
    if daily_data_id in dataBase:
        return {"Error": "Data already added for today"}
    dataBase[daily_data_id] = daily_data
    #x_h = pulp.LpVariable("x_hydrogen_kg", lowBound=0.0, upBound=1000.0)
    x_h2o = pulp.LpVariable("x_water_litres", lowBound=0.0, upBound=min(dataBase[daily_data_id].water_quantity, 9000))
    x_e = pulp.LpVariable("x_electricity_kwh", lowBound=0.0, upBound=min(dataBase[daily_data_id].electricity_quantity, 53000))
    max_profit = pulp.LpProblem("maximize_profit", pulp.LpMaximize)
    max_profit += dataBase[daily_data_id].hydrogen_price_sale / 9 * x_h2o + dataBase[daily_data_id].water_price_sale * (dataBase[daily_data_id].water_quantity - x_h2o) + dataBase[daily_data_id].electricity_price_sale * (dataBase[daily_data_id].electricity_quantity - x_e)
    max_profit += x_h2o <= min(dataBase[daily_data_id].water_quantity, 9000)
    max_profit += 53*x_h2o == 9*x_e
    max_profit += x_e <= min(dataBase[daily_data_id].electricity_quantity, 53000)
    max_profit.solve()
    dataBase[daily_data_id].dailyDecision.hydrogen_produced = x_h2o.varValue / 9
    dataBase[daily_data_id].dailyDecision.water_sold = dataBase[daily_data_id].water_quantity - x_h2o.varValue
    dataBase[daily_data_id].dailyDecision.electricity_sold = dataBase[daily_data_id].electricity_quantity - x_e.varValue
    dataBase[daily_data_id].dailyDecision.profit = pulp.value(max_profit.objective)

    return dataBase[daily_data_id]


@app.get("/get-daily-data/{daily_data_id}")
def get_daily_data(daily_data_id: int):
    if daily_data_id not in dataBase:
        return {"Error": "no match found"}
    return dataBase[daily_data_id]


@app.get("/get-daily-decision/{daily_data_id}")
def get_daily_decision(daily_data_id: int):
    if daily_data_id not in dataBase:
        return {"Error": "no match found"}
    return dataBase[daily_data_id].dailyDecision


@app.get("/")
def home():
    return {"company": "enexflow"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)