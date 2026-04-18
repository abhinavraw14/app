from fastapi import FastAPI, UploadFile, File
import pandas as pd

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Backend is running"}

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        with open("temp.csv", "wb") as f:
            f.write(contents)

        df = pd.read_csv("temp.csv")

        columns = df.columns.tolist()

        if len(columns) < 2:
            return {"error": "Need at least 2 columns"}

        x_col = columns[0]
        y_col = columns[1]

        # Ensure numeric conversion (important 🔥)
        df[x_col] = pd.to_numeric(df[x_col], errors='coerce')
        df[y_col] = pd.to_numeric(df[y_col], errors='coerce')

        # Drop invalid rows
        df = df.dropna(subset=[x_col, y_col])

        # =========================
        # ✅ BAR CHART
        # =========================
        bar_data = []
        for _, row in df.iterrows():
            bar_data.append({
                "name": str(int(row[x_col])) if row[x_col].is_integer() else str(row[x_col]),
                "value": float(row[y_col])
            })

        # =========================
        # ✅ SCATTER PLOT
        # =========================
        scatter_data = []
        for _, row in df.iterrows():
            scatter_data.append({
                "x": float(row[x_col]),
                "y": float(row[y_col])
            })

        # =========================
        # ✅ LINE CHART
        # =========================
        line_data = []
        df_sorted = df.sort_values(by=x_col)

        for _, row in df_sorted.iterrows():
            line_data.append({
                "x": float(row[x_col]),
                "y": float(row[y_col])
            })

        # =========================
        # ✅ FINAL RESPONSE
        # =========================
        return {
            "columns": columns,
            "x_col": x_col,
            "y_col": y_col,
            "bar_chart": bar_data,
            "scatter_chart": scatter_data,
            "line_chart": line_data
        }

    except Exception as e:
        return {"error": str(e)}