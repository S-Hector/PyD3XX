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

# Getting a string descriptor of the opened device just for show.
Status, StringDescriptor = PyD3XX.FT_GetStringDescriptor(Device, 2)
#Status, StringDescriptor, BytesTransferred = PyD3XX.FT_GetDescriptor(Device, PyD3XX.FT_STRING_DESCRIPTOR_TYPE, 2)
if Status != PyD3XX.FT_OK:
    print("FAILED TO GET THE STRING DESCRIPTOR FOR DEVICE 0: ABORTING.")
    exit()
print("---| Device 0 String[2] Descriptor |---")
print("\tLength = " + str(StringDescriptor.bLength))
print("\tDescriptor Type = " + hex(StringDescriptor.bDescriptorType))
print("\tString = '" + StringDescriptor.szString + "'")

# Getting device descriptor of opened device just for show.
Status, DeviceDescriptor = PyD3XX.FT_GetDeviceDescriptor(Device)
#Status, DeviceDescriptor, BytesTransferred = PyD3XX.FT_GetDescriptor(Device, PyD3XX.FT_DEVICE_DESCRIPTOR_TYPE, 0)
if Status != PyD3XX.FT_OK:
    print("FAILED TO GET DEVICE DESCRIPTOR FOR DEVICE 0: ABORTING.")
    exit()
print("---| Device 0 Device Descriptor |---")
print("\tLength = " + str(DeviceDescriptor.bLength))
print("\tDescriptor Type = " + hex(DeviceDescriptor.bDescriptorType))
print("\tcdUSB = " + hex(DeviceDescriptor.bcdUSB))
print("\tDevice Class = " + hex(DeviceDescriptor.bDeviceClass))
print("\tDevice Sub-Class = " + hex(DeviceDescriptor.bDeviceSubClass))
print("\tDevice Protocol = " + hex(DeviceDescriptor.bDeviceProtocol))
print("\tMax Packet Size = " + str(DeviceDescriptor.bMaxPacketSize0))
print("\tVendor ID = " + hex(DeviceDescriptor.idVendor))
print("\tProduct ID = " + hex(DeviceDescriptor.idProduct))
print("\tcdDevice = " + hex(DeviceDescriptor.bcdDevice))
print("\tManufacturer = " + hex(DeviceDescriptor.iManufacturer))
print("\tProduct = " + hex(DeviceDescriptor.iProduct))
print("\tSerial Number = " + hex(DeviceDescriptor.iSerialNumber))
print("\tNum Configurations = " + str(DeviceDescriptor.bNumConfigurations))

# Getting configuration descriptor of opened device just for show.
Status, ConfigurationDescriptor = PyD3XX.FT_GetConfigurationDescriptor(Device)
#Status, ConfigurationDescriptor, BytesTransferred = PyD3XX.FT_GetDescriptor(Device, PyD3XX.FT_CONFIGURATION_DESCRIPTOR_TYPE, 0)
if Status != PyD3XX.FT_OK:
    print("FAILED TO GET THE CONFIGURATION DESCRIPTOR FOR DEVICE 0: ABORTING.")
    exit()
print("---| Device 0 Configuration Descriptor |---")
print("\tLength = " + str(ConfigurationDescriptor.bLength))
print("\tDescriptor Type = " + hex(ConfigurationDescriptor.bDescriptorType))
print("\tTotal Length = " + str(ConfigurationDescriptor.wTotalLength))
print("\tNum Interfaces = " + str(ConfigurationDescriptor.bNumInterfaces))
print("\tConfiguration Value = " + hex(ConfigurationDescriptor.iConfiguration))
print("\tbmAttributes = " + hex(ConfigurationDescriptor.bmAttributes))
print("\tMaxPower = " + str(ConfigurationDescriptor.MaxPower))

# Getting interface descriptor of opened device just for show. Using index 1 for data transfers.
Status, Interface = PyD3XX.FT_GetInterfaceDescriptor(Device, 1) # Index 0 is for proprietary protocols. Using 1 instead.
#Status, Interface, BytesTransferred = PyD3XX.FT_GetDescriptor(Device, PyD3XX.FT_INTERFACE_DESCRIPTOR_TYPE, 1)
if Status != PyD3XX.FT_OK:
    print("FAILED TO GET INTERFACE INFO OF [1]: ABORTING")
    exit()
print("---| Interface 1 |---")
print("\tLength = " + hex(Interface.bLength))
print("\tDescriptor Type = " + hex(Interface.bDescriptorType))
print("\tInterface Number = " + hex(Interface.bInterfaceNumber))
print("\tAlternate Setting = " + hex(Interface.bAlternateSetting))
print("\t# of Endpoints = " + str(Interface.bNumEndpoints))
print("\tInterface Class = " + hex(Interface.bInterfaceClass))
print("\tInterface Sub Class = " + hex(Interface.bInterfaceSubClass))
print("\tInterface Protocol = " + hex(Interface.bInterfaceProtocol))
print("\tiInterface= " + hex(Interface.iInterface))

PyD3XX.FT_Close(Device)