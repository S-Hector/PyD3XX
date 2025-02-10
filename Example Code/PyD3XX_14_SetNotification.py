import PyD3XX
import time

PyD3XX.SetPrintLevel(PyD3XX.PRINT_NONE) # Make PyD3XX not print anything.

Status, DeviceCount = PyD3XX.FT_CreateDeviceInfoList() # Create a device info list.
if Status != PyD3XX.FT_OK:
    print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO CREATE DEVICE INFO LIST: ABORTING")
    exit()
print(str(DeviceCount) + " Devices detected.")
if (DeviceCount == 0):
    print("NO DEVICES DETECTED: ABORTING")
    exit()

Status, Device = PyD3XX.FT_GetDeviceInfoDetail(0) # Get info of a device at index 0.
Status = PyD3XX.FT_Create(0, PyD3XX.FT_OPEN_BY_INDEX, Device) # Open the device we're using.
if Status != PyD3XX.FT_OK:
    print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO OPEN DEVICE: ABORTING")
    exit()

Status, ChipConfiguration = PyD3XX.FT_GetChipConfiguration(Device) # Get chip configuration.
if Status != PyD3XX.FT_OK:
    print("FAILED TO GET CHIP CONFIGURATION OF Device 0: ABORTING.")
    exit()
CH1_NotificationsEnabled = (ChipConfiguration.OptionalFeatureSupport & PyD3XX.CONFIGURATION_OPTIONAL_FEATURE_ENABLENOTIFICATIONMESSAGE_INCH1) != 0
if not(CH1_NotificationsEnabled):
    print("CH1 NOTIFICATIONS NOT ENABLED: ABORTING!")
    exit()
NotificationCount = 0
Status, ReadPipeCH1 = PyD3XX.FT_GetPipeInformation(Device, 1, 1)
if Status != PyD3XX.FT_OK:
    print("FAILED TO GET READ PIPE INFO OF CH1: ABORTING")
    exit()
def CallBackFunction(CallbackType: int, PipeID_GPIO0: int | bool, Length_GPIO1: int | bool):
    global NotificationCount
    NotificationCount += 1
    print("Received " + str(NotificationCount) + " notifications!")
    if(CallbackType == PyD3XX.E_FT_NOTIFICATION_CALLBACK_TYPE_DATA):
        print("CBF: You have " + str(Length_GPIO1) + " bytes to read at pipe " + hex(PipeID_GPIO0) + "!")
        if(NotificationCount != 5): # Disable callback function.
            if(PyD3XX.Platform == "linux") or (PyD3XX.Platform == "darwin"):
                Status, ReadBuffer, BytesRead = PyD3XX.FT_ReadPipe(Device, int("0x82", 16), Length_GPIO1, 0)
            else:
                Status, ReadBuffer, BytesRead = PyD3XX.FT_ReadPipe(Device, ReadPipeCH1, Length_GPIO1, PyD3XX.NULL)
        else:
            Status = PyD3XX.FT_ClearNotificationCallback(Device) # Clear callback function so we don't get called again.
            if Status != PyD3XX.FT_OK:
                print(PyD3XX.FT_STATUS_STR[Status] + " | WARNING: FAILED TO CLEAR CALLBACK FUNCTION OF DEVICE 0")
    elif(CallbackType == PyD3XX.E_FT_NOTIFICATION_CALLBACK_TYPE_GPIO):
        print("CBF: GPIO 0 Status = " + str(PipeID_GPIO0) + " | GPIO 1 Status = " + str(Length_GPIO1))
    return None

PyD3XX.FT_SetNotificationCallback(Device, CallBackFunction)
if Status != PyD3XX.FT_OK:
    print("FAILED TO SET CALLBACK FUNCTION OF DEVICE 0: ABORTING")
    exit()
print("This program will exit after at least 5 notifications or 5 seconds.")
Loops = 0
while((NotificationCount != 5) and not(Loops == 5)):
    time.sleep(1)
    Loops += 1;
print("Total Notifications Received: " + str(NotificationCount))
print("Seconds Passed: " + str(Loops))

#PyD3XX.FT_Close(Device)