import time
import board
import busio
import adafruit_htu31d
import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import displayio
import rgbmatrix
import framebufferio
import terminalio
import adafruit_display_text.label
from adafruit_esp32spi import adafruit_esp32spi
from digitalio import DigitalInOut, Direction, Pull
from secrets import secrets

clockStart = time.monotonic()

JSON_URL = "http://" + secrets["local-url"] + "/index-mysql.php"
JSON_TXT_URL = "https://" + secrets["remote-url"] + "/index-json.php"

# If you are using a board with pre-defined ESP32 Pins:
esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)

i2c = board.I2C()  # uses board.SCL and board.SDA
htu = adafruit_htu31d.HTU31D(i2c)

displayio.release_displays()
matrix = rgbmatrix.RGBMatrix(
    width=64,
    bit_depth=4,
    rgb_pins=[
        board.MTX_R1,
        board.MTX_G1,
        board.MTX_B1,
        board.MTX_R2,
        board.MTX_G2,
        board.MTX_B2,
    ],
    addr_pins=[board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC, board.MTX_ADDRD],
    clock_pin=board.MTX_CLK,
    latch_pin=board.MTX_LAT,
    output_enable_pin=board.MTX_OE,
)
display = framebufferio.FramebufferDisplay(matrix)

#####################################
# Define Colors
##
colorOurdoorTemp = 0x448EE4
colorOurdoorTempDegreesign = 0xFFFFFF
colorOurdoorTempDegreesign = colorOurdoorTemp

colorTopSlash = 0x820FF0  # pink
# colorTopSlash = 0xEBC815 # yellow

colorIndoorTemp = 0xACF573
colorIndoorTempDegree = 0xFFFFFF
colorIndoorTempDegree = colorIndoorTemp

colorTime = 0x274F00
# colorTime = 0x274E10
colorTime = 0xFFFFFF
colorDate = 0x174F10
colorDate = 0x174F40

# Bottom Effects
colorTopDash = colorOurdoorTemp
colorBottomDash = colorOurdoorTemp
colorBottomMain = 0x00FF00
colorTopMain = 0x00FF00
colorBotScroller = 0x174F40
##
# Define Colors
#####################################

def colorTheme(theme):
    black = 0x000000
    blue = 0x0000FF
    green = 0x00FF00

    global colorTopDash
    global colorBottomDash
    global colorBottomMain
    global colorTopMain
    if theme == "dark":
        colorTopDash = black
        colorBottomDash = black
        colorBottomMain = black
        colorTopMain = black
    elif theme == "blue-line":
        colorTopDash = blue
        colorBottomDash = blue
    #         colorBottomMain=black
    #         colorTopMain=black
    elif theme == "green-line":
        colorTopDash = green
        colorBottomDash = green
    #         colorBottomMain=black
    #         colorTopMain=black
    elif theme == "bottom-blue":
        colorBottomDash = blue
    elif theme == "bottom-blue2":
        colorTopDash = black
        colorBottomDash = black
        colorBottomMain = black
        colorTopMain = black
    elif theme == "bottom-blue2":
        colorTopDash = black
        colorBottomDash = black
        colorBottomMain = black
        colorTopMain = black
    elif theme == "bottom-blue2":
        colorTopDash = black
        colorBottomDash = black
        colorBottomMain = black
        colorTopMain = black

        #     elif(theme == ""):
    #         colorTopDash=black
    #         colorBottomDash=black
    #         colorBottomMain=black
    #         colorTopMain=black
    else:
        print()


#############

colorTheme("dark")
# colorTheme("blue-line")
# colorTheme("green-line")
# colorTheme("bottom-blue")

## For bitcoin stuff
lineCoinStatus = adafruit_display_text.label.Label(
    terminalio.FONT, color=0x003400, text=" "
)
lineCoinStatus.x = 1
lineCoinStatus.y = 8
line1ar = adafruit_display_text.label.Label(terminalio.FONT, color=0x820000, text=" ")
line1ar.x = 1
line1ar.y = 8
## For bitcoin stuff

lineBotFull = adafruit_display_text.label.Label(
    terminalio.FONT, color=0x274F00, text=""
)
lineBotFull.x = 1
lineBotFull.y = 20


###
# Top & Bottom effects: Round 1... Fight
##

topTop = adafruit_display_text.label.Label(
    terminalio.FONT, color=colorTopMain, text="XOXOxoXOXOXOx"
)
topTop.x = 0
topTop.y = -2

topTop1 = adafruit_display_text.label.Label(
    terminalio.FONT, color=colorTopDash, text="___________"
)
topTop1.x = 0
topTop1.y = -4

bottomBottom1 = adafruit_display_text.label.Label(
    terminalio.FONT, color=colorBottomDash, text="___________"
)
bottomBottom1.x = -1
bottomBottom1.y = 25

bottomBottom = adafruit_display_text.label.Label(
    terminalio.FONT, color=colorBottomMain, text="XOXOxoXOXOXOx"
)
bottomBottom.x = -1
bottomBottom.y = 32


##
# Outdoor Temp / Indoor Temp
# Percise
##

adjustGlobalHeight = -4
adjustGlobalSide = 0


adjustHeightTop = 0
adjustSideTop = -1

lineOutdoorA = adafruit_display_text.label.Label(
    terminalio.FONT, color=colorOurdoorTemp, text=""
)
lineOutdoorA.x = 1 + adjustSideTop + adjustGlobalSide
lineOutdoorA.y = 8 + adjustHeightTop + adjustGlobalHeight

lineOutdoorB = adafruit_display_text.label.Label(
    terminalio.FONT, color=colorOurdoorTemp, text=""
)
lineOutdoorB.x = 12 + adjustSideTop + adjustGlobalSide
lineOutdoorB.y = 8 + adjustHeightTop + adjustGlobalHeight

lineOutdoorC = adafruit_display_text.label.Label(
    terminalio.FONT, color=colorOurdoorTemp, text=""
)
lineOutdoorC.x = 16 + adjustSideTop + adjustGlobalSide
lineOutdoorC.y = 8 + adjustHeightTop + adjustGlobalHeight

lineOutdoorD = adafruit_display_text.label.Label(
    terminalio.FONT, color=colorOurdoorTempDegreesign, text=""
)
lineOutdoorD.x = 26 + adjustSideTop + adjustGlobalSide
lineOutdoorD.y = 1 + adjustHeightTop + adjustGlobalHeight

lineOutdoorDD = adafruit_display_text.label.Label(
    terminalio.FONT, color=colorOurdoorTempDegreesign, text=""
)
lineOutdoorDD.x = 27 + adjustSideTop + adjustGlobalSide
lineOutdoorDD.y = 1 + adjustHeightTop + adjustGlobalHeight

lineTopDiv = adafruit_display_text.label.Label(
    terminalio.FONT, color=colorTopSlash, text=""
)
lineTopDiv.x = 29 + adjustSideTop + adjustGlobalSide
lineTopDiv.y = 8 + adjustHeightTop + adjustGlobalHeight

colorIndoorTemp = 0xACF573
lineIndoorA = adafruit_display_text.label.Label(
    terminalio.FONT, color=colorIndoorTemp, text=""
)
lineIndoorA.x = 35 + adjustSideTop + adjustGlobalSide
lineIndoorA.y = 8 + adjustHeightTop + adjustGlobalHeight

lineIndoorB = adafruit_display_text.label.Label(
    terminalio.FONT, color=colorIndoorTemp, text=""
)
lineIndoorB.x = 46 + adjustSideTop + adjustGlobalSide
lineIndoorB.y = 8 + adjustHeightTop + adjustGlobalHeight

lineIndoorC = adafruit_display_text.label.Label(
    terminalio.FONT, color=colorIndoorTemp, text=""
)
lineIndoorC.x = 50 + adjustSideTop + adjustGlobalSide
lineIndoorC.y = 8 + adjustHeightTop + adjustGlobalHeight

lineIndoorD = adafruit_display_text.label.Label(
    terminalio.FONT, color=colorIndoorTempDegree, text=""
)
lineIndoorD.x = 60 + adjustSideTop + adjustGlobalSide
lineIndoorD.y = 1 + adjustHeightTop + adjustGlobalHeight

lineIndoorDD = adafruit_display_text.label.Label(
    terminalio.FONT, color=colorIndoorTempDegree, text=""
)
lineIndoorDD.x = 61 + adjustSideTop + adjustGlobalSide
lineIndoorDD.y = 1 + adjustHeightTop + adjustGlobalHeight

##
#  Outdoor Temp / Indoor Temp
#  Old / No Formatting
##

lineTopFull = adafruit_display_text.label.Label(
    terminalio.FONT, color=0x448EE4, text=""
)
lineTopFull.x = 1
lineTopFull.y = 8

lineIndoorTemp = adafruit_display_text.label.Label(
    terminalio.FONT,
    # color=0x003400,
    color=0xACF573,
    text=" ",
)
lineIndoorTemp.x = 38
lineIndoorTemp.y = 8

##
# Time / Date
##

adjustHeightBot = -2
adjustSideBot = -1

lineHour = adafruit_display_text.label.Label(terminalio.FONT, color=colorTime, text="")
lineHour.x = 3 + adjustSideBot + adjustGlobalSide
lineHour.y = 20 + adjustHeightBot + adjustGlobalHeight

lineColon = adafruit_display_text.label.Label(terminalio.FONT, color=colorTime, text="")
lineColon.x = 15 + adjustSideBot + adjustGlobalSide
lineColon.y = 20 + adjustHeightBot + adjustGlobalHeight

lineMin = adafruit_display_text.label.Label(terminalio.FONT, color=colorTime, text="")
lineMin.x = 19 + adjustSideBot + adjustGlobalSide
lineMin.y = 20 + adjustHeightBot + adjustGlobalHeight

lineAmPm = adafruit_display_text.label.Label(terminalio.FONT, color=colorTime, text="")
lineAmPm.x = 29 + adjustSideBot + adjustGlobalSide
lineAmPm.y = 20 + adjustHeightBot + adjustGlobalHeight

lineMonth = adafruit_display_text.label.Label(terminalio.FONT, color=colorDate, text="")
lineMonth.x = 34 + adjustSideBot + adjustGlobalSide
lineMonth.y = 20 + adjustHeightBot + adjustGlobalHeight

lineDateSlash = adafruit_display_text.label.Label(terminalio.FONT, text="")
lineDateSlash.x = 45 + adjustSideBot + adjustGlobalSide
lineDateSlash.y = 20 + adjustHeightBot + adjustGlobalHeight

lineDay = adafruit_display_text.label.Label(terminalio.FONT, color=colorDate, text="")
lineDay.x = 51 + adjustSideBot + adjustGlobalSide
lineDay.y = 20 + adjustHeightBot + adjustGlobalHeight

botLine = adafruit_display_text.label.Label(
    terminalio.FONT, color=colorBotScroller, text=""
)
botLine.x = 1 + adjustSideBot + adjustGlobalSide
botLine.y = 30 + adjustHeightBot + adjustGlobalHeight

##

g1 = displayio.Group()
g1.append(botLine)
g1.append(line1ar)
g1.append(lineCoinStatus)
g1.append(bottomBottom)
g1.append(bottomBottom1)
g1.append(topTop)
g1.append(topTop1)
g1.append(lineOutdoorA)
g1.append(lineOutdoorB)
g1.append(lineOutdoorC)
g1.append(lineOutdoorD)
g1.append(lineOutdoorDD)
g1.append(lineIndoorA)
g1.append(lineIndoorB)
g1.append(lineIndoorC)
g1.append(lineIndoorD)
g1.append(lineIndoorDD)
g1.append(lineBotFull)
g1.append(lineTopFull)
g1.append(lineTopDiv)
g1.append(lineIndoorTemp)
g1.append(lineHour)
g1.append(lineColon)
g1.append(lineMin)
g1.append(lineAmPm)
g1.append(lineMonth)
g1.append(lineDateSlash)
g1.append(lineDay)
display.show(g1)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

requests.set_socket(socket, esp)


def connetWiFi():
    lineTopFull.text = "Connecting "
    lineBotFull.text = "to network..."
    if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
        print("ESP32 found and in idle mode")
    print("Firmware vers.", esp.firmware_version)
    print("MAC addr:", [hex(i) for i in esp.MAC_address])

    for ap in esp.scan_networks():
        print("\t%s\t\tRSSI: %d" % (str(ap["ssid"], "utf-8"), ap["rssi"]))

    print("Connecting to AP...")
    while not esp.is_connected:
        try:
            esp.connect_AP(secrets["ssid"], secrets["password"])
        except RuntimeError as e:
            print("could not connect to AP, retrying: ", e)
            continue
    print("Connected to", str(esp.ssid, "utf-8"), "\tRSSI:", esp.rssi)
    lineTopFull.text = ""
    lineBotFull.text = "Connected!"
    print("My IP address is", esp.pretty_ip(esp.ip_address))
    print("Ping google.com: %d ms" % esp.ping("google.com"))

    lineBotFull.text = ""




####################################
####################################
####################################
####################################
####################################
####################################
####################################
# Debug Options
##

debug = False
# debug = True

if debug == True:
    print()
    print()
    print("#" * 40)
    print("#" * 40)
    print("#" * 10 + " DEBUG ON " + "#" * 10)
    print("#" * 40)
    print("#" * 40)
    print()
    print()

    lineHour.text = "12"
    lineColon.text = ":"
    lineMin.text = "23"
    lineAmPm.text = "."

    lineMonth.text = "11"
    lineDateSlash.text = "/"
    lineDay.text = "21"

    lineOutdoorA.text = "12"
    lineOutdoorB.text = "."
    lineOutdoorC.text = "59"
    lineOutdoorD.text = "."
    lineOutdoorDD.text = "."

    lineIndoorA.text = "77"
    lineIndoorB.text = "."
    lineIndoorC.text = "23"
    lineIndoorD.text = "."
    lineIndoorDD.text = "."
    botLine.text = "ddddTESAs"
    scroll(botLine)
else:
    
    connetWiFi()

# END DEBUG options
####################################

def getLocalTemp():
    tempF = htu.temperature * 9 / 5 + 32
    #tempF = 0 * 9 / 5 + 32
    # tempSplit = str(round(tempF, 2)).split(".")
    tempSplit = str("%.2f" % round(tempF, 2)).split(".")
    tempFa = tempSplit[0]
    tempFb = tempSplit[1]
    lineIndoorA.text = tempFa
    lineIndoorB.text = "."
    lineIndoorC.text = tempFb
    lineIndoorD.text = "."
    lineIndoorDD.text = "."

r1_log = 0
r5_log = 0

def getTimeTemp():
    global r1_log
    global r5_log

    print ("times r1 request error: ", r1_log)

    Printing = True
    while Printing:
        try:
            r1 = requests.get(JSON_URL)
            time.sleep(0.5)
            json_data = r1.json()
            time.sleep(2)
            r1.close()
            time.sleep(2)
            Printing = False
        except Exception as e:
            r1_log = r1_log + 1
            print("1")
            print(e)
            print(e)
            print(e)
            print(e)
            print(e)
            time.sleep(15)
            continue


#     print("1")
#     Printing = True
#     print ("times r5 request error: ", r5_log)
#     while Printing:
#         try:
#             print("a")
#             r5 = requests.get(JSON_TXT_URL)
#             print("b")
#             time.sleep(0.5)
#             json_data5 = r5.json()
#             print("c")
#             time.sleep(2)
#             r5.close()
#             time.sleep(2)
#             print("d")
#             Printing = False
#             print("e")
#         except Exception as e:
#             r5_log = r5_log + 1
#             print("2")
#             print(e)
#             print(e)
#             print(e)
#             print(e)
#             print(e)
#             time.sleep(15)
#             connetWiFi()
#             continue

    am_pm = json_data[0]["am_pm"]
    justMonthNo = json_data[0]["justMonthNo"]
    justDayNo = json_data[0]["justDayNo"]
    justHourNo = json_data[0]["justHourNo"]
    justMinNo = json_data[0]["justMinNo"]

    outdoor_tempB = json_data[0]["outdoor_tempB"]  # right of decie
    outdoor_tempA = json_data[0]["outdoor_tempA"]  # left of decimel

    outdoor_tempB = (
        str(outdoor_tempB) + "0"
    )  # hack to always show 2 digits. e.x. 32.20 vs 32.2: always add 0, print begining two digits [0] [1]
    lineOutdoorA.text = str(outdoor_tempA)
    lineOutdoorB.text = "."
    lineOutdoorC.text = str(outdoor_tempB[0] + outdoor_tempB[1])

    lineOutdoorD.text = "."
    lineOutdoorDD.text = "."

    # Dim the LEDs when it's late at night
    if am_pm == "am":
        if 1 < int(justHourNo) < 6:
        # if True:
            dark_grey = 0x202020
            dark_grey = 0x101010
            lineTopDiv.color = dark_grey
            
            lineHour.color = dark_grey
            lineColon.color = dark_grey
            lineMin.color = dark_grey
            lineAmPm.color = dark_grey

            lineMonth.color = dark_grey
            lineDateSlash.color = dark_grey
            lineDay.color = dark_grey

            lineOutdoorA.color = dark_grey
            lineOutdoorB.color = dark_grey
            lineOutdoorC.color = dark_grey
            lineOutdoorD.color = dark_grey
            lineOutdoorDD.color = dark_grey

            lineIndoorA.color = dark_grey
            lineIndoorB.color = dark_grey
            lineIndoorC.color = dark_grey
            lineIndoorD.color = dark_grey
            lineIndoorDD.color = dark_grey
            
            botLine.color = dark_grey
        else:
            lineHour.color = int(json_data[0]["timeColor"])
            lineColon.color = int(json_data[0]["timeColor"])
            lineMin.color = int(json_data[0]["timeColor"])
            lineAmPm.color = int(json_data[0]["timeColor"])

            lineMonth.color = int(json_data[0]["dateColor"])
            lineDateSlash.color = int(json_data[0]["dateColor"])
            lineDay.color = int(json_data[0]["dateColor"])

            lineOutdoorA.color = int(json_data[0]["outsideColor"])
            lineOutdoorB.color = int(json_data[0]["outsideColor"])
            lineOutdoorC.color = int(json_data[0]["outsideColor"])
            lineOutdoorD.color = int(json_data[0]["outsideColor"])
            lineOutdoorDD.color = int(json_data[0]["outsideColor"])

            lineIndoorA.color = int(json_data[0]["insideColor"])
            lineIndoorB.color = int(json_data[0]["insideColor"])
            lineIndoorC.color = int(json_data[0]["insideColor"])
            lineIndoorD.color = int(json_data[0]["insideColor"])
            lineIndoorDD.color = int(json_data[0]["insideColor"])
    time.sleep(2)

    if am_pm[0] == "p":
        lineAmPm.text = "."
    else:
        lineAmPm.text = "."

    lineHour.text = justHourNo
    lineMin.text = justMinNo  # + am_pm
    lineMonth.text = justMonthNo
    lineDay.text = justDayNo
    lineColon.text = ":"
    lineDateSlash.text = "/"

    # Message Display
    mainTextJSON = json_data[0]["mainText"]
    time.sleep(0.5)
    print("wtftest")
    print(mainTextJSON)

    global botLineMem
    botLineMem = mainTextJSON

botLineMem = ""

while True:
    
    clockLoopStart = time.monotonic()
    print('Running time: {0:.0f} seconds'.format(clockLoopStart - clockStart))

#     if tmpClockLoopStart == 0:
#         tmpClockLoopStart = time.monotonic()
#     print("time: tmp %i / main %i " % (tmpClockLoopStart, clockLoopStart))

    if debug == False:
        getTimeTemp()
        lineTopDiv.text = str("/")
        getLocalTemp()


    botLine.text = botLineMem
    # display.refresh(minimum_frames_per_second=0)
    time.sleep(5)


