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

Status, ChipConfiguration = PyD3XX.FT_GetChipConfiguration(Device) # Get chip configuration.
CallbackNotificationsEnabled = (ChipConfiguration.OptionalFeatureSupport & PyD3XX.CONFIGURATION_OPTIONAL_FEATURE_ENABLENOTIFICATIONMESSAGE_INCHALL) != 0
if(PyD3XX.Platform != "windows"):
    print("FT_SetSuspendTimeout is only available on Windows!")
    exit()
if(CallbackNotificationsEnabled != False): # Can only disable suspend timeout if callback notifications are disabled.
    print("WARNING: Callback notifications are enabled!")
Status = PyD3XX.FT_SetSuspendTimeout(Device, 0) # Disable suspend timeout so CLK is always outputted.
if Status != PyD3XX.FT_OK:
    print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO DISABLE SUSPEND MODE: ABORTING")
    exit()
Status, SuspendTimeout = PyD3XX.FT_GetSuspendTimeout(Device)
if (Status != PyD3XX.FT_OK) or (SuspendTimeout != 0):
    print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO CONFIRM SUSPEND MODE: ABORTING")
    exit()
print("Successfully disabled suspend mode!");

PyD3XX.FT_Close(Device)