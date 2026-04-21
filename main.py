from fastapi import FastAPI, UploadFile, File
import pandas as pd
import numpy as np

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

        # CLEAN DATA
        df[x_col] = pd.to_numeric(df[x_col], errors='coerce')
        df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
        df = df.dropna(subset=[x_col, y_col])

        #STATISTICS
        stats = {
            "mean": float(df[y_col].mean()),
            "median": float(df[y_col].median()),
            "min": float(df[y_col].min()),
            "max": float(df[y_col].max()),
            "std": float(df[y_col].std())
        }

        #CORRELATION
        correlation = float(df[x_col].corr(df[y_col]))

        # OUTLIER DETECTION (IQR)
        Q1 = df[y_col].quantile(0.25)
        Q3 = df[y_col].quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        df["is_outlier"] = (df[y_col] < lower) | (df[y_col] > upper)

        # BAR CHART
        bar_data = []
        for _, row in df.iterrows():
            bar_data.append({
                "name": str(int(row[x_col])) if row[x_col].is_integer() else str(row[x_col]),
                "value": float(row[y_col]),
                "is_outlier": bool(row["is_outlier"])
            })

        # SCATTER PLOT
        scatter_data = []
        for _, row in df.iterrows():
            scatter_data.append({
                "x": float(row[x_col]),
                "y": float(row[y_col]),
                "is_outlier": bool(row["is_outlier"])
            })

        # LINE CHART
        df_sorted = df.sort_values(by=x_col)

        line_data = []
        for _, row in df_sorted.iterrows():
            line_data.append({
                "x": float(row[x_col]),
                "y": float(row[y_col]),
                "is_outlier": bool(row["is_outlier"])
            })

        # HISTOGRAM
        counts, bin_edges = np.histogram(df[y_col], bins=10)

        histogram_data = []
        for i in range(len(counts)):
            histogram_data.append({
                "bin_start": float(bin_edges[i]),
                "bin_end": float(bin_edges[i+1]),
                "count": int(counts[i])
            })

        # BOX PLOT 
        box_plot = {
            "min": float(df[y_col].min()),
            "Q1": float(Q1),
            "median": float(df[y_col].median()),
            "Q3": float(Q3),
            "max": float(df[y_col].max())
        }

        # OUTLIERS
        outliers = df[df["is_outlier"]]

        outlier_points = []
        for _, row in outliers.iterrows():
            outlier_points.append({
                "x": float(row[x_col]),
                "y": float(row[y_col])
            })

        # FINAL 
        return {
            "columns": columns,
            "x_col": x_col,
            "y_col": y_col,

            "bar_chart": bar_data,
            "scatter_chart": scatter_data,
            "line_chart": line_data,

            "histogram": histogram_data,
            "box_plot": box_plot,

            "outliers": outlier_points,
            "outlier_bounds": {
                "lower": float(lower),
                "upper": float(upper)
            },

            "statistics": stats,
            "correlation": correlation
        }

    except Exception as e:
        return {"error": str(e)}