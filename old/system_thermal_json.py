import pandas as pd
import json


def load_file(filename):
    df = pd.read_csv(filename, sep=";", encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    df = df.fillna(0)

    def load_file(filename):
        print("Loading:", filename)
        df = pd.read_csv(filename, sep=";", encoding="utf-8-sig")
        print("Rows:", len(df))
        ...

    # очистка нечисловых значений
    df["source_type"] = pd.to_numeric(df["source_type"], errors="coerce")
    df = df.dropna(subset=["source_type"])

    items = []

    for _, row in df.iterrows():
        item = {
            "canid": int(row["canid"]),
            "data_num": int(row["data_num"]),
            "max": float(row["max"]),
            "min": float(row["min"]),
            "name": str(row["name"]),
            "pos_heigth": int(row["pos_heigth"]),
            "pos_width": int(row["pos_width"]),
            "pre_max": float(row["pre_max"]),
            "pre_min": float(row["pre_min"]),
            "source_type": int(row["source_type"]),
            "subtype": int(row["subtype"])
        }
        items.append(item)

    return items


result = {
    "optional_views": {
        "TERMU_KA": load_file("TERMU_KA.csv"),
        "TERMU_OPN": load_file("TERMU_OPN.csv")
    }
}

with open("system_thermal.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=4)