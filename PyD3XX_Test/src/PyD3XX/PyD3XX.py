# Created by Hector Soto
# A Python conversion of the FTD3XX library.

import ctypes
import ctypes.wintypes
import typing
import platform as _Platform
import subprocess
import locale

from importlib.resources import files as _files
from sys import platform as Platform

# ---| Python Library Specific Definitions |---

VERSION = "1.1.0"
VERSION_TEST = "1.0.67_moní_ourá"

PRINT_NONE =            int("00000", 2) # Print no messages.
PRINT_ERROR_CRITICAL =  int("00001", 2) # Print critical error messages.
PRINT_ERROR_MAJOR =     int("00010", 2) # Print major error messages.
PRINT_ERROR_MINOR =     int("00100", 2) # Print minor error messages.
PRINT_ERROR_ALL =       int("00111", 2) # Print all error messages.

PRINT_INFO_START =      int("01000", 2) # Print informational startup messages.
PRINT_INFO_DEVICE =     int("10000", 2) # Print device information.
PRINT_INFO_ALL =        int("11000", 2) # Print all informational messages.
PRINT_ALL =             int("11111", 2) # Print all messages.

_PrintLevel = PRINT_NONE # What levels of printing are allowed.
_PrintQueue = []

def SetPrintLevel(PrintLevel: int):
    global _PrintLevel
    global _PrintQueue
    _PrintLevel = PrintLevel
    if _PrintQueue:
        for Message in _PrintQueue:
            _Print(Message[0], Message[1], False)
        _PrintQueue = []
    return FT_OK

def _Print(Message: str, Level: int, Queue: bool):
    if Queue:
        _PrintQueue.append([Message, Level])
    elif(Level & PRINT_ERROR_CRITICAL & _PrintLevel):
        print("PyD3XX - CRITICAL ERROR: " + Message)
    elif(Level & PRINT_ERROR_MAJOR & _PrintLevel):
        print("PyD3XX - MAJOR ERROR: " + Message)
    elif(Level & PRINT_ERROR_MINOR & _PrintLevel):
        print("PyD3XX - MINOR ERROR: " + Message)
    elif(Level & PRINT_INFO_START & _PrintLevel):
        print("PyD3XX - Startup INFO: " + Message)

# Determine OS and type sizes.

if (Platform.startswith("linux")):
    Platform = "linux"
elif (Platform.startswith("win")):
    Platform = "windows"
elif (Platform.startswith("darwin")):
    Platform = "darwin"
elif (Platform.startswith("cygwin")):
    Platform = "windows"
else: # Default to linux if we didn't catch the platform.
    _Print("OS UNKNOWN: Assuming OS is linux.", PRINT_INFO_START, True)
    Platform = "linux"

if Platform == "linux":
    import gc

_IsARM = _Platform.machine().startswith('arm') or _Platform.machine().startswith('aarch64')

if ((Platform == "linux") or (Platform == "darwin")): #Fix type sizes for Linux and macOS
    ctypes.c_ulong = ctypes.c_int32
    ctypes.wintypes.DWORD = ctypes.c_int32

SIZE_UINT = ctypes.sizeof(ctypes.c_uint)
SIZE_ULONG = ctypes.sizeof(ctypes.c_ulong)
SIZE_SHORT = ctypes.sizeof(ctypes.c_short)
SIZE_CHAR = ctypes.sizeof(ctypes.c_char)
SIZE_WCHAR = ctypes.sizeof(ctypes.c_wchar)
SIZE_PTR = ctypes.sizeof(ctypes.c_void_p)
SIZE_DWORD = ctypes.sizeof(ctypes.wintypes.DWORD)
SIZE_DEVICE_DESCRIPTOR = (SIZE_CHAR * 10) + (SIZE_SHORT * 4)
SIZE_CONFIGURATION_DESCRIPTOR = (SIZE_CHAR * 7) + SIZE_SHORT
SIZE_INTERFACE_DESCRIPTOR = SIZE_CHAR * 9
SIZE_STRING_DESCRIPTOR = (SIZE_CHAR * 2) + (SIZE_WCHAR * 256)
SIZE_ENDPOINT_DESCRIPTOR = (SIZE_CHAR * 5) + SIZE_SHORT

# ---| FTD3XX C/C++ HEADER EQUIVALENT STARTS HERE |---
# THIS IS NOT A FULL EQUIVALENT TO THE FTD3XX HEADER.
# I HAVE TAKEN MY OWN LIBERTIES ON HOW TO REPRESENT STRUCTS.

NULL = ctypes.c_void_p(0)

# FT_Status values.
FT_OK = 0
FT_INVALID_HANDLE = 1
FT_DEVICE_NOT_FOUND = 2
FT_DEVICE_NOT_OPENED = 3
FT_IO_ERROR = 4
FT_INSUFFICIENT_RESOURCES = 5
FT_INVALID_PARAMETER = 6
FT_INVALID_BAUD_RATE = 7
FT_DEVICE_NOT_OPENED_FOR_ERASE = 8
FT_DEVICE_NOT_OPENED_FOR_WRITE = 9
FT_FAILED_TO_WRITE_DEVICE = 10
FT_EEPROM_READ_FAILED = 11
FT_EEPROM_WRITE_FAILED = 12
FT_EEPROM_ERASE_FAILED = 13
FT_EEPROM_NOT_PRESENT = 14
FT_EEPROM_NOT_PROGRAMMED = 15
FT_INVALID_ARGS = 16
FT_NOT_SUPPORTED = 17
FT_NO_MORE_ITEMS = 18
FT_TIMEOUT = 19
FT_OPERATION_ABORTED = 20
FT_RESERVED_PIPE = 21
FT_INVALID_CONTROL_REQUEST_DIRECTION = 22
FT_INVALID_CONTROL_REQUEST_TYPE = 23
FT_IO_PENDING = 24
FT_IO_INCOMPLETE = 25
FT_HANDLE_EOF = 26
FT_BUSY = 27
FT_NO_SYSTEM_RESOURCES = 28
FT_DEVICE_LIST_NOT_READY = 29
FT_DEVICE_NOT_CONNECTED = 30
FT_INCORRECT_DEVICE_PATH = 31
FT_OTHER_ERROR = 32

# Describe dictionaries for easier error code conversion.
FT_STATUS_STR = {
    FT_OK: "FT_OK",
    FT_INVALID_HANDLE: "FT_INVALID_HANDLE",
    FT_DEVICE_NOT_FOUND: "FT_DEVICE_NOT_FOUND",
    FT_DEVICE_NOT_OPENED: "FT_DEVICE_NOT_OPENED",
    FT_IO_ERROR: "FT_IO_ERROR",
    FT_INSUFFICIENT_RESOURCES: "FT_INSUFFICIENT_RESOURCES",
    FT_INVALID_PARAMETER: "FT_INVALID_PARAMETER",
    FT_INVALID_BAUD_RATE: "FT_INVALID_BAUD_RATE",
    FT_DEVICE_NOT_OPENED_FOR_ERASE: "FT_DEVICE_NOT_OPENED_FOR_ERASE",
    FT_DEVICE_NOT_OPENED_FOR_WRITE: "FT_DEVICE_NOT_OPENED_FOR_WRITE",
    FT_FAILED_TO_WRITE_DEVICE: "FT_FAILED_TO_WRITE_DEVICE",
    FT_EEPROM_READ_FAILED: "FT_EEPROM_READ_FAILED",
    FT_EEPROM_WRITE_FAILED: "FT_EEPROM_WRITE_FAILED",
    FT_EEPROM_ERASE_FAILED: "FT_EEPROM_ERASE_FAILED",
    FT_EEPROM_NOT_PRESENT: "FT_EEPROM_NOT_PRESENT",
    FT_EEPROM_NOT_PROGRAMMED: "FT_EEPROM_NOT_PROGRAMMED",
    FT_INVALID_ARGS: "FT_INVALID_ARGS",
    FT_NOT_SUPPORTED: "FT_NOT_SUPPORTED",
    FT_NO_MORE_ITEMS: "FT_NO_MORE_ITEMS",
    FT_TIMEOUT: "FT_TIMEOUT",
    FT_OPERATION_ABORTED: "FT_OPERATION_ABORTED",
    FT_RESERVED_PIPE: "FT_RESERVED_PIPE",
    FT_INVALID_CONTROL_REQUEST_DIRECTION: "FT_INVALID_CONTROL_REQUEST_DIRECTION",
    FT_INVALID_CONTROL_REQUEST_TYPE: "FT_INVALID_CONTROL_REQUEST_TYPE",
    FT_IO_PENDING: "FT_IO_PENDING",
    FT_IO_INCOMPLETE: "FT_IO_INCOMPLETE",
    FT_HANDLE_EOF: "FT_HANDLE_EOF",
    FT_BUSY: "FT_BUSY",
    FT_NO_SYSTEM_RESOURCES: "FT_NO_SYSTEM_RESOURCES",
    FT_DEVICE_LIST_NOT_READY: "FT_DEVICE_LIST_NOT_READY",
    FT_DEVICE_NOT_CONNECTED: "FT_DEVICE_NOT_CONNECTED",
    FT_INCORRECT_DEVICE_PATH: "FT_INCORRECT_DEVICE_PATH",
    FT_OTHER_ERROR: "FT_OTHER_ERROR"
}
#^ FT_STATUS_STR[FT_OTHER_ERROR] == FT_STATUS_STR[32] == "FT_OTHER_ERROR"
FT_STATUS = {v: k for k, v in FT_STATUS_STR.items()}
#^ FT_STATUS["FT_OTHER_ERROR"] == FT_OTHER_ERROR == 32

FT_DEVICE_UNKNOWN = 3
FT_DEVICE_600 = 600
FT_DEVICE_601 = 601
FT_FLAGS_OPENED = 1
FT_FLAGS_HISPEED = 2
FT_FLAGS_SUPERSPEED = 4
FTPipeTypeControl = 0
FTPipeTypeIsochronous = 1
FTPipeTypeBulk = 2
FTPipeTypeInterrupt = 3
FT_LIST_NUMBER_ONLY = int("0x80000000", 16)
FT_LIST_BY_INDEX = int("0x40000000", 16)
FT_LIST_ALL = int("0x20000000", 16)
FT_OPEN_BY_SERIAL_NUMBER = int("0x00000001", 16)
FT_OPEN_BY_DESCRIPTION = int("0x00000002", 16)
FT_OPEN_BY_LOCATION = int("0x00000004", 16)
FT_OPEN_BY_GUID = int("0x00000008", 16)
FT_OPEN_BY_INDEX = int("0x00000010", 16)
FT_GPIO_DIRECTION_IN = 0
FT_GPIO_DIRECTION_OUT = 1
FT_GPIO_VALUE_LOW = 0
FT_GPIO_VALUE_HIGH = 1
FT_GPIO_0 = 0
FT_GPIO_1 = 1
E_FT_NOTIFICATION_CALLBACK_TYPE_DATA = 0
E_FT_NOTIFICATION_CALLBACK_TYPE_GPIO = 1
E_FT_NOTIFICATION_CALLBACK_TYPE_INTERRUPT = 2
CONFIGURATION_OPTIONAL_FEATURE_DISABLEALL = 0
CONFIGURATION_OPTIONAL_FEATURE_ENABLEBATTERYCHARGING = int("0x001", 16)
CONFIGURATION_OPTIONAL_FEATURE_DISABLECANCELSESSIONUNDERRUN = int("0x002",16)
CONFIGURATION_OPTIONAL_FEATURE_ENABLENOTIFICATIONMESSAGE_INCH1 = int("0x004", 16)
CONFIGURATION_OPTIONAL_FEATURE_ENABLENOTIFICATIONMESSAGE_INCH2 = int("0x008", 16)
CONFIGURATION_OPTIONAL_FEATURE_ENABLENOTIFICATIONMESSAGE_INCH3 = int("0x010", 16)
CONFIGURATION_OPTIONAL_FEATURE_ENABLENOTIFICATIONMESSAGE_INCH4 = int("0x020", 16)
CONFIGURATION_OPTIONAL_FEATURE_ENABLENOTIFICATIONMESSAGE_INCHALL = int("0x03C", 16)
CONFIGURATION_OPTIONAL_FEATURE_DISABLEUNDERRUN_INCH1 = int("0x040", 16)
CONFIGURATION_OPTIONAL_FEATURE_DISABLEUNDERRUN_INCH2 = int("0x080", 16)
CONFIGURATION_OPTIONAL_FEATURE_DISABLEUNDERRUN_INCH3 = int("0x100", 16)
CONFIGURATION_OPTIONAL_FEATURE_DISABLEUNDERRUN_INCH4 = int("0x200", 16)
CONFIGURATION_OPTIONAL_FEATURE_SUPPORT_ENABLE_FIFO_IN_SUSPEND = int("0x400", 16)
# available in RevB parts only
CONFIGURATION_OPTIONAL_FEATURE_SUPPORT_DISABLE_CHIP_POWERDOWN = int("0x800", 16)
# available in RevB parts only
CONFIGURATION_OPTIONAL_FEATURE_DISABLEUNDERRUN_INCHALL = int("0x3C0", 16)
CONFIGURATION_OPTIONAL_FEATURE_ENABLEALL = int("0xFFFF", 16)

FT_DEVICE_DESCRIPTOR_TYPE = int("0x01", 16)
FT_CONFIGURATION_DESCRIPTOR_TYPE = int("0x02", 16)
FT_STRING_DESCRIPTOR_TYPE = int("0x03", 16)
FT_INTERFACE_DESCRIPTOR_TYPE = int("0x04", 16)
FT_ENDPOINT_DESCRIPTOR_TYPE = int("0x05", 16) # THIS IS PYTHON API SPECIFIC.

class FT_Buffer:
    def __init__(self, Size: int = None):
        if(isinstance(Size, int)):
            self._RawAddress = ctypes.c_buffer(init=0, size=Size)
            self._Length = Size
        else:
            self._RawAddress = "FT_OTHER_ERROR"
            self._Length = 0

    def from_int(Integer: int):
        NewBuffer = FT_Buffer()
        if(isinstance(Integer, int)):
            NewBuffer._RawAddress = ctypes.c_buffer(Integer.to_bytes(SIZE_UINT, "little"), SIZE_UINT)
            NewBuffer._Length = SIZE_UINT
        else:
            _Print("FT_Buffer(int), not given an int!", PRINT_ERROR_MINOR, False)
        return NewBuffer
    def from_str(String: str):
        NewBuffer = FT_Buffer()
        if(isinstance(String, str)):
            NewBuffer._Length = len(String) + 1
            NewBuffer._RawAddress = ctypes.create_string_buffer(init=String.encode("ascii"))
        else:
            _Print("FT_Buffer(str), not given a str!", PRINT_ERROR_MINOR, False)
        return NewBuffer
    def from_bytearray(ByteArray: bytearray):
        NewBuffer = FT_Buffer()
        if(isinstance(ByteArray, bytearray)):
            NewBuffer._Length = len(ByteArray)
            NewBuffer._RawAddress = ctypes.c_buffer(init=bytes(ByteArray), size=NewBuffer._Length)
        else:
            _Print("FT_Buffer(bytearray), not given a bytearray!", PRINT_ERROR_MINOR, False)
        return NewBuffer
    def from_bytes(Bytes: bytes):
        NewBuffer = FT_Buffer()
        if(isinstance(Bytes, bytes)):
            NewBuffer._Length = len(Bytes)
            NewBuffer._RawAddress = ctypes.c_buffer(init=Bytes, size=NewBuffer._Length)
        else:
            _Print("FT_Buffer(bytes), not given bytes!", PRINT_ERROR_MINOR, False)
        return NewBuffer

        # Value has to be a function, a variable version of "Value" will not update in real time.
        # ^ If Value was a variable, it can sometimes falsely be zero if read calls happen too often.
        # By keeping Value as a function call, we always get correct data.
        # Never change Value to a variable. Always leave it as a function.
    def Value(self) -> bytearray:
        if isinstance(self._RawAddress, str):
            return self._RawAddress.encode("ascii")
        return bytearray(self._RawAddress)

class FT_Device:
    Handle = "FT_OTHER_ERROR"
    Flags = 0
    Type = 0
    ID = 0
    LocID = 0
    SerialNumber = ""
    Description = ""
    _Handle = "FT_OTHER_ERROR"
    _Flags = 0
    _Type = 0
    _ID = 0
    _LocID = 0
    _SerialNumber = 0
    _Description = 0

def _CreateDevice():
    NewDevice = FT_Device()
    NewDevice._Handle = ctypes.c_void_p(0)
    NewDevice._Flags = ctypes.c_ulong(0)
    NewDevice._Type = ctypes.c_ulong(0)
    NewDevice._ID = ctypes.c_ulong(0)
    NewDevice._LocID = ctypes.wintypes.DWORD(0)
    # The buffers should be 16, and 32.
    # However, Linux dynamic libraries require different sizes.
    NewDevice._SerialNumber = ctypes.create_string_buffer(25)
    NewDevice._Description = ctypes.create_string_buffer(33)
    NewDevice.SerialNumber = ""
    NewDevice.Description = ""
    return NewDevice

class FT_DeviceDescriptor:
    bLength = 0
    bDescriptorType = 0
    bcdUSB = 0
    bDeviceClass = 0
    bDeviceSubClass = 0
    bDeviceProtocol = 0
    bMaxPacketSize0 = 0
    idVendor = 0
    idProduct = 0
    bcdDevice = 0
    iManufacturer = 0
    iProduct = 0
    iSerialNumber = 0
    bNumConfigurations = 0
    _RawAddress = "FT_OTHER_ERROR"
    _bLength = 0
    _bDescriptorType = 0
    _bcdUSB = 0
    _bDeviceClass = 0
    _bDeviceSubClass = 0
    _bDeviceProtocol = 0
    _bMaxPacketSize0 = 0
    _idVendor = 0
    _idProduct = 0
    _bcdDevice = 0
    _iManufacturer = 0
    _iProduct = 0
    _iSerialNumber = 0
    _bNumConfigurations = 0

class FT_ConfigurationDescriptor:
    bLength = 0
    bDescriptorType = 0
    wTotalLength = 0
    bNumInterfaces = 0
    bConfigurationValue = 0
    iConfiguration = 0
    bmAttributes = 0
    MaxPower = 0
    _RawAddress = "FT_OTHER_ERROR"
    _bLength = 0
    _bDescriptorType = 0
    _wTotalLength = 0
    _bNumInterfaces = 0
    _bConfigurationValue = 0
    _iConfiguration = 0
    _bmAttributes = 0
    _MaxPower = 0

class FT_InterfaceDescriptor:
    bLength = 0
    bDescriptorType = 0
    bInterfaceNumber = 0
    bAlternateSetting = 0
    bNumEndpoints = 0
    bInterfaceClass = 0
    bInterfaceSubClass = 0
    bInterfaceProtocol = 0
    iInterface = 0
    _RawAddress = "FT_OTHER_ERROR"
    _bLength = 0
    _bDescriptorType = 0
    _bInterfaceNumber = 0
    _bAlternateSetting = 0
    _bNumEndpoints = 0
    _bInterfaceClass = 0
    _bInterfaceSubClass = 0
    _bInterfaceProtocol = 0
    _iInterface = 0

class FT_StringDescriptor:
    bLength = 0
    bDescriptorType = 0
    szString = ""
    _RawAddress = "FT_OTHER_ERROR"
    _bLength = 0
    _bDescriptorType = 0
    _szString = ""

class FT_EndpointDescriptor: # THIS IS PYTHON API SPECIFIC.
    bLength = 0
    bDescriptorType = 0
    bEndpointAddress = 0
    bmAttributes = 0
    wMaxPacketSize = 0
    bInterval = 0
    _RawAddress = "FT_OTHER_ERROR"
    _bLength = 0
    _bDescriptorType = 0
    _bEndpointAddress = 0
    _bmAttributes = 0
    _wMaxPacketSize = 0
    _bInterval = 0

class FT_Pipe:
    PipeType = 0
    PipeID = 0
    MaximumPacketSize = 0
    Interval = 0
    _RawAddress = "FT_OTHER_ERROR"
    _PipeType = 0
    _PipeID = 0
    _MaximumPacketSize = 0
    _Interval = 0

class FT_Overlapped:
    Internal = 0
    InternalHigh = 0
    DummyUnion = 0
    DummyUnion_Offset = 0
    DummyUnion_OffsetHigh = 0
    DummyUnion_Pointer = 0
    Handle = 0
    _RawAddress = "FT_OTHER_ERROR"
    _Internal = 0
    _InternalHigh = 0
    _DummyUnion = 0
    _DummyUnion_Offset = 0
    _DummyUnion_OffsetHigh = 0
    _DummyUnion_Pointer = 0
    _Handle = 0

class FT_SetupPacket:
    RequestType = 0
    Request = 0
    Value = 0
    Index = 0
    Length = 0

class FT_60XCONFIGURATION:
    VendorID = 0
    ProductID = 0
    StringDescriptors = 0
    bInterval = 0
    PowerAttributes = 0
    PowerConsumption = 0
    Reserved2 = 0
    FIFOClock = 0
    FIFOMode = 0
    ChannelConfig = 0
    OptionalFeatureSupport = 0
    BatteryChargingGPIOConfig = 0
    FlashEEPROMDetection = 0
    MSIO_Control = 0
    GPIO_Control = 0
    _RawAddress = "FT_OTHER_ERROR"
    _VendorID = 0
    _ProductID = 0
    _StringDescriptors = 0
    _bInterval = 0
    _PowerAttributes = 0
    _PowerConsumption = 0
    _Reserved2 = 0
    _FIFOClock = 0
    _FIFOMode = 0
    _ChannelConfig = 0
    _OptionalFeatureSupport = 0
    _BatteryChargingGPIOConfig = 0
    _FlashEEPROMDetection = 0
    _MSIO_Control = 0
    _GPIO_Control = 0

# ---| END OF EQUIVALENT HEADER PORTION |---

# ---| LIBRARY INCLUSION PART |---
_Python64 = (ctypes.sizeof(ctypes.c_void_p) == 8) # True if 64-bit version of Python is running.
_DriverIsD3XX = False
_DriverIsWinUSB = False
if Platform == "windows": # Check if system has WinUSB D3XX driver installed.
    try: # Check for WinUSB
        _SearchWinUSB = subprocess.Popen("pnputil /enum-drivers", shell=False, stdout=subprocess.PIPE).stdout.read()
    except:
        _SearchWinUSB = subprocess.Popen("/windows/sysnative/pnputil /enum-drivers", shell=False, stdout=subprocess.PIPE).stdout.read()
    if b"ftd3xxwu.inf" in _SearchWinUSB: # Check raw bytes before trying to decode.
        _DriverIsWinUSB = True
    try:
        if not _DriverIsWinUSB: # If raw byte check failed, try again after decoding.
            _DriverIsWinUSB = _SearchWinUSB.decode(locale.getpreferredencoding(False)) # Ignore local encoding.
            if "ftd3xxwu.inf" in _DriverIsWinUSB:
                _DriverIsWinUSB = True
            else:
                _DriverIsWinUSB = False
    except:
        _DriverIsWinUSB = False
    if _DriverIsWinUSB:
        _Print("DETECTED WinUSB: Will use WinUSB dynamic library.", PRINT_INFO_START, True)
    else:
        _Print("DID NOT DETECT WinUSB driver: Will check for D3XX driver.", PRINT_INFO_START, True)
        # Check for FTDI D3XX driver.
        try:
            _SearchD3XX = subprocess.Popen("pnputil /enum-drivers", shell=False, stdout=subprocess.PIPE).stdout.read()
        except:
            _SearchD3XX = subprocess.Popen("/windows/sysnative/pnputil /enum-drivers", shell=False, stdout=subprocess.PIPE).stdout.read()
        if b"ftdibus3.inf" in _SearchD3XX: # Check raw bytes before trying to decode.
            _DriverIsD3XX = True
        try:
            if not _DriverIsD3XX: # If raw byte check failed, try again after decoding.
                _DriverIsD3XX = _SearchD3XX.decode(locale.getpreferredencoding(False))
                if "ftdibus3.inf" in _DriverIsD3XX:
                    _DriverIsD3XX = True
                else:
                    _DriverIsD3XX = False
        except:
            _DriverIsD3XX = False
        if _DriverIsD3XX:
            _Print("DETECTED D3XX driver: Will use D3XX dynamic library.", PRINT_INFO_START, True)
        else:
            _Print("DID NOT DETECT ANY DRIVER. Will try using D3XX dynamic library anyways.", PRINT_ERROR_CRITICAL, True)
            _DriverIsD3XX = True

# ---| Try to Load Dynamic Library |---
_LibraryFile = ""
_LibraryFile += "FTD3XX" if (Platform=="windows") else "libftd3xx"
_LibraryFile += "WU" if (_DriverIsWinUSB) else ""
_LibraryFile += ("_ARM" if (_IsARM) else ("_32" if not(_Python64) else ""))
_LibraryFile += ".dll" if (Platform=="windows") else (".dylib" if (Platform=="darwin") else ".so")
_DLL_Path = str(_files("PyD3XX").joinpath(_LibraryFile))
try:
    if(Platform == "windows"):
        _DLL = ctypes.windll.LoadLibrary(_DLL_Path) # Check if dll exists in same directory as executable.
    else:
        _DLL = ctypes.cdll.LoadLibrary(_DLL_Path) # Check if dll exists in same directory as executable.
except:
    print("PyD3XX ERROR: Did not find '" + _DLL_Path + "', EXITING.")
    exit()
_Print("Successfully loaded D3XX: '" + _LibraryFile + "'", PRINT_INFO_START, True)

# ---| Python-Specific Functions |---

# ---| FTD3XX Python Function Implementations |---
# Python doesn't natively do "pass by reference" like in C++.
# So we return multiple values instead of using ctypes.
# I want Python users to not have to know about or need to use ctypes.

def FT_CreateDeviceInfoList() -> int | int:
    DeviceCount = ctypes.c_ulong(0)
    Status = _DLL.FT_CreateDeviceInfoList(ctypes.byref(DeviceCount))
    return Status, DeviceCount.value # Device count is converted to a Python int.  

def FT_GetDeviceInfoDetail(Index: int) -> int | FT_Device:
    ReturnDevice = _CreateDevice()
    Status = _DLL.FT_GetDeviceInfoDetail(Index,
                                ctypes.byref(ReturnDevice._Flags),
                                ctypes.byref(ReturnDevice._Type),
                                ctypes.byref(ReturnDevice._ID),
                                ctypes.byref(ReturnDevice._LocID),
                                ctypes.byref(ReturnDevice._SerialNumber),
                                ctypes.byref(ReturnDevice._Description),
                                ctypes.byref(ReturnDevice._Handle))
    ReturnDevice.Flags = ReturnDevice._Flags.value
    ReturnDevice.Type = ReturnDevice._Type.value
    ReturnDevice.ID = ReturnDevice._ID.value
    ReturnDevice.LocID = ReturnDevice._LocID.value
    ReturnDevice.SerialNumber = ReturnDevice._SerialNumber.value.decode("ascii")
    ReturnDevice.Description = ReturnDevice._Description.value.decode("ascii")
    ReturnDevice.Handle = ReturnDevice._Handle.value
    return Status, ReturnDevice

def FT_GetDeviceInfoList(DeviceCount: int) -> int | list[FT_Device]:
    DeviceCount = ctypes.c_ulong(DeviceCount)
    Devices = []
    SizeOfDeviceNode = (SIZE_ULONG * 3) + SIZE_DWORD + 16 + 32 + SIZE_PTR
    RawAddress = ctypes.c_buffer(SizeOfDeviceNode * DeviceCount.value)
    Status = _DLL.FT_GetDeviceInfoList(RawAddress, ctypes.byref(DeviceCount))
    if(Status != FT_OK):
        _Print(FT_STATUS_STR[Status] + " | ERROR: FAILED TO GET DEVICE INFO LIST.", PRINT_ERROR_MAJOR, False)
        return Status, [FT_Device()]
    for i in range(DeviceCount.value):
        Devices.append(FT_Device())
        Devices[i]._Flags = ctypes.c_ulong.from_address(ctypes.addressof(RawAddress) + SizeOfDeviceNode*i + 0)
        Devices[i]._Type = ctypes.c_ulong.from_address(ctypes.addressof(RawAddress) + SizeOfDeviceNode*i + SIZE_ULONG)
        Devices[i]._ID = ctypes.c_ulong.from_address(ctypes.addressof(RawAddress) + SizeOfDeviceNode*i + SIZE_ULONG*2)
        Devices[i]._LocID = ctypes.wintypes.DWORD.from_address(ctypes.addressof(RawAddress) + SizeOfDeviceNode*i + SIZE_ULONG*3)
        Devices[i]._SerialNumber = ctypes.c_char_p(ctypes.addressof(RawAddress) + SizeOfDeviceNode*i + SIZE_ULONG*3 + SIZE_DWORD)
        Devices[i]._Description = ctypes.c_char_p(ctypes.addressof(RawAddress) + SizeOfDeviceNode*i + SIZE_ULONG*3 + SIZE_DWORD + 16*SIZE_CHAR)
        Devices[i]._Handle = ctypes.c_void_p(ctypes.addressof(RawAddress) + SizeOfDeviceNode*i + SIZE_ULONG*3 + SIZE_DWORD + 16*SIZE_CHAR + 32*SIZE_CHAR)
        Devices[i].Flags = Devices[i]._Flags.value
        Devices[i].Type = Devices[i]._Type.value
        Devices[i].ID = Devices[i]._ID.value
        Devices[i].LocID = Devices[i]._LocID.value
        Devices[i].SerialNumber = Devices[i]._SerialNumber.value.decode("ascii")
        Devices[i].Description = Devices[i]._Description.value.decode("ascii")
        Devices[i].Handle = Devices[i]._Handle.value
    return Status, Devices

def FT_GetDeviceInfoDict(DeviceCount: int) -> int | dict[int, FT_Device]:
    ReturnStatus = FT_OK
    Devices = {}
    for i in range(0, DeviceCount): # Get device info at each index from 0->(DeviceCount - 1).
        Status, Devices[i] = FT_GetDeviceInfoDetail(i) # Get info of a device at a specific index.
        if Status != FT_OK:
            _Print(FT_STATUS_STR[Status] + " | WARNING: FAILED TO GET INFO FOR DEVICE " + str(i), PRINT_ERROR_MAJOR, False)
            ReturnStatus = FT_OTHER_ERROR, {1: FT_Device()}
    return ReturnStatus, Devices

def FT_ListDevices(IndexCount: int, Flags: int) -> int | (int | str | list[str]):
    Status = FT_OTHER_ERROR
    ReturnValue = FT_OTHER_ERROR
    if(Flags & FT_LIST_NUMBER_ONLY):
        ReturnValue = ctypes.wintypes.DWORD(0)
        Status = _DLL.FT_ListDevices(ctypes.byref(ReturnValue), NULL, Flags)
        if(Status == FT_OK):
            ReturnValue = ReturnValue.value
        else:
            ReturnValue = 0
            _Print(FT_STATUS_STR[Status] + " | FT_ListDevices(), ERROR: FAILED TO LIST DEVICE COUNT.", PRINT_ERROR_MAJOR, False)
    elif(Flags & FT_LIST_BY_INDEX):
        Buffer = ctypes.c_buffer(SIZE_CHAR * 32)
        DeviceIndex = ctypes.wintypes.DWORD(IndexCount)
        Status = _DLL.FT_ListDevices(DeviceIndex, ctypes.byref(Buffer), Flags)
        if(Status == FT_OK):
            ReturnValue = Buffer.value.decode("ascii")
        else:
            ReturnValue = FT_STATUS_STR[Status]
            _Print(FT_STATUS_STR[Status] + " | FT_ListDevices(), ERROR: FAILED TO GET DEVICE INFO.", PRINT_ERROR_MAJOR, False)
    elif(Flags & FT_LIST_ALL):
        ReturnValue = []
        PointerArray = (ctypes.c_void_p * (IndexCount + 1))()
        PointerArray[IndexCount] = NULL
        for i in range(IndexCount):
            PointerArray[i] = ctypes.cast(ctypes.c_buffer(SIZE_CHAR*32), ctypes.c_void_p)
        DeviceCount = ctypes.wintypes.DWORD(IndexCount)
        Status = _DLL.FT_ListDevices(PointerArray, ctypes.byref(DeviceCount), Flags)
        if(Status == FT_OK):
            for i in range(IndexCount):
                ReturnValue.append(ctypes.cast(PointerArray[i], ctypes.c_char_p).value.decode("ascii"))
        else:
            for i in range(IndexCount):
                ReturnValue.append(FT_STATUS_STR[Status])
            _Print(FT_STATUS_STR[Status] + " | FT_ListDevices(), ERROR: FAILED TO GET INFO FOR DEVICES.", PRINT_ERROR_MAJOR, False)
    else:
        _Print(FT_STATUS_STR[Status] + " | FT_ListDevices(), WARNING: NOT GIVEN VALID FLAGS.", PRINT_ERROR_MAJOR, False)
    return Status, ReturnValue

def FT_GetPipeInformation(Device: FT_Device, InterfaceIndex: int, PipeIndex: int) -> int | FT_Pipe:
    NewPipe = FT_Pipe()
    RawSize = SIZE_UINT + SIZE_SHORT + SIZE_SHORT + SIZE_UINT # Overall struct is 4-byte aligned and PipeId is 2-byte aligned.
    NewPipe._RawAddress = ctypes.c_buffer(RawSize)
    Status = _DLL.FT_GetPipeInformation(Device._Handle, InterfaceIndex, PipeIndex, NewPipe._RawAddress)
    if FT_STATUS_STR[Status] != "FT_OK":
        _Print(FT_STATUS_STR[Status] + " | Failed to get pipe information!", PRINT_ERROR_MAJOR, False)
        NewPipe._RawAddress = "FT_OTHER_ERROR"
        return Status, NewPipe # Return bad pipe with ft other error code.
    NewPipe._PipeType = ctypes.c_uint.from_address(ctypes.addressof(NewPipe._RawAddress) + 0)
    NewPipe.PipeType = NewPipe._PipeType.value
    NewPipe._PipeID = ctypes.c_char.from_address(ctypes.addressof(NewPipe._RawAddress) + SIZE_UINT)
    NewPipe.PipeID = int.from_bytes(NewPipe._PipeID.value, "little") # Due to byte alignment this takes up a SHORT amount of space.
    NewPipe._MaximumPacketSize = ctypes.c_ushort.from_address(ctypes.addressof(NewPipe._RawAddress) + SIZE_UINT + SIZE_SHORT)
    NewPipe.MaximumPacketSize = NewPipe._MaximumPacketSize.value
    NewPipe._Interval = ctypes.c_char.from_address(ctypes.addressof(NewPipe._RawAddress) + SIZE_UINT + SIZE_SHORT + SIZE_SHORT)
    NewPipe.Interval = int.from_bytes(NewPipe._Interval.value, "little")
    return Status, NewPipe

def FT_InitializeOverlapped(Device: FT_Device) -> int | FT_Overlapped:
    NewOverlap = FT_Overlapped()
    RawSize = SIZE_PTR + SIZE_PTR + SIZE_DWORD + SIZE_DWORD + SIZE_PTR
    NewOverlap._RawAddress = ctypes.c_buffer(RawSize)
    Status = _DLL.FT_InitializeOverlapped(Device._Handle, NewOverlap._RawAddress)
    if FT_STATUS_STR[Status] != "FT_OK":
        _Print(FT_STATUS_STR[Status] + " | Failed to get overlap information!", PRINT_ERROR_MAJOR, False)
        NewOverlap._RawAddress = "FT_OTHER_ERROR"
        return Status, NewOverlap #Return bad overlap with ft other error code.
    NewOverlap._Internal = ctypes.c_void_p.from_address(ctypes.addressof(NewOverlap._RawAddress) + 0)
    NewOverlap.Internal = NewOverlap._Internal.value
    NewOverlap._InternalHigh = ctypes.c_void_p.from_address(ctypes.addressof(NewOverlap._RawAddress) + SIZE_PTR)
    NewOverlap.InternalHigh = NewOverlap._InternalHigh.value
    NewOverlap._DummyUnion = ctypes.c_void_p.from_address(ctypes.addressof(NewOverlap._RawAddress) + SIZE_PTR + SIZE_PTR)
    NewOverlap.DummyUnion = NewOverlap._DummyUnion.value
    NewOverlap._DummyUnion_Pointer = ctypes.c_void_p.from_address(ctypes.addressof(NewOverlap._RawAddress) + SIZE_PTR + SIZE_PTR)
    NewOverlap.DummyUnion_Pointer = NewOverlap._DummyUnion_Pointer.value
    NewOverlap._DummyUnion_Offset = ctypes.wintypes.DWORD.from_address(ctypes.addressof(NewOverlap._RawAddress) + SIZE_PTR + SIZE_PTR)
    NewOverlap.DummyUnion_Offset = NewOverlap._DummyUnion_Offset.value
    NewOverlap._DummyUnion_OffsetHigh = ctypes.wintypes.DWORD.from_address(ctypes.addressof(NewOverlap._RawAddress) + SIZE_PTR + SIZE_PTR + SIZE_DWORD)
    NewOverlap.DummyUnion_OffsetHigh = NewOverlap._DummyUnion_OffsetHigh.value
    NewOverlap._Handle = ctypes.c_void_p.from_address(ctypes.addressof(NewOverlap._RawAddress) + SIZE_PTR + SIZE_PTR + SIZE_DWORD + SIZE_DWORD)
    NewOverlap.Handle = NewOverlap._Handle.value
    return Status, NewOverlap

def FT_Create(Identifier, OpenFlag: int, Device: FT_Device) -> int:
    Status = FT_OTHER_ERROR
    if(not(isinstance(Device, FT_Device))):
        _Print("FT_Create(), did not get an FT_Device!", PRINT_ERROR_MAJOR, False)
    elif(not(isinstance(Device._Handle, ctypes.c_void_p))):
        _Print("FT_Create(), got an uninitialized or broken FT_Device object!", PRINT_ERROR_MAJOR, False)
    elif(OpenFlag & FT_OPEN_BY_INDEX):
        if(isinstance(Identifier, int)):
            Status = _DLL.FT_Create(Identifier, FT_OPEN_BY_INDEX, ctypes.byref(Device._Handle))
            Device.Handle = Device._Handle.value
        else:
            _Print("FT_Create(), did not get expected int for index!", PRINT_ERROR_MAJOR, False)
    elif(OpenFlag & FT_OPEN_BY_SERIAL_NUMBER):
        if(isinstance(Identifier, str)):
            Status = _DLL.FT_Create(Identifier.encode("ascii"), FT_OPEN_BY_SERIAL_NUMBER, ctypes.byref(Device._Handle))
            Device.Handle = Device._Handle.value
        else:
            _Print("FT_Create(), did not get expected str for serial number!", PRINT_ERROR_MAJOR, False)
    elif(OpenFlag & FT_OPEN_BY_DESCRIPTION):
        if(isinstance(Identifier, str)):
            Status = _DLL.FT_Create(Identifier.encode("ascii"), FT_OPEN_BY_DESCRIPTION, ctypes.byref(Device._Handle))
            Device.Handle = Device._Handle.value
        else:
            _Print("FT_Create(), did not get expected str for description!", PRINT_ERROR_MAJOR, False)
    else:
        _Print("FT_Create(), given invalid open flag!", PRINT_ERROR_MAJOR, False)
    return Status

def FT_Close(Device: FT_Device) -> int:
    return _DLL.FT_Close(Device._Handle)

def FT_SetSuspendTimeout(Device: FT_Device, Timeout: int) -> int:
    Status = FT_OTHER_ERROR
    if Platform != "windows":
        _Print("FT_SetSuspendTimeout() DOES NOT EXIST IN LINUX OR MACOS", PRINT_ERROR_CRITICAL, False)
    else:
        Status = _DLL.FT_SetSuspendTimeout(Device._Handle, ctypes.c_ulong(Timeout))
    return Status

def FT_GetSuspendTimeout(Device: FT_Device) -> int | int:
    Status = FT_OTHER_ERROR
    Timeout = ctypes.c_ulong(0)
    if Platform != "windows":
        _Print("FT_GetSuspendTimeout() DOES NOT EXIST IN LINUX OR MACOS", PRINT_ERROR_CRITICAL, False)
    else:
        Status = _DLL.FT_GetSuspendTimeout(Device._Handle, ctypes.byref(Timeout))
    return Status, Timeout.value

def FT_SetPipeTimeout(Device: FT_Device, Pipe: FT_Pipe, Timeout: int) -> int:
    Timeout = ctypes.c_ulong(Timeout)
    return _DLL.FT_SetPipeTimeout(Device._Handle, Pipe._PipeID, Timeout)

def FT_GetPipeTimeout(Device: FT_Device, Pipe: FT_Pipe) -> int | int:
    if Platform != "windows":
        _Print("FT_GetPipeTimeout() DOES NOT EXIST IN LINUX OR MACOS", PRINT_ERROR_CRITICAL, False)
        return FT_OTHER_ERROR, 0
    TimeOut = ctypes.c_ulong(0)
    Status = _DLL.FT_GetPipeTimeout(Device._Handle, Pipe._PipeID, ctypes.byref(TimeOut))
    return Status, TimeOut.value

def FT_AbortPipe(Device: FT_Device, Pipe: FT_Pipe) -> int:
    return _DLL.FT_AbortPipe(Device._Handle, Pipe._PipeID)

def _GetDeviceDescriptorHelper(Descriptor: FT_DeviceDescriptor) -> FT_DeviceDescriptor:
    Descriptor._bLength = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + 0)
    Descriptor.bLength = int.from_bytes(Descriptor._bLength, "little")
    Descriptor._bDescriptorType = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR)
    Descriptor.bDescriptorType = int.from_bytes(Descriptor._bDescriptorType, "little")
    Descriptor._bcdUSB = ctypes.c_ushort.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*2)
    Descriptor.bcdUSB = int.from_bytes(bytes=Descriptor._bcdUSB, byteorder="little")
    Descriptor._bDeviceClass = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*2 + SIZE_SHORT)
    Descriptor.bDeviceClass = int.from_bytes(Descriptor._bDeviceClass, "little")
    Descriptor._bDeviceSubClass = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*3 + SIZE_SHORT)
    Descriptor.bDeviceSubClass = int.from_bytes(Descriptor._bDeviceSubClass, "little")
    Descriptor._bDeviceProtocol = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*4 + SIZE_SHORT)
    Descriptor.bDeviceProtocol = int.from_bytes(Descriptor._bDeviceProtocol, "little")
    Descriptor._bMaxPacketSize0 = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*5 + SIZE_SHORT)
    Descriptor.bMaxPacketSize0 = int.from_bytes(Descriptor._bMaxPacketSize0, "little")
    Descriptor._idVendor = ctypes.c_ushort.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*6 + SIZE_SHORT)
    Descriptor.idVendor = int.from_bytes(bytes=Descriptor._idVendor, byteorder="little")
    Descriptor._idProduct = ctypes.c_ushort.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*6 + SIZE_SHORT*2)
    Descriptor.idProduct = int.from_bytes(bytes=Descriptor._idProduct, byteorder="little")
    Descriptor._bcdDevice = ctypes.c_ushort.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*6 + SIZE_SHORT*3)
    Descriptor.bcdDevice = int.from_bytes(bytes=Descriptor._idProduct, byteorder="little")
    Descriptor._iManufacturer = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*6 + SIZE_SHORT*4)
    Descriptor.iManufacturer = int.from_bytes(Descriptor._iManufacturer, "little")
    Descriptor._iProduct = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*7 + SIZE_SHORT*4)
    Descriptor.iProduct = int.from_bytes(Descriptor._iProduct, "little")
    Descriptor._iSerialNumber = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*8 + SIZE_SHORT*4)
    Descriptor.iSerialNumber = int.from_bytes(Descriptor._iSerialNumber, "little")
    Descriptor._bNumConfigurations = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*9 + SIZE_SHORT*4)
    Descriptor.bNumConfigurations = int.from_bytes(Descriptor._bNumConfigurations, "little")
    return Descriptor

def FT_GetDeviceDescriptor(Device: FT_Device) -> int | FT_DeviceDescriptor:
    Descriptor = FT_DeviceDescriptor()
    Descriptor._RawAddress = ctypes.c_buffer(SIZE_DEVICE_DESCRIPTOR)
    Status = _DLL.FT_GetDeviceDescriptor(Device._Handle, Descriptor._RawAddress)
    if(Status != FT_OK):
        _Print(FT_STATUS_STR[Status] + " | ERROR: FAILED TO GET DEVICE DESCRIPTOR.", PRINT_ERROR_MAJOR, False)
        Descriptor = FT_DeviceDescriptor()
        return Status, Descriptor
    Descriptor = _GetDeviceDescriptorHelper(Descriptor)
    return Status, Descriptor

def _GetConfigurationDescriptorHelper(Descriptor: FT_ConfigurationDescriptor) -> FT_ConfigurationDescriptor:
    Descriptor._bLength = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + 0)
    Descriptor.bLength = int.from_bytes(Descriptor._bLength, "little")
    Descriptor._bDescriptorType = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR)
    Descriptor.bDescriptorType = int.from_bytes(Descriptor._bDescriptorType, "little")
    Descriptor._wTotalLength = ctypes.c_ushort.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*2)
    Descriptor.wTotalLength = int.from_bytes(bytes=Descriptor._wTotalLength, byteorder="little")
    Descriptor._bNumInterfaces = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*2 + SIZE_SHORT)
    Descriptor.bNumInterfaces = int.from_bytes(Descriptor._bNumInterfaces, "little")
    Descriptor._bConfigurationValue = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*3 + SIZE_SHORT)
    Descriptor.bConfigurationValue = int.from_bytes(Descriptor._bConfigurationValue, "little")
    Descriptor._iConfiguration = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*4 + SIZE_SHORT)
    Descriptor.iConfiguration = int.from_bytes(Descriptor._iConfiguration, "little")
    Descriptor._bmAttributes = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*5 + SIZE_SHORT)
    Descriptor.bmAttributes = int.from_bytes(Descriptor._bmAttributes, "little")
    Descriptor._MaxPower = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*6 + SIZE_SHORT)
    Descriptor.MaxPower = int.from_bytes(Descriptor._MaxPower, "little")
    return Descriptor

def FT_GetConfigurationDescriptor(Device: FT_Device) -> int | FT_ConfigurationDescriptor:
    Descriptor = FT_ConfigurationDescriptor()
    Descriptor._RawAddress = ctypes.c_buffer(SIZE_CONFIGURATION_DESCRIPTOR)
    Status = _DLL.FT_GetConfigurationDescriptor(Device._Handle, Descriptor._RawAddress)
    if(Status != FT_OK):
        _Print(FT_STATUS_STR[Status] + " | ERROR: FAILED TO GET CONFIGURATION DESCRIPTOR.", PRINT_ERROR_MAJOR, False)
        Descriptor = FT_ConfigurationDescriptor()
        return Status, Descriptor
    Descriptor = _GetConfigurationDescriptorHelper(Descriptor)
    return Status, Descriptor

def _GetInterfaceDescriptorHelper(Descriptor: FT_InterfaceDescriptor) -> FT_InterfaceDescriptor:
    Descriptor._bLength = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*0)
    Descriptor.bLength = int.from_bytes(Descriptor._bLength.value, "little")
    Descriptor._bDescriptorType = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*1)
    Descriptor.bDescriptorType = int.from_bytes(Descriptor._bDescriptorType.value, "little")
    Descriptor._bInterfaceNumber = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*2)
    Descriptor.bInterfaceNumber = int.from_bytes(Descriptor._bInterfaceNumber.value, "little")
    Descriptor._bAlternateSetting = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*3)
    Descriptor.bAlternateSetting = int.from_bytes(Descriptor._bAlternateSetting.value, "little")
    Descriptor._bNumEndpoints = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*4)
    Descriptor.bNumEndpoints = int.from_bytes(Descriptor._bNumEndpoints.value, "little")
    Descriptor._bInterfaceClass = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*5)
    Descriptor.bInterfaceClass = int.from_bytes(Descriptor._bInterfaceClass.value, "little")
    Descriptor._bInterfaceSubClass = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*6)
    Descriptor.bInterfaceSubClass = int.from_bytes(Descriptor._bInterfaceSubClass.value, "little")
    Descriptor._bInterfaceProtocol = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*7)
    Descriptor.bInterfaceProtocol = int.from_bytes(Descriptor._bInterfaceProtocol.value, "little")
    Descriptor._iInterface = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*8)
    Descriptor.iInterface = int.from_bytes(Descriptor._iInterface.value, "little")
    return Descriptor

def FT_GetInterfaceDescriptor(Device: FT_Device, InterfaceIndex) -> int | FT_InterfaceDescriptor:
    Descriptor = FT_InterfaceDescriptor()
    Descriptor._RawAddress = ctypes.c_buffer(SIZE_INTERFACE_DESCRIPTOR)
    Status = _DLL.FT_GetInterfaceDescriptor(Device._Handle, InterfaceIndex, Descriptor._RawAddress)
    if FT_STATUS_STR[Status] != "FT_OK":
        _Print(FT_STATUS_STR[Status] + " | Failed to get interface information!", PRINT_ERROR_MAJOR, False)
        Descriptor.RawAddress = "FT_OTHER_ERROR"
        return Status, Descriptor #Return bad interface with ft other error code.
    Descriptor = _GetInterfaceDescriptorHelper(Descriptor)
    return Status, Descriptor

def _GetStringDescriptorHelper(Descriptor: FT_StringDescriptor) -> FT_StringDescriptor:
    Descriptor._bLength = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + 0)
    Descriptor.bLength = int.from_bytes(Descriptor._bLength, "little")
    Descriptor._bDescriptorType = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR)
    Descriptor.bDescriptorType = int.from_bytes(Descriptor._bDescriptorType, "little")
    Descriptor._szString = ctypes.string_at(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*2, 256)
    Descriptor.szString = Descriptor._szString.decode("utf-16")
    return Descriptor

def FT_GetStringDescriptor(Device: FT_Device, StringIndex: int) -> int | FT_StringDescriptor:
    Descriptor = FT_StringDescriptor()
    Descriptor._RawAddress = ctypes.c_buffer(SIZE_STRING_DESCRIPTOR)
    Status = _DLL.FT_GetStringDescriptor(Device._Handle, ctypes.c_char(StringIndex), Descriptor._RawAddress)
    if(Status != FT_OK):
        _Print(FT_STATUS_STR[Status] + " | ERROR: FAILED TO GET STRING DESCRIPTOR.", PRINT_ERROR_MAJOR, False)
        Descriptor = FT_StringDescriptor()
        return Status, Descriptor
    Descriptor = _GetStringDescriptorHelper(Descriptor)
    return Status, Descriptor

def _GetEndpointDescriptorHelper(Descriptor: FT_EndpointDescriptor) -> FT_EndpointDescriptor:
    Descriptor._bLength = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + 0)
    Descriptor.bLength = int.from_bytes(Descriptor._bLength, "little")
    Descriptor._bDescriptorType = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR)
    Descriptor.bDescriptorType = int.from_bytes(Descriptor._bDescriptorType, "little")
    Descriptor._bEndpointAddress = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*2)
    Descriptor.bEndpointAddress = int.from_bytes(Descriptor._bEndpointAddress, "little")
    Descriptor._bmAttributes = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*3)
    Descriptor.bmAttributes = int.from_bytes(Descriptor._bmAttributes, "little")
    Descriptor._wMaxPacketSize = ctypes.c_ushort.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*4)
    Descriptor.wMaxPacketSize = int.from_bytes(bytes=Descriptor._wMaxPacketSize, byteorder="little")
    Descriptor._bInterval = ctypes.c_char.from_address(ctypes.addressof(Descriptor._RawAddress) + SIZE_CHAR*4 + SIZE_SHORT)
    Descriptor.bInterval = int.from_bytes(Descriptor._bInterval, "little")
    return Descriptor

class _GetDescriptorHelperClass: # Python match/case statement is lame and requires this.
    DEVICE = FT_DEVICE_DESCRIPTOR_TYPE
    CONFIGURATION = FT_CONFIGURATION_DESCRIPTOR_TYPE
    STRING = FT_STRING_DESCRIPTOR_TYPE
    INTERFACE = FT_INTERFACE_DESCRIPTOR_TYPE
    ENDPOINT = FT_ENDPOINT_DESCRIPTOR_TYPE

def FT_GetDescriptor(Device: FT_Device, DescriptorType: int, Index: int) -> int | FT_DeviceDescriptor | FT_InterfaceDescriptor | FT_ConfigurationDescriptor | FT_StringDescriptor | int:
    Status = FT_OTHER_ERROR
    Descriptor = FT_OTHER_ERROR
    LengthTransferred = ctypes.c_ulong(0)
    match DescriptorType:
        case _GetDescriptorHelperClass.DEVICE:
            Descriptor = FT_DeviceDescriptor()
            Descriptor._RawAddress = ctypes.c_buffer(SIZE_DEVICE_DESCRIPTOR)
            Status = _DLL.FT_GetDescriptor(Device._Handle, DescriptorType, ctypes.c_char(Index),
                                            Descriptor._RawAddress, SIZE_DEVICE_DESCRIPTOR, ctypes.byref(LengthTransferred))
            if(Status != FT_OK):
                _Print(FT_STATUS_STR[Status] + " | FT_GetDescriptor(), ERROR: FAILED TO GET DEVICE DESCRIPTOR.", PRINT_ERROR_MAJOR, False)
                Descriptor = FT_DeviceDescriptor()
            else:
                Descriptor = _GetDeviceDescriptorHelper(Descriptor)
        case _GetDescriptorHelperClass.CONFIGURATION:
            Descriptor = FT_ConfigurationDescriptor()
            Descriptor._RawAddress = ctypes.c_buffer(SIZE_CONFIGURATION_DESCRIPTOR)
            Status = _DLL.FT_GetDescriptor(Device._Handle, DescriptorType, ctypes.c_char(Index),
                                            Descriptor._RawAddress, SIZE_CONFIGURATION_DESCRIPTOR, ctypes.byref(LengthTransferred))
            if(Status != FT_OK):
                _Print(FT_STATUS_STR[Status] + " | FT_GetDescriptor(), ERROR: FAILED TO GET CONFIGURATION DESCRIPTOR.", PRINT_ERROR_MAJOR, False)
                Descriptor = FT_ConfigurationDescriptor()
            else:
                Descriptor = _GetConfigurationDescriptorHelper(Descriptor)
        case _GetDescriptorHelperClass.STRING:
            Descriptor = FT_StringDescriptor()
            Descriptor._RawAddress = ctypes.c_buffer(SIZE_STRING_DESCRIPTOR)
            Status = _DLL.FT_GetDescriptor(Device._Handle, DescriptorType, ctypes.c_char(Index),
                                            Descriptor._RawAddress, SIZE_STRING_DESCRIPTOR, ctypes.byref(LengthTransferred))
            if(Status != FT_OK):
                _Print(FT_STATUS_STR[Status] + " | FT_GetDescriptor(), ERROR: FAILED TO GET STRING DESCRIPTOR.", PRINT_ERROR_MAJOR, False)
                Descriptor = FT_StringDescriptor()
            else:
                Descriptor = _GetStringDescriptorHelper(Descriptor)
        case _GetDescriptorHelperClass.INTERFACE:
            #Descriptor = FT_InterfaceDescriptor()
            #Descriptor._RawAddress = ctypes.c_buffer(SIZE_INTERFACE_DESCRIPTOR)
            #Status = _DLL.FT_GetDescriptor(Device._Handle, DescriptorType, ctypes.c_char(Index),
            #                                Descriptor._RawAddress, SIZE_INTERFACE_DESCRIPTOR, ctypes.byref(LengthTransferred))
            #if(Status != FT_OK):
            #    _Print(FT_STATUS_STR[Status] + " | FT_GetDescriptor(), ERROR: FAILED TO GET INTERFACE DESCRIPTOR.", PRINT_ERROR_MAJOR, False)
            #    Descriptor = FT_InterfaceDescriptor()
            #else:
            #    Descriptor = _GetInterfaceDescriptorHelper(Descriptor)
            # The above fails with FT_OTHER_ERROR and I don't know why, so we're calling the get interface descriptor function instead.
            Status, Descriptor = FT_GetInterfaceDescriptor(Device, Index)
            if(Status != FT_OK):
                _Print(FT_STATUS_STR[Status] + " | FT_GetDescriptor(), ERROR: FAILED TO GET INTERFACE DESCRIPTOR.", PRINT_ERROR_MAJOR, False)
                Descriptor = FT_InterfaceDescriptor()
            LengthTransferred = ctypes.c_ulong(SIZE_INTERFACE_DESCRIPTOR)
        case _GetDescriptorHelperClass.ENDPOINT: # This does not work :(, but it is not mentioned in the programmers guide.
            Descriptor = FT_EndpointDescriptor()
            Descriptor._RawAddress = ctypes.c_buffer(SIZE_ENDPOINT_DESCRIPTOR)
            Status = _DLL.FT_GetDescriptor(Device._Handle, DescriptorType, ctypes.c_char(Index),
                                            Descriptor._RawAddress, SIZE_ENDPOINT_DESCRIPTOR, ctypes.byref(LengthTransferred))
            if(Status != FT_OK):
                _Print(FT_STATUS_STR[Status] + " | FT_GetDescriptor(), ERROR: FAILED TO GET ENDPOINT DESCRIPTOR.", PRINT_ERROR_MAJOR, False)
                Descriptor = FT_EndpointDescriptor()
            else:
                Descriptor = _GetEndpointDescriptorHelper(Descriptor)
        case _: # Default case.
            _Print(FT_STATUS_STR[Status] + " | FT_GetDescriptor(), WARNING: GIVEN INVALID DESCRIPTOR TYPE.", PRINT_ERROR_MINOR, False)
    return Status, Descriptor, LengthTransferred.value

def FT_ControlTransfer(Device: FT_Device, SetupPacket: FT_SetupPacket, Buffer: FT_Buffer, BufferLength: int) -> int | int:
    Status = FT_OTHER_ERROR
    LengthTransferred = ctypes.c_ulong(0)
    if(Buffer._RawAddress == "FT_OTHER_ERROR"):
        _Print(FT_STATUS_STR[Status] + " | FT_ControlTransfer(), ERROR: GIVEN INVALID FT_Buffer.", PRINT_ERROR_MAJOR, False)
        return Status, LengthTransferred.value
    Packet = 0
    Packet = Packet | SetupPacket.RequestType & int("0x000000FF", 16)
    Packet = Packet | (SetupPacket.Request & int("0x000000FF", 16)) << 8
    Packet = Packet | (SetupPacket.Value & int("0x0000FFFF", 16)) << 16
    Packet = Packet | (SetupPacket.Index & int("0x0000FFFF", 16)) << 32
    Packet = Packet | (SetupPacket.Length & int("0x0000FFFF", 16)) << 48
    Status = _DLL.FT_ControlTransfer(Device._Handle, ctypes.c_uint64(Packet), ctypes.byref(Buffer._RawAddress),
                                        ctypes.c_ulong(BufferLength), ctypes.byref(LengthTransferred))
    if(Status != FT_OK):
        _Print(FT_STATUS_STR[Status] + " | FT_ControlTransfer(), ERROR: Failed to transmit data.", PRINT_ERROR_MAJOR, False)
    return Status, LengthTransferred.value

def FT_GetVIDPID(Device: FT_Device) -> int | int | int:
    VID = ctypes.c_ushort(0)
    PID = ctypes.c_ushort(0)
    if(Platform != "windows"): # Linux FT_GetVIDPID is broken. Use alternative.
        Status, DeviceDescriptor = FT_GetDeviceDescriptor(Device)
        if(Status != FT_OK):
            _Print(FT_STATUS_STR[Status] + " | FT_GetVIDPID(), ERROR: Failed to get VID & PID.", PRINT_ERROR_MAJOR, False)
            return Status, 0, 0
        return Status, DeviceDescriptor.idVendor, DeviceDescriptor.idProduct
    Status = _DLL.FT_GetVIDPID(Device._Handle, ctypes.byref(VID), ctypes.byref(PID))
    if(Status != FT_OK):
        _Print(FT_STATUS_STR[Status] + " | FT_GetVIDPID(), ERROR: Failed to get VID & PID.", PRINT_ERROR_MAJOR, False)
    return Status, VID.value, PID.value

def FT_EnableGPIO(Device: FT_Device, EnableMask: int, DirectionMask: int) -> int:
    Status = _DLL.FT_EnableGPIO(Device._Handle, ctypes.c_uint32(EnableMask), ctypes.c_uint32(DirectionMask))
    if(Status != FT_OK):
        _Print(FT_STATUS_STR[Status] + " | FT_EnableGPIO(), ERROR: Failed to enable GPIO.", PRINT_ERROR_MAJOR, False)
    return Status

def FT_WriteGPIO(Device: FT_Device, SelectMask: int, Data: int) -> int:
    Status = _DLL.FT_WriteGPIO(Device._Handle, ctypes.c_uint32(SelectMask), ctypes.c_uint32(Data))
    if(Status != FT_OK):
        _Print(FT_STATUS_STR[Status] + " | FT_WriteGPIO(), ERROR: Failed to write to GPIO.", PRINT_ERROR_MAJOR, False)
    return Status

def FT_ReadGPIO(Device: FT_Device) -> int | int:
    GPIO_Data = ctypes.c_uint32(0)
    Status = _DLL.FT_ReadGPIO(Device._Handle, ctypes.byref(GPIO_Data))
    if(Status != FT_OK):
        _Print(FT_STATUS_STR[Status] + " | FT_ReadGPIO(), ERROR: Failed to read GPIO.", PRINT_ERROR_MAJOR, False)
    return Status, GPIO_Data.value

def FT_SetGPIOPull(Device: FT_Device, SelectMask: int, PullMask: int) -> int:
    Status = _DLL.FT_SetGPIOPull(Device._Handle, ctypes.c_uint32(SelectMask), ctypes.c_uint32(PullMask))
    if(Status != FT_OK):
        _Print(FT_STATUS_STR[Status] + " | FT_WriteGPIO(), ERROR: Failed to write to GPIO.", PRINT_ERROR_MAJOR, False)
    return Status

_FT_SetNotificationCallback_PythonFunction = None

def _FT_SetNotificationCallbackHelper(Context, CallbackType, CallbackInfoPointer):
    PipeID = 0
    Length = 0
    bGPIO0 = False
    bGPIO1 = False
    if(CallbackType == E_FT_NOTIFICATION_CALLBACK_TYPE_DATA):
        if(Platform != "windows"): # Linux uses uint despite ulong type declaration.
            Length = ctypes.c_uint.from_address(CallbackInfoPointer)
            PipeID = ctypes.c_char.from_address(CallbackInfoPointer + SIZE_UINT)
        else:
            Length = ctypes.c_ulong.from_address(CallbackInfoPointer)
            PipeID = ctypes.c_char.from_address(CallbackInfoPointer + SIZE_ULONG)
        try: #Ignore exception due to callback clearing.
            _FT_SetNotificationCallback_PythonFunction(E_FT_NOTIFICATION_CALLBACK_TYPE_DATA, int.from_bytes(PipeID.value, "little"), Length.value)
        except:
            None
    elif(CallbackType == E_FT_NOTIFICATION_CALLBACK_TYPE_GPIO):
        bGPIO0 = (ctypes.c_uint.from_address(CallbackInfoPointer)).value != 0 # Get bool.
        bGPIO1 = (ctypes.c_uint.from_address(CallbackInfoPointer + SIZE_UINT)).value != 0 # Get bool.
        try: #Ignore exception due to callback clearing.
            _FT_SetNotificationCallback_PythonFunction(E_FT_NOTIFICATION_CALLBACK_TYPE_GPIO, bGPIO0, bGPIO1)
        except:
            None
    else:
        _Print("INTERNAL LIBRARY ERROR: CALLBACK FUNCTION GOT INVALID CALLBACK TYPE.", PRINT_ERROR_MAJOR, False)
    return None

def FT_SetNotificationCallback(Device: FT_Device, CallbackFunction: typing.Callable[[int, int, int], None]) -> int:
    global _FT_SetNotificationCallback_PythonFunction
    if not hasattr(FT_SetNotificationCallback, "_CFUNC"):
        FT_SetNotificationCallback._CFUNC = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p)
        FT_SetNotificationCallback._PythonFunctionHelper = FT_SetNotificationCallback._CFUNC(_FT_SetNotificationCallbackHelper)
    _FT_SetNotificationCallback_PythonFunction = CallbackFunction
    Status = _DLL.FT_SetNotificationCallback(Device._Handle, FT_SetNotificationCallback._PythonFunctionHelper, NULL)
    if(Status != FT_OK):
        _Print(FT_STATUS_STR[Status] + " | FT_SetNotificationCallback(), ERROR: Failed to set callback function.", PRINT_ERROR_MAJOR, False)
    return Status

# Note: Same as FT_SetNotificationCallback with an 'X' but this just straight up seg faults. So we return immediately instead of calling it.
def FT_ClearNotificationCallback(Device: FT_Device) -> int:
    Status = _DLL.FT_ClearNotificationCallback(Device._Handle)
    if(Status != FT_OK):
        _Print(FT_STATUS_STR[Status] + " | FT_ClearNotificationCallback(), ERROR: Failed to clear callback function.", PRINT_ERROR_MAJOR, False)
    return Status

def FT_GetChipConfiguration(Device: FT_Device) -> int | FT_60XCONFIGURATION:
    Configuration = FT_60XCONFIGURATION()
    Configuration._RawAddress = ctypes.c_buffer((SIZE_CHAR*(8 + 128)) + (SIZE_SHORT*4) + (SIZE_ULONG*2))
    Status = _DLL.FT_GetChipConfiguration(Device._Handle, Configuration._RawAddress)
    if(Status != FT_OK):
        _Print(FT_STATUS_STR[Status] + " | FT_GetChipConfiguration(), ERROR: Failed to get chip configuration.", PRINT_ERROR_MAJOR, False)
        return Status, Configuration
    Configuration._VendorID = ctypes.c_ushort.from_address(ctypes.addressof(Configuration._RawAddress) + 0)
    Configuration.VendorID = int.from_bytes(bytes=Configuration._VendorID, byteorder="little")
    Configuration._ProductID = ctypes.c_ushort.from_address(ctypes.addressof(Configuration._RawAddress) + SIZE_SHORT)
    Configuration.ProductID = int.from_bytes(bytes=Configuration._ProductID, byteorder="little")
    Configuration._StringDescriptors = ctypes.string_at(ctypes.addressof(Configuration._RawAddress) + SIZE_SHORT*2, 128)
    # I could return a bytearray instead of making a list of strings, but I like pain. :(
    # Configuration.StringDescriptors = Configuration._StringDescriptors.decode("utf_16_le")
    Configuration.StringDescriptors = []
    String = -1
    for i in range(64):
        Upper = i*2 + 1
        Lower = i*2
        Character = (Configuration._StringDescriptors[Upper] << 8) | Configuration._StringDescriptors[Lower]
        if(Configuration._StringDescriptors[Upper] == int("0x03", 16)): # New string!
            Configuration.StringDescriptors.append("")
            String = String + 1
        else: # Add to string!
            Configuration.StringDescriptors[String] = Configuration.StringDescriptors[String] + chr(Character)
    # Get rid of trailing zeros in last string. This is necessary for when we convert back in a setchipconfig call.
    while Configuration.StringDescriptors[String][len(Configuration.StringDescriptors[String]) - 1] == chr(0):
        Configuration.StringDescriptors[String] = Configuration.StringDescriptors[String][:-1] # Remove last byte.
    Configuration._bInterval = ctypes.c_char.from_address(ctypes.addressof(Configuration._RawAddress) + (SIZE_CHAR * 128) + SIZE_SHORT*2)
    Configuration.bInterval = int.from_bytes(Configuration._bInterval, "little")
    Configuration._PowerAttributes = ctypes.c_char.from_address(ctypes.addressof(Configuration._RawAddress) + (SIZE_CHAR * (128 + 1)) + (SIZE_SHORT*2))
    Configuration.PowerAttributes = int.from_bytes(Configuration._PowerAttributes, "little")
    Configuration._PowerConsumption = ctypes.c_ushort.from_address(ctypes.addressof(Configuration._RawAddress) + (SIZE_CHAR * (128 + 2)) + (SIZE_SHORT*2))
    Configuration.PowerConsumption = int.from_bytes(bytes=Configuration._PowerConsumption, byteorder="little")
    Configuration._Reserved2 = ctypes.c_char.from_address(ctypes.addressof(Configuration._RawAddress) + (SIZE_CHAR * (128 + 2)) + (SIZE_SHORT*3))
    Configuration.Reserved2 = int.from_bytes(Configuration._Reserved2, "little")
    Configuration._FIFOClock = ctypes.c_char.from_address(ctypes.addressof(Configuration._RawAddress) + (SIZE_CHAR * (128 + 3)) + (SIZE_SHORT*3))
    Configuration.FIFOClock = int.from_bytes(Configuration._FIFOClock, "little")
    Configuration._FIFOMode = ctypes.c_char.from_address(ctypes.addressof(Configuration._RawAddress) + (SIZE_CHAR * (128 + 4)) + (SIZE_SHORT*3))
    Configuration.FIFOMode = int.from_bytes(Configuration._FIFOMode, "little")
    Configuration._ChannelConfig = ctypes.c_char.from_address(ctypes.addressof(Configuration._RawAddress) + (SIZE_CHAR * (128 + 5)) + (SIZE_SHORT*3))
    Configuration.ChannelConfig = int.from_bytes(Configuration._ChannelConfig, "little")
    Configuration._OptionalFeatureSupport = ctypes.c_ushort.from_address(ctypes.addressof(Configuration._RawAddress) + (SIZE_CHAR * (128 + 6)) + (SIZE_SHORT*3))
    Configuration.OptionalFeatureSupport = int.from_bytes(bytes=Configuration._OptionalFeatureSupport, byteorder="little")
    Configuration._BatteryChargingGPIOConfig = ctypes.c_char.from_address(ctypes.addressof(Configuration._RawAddress) + (SIZE_CHAR * (128 + 6)) + (SIZE_SHORT*4))
    Configuration.BatteryChargingGPIOConfig = int.from_bytes(Configuration._BatteryChargingGPIOConfig, "little")
    Configuration._FlashEEPROMDetection = ctypes.c_char.from_address(ctypes.addressof(Configuration._RawAddress) + (SIZE_CHAR * (128 + 7)) + (SIZE_SHORT*4))
    Configuration.FlashEEPROMDetection = int.from_bytes(Configuration._FlashEEPROMDetection, "little")
    Configuration._MSIO_Control = ctypes.c_ulong.from_address(ctypes.addressof(Configuration._RawAddress) + (SIZE_CHAR * (128 + 8)) + (SIZE_SHORT*4))
    Configuration.MSIO_Control = int.from_bytes(bytes=Configuration._MSIO_Control, byteorder="little")
    Configuration._GPIO_Control = ctypes.c_ulong.from_address(ctypes.addressof(Configuration._RawAddress) + (SIZE_CHAR * (128 + 8)) + (SIZE_SHORT*4) + SIZE_ULONG)
    Configuration.GPIO_Control = int.from_bytes(bytes=Configuration._GPIO_Control, byteorder="little")
    return Status, Configuration

def FT_SetChipConfiguration(Device: FT_Device, Configuration: FT_60XCONFIGURATION) -> int:
    NewConfiguration = ctypes.c_buffer((SIZE_CHAR*(8 + 128)) + (SIZE_SHORT*4) + (SIZE_ULONG*2))
    NewConfiguration[0] = ctypes.c_char(Configuration.VendorID & int("0x000000FF", 16))
    NewConfiguration[1] = ctypes.c_char((Configuration.VendorID & int("0x0000FF00", 16)) >> 8)
    NewConfiguration[2] = ctypes.c_char(Configuration.ProductID & int("0x000000FF", 16))
    NewConfiguration[3] = ctypes.c_char((Configuration.ProductID & int("0x0000FF00", 16)) >> 8)
    Index = 3
    for String in Configuration.StringDescriptors:
        Length = len(String)
        Index = Index + 1
        NewConfiguration[Index] = ctypes.c_char(Length*2 + 2)
        Index = Index + 1
        NewConfiguration[Index] = ctypes.c_char(int("0x03", 16))
        Decode = String.encode("utf_16_le")
        for i in range(Length):
            Index = Index + 1
            NewConfiguration[Index] = ctypes.c_char(Decode[i*2])
            Index = Index + 1
            NewConfiguration[Index] = ctypes.c_char(Decode[i*2 + 1])
    while(Index < 131): # We will write to [131]. [132] is start of next data field.
        Index = Index + 1
        NewConfiguration[Index] = ctypes.c_char(0)

    NewConfiguration[132] = ctypes.c_char(Configuration.bInterval & int("0x000000FF", 16))
    NewConfiguration[133] = ctypes.c_char(Configuration.PowerAttributes & int("0x000000FF", 16))
    NewConfiguration[134] = ctypes.c_char(Configuration.PowerConsumption & int("0x000000FF", 16))
    NewConfiguration[135] = ctypes.c_char((Configuration.PowerConsumption & int("0x0000FF00", 16)) >> 8)
    NewConfiguration[136] = ctypes.c_char(Configuration.Reserved2 & int("0x000000FF", 16))
    NewConfiguration[137] = ctypes.c_char(Configuration.FIFOClock & int("0x000000FF", 16))
    NewConfiguration[138] = ctypes.c_char(Configuration.FIFOMode & int("0x000000FF", 16))
    NewConfiguration[139] = ctypes.c_char(Configuration.ChannelConfig & int("0x000000FF", 16))
    NewConfiguration[140] = ctypes.c_char(Configuration.OptionalFeatureSupport & int("0x000000FF", 16))
    NewConfiguration[141] = ctypes.c_char((Configuration.OptionalFeatureSupport & int("0x0000FF00", 16)) >> 8)
    NewConfiguration[142] = ctypes.c_char(Configuration.BatteryChargingGPIOConfig & int("0x000000FF", 16))
    NewConfiguration[143] = ctypes.c_char(Configuration.FlashEEPROMDetection & int("0x000000FF", 16))
    NewConfiguration[144] = ctypes.c_char(Configuration.MSIO_Control & int("0x00000000FF", 16))
    NewConfiguration[145] = ctypes.c_char((Configuration.MSIO_Control & int("0x000000FF00", 16)) >> 8)
    NewConfiguration[146] = ctypes.c_char((Configuration.MSIO_Control & int("0x0000FF0000", 16)) >> 16)
    NewConfiguration[147] = ctypes.c_char((Configuration.MSIO_Control & int("0x00FF000000", 16)) >> 24)
    NewConfiguration[148] = ctypes.c_char(Configuration.GPIO_Control & int("0x00000000FF", 16))
    NewConfiguration[149] = ctypes.c_char((Configuration.GPIO_Control & int("0x000000FF00", 16)) >> 8)
    NewConfiguration[150] = ctypes.c_char((Configuration.GPIO_Control & int("0x0000FF0000", 16)) >> 16)
    NewConfiguration[151] = ctypes.c_char((Configuration.GPIO_Control & int("0x00FF000000", 16)) >> 24)
    Status = _DLL.FT_SetChipConfiguration(Device._Handle, ctypes.byref(NewConfiguration))
    if(Status != FT_OK):
        _Print(FT_STATUS_STR[Status] + " | FT_SetChipConfiguration(), ERROR: Failed to set chip configuration.", PRINT_ERROR_MAJOR, False)
        return Status, Configuration
    return Status

def FT_IsDevicePath(Device: FT_Device, DevicePath: str) -> int: # HAVE NOT CONFIRMED THIS WORKS YET.
    if(Platform != "windows"):
        _Print("FT_IsDevicePath() DOES NOT EXIST IN LINUX OR MACOS", PRINT_ERROR_CRITICAL, False)
        return FT_OTHER_ERROR
    return _DLL.FT_IsDevicePath(Device._Handle, DevicePath.encode("ascii"))

def FT_GetDriverVersion(Device: FT_Device) -> int | int:
    DriverVersion = ctypes.wintypes.DWORD(0)
    Status = _DLL.FT_GetDriverVersion(Device._Handle, ctypes.byref(DriverVersion))
    if(Status != FT_OK):
        _Print(FT_STATUS_STR[Status] + " | FT_GetDriverVersion(), ERROR: Failed to get driver version.", PRINT_ERROR_MAJOR, False)
    return Status, DriverVersion.value

def GetDriverVersion(Device: FT_Device) -> int | str:
    Status, DV = FT_GetDriverVersion(Device)
    DriverVersion = FT_STATUS_STR[Status]
    if(Status == FT_OK):
        if(Platform == "windows"):
            DriverVersion = format((DV & int("0xFF000000", 16)) >> 24, 'x') + '.' \
            + format((DV & int("0x00FF0000", 16)) >> 16, 'x') + '.' \
            + format((DV & int("0x0000FF00", 16)) >> 8, 'x') + '.' \
            + format(DV & int("0x000000FF", 16), 'x')
        else:
            DriverVersion = str((DV & int("0xFF000000", 16)) >> 24) + '.' \
            + str((DV & int("0x00FF0000", 16)) >> 16) + '.' \
            + str(DV & int("0x0000FFFF", 16))
    return Status, DriverVersion

def FT_GetLibraryVersion() -> int | int:
    LibraryVersion = ctypes.wintypes.DWORD(0)
    Status = _DLL.FT_GetLibraryVersion(ctypes.byref(LibraryVersion))
    if(Status != FT_OK):
        _Print(FT_STATUS_STR[Status] + " | FT_GetLibraryVersion(), ERROR: Failed to get library version.", PRINT_ERROR_MAJOR, False)
    return Status, LibraryVersion.value

def GetLibraryVersion() -> int | str:
    Status, LV = FT_GetLibraryVersion()
    LibraryVersion = FT_STATUS_STR[Status]
    if(Status == FT_OK):
        if(Platform == "windows"):
            LibraryVersion = format((LV & int("0xFF000000", 16)) >> 24, 'x') + '.' \
            + format((LV & int("0x00FF0000", 16)) >> 16, 'x') + '.' \
            + format((LV & int("0x0000FF00", 16)) >> 8, 'x') + '.' \
            + format(LV & int("0x000000FF", 16), 'x')
        else:
            LibraryVersion = str((LV & int("0xFF000000", 16)) >> 24) + '.' \
            + str((LV & int("0x00FF0000", 16)) >> 16) + '.' \
            + str(LV & int("0x0000FFFF", 16))
    return Status, LibraryVersion

def FT_CycleDevicePort(Device: FT_Device) -> int:
    Status = _DLL.FT_CycleDevicePort(Device._Handle)
    if(Status != FT_OK):
        _Print(FT_STATUS_STR[Status] + " | FT_CycleDevicePort(), ERROR: Failed to cycle device port.", PRINT_ERROR_MAJOR, False)
    return Status

def FT_ReadPipe(Device: FT_Device, Pipe_Endpoint, BufferLength: int, Overlapped_TimeoutMs) -> int | FT_Buffer | int:
    Status = FT_OTHER_ERROR
    Buffer = FT_Buffer()
    Buffer._RawAddress = ctypes.c_buffer(BufferLength)
    BytesTransferred = ctypes.c_ulong(0)
    if(Platform != "windows"): # Overlapped is instead a timeout in ms.
        Status = _DLL.FT_ReadPipe(Device._Handle,
                                    Pipe_Endpoint,
                                    ctypes.byref(Buffer._RawAddress),
                                    BufferLength,
                                    ctypes.byref(BytesTransferred),
                                    Overlapped_TimeoutMs)
    elif(isinstance(Overlapped_TimeoutMs, FT_Overlapped)):
        Status = _DLL.FT_ReadPipe(Device._Handle,
                                    Pipe_Endpoint._PipeID,
                                    ctypes.byref(Buffer._RawAddress),
                                    BufferLength,
                                    ctypes.byref(BytesTransferred),
                                    Overlapped_TimeoutMs._RawAddress)
    elif((Overlapped_TimeoutMs == NULL) or (Overlapped_TimeoutMs == 0)):
        Status = _DLL.FT_ReadPipe(Device._Handle,
                                    Pipe_Endpoint._PipeID,
                                    ctypes.byref(Buffer._RawAddress),
                                    BufferLength,
                                    ctypes.byref(BytesTransferred),
                                    NULL)
    else:
        _Print("FT_ReadPipe(), invalid Overlapped type given, expecting FT_Overlapped or NULL", PRINT_ERROR_MAJOR, False)
    return Status, Buffer, BytesTransferred.value

def FT_ReadPipeEx(Device: FT_Device, Pipe_FIFOindex, BufferLength: int, Overlapped_TimeoutMs) -> int | FT_Buffer | int:
    Status = FT_OTHER_ERROR
    Buffer = FT_Buffer()
    Buffer._RawAddress = ctypes.c_buffer(BufferLength)
    BytesTransferred = ctypes.c_ulong(0)
    if(Platform != "windows"): # Overlapped is instead a timeout in ms.
        Status = _DLL.FT_ReadPipeEx(Device._Handle,
                                    Pipe_FIFOindex,
                                    ctypes.byref(Buffer._RawAddress),
                                    BufferLength,
                                    ctypes.byref(BytesTransferred),
                                    Overlapped_TimeoutMs)
    elif(isinstance(Overlapped_TimeoutMs, FT_Overlapped)):
        Status = _DLL.FT_ReadPipeEx(Device._Handle,
                                    Pipe_FIFOindex._PipeID,
                                    ctypes.byref(Buffer._RawAddress),
                                    BufferLength,
                                    ctypes.byref(BytesTransferred),
                                    Overlapped_TimeoutMs._RawAddress)
    elif((Overlapped_TimeoutMs == NULL) or (Overlapped_TimeoutMs == 0)):
        Status = _DLL.FT_ReadPipeEx(Device._Handle,
                                    Pipe_FIFOindex._PipeID,
                                    ctypes.byref(Buffer._RawAddress),
                                    BufferLength,
                                    ctypes.byref(BytesTransferred),
                                    NULL)
    else:
        _Print("FT_ReadPipeEx(), invalid Overlapped type given, expecting FT_Overlapped or NULL", PRINT_ERROR_MAJOR, False)
    return Status, Buffer, BytesTransferred.value

def FT_ReadPipeAsync(Device: FT_Device, FIFO_Index: int, BufferLength: int, Overlapped) -> int | FT_Buffer | int:
    Status = FT_OTHER_ERROR
    Buffer = FT_Buffer()
    Buffer._RawAddress = ctypes.c_buffer(BufferLength)
    BytesTransferred = ctypes.c_ulong(0)
    if(Platform == "windows"):
        _Print("FT_ReadPipeAsync() DOES NOT EXIST IN WINDOWS", PRINT_ERROR_CRITICAL, False)
        return FT_OTHER_ERROR, FT_Buffer(), 0
    if((Overlapped == NULL) or (Overlapped == 0)):
        Status = _DLL.FT_ReadPipeAsync(Device._Handle,
                                    FIFO_Index,
                                    ctypes.byref(Buffer._RawAddress),
                                    BufferLength,
                                    ctypes.byref(BytesTransferred),
                                    NULL)
    else:
        Status = _DLL.FT_ReadPipeAsync(Device._Handle,
                                    FIFO_Index,
                                    ctypes.byref(Buffer._RawAddress),
                                    BufferLength,
                                    ctypes.byref(BytesTransferred),
                                    Overlapped._RawAddress)
    return Status, Buffer, BytesTransferred.value

def FT_WritePipe(Device: FT_Device, Pipe_Endpoint, Buffer: FT_Buffer, BufferLength: int, Overlapped_TimeoutMs) -> int | int:
    Status = FT_OTHER_ERROR
    if(isinstance(Buffer._RawAddress, FT_Buffer)):
        _Print("FT_WritePipe(), was not given expected FT_Buffer.", PRINT_ERROR_MAJOR, False)
        return Status, 0
    BytesTransferred = ctypes.c_ulong(0)
    if(Platform != "windows"): # Overlapped is instead a timeout in ms.
        Status = _DLL.FT_WritePipe(Device._Handle,
                                    Pipe_Endpoint,
                                    ctypes.byref(Buffer._RawAddress),
                                    BufferLength,
                                    ctypes.byref(BytesTransferred),
                                    Overlapped_TimeoutMs)
    elif(isinstance(Overlapped_TimeoutMs, FT_Overlapped)):
        Status = _DLL.FT_WritePipe(Device._Handle,
                                    Pipe_Endpoint._PipeID,
                                    ctypes.byref(Buffer._RawAddress),
                                    BufferLength,
                                    ctypes.byref(BytesTransferred),
                                    Overlapped_TimeoutMs._RawAddress)
    elif((Overlapped_TimeoutMs == NULL) or (Overlapped_TimeoutMs == 0)):
        Status = _DLL.FT_WritePipe(Device._Handle,
                                    Pipe_Endpoint._PipeID,
                                    ctypes.byref(Buffer._RawAddress),
                                    BufferLength,
                                    ctypes.byref(BytesTransferred),
                                    NULL)
    else:
        _Print("FT_WritePipe(), invalid Overlapped type given, expecting FT_Overlapped or NULL", PRINT_ERROR_MAJOR, False)
    return Status, BytesTransferred.value

def FT_WritePipeEx(Device: FT_Device, Pipe_FIFOindex, Buffer: FT_Buffer, BufferLength: int, Overlapped_TimeoutMs) -> int | int:
    Status = FT_OTHER_ERROR
    if(isinstance(Buffer._RawAddress, ctypes.c_char_p)):
        _Print("FT_WritePipeEx(), was not given expected FT_Buffer.", PRINT_ERROR_MAJOR, False)
        return Status, 0
    BytesTransferred = ctypes.c_ulong(0)
    if(Platform != "windows"): # Overlapped is instead a timeout in ms.
        Status = _DLL.FT_WritePipeEx(Device._Handle,
                                    Pipe_FIFOindex,
                                    ctypes.byref(Buffer._RawAddress),
                                    BufferLength,
                                    ctypes.byref(BytesTransferred),
                                    Overlapped_TimeoutMs)
    elif(isinstance(Overlapped_TimeoutMs, FT_Overlapped)):
        Status = _DLL.FT_WritePipeEx(Device._Handle,
                                        Pipe_FIFOindex._PipeID,
                                        ctypes.byref(Buffer._RawAddress),
                                        BufferLength,
                                        ctypes.byref(BytesTransferred),
                                        Overlapped_TimeoutMs._RawAddress)
    elif((Overlapped_TimeoutMs == NULL) or (Overlapped_TimeoutMs == 0)):
        Status = _DLL.FT_WritePipeEx(Device._Handle,
                                        Pipe_FIFOindex._PipeID,
                                        ctypes.byref(Buffer._RawAddress),
                                        BufferLength,
                                        ctypes.byref(BytesTransferred),
                                        NULL)
    else:
        _Print("FT_WritePipeEx(), invalid Overlapped type given, expecting FT_Overlapped or NULL", PRINT_ERROR_MAJOR, False)
    return Status, BytesTransferred.value

def FT_WritePipeAsync(Device: FT_Device, FIFO_Index, Buffer: FT_Buffer, BufferLength: int, Overlapped) -> int | int:
    Status = FT_OTHER_ERROR
    if(isinstance(Buffer._RawAddress, ctypes.c_char_p)):
        _Print("FT_WritePipeEx(), was not given expected FT_Buffer.", PRINT_ERROR_MAJOR, False)
        return Status, 0
    BytesTransferred = ctypes.c_ulong(0)
    if(Platform == "windows"):
        _Print("FT_WritePipeAsync() DOES NOT EXIST IN WINDOWS", PRINT_ERROR_CRITICAL, False)
        return FT_OTHER_ERROR, 0
    elif((Overlapped == NULL) or (Overlapped == 0)):
        Status = _DLL.FT_WritePipeAsync(Device._Handle,
                                        FIFO_Index,
                                        ctypes.byref(Buffer._RawAddress),
                                        BufferLength,
                                        ctypes.byref(BytesTransferred),
                                        NULL)
    else:
        Status = _DLL.FT_WritePipeAsync(Device._Handle,
                                        FIFO_Index,
                                        ctypes.byref(Buffer._RawAddress),
                                        BufferLength,
                                        ctypes.byref(BytesTransferred),
                                        Overlapped._RawAddress)
    return Status, BytesTransferred.value

def FT_GetOverlappedResult(Device: FT_Device, Overlapped: FT_Overlapped, Wait: bool) -> int | int:
    LengthTransferred = ctypes.c_ulong(0)
    Status = _DLL.FT_GetOverlappedResult(Device._Handle,
                                            Overlapped._RawAddress,
                                            ctypes.byref(LengthTransferred),
                                            int(Wait))
    return Status, LengthTransferred.value
def FT_ReleaseOverlapped(Device: FT_Device, Overlapped: FT_Overlapped) -> int:
    return _DLL.FT_ReleaseOverlapped(Device._Handle, Overlapped._RawAddress)

def FT_SetStreamPipe(Device: FT_Device, AllWritePipes: bool, AllReadPipes: bool, Pipe, StreamSize: int) -> int:
    Status = FT_OTHER_ERROR
    MaxPacketSize = 0
    MPS_String = "Unknown"
    # Determine MaxPacketSize
    if (Device.Flags == FT_FLAGS_OPENED):
            _Print("FT_SetStreamPipe(), Device was opened by another process!", PRINT_ERROR_MAJOR, False)
    elif (Device.Flags == FT_FLAGS_HISPEED):
            MaxPacketSize = 512
            MPS_String = "Hi-Speed"
    elif (FT_FLAGS_SUPERSPEED):
            MaxPacketSize = 1024
            MPS_String = "SuperSpeed"
    else:
        _Print("FT_SetStreamPipe(), Device has unknown flag value!", PRINT_ERROR_MAJOR, False)
    if((StreamSize % MaxPacketSize) and (MaxPacketSize)):
        _Print("FT_SetStreamPipe(), StreamSize " + str(StreamSize) + " is not a multiple of " + str(MaxPacketSize) + " for " + MPS_String + " mode!", PRINT_ERROR_MAJOR, False)
    if(isinstance(Pipe, FT_Pipe)):
        if(AllWritePipes or AllReadPipes):
            _Print("FT_SetStreamPipe(), PipeID will be ignored because AllXPipes arguments are not both False.", PRINT_ERROR_MINOR, False)
        Status =_DLL.FT_SetStreamPipe(Device._Handle, AllWritePipes, AllReadPipes, Pipe._PipeID, StreamSize)
    elif((Pipe == NULL) or (Pipe == 0)):
        Status = _DLL.FT_SetStreamPipe(Device._Handle, AllWritePipes, AllReadPipes, NULL, StreamSize)
    else:
        _Print("FT_SetStreamPipe(), Was not given expected FT_Pipe or NULL.", PRINT_ERROR_MAJOR, False)
    return Status

def FT_ClearStreamPipe(Device: FT_Device, AllWritePipes: bool, AllReadPipes: bool, Pipe) -> int:
    Status = FT_OTHER_ERROR
    if(isinstance(Pipe, FT_Pipe)):
        if(AllWritePipes or AllReadPipes):
            _Print("FT_ClearStreamPipe(), PipeID will be ignored because AllXPipes arguments are not both False.", PRINT_ERROR_MINOR, False)
        Status =_DLL.FT_ClearStreamPipe(Device._Handle, AllWritePipes, AllReadPipes, Pipe._PipeID)
    elif((Pipe == NULL) or (Pipe == 0)):
        Status = _DLL.FT_ClearStreamPipe(Device._Handle, AllWritePipes, AllReadPipes, NULL)
    else:
        _Print("FT_ClearStreamPipe(), Was not given expected FT_Pipe or NULL.", PRINT_ERROR_MAJOR, False)
    return Status

def FT_ResetDevicePort(Device: FT_Device) -> int:
    Status = _DLL.FT_ResetDevicePort(Device._Handle)
    if(Status != FT_OK):
        _Print(FT_STATUS_STR[Status] + " | FT_ResetDevicePort(), ERROR: Failed to reset device port.", PRINT_ERROR_MAJOR, False)
    return Status