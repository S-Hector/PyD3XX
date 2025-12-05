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
    print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO CONFIRM DEVICE: ABORTING")
    exit()
DevicePath = "\\\\?\\usb#vid_0403&pid_601e#44TXERgJa3h2IHD#{36fc9e60-c465-11cf-8056-444553540000}"
Status = PyD3XX.FT_IsDevicePath(Device, DevicePath)
if Status != PyD3XX.FT_OK:
    print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO CONFIRM DEVICE PATH.")
else:
    print("SUCCESSFULLY CONFIRMED DEVICE PATH.")

PyD3XX.FT_Close(Device)