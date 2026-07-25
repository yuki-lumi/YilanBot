import time
import pyautogui
from math import sin, cos, atan
import cv2
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By


def main():
    driver = StartBot()
    frequency = 30

    # Game loop
    while True:
        image, contours = GetScreenshot(driver)
        grid, height, width = DetectZones(image=image, contours=contours)
        direction = CalculateVectors(grid=grid, height=height, width=width)
        MoveMouse(direction, height, width)
        Timer(frequency)


def CalculateVectors(grid, height, width):
    center = [(height // 2), (width // 2)]
    vectors = []
    for y in range(height):
        for x in range(width):
            if (grid[y][x] != 0):
                vectorb = np.array([])
                diff_y = abs(center[0] - y)
                diff_x = abs(center[1] - x)
                if (diff_y != 0):
                    degree = atan(diff_x / diff_y)
                    vectorb = np.append(vectorb, grid[y][x] * sin(degree) * np.sign(center[1] - x))
                    vectorb = np.append(vectorb, grid[y][x] * cos(degree) * np.sign(center[0] - y))
                    vectors.append(vectorb)
    return sum(vectors)


## Detects pull and push zones and saves it in a grid. Returns grid
def DetectZones(image, contours):
    center_threshold = 100
    pullce = 1
    pushce = -5
    width = image.shape[1]
    height = image.shape[0]
    grid = np.zeros((height, width))
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 600:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 3)
            grid[y][x] += pullce
        elif area > 1200:
            x, y, w, h = cv2.boundingRect(cnt)
            if abs(width // 2 - x) > center_threshold and abs(height // 2 - y) > center_threshold:
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 3)
                grid[y][x] += pushce
    return grid, height, width


## Gets webdriver as input. Takes screenshot and locates enemies and food. Returns contours and image
def GetScreenshot(driver):
        # image stuff
        # read image 
        screen_png = driver.get_screenshot_as_png()
        screen_np = np.frombuffer(screen_png, dtype=np.uint8)
        screen_image = cv2.imdecode(screen_np, cv2.IMREAD_COLOR)
        # convert to hsv format
        hsv_image = cv2.cvtColor(screen_image, cv2.COLOR_BGR2HSV)
        # define saturation range. Important objects have higher saturation
        lower_boundary = np.array([0, 65, 70])
        upper_boundary = np.array([179, 255, 255])
        mask = cv2.inRange(hsv_image, lower_boundary, upper_boundary)
        # detect snakes and food
        contours, hierarcy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #cv2.drawContours(screen_image, contours, -1, (0, 255, 75), 2)
        cv2.imwrite("image.png", screen_image)
        return screen_image, contours


def MoveMouse(direction, height, width):
    center = [(height // 2), (width // 2)]
    y = center[0] + direction[0] * 5
    x = center[1] + direction[1] * 5
    pyautogui.moveTo(y=y, x=x)


## adds delay so it runs at 30fps
def Timer(frequency):
    # timer
    start_time = time.time()
    now = time.time()
    deltaTime = now - start_time
    time.sleep(max(0, ((1 / frequency) - deltaTime)))
    start_time = now


## opens browser and enters username. returns webdriver
def StartBot():
    options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(
        options=options
    )
    driver.maximize_window()
    driver.get("http://slither.com/io")
    nickname_form = driver.find_element(By.XPATH, '//*[@id="nick"]')
    nickname = "tisyilanbot"
    nickname_form.send_keys(nickname)
    driver.find_element(By.XPATH, "/html/body/div[2]/div[5]/div").click()
    to_remove = [driver.find_element(By.XPATH, "/html/body/div[9]"),
                 driver.find_element(By.XPATH, "/html/body/div[10]"),
                 driver.find_element(By.XPATH, "/html/body/div[11]"),
                 driver.find_element(By.XPATH, "/html/body/div[12]")]
    js = "arguments[0].remove();"
    for node in to_remove:
        driver.execute_script(js, node)
    return driver


if __name__ == "__main__":
    main()