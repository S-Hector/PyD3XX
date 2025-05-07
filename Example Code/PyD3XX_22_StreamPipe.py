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

Pipes = {}
for i in range(2): # Get in and out pipes for channel 1.
    Status, Pipes[i] = PyD3XX.FT_GetPipeInformation(Device, 1, i)
    if Status != PyD3XX.FT_OK:
        print("FAILED TO GET PIPE INFO OF [1," + str(i) +"]: ABORTING")
        exit()
Status = PyD3XX.FT_SetStreamPipe(Device, True, True, PyD3XX.NULL, 1024)
if Status != PyD3XX.FT_OK:
    print("FAILED TO SET STREAM SIZE FOR ALL PIPES.")
    exit()
else:
    print("Stream size for all pipes set to 1024 bytes!")
Status = PyD3XX.FT_ClearStreamPipe(Device, False, False, Pipes[1])
if Status != PyD3XX.FT_OK:
    print("FAILED TO CLEAR STREAM SIZE FOR CH1 READ PIPE.")
    exit()
else:
    print("Cleared stream size for CH1 read pipe!")

PyD3XX.FT_Close(Device)