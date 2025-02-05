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

Status = PyD3XX.FT_EnableGPIO(Device, int("11", 2), int("11", 2))
if Status != PyD3XX.FT_OK:
    print("WARNING: FAILED TO ENABLE GPIO OF DEVICE 0")
else:
    print("Successfully enabled GPIO[1:0] as outputs.");
Status = PyD3XX.FT_WriteGPIO(Device, int("11", 2), int("11", 2))
if Status != PyD3XX.FT_OK:
    print("WARNING: FAILED TO WRITE GPIO OF DEVICE 0")
else:
    print("Successfully wrote 0b11 to GPIO pins!");
Status = PyD3XX.FT_WriteGPIO(Device, int("11", 2), int("00", 2))
if Status != PyD3XX.FT_OK:
    print("WARNING: FAILED TO WRITE GPIO OF DEVICE 0")
Status = PyD3XX.FT_EnableGPIO(Device, int("11", 2), int("00", 2))
if Status != PyD3XX.FT_OK:
    print("WARNING: FAILED TO DISABLE GPIO OF DEVICE 0")
Status, GPIO_Data = PyD3XX.FT_ReadGPIO(Device)
if Status != PyD3XX.FT_OK:
    print("WARNING: FAILED TO READ GPIO OF DEVICE 0")
else:
    print("GPIO DATA = 0b" + format(GPIO_Data, "02b"))
Status = PyD3XX.FT_SetGPIOPull(Device, int("11", 2), int("1111", 2))
if Status != PyD3XX.FT_OK:
    print("WARNING: FAILED TO SET GPIO PULL OF DEVICE 0")
else:
    print("Successfully set GPIO pull to hi-Z!");
PyD3XX.FT_Close(Device)