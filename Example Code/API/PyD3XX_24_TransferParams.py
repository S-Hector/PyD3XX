import PyD3XX
import time

PyD3XX.SetPrintLevel(PyD3XX.PRINT_NONE) # Make PyD3XX not print anything.

CHANNEL_COUNT = 4

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
print("Device (index, serial, desc): 0, " + Device.SerialNumber + ", " + Device.Description);
Status = PyD3XX.FT_Create(0, PyD3XX.FT_OPEN_BY_INDEX, Device) # Open the device we're using.
if Status != PyD3XX.FT_OK:
    print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO OPEN DEVICE: ABORTING")
    exit()
print("Successfully opened device!")
TransferParams = {}
for i in range(CHANNEL_COUNT):
    Status, TransferParams[i] = PyD3XX.FT_GetTransferParams(i)
    if Status != PyD3XX.FT_OK:
        print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO GET TRANSFER PARAMS: ABORTING")
        exit()
    print("---| Channel " + str(i+1) + " DEFAULT Transfer Params |---")
    print("  wStructSize = " + str(TransferParams[i].wStructSize) + " bytes")
    for j in range(PyD3XX.FT_PIPE_DIR_COUNT):
        print("  " + ("OUT" if (j == PyD3XX.FT_PIPE_DIR_OUT) else "IN") + " PIPE PARAMS")
        print("    " + ("Pipe is DISABLED!" if TransferParams[i].pipe[j].fPipeNotUsed else "Pipe is ENABLED!"))
        print("    " + ("Pipe is NOT THREAD SAFE!" if TransferParams[i].pipe[j].fNonThreadSafeTransfer else "Pipe is THREAD SAFE!"))
        print("    " + "bURBCount = " + str(TransferParams[i].pipe[j].bURBCount))
        print("    " + "wURBBufferCount = " + str(TransferParams[i].pipe[j].wURBBufferCount))
        print("    " + "dwURBBufferSize = " + str(TransferParams[i].pipe[j].dwURBBufferSize))
        print("    " + "dwStreamingSize = " + str(TransferParams[i].pipe[j].dwStreamingSize))
    print("  fStopReadingOnURBUnderrun = " + str(TransferParams[i].fStopReadingOnURBUnderrun))
    print("  fKeepDeviceSideBufferAfterReopen = " + str(TransferParams[i].fKeepDeviceSideBufferAfterReopen))

PyD3XX.FT_Close(Device) # Close device.
if(Status != PyD3XX.FT_OK):
    print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO CLOSE DEVICE: ABORTING")
    exit()
print("Successfully closed device!\n")

# Set custom params. Purely for example!
for j in range(PyD3XX.FT_PIPE_DIR_COUNT):
    TransferParams[0].pipe[j].fPipeNotUsed = True
    TransferParams[0].pipe[j].fNonThreadSafeTransfer = True
    TransferParams[0].pipe[j].bURBCount = int(TransferParams[0].pipe[j].bURBCount / 2 + j)
    TransferParams[0].pipe[j].wURBBufferCount = int(TransferParams[0].pipe[j].wURBBufferCount / 2 + j)
    TransferParams[0].pipe[j].dwURBBufferSize = int(TransferParams[0].pipe[j].dwURBBufferSize / 2 + j)
    TransferParams[0].pipe[j].dwStreamingSize = int(TransferParams[0].pipe[j].dwStreamingSize / 2 + j)
    TransferParams[0].fStopReadingOnURBUnderrun = True
    TransferParams[0].fKeepDeviceSideBufferAfterReopen = True

for i in range(CHANNEL_COUNT):
    Status = PyD3XX.FT_SetTransferParams(TransferParams[0], i)
    if Status != PyD3XX.FT_OK:
        print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO SET TRANSFER PARAMS: ABORTING")
        exit()
print("Set transfer parameters, waiting 5 seconds...")
time.sleep(5)
Status = PyD3XX.FT_Create(0, PyD3XX.FT_OPEN_BY_INDEX, Device) # Open the device we're using.
if Status != PyD3XX.FT_OK:
    print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO OPEN DEVICE: ABORTING")
    exit()
print("Successfully opened device!")

TransferParams = {}
for i in range(CHANNEL_COUNT):
    Status, TransferParams[i] = PyD3XX.FT_GetTransferParams(i)
    if Status != PyD3XX.FT_OK:
        print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO GET TRANSFER PARAMS: ABORTING")
        exit()
    print("---| Channel " + str(i+1) + " NEW Transfer Params |---")
    print("  wStructSize = " + str(TransferParams[i].wStructSize) + " bytes")
    for j in range(PyD3XX.FT_PIPE_DIR_COUNT):
        print("  " + ("OUT" if (j == PyD3XX.FT_PIPE_DIR_OUT) else "IN") + " PIPE PARAMS")
        print("    " + ("Pipe is DISABLED!" if TransferParams[i].pipe[j].fPipeNotUsed else "Pipe is ENABLED!"))
        print("    " + ("Pipe is NOT THREAD SAFE!" if TransferParams[i].pipe[j].fNonThreadSafeTransfer else "Pipe is THREAD SAFE!"))
        print("    " + "bURBCount = " + str(TransferParams[i].pipe[j].bURBCount))
        print("    " + "wURBBufferCount = " + str(TransferParams[i].pipe[j].wURBBufferCount))
        print("    " + "dwURBBufferSize = " + str(TransferParams[i].pipe[j].dwURBBufferSize))
        print("    " + "dwStreamingSize = " + str(TransferParams[i].pipe[j].dwStreamingSize))
    print("  fStopReadingOnURBUnderrun = " + str(TransferParams[i].fStopReadingOnURBUnderrun))
    print("  fKeepDeviceSideBufferAfterReopen = " + str(TransferParams[i].fKeepDeviceSideBufferAfterReopen))

PyD3XX.FT_Close(Device) # Close device.
if(Status != PyD3XX.FT_OK):
    print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO CLOSE DEVICE: ABORTING")
    exit()
print("Successfully closed device!\n")