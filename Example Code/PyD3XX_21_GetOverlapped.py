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

Pipes = {}
Overlaps = {}
for i in range(2): # Get in and out pipes for channel 1 and create overlaps.
    Status, Pipes[i] = PyD3XX.FT_GetPipeInformation(Device, 1, i)
    if Status != PyD3XX.FT_OK:
        print("FAILED TO GET PIPE INFO OF [1," + str(i) +"]: ABORTING")
        exit()
    Status, Overlaps[i] = PyD3XX.FT_InitializeOverlapped(Device)
    if(Status != PyD3XX.FT_OK):
        print("FAILED TO CREATE OVERLAP FOR PIPE " + str(i) + ": ABORTING")
        exit()
    Status = PyD3XX.FT_SetPipeTimeout(Device, Pipes[i], 100)
    if(Status != PyD3XX.FT_OK):
        print("WARNING: FAILED TO SET PIPE TIMEOUT TO 100")
        print("Status = " + PyD3XX.FT_STATUS_STR[Status])
if(PyD3XX.Platform == "linux") or (PyD3XX.Platform == "darwin"):
    Status, ReadBuffer, BytesRead = PyD3XX.FT_ReadPipeAsync(Device, 0, 1, Overlaps[1])
else:
    Status, ReadBuffer, BytesRead = PyD3XX.FT_ReadPipe(Device, Pipes[1], 1, Overlaps[1])
Attempts = 0
Status = PyD3XX.FT_IO_INCOMPLETE
while(Status == PyD3XX.FT_IO_INCOMPLETE):
    Status, BytesTransferred = PyD3XX.FT_GetOverlappedResult(Device, Overlaps[1], False)
    print("Waiting on input...")
    Attempts += 1
    time.sleep(1)
    if((Status != PyD3XX.FT_OK) and (Status != PyD3XX.FT_IO_PENDING)) or (Attempts == 3):
        StatusAP = PyD3XX.FT_AbortPipe(Device, Pipes[1])
        if(StatusAP != PyD3XX.FT_OK):
            print("FT_AbortPipe failed!")
        else:
            print("Aborted read pipe!")
        break
print(PyD3XX.FT_STATUS_STR[Status] + " | Encountered error or FT_ReadPipe was successful.")
ReadValue = format(int.from_bytes(ReadBuffer.Value(), "little"), "x").zfill(1*2)
print("Channel 1 = 0x" + ReadValue)
for i in range(2): # Release overlaps since we're done using them.
    Status = PyD3XX.FT_ReleaseOverlapped(Device, Overlaps[i])
    if Status != PyD3XX.FT_OK:
        print(PyD3XX.FT_STATUS_STR[Status] + " | WARNING: FAILED TO RELEASE OVERLAP " + str(i))

PyD3XX.FT_Close(Device)