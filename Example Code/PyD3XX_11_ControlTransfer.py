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

Buffer = PyD3XX.FT_Buffer(1)
SetupPacket = PyD3XX.FT_SetupPacket
SetupPacket.RequestType = int("10000001", 2)
SetupPacket.Request = 10
SetupPacket.Value = 0
SetupPacket.Index = 1
SetupPacket.Length = 1
Status, DataWritten = PyD3XX.FT_ControlTransfer(Device, SetupPacket, Buffer, 1)
if Status != PyD3XX.FT_OK:
    print("WARNING: FAILED TO GET ALTERNATE SETTINGS OF INTERFACE 1 FROM DEVICE 0.")
print("Alternate Settings of Interface 1: " + hex(int.from_bytes(Buffer.Value(), "little")))

PyD3XX.FT_Close(Device)