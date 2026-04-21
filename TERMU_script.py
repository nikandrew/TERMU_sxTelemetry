import cv2
import pandas as pd
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# --- Настройки шрифта ---
FONT_PATH = "arial.ttf"  # при необходимости укажи полный путь
FONT_SIZE = 24

clicked_point = None


def mouse_callback(event, x, y, flags, param):
    global clicked_point
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_point = (x, y)


def draw_text_cv(image, text, position=(10, 30)):
    """Отрисовка UTF-8 текста через PIL"""
    img_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)

    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    draw.text(position, text, font=font, fill=(0, 255, 0))

    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)


def fill_coordinates(csv_file, image_file):
    global clicked_point

    print(f"\nОбработка файла: {csv_file}")

    df = pd.read_csv(csv_file, sep=";", encoding="utf-8-sig")
    df.columns = df.columns.str.strip()

    image = cv2.imread(image_file)
    if image is None:
        raise Exception(f"Не удалось открыть изображение: {image_file}")

    cv2.namedWindow("Image")
    cv2.setMouseCallback("Image", mouse_callback)

    for i, row in df.iterrows():
        name = str(row["name"])

        while True:
            display = image.copy()

            display = draw_text_cv(
                display,
                f"Укажите точку: {name} (ЛКМ — выбрать, SPACE — пропустить, ESC — выход)",
                position=(10, 30)
            )

            cv2.imshow("Image", display)

            key = cv2.waitKey(1)

            # Клик мыши
            if clicked_point is not None:
                x, y = clicked_point
                print(f"{name}: x={x}, y={y}")

                df.at[i, "pos_width"] = x
                df.at[i, "pos_heigth"] = y

                clicked_point = None
                break

            # Пропуск строки
            if key == 32:  # SPACE
                print(f"{name}: пропущено")
                clicked_point = None
                break

            # Выход
            if key == 27:  # ESC
                print("Прервано пользователем")
                cv2.destroyAllWindows()
                exit()

    cv2.destroyAllWindows()

    # Сохраняем обновлённый CSV
    df.to_csv(csv_file, sep=";", index=False, encoding="utf-8-sig")
    return df


def convert_df(df):
    df = df.fillna(0)

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


if __name__ == "__main__":

    # --- 1. Заполнение координат ---
    df_ka = fill_coordinates("TERMU_KA.csv", "TERMU_KA.png")
    df_opn = fill_coordinates("TERMU_OPN.csv", "TERMU_OPN.png")

    # --- 2. Формирование JSON ---
    result = {
        "optional_views": {
            "TERMU_KA": convert_df(df_ka),
            "TERMU_OPN": convert_df(df_opn)
        }
    }

    with open("system_thermal.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    print("\nГотово: system_thermal.json создан")