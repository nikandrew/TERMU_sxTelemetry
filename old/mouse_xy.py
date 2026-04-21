import cv2

# Загружаем изображение
image = cv2.imread("image.png")

# Копия для отрисовки
display = image.copy()

def mouse_callback(event, x, y, flags, param):
    global display
    
    if event == cv2.EVENT_MOUSEMOVE:
        display = image.copy()
        
        text = f"X: {x}, Y: {y}"
        
        # Рисуем текст под изображением (внизу)
        cv2.putText(display, text, (10, image.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

# Создаем окно и назначаем обработчик
cv2.namedWindow("Image")
cv2.setMouseCallback("Image", mouse_callback)

while True:
    cv2.imshow("Image", display)
    
    if cv2.waitKey(1) & 0xFF == 27:  # ESC для выхода
        break

cv2.destroyAllWindows()