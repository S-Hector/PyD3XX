import PyD3XX

PyD3XX.SetPrintLevel(PyD3XX.PRINT_NONE) # Make PyD3XX not print anything.

CHANNEL_COUNT = 1 # How many channels your FT60X device is configured to have.

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

Pipes = {}
for i in range(CHANNEL_COUNT * 2): # Set timeout of all pipes to 10.
    Status, Pipes[i] = PyD3XX.FT_GetPipeInformation(Device, 1, i) # Get pipe information.
    if Status != PyD3XX.FT_OK:
        print("FAILED TO GET PIPE INFO OF [1," + str(i) +"]: ABORTING")
        exit()
    Status_SPT = PyD3XX.FT_SetPipeTimeout(Device, Pipes[i], 100)
    if(PyD3XX.Platform == "windows"): # FT_GetPipeTimeout does not exist in D3XX Linux library.
        Status, TimeOut = PyD3XX.FT_GetPipeTimeout(Device, Pipes[i])
        if (Status != PyD3XX.FT_OK) or (TimeOut != 100):
            print("FAILED TO SET AND/OR CONFIRM PIPE TIMEOUT TO 100: ABORTING")
            print("Status = " + PyD3XX.FT_STATUS_STR[Status] + " | Timeout = " + str(TimeOut))
            exit()
    if(Status_SPT != PyD3XX.FT_OK):
        print("FAILED TO SET AND/OR CONFIRM PIPE TIMEOUT TO 100: ABORTING")
        print("Status = " + PyD3XX.FT_STATUS_STR[Status] + " | Timeout = " + str(TimeOut))
    else:
        print("Successfully set timeout of pipe " + str(i) + " to 100!")

PyD3XX.FT_Close(Device)