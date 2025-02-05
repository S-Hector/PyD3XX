import PyD3XX

PyD3XX.SetPrintLevel(PyD3XX.PRINT_NONE) # Make PyD3XX not print anything.

DeviceCount = 0
Devices = {} # Dictionary of devices.

CREATE_MANUAL_DICT = 0 # Create a device dictionary manually over multiple function calls.
CREATE_LIST = 1 # Create a device list in one function call.
CREATE_DICT = 2 # Create a device dictionary in one function call.

MakeList = CREATE_DICT # Controls how we make a list in this example.


Status, DeviceCount = PyD3XX.FT_CreateDeviceInfoList() # Create a device info list.
if Status != PyD3XX.FT_OK:
    print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO CREATE DEVICE INFO LIST: ABORTING")
    exit()
print(str(DeviceCount) + " Devices detected.")
if (DeviceCount == 0):
    print("NO DEVICES DETECTED: ABORTING")
    exit()

if MakeList == CREATE_DICT:
    Status, Devices = PyD3XX.FT_GetDeviceInfoDict(DeviceCount) # This will create a Python dictionary.
    if Status != PyD3XX.FT_OK:
        print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO CREATE DEVICE INFO LIST: ABORTING")
        exit()
elif MakeList == CREATE_LIST:
    Status, Devices = PyD3XX.FT_GetDeviceInfoList(DeviceCount) # This will create a Python list.
    if Status != PyD3XX.FT_OK:
        print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO CREATE DEVICE INFO LIST: ABORTING")
        exit()

for i in range(0, DeviceCount): # Get device info at each index from 0->(DeviceCount - 1).
    if MakeList == CREATE_MANUAL_DICT: # Manually create a Python dictionary.
        Status, Devices[i] = PyD3XX.FT_GetDeviceInfoDetail(i) # Get info of a device at a specific index.
    if Status != PyD3XX.FT_OK:
        print(PyD3XX.FT_STATUS_STR[Status] + " | WARNING: FAILED TO GET INFO FOR DEVICE " + str(i))
        continue # Device info not valid. Move onto next device.
    if(Devices[i].Flags & PyD3XX.FT_FLAGS_OPENED):
        print("Device " + str(i) + " is opened by another process!")
        continue # Device info not valid. Move onto next device.
    print("---| Device " + str(i) + " |---")
    if(Devices[i].Type == PyD3XX.FT_DEVICE_601):
        print("Device " + str(i) + " is a FT601 device!")
    elif(Devices[i].Type == PyD3XX.FT_DEVICE_600):
        print("Device " + str(i) + " is a FT600 device!")
    print("\tFlags = " + hex(Devices[i].Flags))
    print("\tType = " + str(Devices[i].Type))
    print("\tID = " + hex(Devices[i].ID))
    print("\tLocID = " + hex(Devices[i].LocID))
    print("\tSerial Number = " + Devices[i].SerialNumber)
    print("\tDescription = " + Devices[i].Description)

