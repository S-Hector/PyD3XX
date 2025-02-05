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
if(PyD3XX.Platform == "linux") or (PyD3XX.Platform == "darwin"):
    Status, ReadBuffer, BytesRead = PyD3XX.FT_ReadPipeEx(Device, 0, 1, 0)
else:
    Status, ReadBuffer, BytesRead = PyD3XX.FT_ReadPipeEx(Device, Pipes[1], 1, PyD3XX.NULL)
if(Status == PyD3XX.FT_OK):
    ReadValue = format(int.from_bytes(ReadBuffer.Value(), "little"), "x").zfill(1*2)
    print("Channel 1 = 0x" + ReadValue)
else:
    print("Failed to read data!: ABORTING")
    exit()
WriteBuffer = PyD3XX.FT_Buffer.from_int(int.from_bytes(ReadBuffer.Value(), "little") + 1)
if(PyD3XX.Platform == "linux") or (PyD3XX.Platform == "darwin"):
    Status, BytesWrote = PyD3XX.FT_WritePipeEx(Device, 0, WriteBuffer, 1, PyD3XX.NULL)
else:
    Status, BytesWrote = PyD3XX.FT_WritePipeEx(Device, Pipes[0], WriteBuffer, 1, PyD3XX.NULL)
if(Status == PyD3XX.FT_OK):
    WriteValue = format(int.from_bytes(WriteBuffer.Value(), "little"), "x").zfill(1*2)
    print("Wrote 0x" + WriteValue + " to Channel 1!")
else:
    print("Failed to write data!: ABORTING")
    exit()

PyD3XX.FT_Close(Device)