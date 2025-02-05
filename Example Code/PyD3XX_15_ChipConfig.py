import PyD3XX

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
print("Device 0 Description: '" + ChipConfiguration.StringDescriptors[1] + "'")
if(ChipConfiguration.StringDescriptors[1] == "TEST 0"):
    ChipConfiguration.StringDescriptors[1] = "TEST 1"
else:
    ChipConfiguration.StringDescriptors[1] = "TEST 0"
Status = PyD3XX.FT_SetChipConfiguration(Device, ChipConfiguration)
if Status != PyD3XX.FT_OK:
    print("WARNING: FAILED TO SET CHIP CONFIGURATION OF DEVICE 0")

PyD3XX.FT_Close(Device)