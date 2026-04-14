from fastapi import FastAPI, UploadFile, File
import pandas as pd

# Object creation for FastAPI class
app = FastAPI() # app -> object for class FastAPI

@app.get("/") # / -> home page
def home(): #home page
  return {"message: Backend is running"}

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        with open("temp.csv", "wb") as f:
            f.write(contents)

        df = pd.read_csv("temp.csv")

        # 👉 SIMPLE BAR CHART LOGIC
        # Take first column as category
        # Second column as values

        columns = df.columns.tolist()

        if len(columns) < 2:
            return {"error": "Need at least 2 columns"}

        x_col = columns[0]
        y_col = columns[1]

        # Convert to chart-friendly format
        chart_data = []

        for _, row in df.iterrows():
            chart_data.append({
                "name": str(row[x_col]),
                "value": float(row[y_col])
            })

        return {
            "columns": columns,
            "chart_data": chart_data,
            "x_col": x_col,
            "y_col": y_col
        }

    except Exception as e:
        return {"error": str(e)}

