import cv2
import pandas as pd
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "arial.ttf"
FONT_SIZE = 24

clicked_point = None
mouse_x, mouse_y = 0, 0


def mouse_callback(event, x, y, flags, param):
    global clicked_point, mouse_x, mouse_y

    mouse_x, mouse_y = x, y

    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_point = (x, y)


def draw_text_cv(image, text, position):
    img_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)

    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    draw.text(position, text, font=font, fill=(0, 255, 0))

    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)


def read_csv(csv_file):
    encodings = ["utf-8-sig", "cp1251", "utf-16", "latin1"]

    for enc in encodings:
        try:
            return pd.read_csv(csv_file, sep=";", encoding=enc)
        except Exception:
            pass

    return pd.read_csv(csv_file, sep=";", encoding="latin1", errors="replace")


def fill_coordinates(csv_file, image_file):
    global clicked_point, mouse_x, mouse_y

    print(f"\nОбработка файла: {csv_file}")

    df = read_csv(csv_file)
    df.columns = df.columns.str.strip()

    image = cv2.imread(image_file)
    if image is None:
        raise Exception(f"Не удалось открыть изображение: {image_file}")

    if "pos_width" not in df.columns:
        df["pos_width"] = 0
    if "pos_heigth" not in df.columns:
        df["pos_heigth"] = 0

    cv2.namedWindow("Image")
    cv2.setMouseCallback("Image", mouse_callback)

    for i, row in df.iterrows():
        name = str(row["name"])

        # --- просто информирование ---
        if (
            not pd.isna(row["pos_width"]) and
            not pd.isna(row["pos_heigth"]) and
            float(row["pos_width"]) != 0 and
            float(row["pos_heigth"]) != 0
        ):
            print(f"{name}: координаты уже заданы ({row['pos_width']}, {row['pos_heigth']})")
            continue

        while True:
            display = image.copy()

            display = draw_text_cv(
                display,
                f"{name} | ЛКМ: точка | SPACE: пропуск | ESC: выход",
                (10, 20)
            )

            display = draw_text_cv(
                display,
                f"X: {mouse_x}  Y: {mouse_y}",
                (10, image.shape[0] - 40)
            )

            cv2.imshow("Image", display)
            key = cv2.waitKey(1)

            # клик
            if clicked_point is not None:
                x, y = clicked_point
                print(f"{name}: x={x}, y={y}")

                df.at[i, "pos_width"] = x
                df.at[i, "pos_heigth"] = y

                clicked_point = None
                break

            # пропуск
            if key == 32:
                print(f"{name}: пропущено")
                break

            # выход
            if key == 27:
                print("Прервано пользователем")
                cv2.destroyAllWindows()
                exit()

    cv2.destroyAllWindows()

    df.to_csv(csv_file, sep=";", index=False, encoding="utf-8-sig")
    return df


def convert_df(df):
    df = df.fillna(0)
    df["source_type"] = pd.to_numeric(df["source_type"], errors="coerce")
    df = df.dropna(subset=["source_type"])

    return [
        {
            "canid": int(r["canid"]),
            "data_num": int(r["data_num"]),
            "max": float(r["max"]),
            "min": float(r["min"]),
            "name": str(r["name"]),
            "pos_heigth": int(r["pos_heigth"]),
            "pos_width": int(r["pos_width"]),
            "pre_max": float(r["pre_max"]),
            "pre_min": float(r["pre_min"]),
            "source_type": int(r["source_type"]),
            "subtype": int(r["subtype"])
        }
        for _, r in df.iterrows()
    ]


if __name__ == "__main__":

    df_ka = fill_coordinates("TERMU_KA.csv", "TERMU_KA.png")
    df_opn = fill_coordinates("TERMU_OPN.csv", "TERMU_OPN.png")

    result = {
        "optional_views": {
            "TERMU_KA": convert_df(df_ka),
            "TERMU_OPN": convert_df(df_opn)
        }
    }

    with open("system_thermal.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    print("\nГотово: system_thermal.json создан")