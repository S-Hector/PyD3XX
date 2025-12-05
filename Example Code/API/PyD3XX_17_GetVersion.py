import PyD3XX

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
    print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO CONFIRM DEVICE: ABORTING")
    exit()

Status, DriverVersion = PyD3XX.FT_GetDriverVersion(Device)
if(PyD3XX.Platform == "windows"):
    print("Device 0 Driver Version: " + format((DriverVersion & int("0xFF000000", 16)) >> 24, 'x') + '.' \
        + format((DriverVersion & int("0x00FF0000", 16)) >> 16, 'x') + '.' \
        + format((DriverVersion & int("0x0000FF00", 16)) >> 8, 'x') + '.' \
        + format(DriverVersion & int("0x000000FF", 16), 'x')
        )
else:
    print("Device 0 Driver Version: " + str((DriverVersion & int("0xFF000000", 16)) >> 24) + '.' \
        + str((DriverVersion & int("0x00FF0000", 16)) >> 16) + '.' \
        + str(DriverVersion & int("0x0000FFFF", 16))
        )
Status, DriverVersion = PyD3XX.GetDriverVersion(Device)
print("Device 0 Driver Version: " + DriverVersion)
if(PyD3XX.Platform == "windows"):
    Status, LibraryVersion = PyD3XX.FT_GetLibraryVersion()
    print("Device 0 Library Version: " + format((LibraryVersion & int("0xFF000000", 16)) >> 24, 'x') + '.' \
        + format((LibraryVersion & int("0x00FF0000", 16)) >> 16, 'x') + '.' \
        + format((LibraryVersion & int("0x0000FF00", 16)) >> 8, 'x') + '.' \
        + format(LibraryVersion & int("0x000000FF", 16), 'x')
        )
else:
    Status, LibraryVersion = PyD3XX.FT_GetLibraryVersion()
    print("Device 0 Library Version: " + str((LibraryVersion & int("0xFF000000", 16)) >> 24) + '.' \
        + str((LibraryVersion & int("0x00FF0000", 16)) >> 16) + '.' \
        + str(LibraryVersion & int("0x0000FFFF", 16))
        )

Status, LibraryVersion = PyD3XX.GetLibraryVersion()
print("Device 0 Library Version: " + LibraryVersion)