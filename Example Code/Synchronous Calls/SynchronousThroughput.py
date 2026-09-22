import PyD3XX
import time
import threading
import queue

CHANNEL_COUNT = 4 # How many channels we're streaming.
READ_SIZE = 1024 * 1024 # How many bytes each read pipe call is.
TEST_LOOPS = 100 # How many times to loop through the test.


if(CHANNEL_COUNT > 4):
    print("ERROR: CHANNEL_COUNT must be 4 or less.")
    exit()

# ---| Main Code Starts Here |---
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

if(Device.Flags == PyD3XX.FT_FLAGS_SUPERSPEED):
    print("Operating at SUPERSPEED")

Pipes = {}
for i in range(1, (CHANNEL_COUNT * 2), 2): # Get IN pipes.
    Status, Pipes[i] = PyD3XX.FT_GetPipeInformation(Device, 1, i)
    if Status != PyD3XX.FT_OK:
        print("FAILED TO GET PIPE INFO OF [1," + str(i) +"]: ABORTING")
        exit()

while(TEST_LOOPS > 0):
    TotalBytesRead = 0
    StartTime = time.perf_counter() # Get start time of second.
    for Pipe in Pipes.values():
        if(PyD3XX.Platform == "windows"):
            Status, Data, BytesRead = PyD3XX.FT_ReadPipe(Device, Pipe, READ_SIZE, 0)
        else:
            Status, Data, BytesRead = PyD3XX.FT_ReadPipe(Device, Pipe.PipeID, READ_SIZE, 0)
        if(Status != PyD3XX.FT_OK):
            print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO READ ON PIPE " + format(Pipe.PipeID, '#02x') + ": ABORTING")
            exit()
        if(BytesRead != READ_SIZE):
            print("SESSION UNDERRUN ERROR: Received " + str(BytesRead) + " bytes instead of the requested " + str(READ_SIZE) + "bytes!")
            exit()
        TotalBytesRead += BytesRead
    ElapsedTime = time.perf_counter() - StartTime
    MB = str(round(TotalBytesRead / 1000000 / ElapsedTime, 2))
    MiB = str(round(TotalBytesRead / 1048576 / ElapsedTime, 2))
    print("Performance = " + MiB + " MiB/s\t| " + MB + " MB/s") # Print MiB/s.

    TEST_LOOPS -= 1