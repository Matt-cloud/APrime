""" A ripoff version of the logging module that suit my needs """

from termcolor import colored
from colorama import init as termcolorInit
from inspect import getframeinfo, stack

import datetime
import time
import traceback as tb
import os

termcolorInit()

LEVELS = [
    "debug",
    "info",
    "warning",
    "error",
    "critical"
]

LEVELCOLORS = [
    "magenta",
    "cyan",
    "yellow",
    "red",
    "red"
]

lastLog = 0


class Logger:
    def __init__(self, loggingFile=None, database=None, dateFormat="%b %m %Y at %I:%M %p", defaultLevel="info", fileLogLevel=3):
        self.loggingFile = loggingFile
        self.database = database 
        self.dateFormat = dateFormat
        self.defaultLevel = defaultLevel
        self.fileLogLevel = fileLogLevel
    
    def log(self, message, color=None, level=None, showError=True):
        global lastLog

        if not level:
            level = self.defaultLevel

        levelIndex = LEVELS.index(level) # ik not index but ok

        if not color:
            color = LEVELCOLORS[levelIndex]

        caller = getframeinfo(stack()[1][0])
        
        callerInfo = f"[{os.path.basename(caller.filename)}:{caller.lineno}]"
        dateInfo = f"[{datetime.datetime.now().strftime(self.dateFormat)}]"
        debugInfo = f"{callerInfo} {dateInfo} "

        coloredMessage = debugInfo + colored(str(message), color)
        message = debugInfo + str(message)

        traceback = tb.format_exc()
        if not showError:
            traceback = "NoneType: None" # pulled a little sneaky on ya

        if traceback.strip() != "NoneType: None":
            coloredMessage = coloredMessage + "\n" + colored(traceback, "red")
            message = message + "\n" + traceback

            level = "error"
            levelIndex = LEVELS.index(level)
            color = LEVELCOLORS[levelIndex]
        
        if int(time.time()) == lastLog:
            time.sleep(.02)

        print(coloredMessage)
        lastLog = int(time.time())

        if self.loggingFile:
            if levelIndex + 1 >= self.fileLogLevel:
                with open(self.loggingFile, "a") as f:
                    f.write(f"{level.upper()} {message}\n")
                
                data = {
                    "time": int(time.time()),
                    "levelIndex": levelIndex,
                    "level": level,
                    "message": message,
                    "color": color
                }

                if self.database:
                    self.database.logs.insert_one(data)
