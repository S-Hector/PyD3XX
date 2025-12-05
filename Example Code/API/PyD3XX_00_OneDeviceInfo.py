import PyD3XX

PyD3XX.SetPrintLevel(PyD3XX.PRINT_NONE) # Make PyD3XX not print anything.

DeviceCount = 0

Status, DeviceCount = PyD3XX.FT_CreateDeviceInfoList() # Create a device info list.
if Status != PyD3XX.FT_OK:
    print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO CREATE DEVICE INFO LIST: ABORTING")
    exit()
print(str(DeviceCount) + " Devices detected.")
if (DeviceCount == 0):
    print("NO DEVICES DETECTED: ABORTING")
    exit()

Status, Device = PyD3XX.FT_GetDeviceInfoDetail(0) # Get info of a device at index 0.
if Status != PyD3XX.FT_OK:
    print(PyD3XX.FT_STATUS_STR[Status] + " | WARNING: FAILED TO GET INFO FOR DEVICE 0")
else:
    if(Device.Flags & PyD3XX.FT_FLAGS_OPENED):
        print("Device 0 is opened by another process!")
    else:
        if(Device.Type == PyD3XX.FT_DEVICE_601):
                print("Device 0 is a FT601 device!")
        elif(Device.Type == PyD3XX.FT_DEVICE_600):
            print("Device 0 is a FT600 device!")

