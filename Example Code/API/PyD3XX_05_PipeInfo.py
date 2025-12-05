import PyD3XX

PyD3XX.SetPrintLevel(PyD3XX.PRINT_NONE) # Make PyD3XX not print anything.

CHANNEL_COUNT = 4 # How many channels your FT60X device is configured to have.

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
for i in range(CHANNEL_COUNT * 2): # Print info for all pipes for interface 1.
    Status, Pipes[i] = PyD3XX.FT_GetPipeInformation(Device, 1, i) # Get pipe information.
    if Status != PyD3XX.FT_OK:
        print("FAILED TO GET PIPE INFO OF [1," + str(i) +"]: ABORTING")
        exit()
    print("---| Pipe " + str(i) + " |---")
    print("\tPipe Type = " + hex(Pipes[i].PipeType))
    print("\tPipe ID = " + hex(Pipes[i].PipeID))
    print("\tPipe MaxPacketSize = " + str(Pipes[i].MaximumPacketSize))
    print("\tPipe Interval = " + str(Pipes[i].Interval))

PyD3XX.FT_Close(Device)