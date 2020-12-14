#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime
import argparse
import lnetatmo
import ephem
import requests
import lxml.html
import re

from PIL import Image, ImageDraw, ImageFont

from inky import InkyPHAT

# Get the current path

PATH = os.path.dirname(__file__)

# Command line arguments to set display type and colour

parser = argparse.ArgumentParser()
parser.add_argument('--colour', '-c', type=str, required=False, default="auto", choices=["auto", "red", "black", "yellow"], help="ePaper display colour")
args = parser.parse_args()

colour = args.colour

# Set up the display
if colour == "auto":
    from inky.auto import auto
    inky_display = auto()
    colour = inky_display.colour
else:
    inky_display = InkyPHAT(colour)

inky_display.set_border(inky_display.WHITE)

# Uncomment the following if you want to rotate the display 180 degrees
# inky_display.h_flip = True
# inky_display.v_flip = True

# CO2 alert color
bg_color1 = inky_display.WHITE
bg_color2 = inky_display.WHITE


# Netatmo Credential
authorization = lnetatmo.ClientAuth(
    clientId = "",
    clientSecret = "",
    username = "",
    password = ""
)

# Get Netatmo Data
try:
    weather_station = lnetatmo.WeatherStationData(authorization)
except:
    IndoorTemp = '--'
    IndoorHum = '--'
    IndoorCO2 = '--'
    BedroomTemp = '--'
    BedroomHum = '--'
    BedroomCO2 = '--'
else:
    IndoorTemp = weather_station.lastData()['Indoor']['Temperature']
    IndoorHum = weather_station.lastData()['Indoor']['Humidity']
    IndoorCO2 = weather_station.lastData()['Indoor']['CO2']
    if IndoorCO2 > 1000:
        # Set CO2 alert color 
        bg_color1 = inky_display.YELLOW
    BedroomTemp = weather_station.lastData()['bedroom']['Temperature']
    BedroomHum = weather_station.lastData()['bedroom']['Humidity']
    BedroomCO2 = weather_station.lastData()['bedroom']['CO2']
    if BedroomCO2 > 1000:
        # Set CO2 alert color 
        bg_color2 = inky_display.YELLOW

# Calculate Sunrise, Sunset time, Moon age
Tokyo = ephem.city('Tokyo')
Tokyo.date = datetime.datetime.utcnow()
sun = ephem.Sun()
moon = ephem.Moon()
next_rising = ephem.localtime(Tokyo.next_rising(sun))
next_setting = ephem.localtime(Tokyo.next_setting(sun))
moon_age = Tokyo.date - ephem.previous_new_moon(Tokyo.date)
sunrise = str(next_rising.strftime('%H:%M'))
sunset = str(next_setting.strftime('%H:%M'))

# Get Weather forecast, AMeDAS data

# forecast web site
url_forecast = 'https://weather.yahoo.co.jp/weather/jp/13/4410.html'

# AMeDAS data site
# url_tokyo = 'https://tenki.jp/live/3/16/'
url_jmatokyo = 'http://www.jma.go.jp/jp/amedas_h/today-44132.html'

# Scraping forecast
forecast_response = requests.get(url_forecast)
forecast_html = lxml.html.fromstring(forecast_response.text)
today_forecast = forecast_html.xpath("/html/body/div[1]/div[2]/div[2]/div[1]/div[6]/table/tr/td[1]/div/p[2]")[0].text_content()
today_max = forecast_html.xpath("/html/body/div[1]/div[2]/div[2]/div[1]/div[6]/table/tr/td[1]/div/ul/li[1]/em")[0].text
today_min = forecast_html.xpath("/html/body/div[1]/div[2]/div[2]/div[1]/div[6]/table/tr/td[1]/div/ul/li[2]/em")[0].text
tomorrow_forecast = forecast_html.xpath("/html/body/div[1]/div[2]/div[2]/div[1]/div[6]/table/tr/td[2]/div/p[2]")[0].text_content()
tomorrow_max = forecast_html.xpath("/html/body/div[1]/div[2]/div[2]/div[1]/div[6]/table/tr/td[2]/div/ul/li[1]/em")[0].text
tomorrow_min = forecast_html.xpath("/html/body/div[1]/div[2]/div[2]/div[1]/div[6]/table/tr/td[2]/div/ul/li[2]/em")[0].text

# Scraping AMeDAS data

# now_response = requests.get(url_tokyo)
# now_html = lxml.html.fromstring(now_response.text)
# now_temp = now_html.xpath("/html/body/div[2]/section/section[2]/table/tr[2]/td[4]/span")[0].text
# now_humd = now_html.xpath("/html/body/div[2]/section/section[2]/table/tr[2]/td[6]/span")[0].text
# now_time = now_html.xpath("/html/body/div[2]/section/section[2]/h3/time")[0].text

jma_response = requests.get(url_jmatokyo)
jma_html = lxml.html.fromstring(jma_response.text)
jma_temp = ''
jma_humd = ''
jma_time = ''
# last data put jam_*
for i in range(24):
    temp_path = '/html/body/div[2]/div[2]/div[4]/div[1]/div[2]/table/tr[{}]/td[2]'.format(i+3)
    #humd_path = '/html/body/div[2]/div[2]/div[4]/div[1]/div[2]/table/tr[{}]/td[7]'.format(i+3)
    humd_path = '/html/body/div[2]/div[2]/div[4]/div[1]/div[2]/table/tr[{}]/td[8]'.format(i+3)
    temp = jma_html.xpath(temp_path)[0].text
    humd = jma_html.xpath(humd_path)[0].text
    # if data is None then break
    if temp is '\xa0' and humd is '\xa0':
        break
    jma_time, jma_temp, jma_humd = i+1, temp, humd


# Load background image
img = Image.open(os.path.join(PATH, "resources/nekomimi_bg.png")).resize(inky_display.resolution)
draw = ImageDraw.Draw(img)

# Grab the current date, and prepare our calendar
now = datetime.datetime.now()

# main contents area
cal_w = 155
cal_h = 80

# main contents points 
cal_x = inky_display.WIDTH - cal_w - 2
cal_y = 16

# Paint out a white rectangle onto which we'll draw our canvas
draw.rectangle((cal_x, cal_y, cal_x + cal_w - 1, cal_y + cal_h - 1), fill=inky_display.WHITE, outline=inky_display.WHITE)

draw.rectangle((cal_x, cal_y + 17 , cal_x + 4, cal_y + 28 - 1), fill=bg_color1)
draw.rectangle((cal_x, cal_y + 30 , cal_x + 4, cal_y + 41 - 1), fill=bg_color2)


font_size = 12
font = ImageFont.truetype(font = '/usr/share/fonts/truetype/mplus/mplus-2c-regular.ttf', size = font_size)
font_cal = ImageFont.truetype(font = '/usr/share/fonts/truetype/mplus/mplus-2c-bold.ttf', size = font_size+4)


date_text = now.strftime('%b %d %H:%M')
Indoor_text = "L "+str('%4.1f'%IndoorTemp if IndoorTemp is not '--' else IndoorTemp)+"℃ "+str(IndoorHum)+"% "+str(IndoorCO2)+"ppm"
Bedroom_text = "B "+str('%4.1f'%BedroomTemp if BedroomTemp is not '--' else BedroomTemp)+"℃ "+str(BedroomHum)+"% "+str(BedroomCO2)+"ppm"
#now_text = "東京 "+now_temp+"℃ "+now_humd+"% ("+(re.search(r'\d+\:\d+',now_time).group())+")"
now_text = "東京 "+jma_temp+"℃ "+jma_humd+"% ("+str(jma_time)+"時)"
today_text = "今日 "+today_forecast+" "+today_max+"℃ "+today_min+"℃"
tomorrow_text = "明日 "+tomorrow_forecast+" "+tomorrow_max+"℃ "+tomorrow_min+"℃"

draw.text((cal_x - 10, cal_y - (font_size +4 +2) ), date_text, font=font_cal, fill=inky_display.BLACK)
draw.text((cal_x + 100, cal_y - (font_size +2)), "月齢 "+str('%4.1f'%moon_age), font=font, fill=inky_display.BLACK)

draw.text((cal_x + 5, cal_y + 1), "日出 "+sunrise+" 日没 "+sunset, font=font, fill=inky_display.BLACK)

draw.text((cal_x + 5, cal_y + 1 + font_size + 1), Indoor_text, font=font, fill=inky_display.BLACK)
draw.rectangle((cal_x, cal_y + 4 + font_size + 1 , cal_x + 4, cal_y + 28 - 1), fill=bg_color1)
draw.text((cal_x +5 , cal_y + 1 + (font_size + 1)*2 ), Bedroom_text, font=font, fill=inky_display.BLACK)
draw.rectangle((cal_x, cal_y + 4 + (font_size + 1)*2 , cal_x + 4, cal_y + 41 - 1), fill=bg_color2)

draw.text((cal_x + 5, cal_y + 1 + (font_size + 1)*3 ), now_text, font=font, fill=inky_display.BLACK)
draw.text((cal_x + 5, cal_y + 1 + (font_size + 1)*4 ), today_text, font=font, fill=inky_display.BLACK)
draw.text((cal_x + 5, cal_y + 1 + (font_size + 1)*5 ), tomorrow_text, font=font, fill=inky_display.BLACK)

# Display the completed contents on Inky pHAT
inky_display.set_image(img)
inky_display.show()
