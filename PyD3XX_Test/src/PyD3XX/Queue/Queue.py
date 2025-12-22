# Created by Hector Soto
# A wrapper to D3XX to create true multi-core multi-threaded Queue objects.

import PyD3XX
import ctypes

from importlib.resources import files as _files

# ---| Import QueueD3XX |---
# Create library file string.
_LF = PyD3XX._LibraryFile.replace("FTD3XX", "QueueD3XX")
_LF = _LF.replace("libftd3xx", "QueueD3XX")
_DLL_Path = str(_files("PyD3XX").joinpath("Queue/" + _LF))
try:
    if(PyD3XX.Platform == "windows"):
        _DLL = ctypes.windll.LoadLibrary(_DLL_Path) # Check if dll exists in same directory as executable.
    else:
        _DLL = ctypes.cdll.LoadLibrary(_DLL_Path) # Check if dll exists in same directory as executable.
except:
    print("QueueD3XX ERROR: Did not find '" + _DLL_Path + "', EXITING.")
    exit()
PyD3XX._Print("Successfully loaded QueueD3XX: '" + _LF + "'", PyD3XX.PRINT_INFO_START, True)

class Queue:
    _HS_Queue = ctypes.c_void_p(0) # Address of HS_Queue
    _StreamSize = 0
    def __init__(self): # Make sure each instance has its own queue address.
        self._HS_Queue = ctypes.c_void_p(0)
        self._StreamSize = 0

def GetVersionQueueD3XX() -> int:
    LV = _DLL.HS_GetVersionQueueD3XX()
    Version = format((LV & int("0xFF000000", 16)) >> 24, 'x') + '.' \
            + format((LV & int("0x00FF0000", 16)) >> 16, 'x') + '.' \
            + format((LV & int("0x0000FF00", 16)) >> 8, 'x') + '.' \
            + format(LV & int("0x000000FF", 16), 'x')
    return Version

def Open(Identifier, OpenFlag: int, Device: PyD3XX.FT_Device) -> int:
    Status = PyD3XX.FT_OTHER_ERROR
    if(not(isinstance(Device, PyD3XX.FT_Device))):
        PyD3XX._Print("Open(), did not get an FT_Device!", PRINT_ERROR_MAJOR, False)
    elif(not(isinstance(Device._Handle, ctypes.c_void_p))):
        PyD3XX._Print("Open(), got an uninitialized or broken FT_Device object!", PyD3XX.PRINT_ERROR_MAJOR, False)
    elif(OpenFlag & PyD3XX.FT_OPEN_BY_INDEX):
        if(isinstance(Identifier, int)):
            Status = _DLL.HS_Open(Identifier, PyD3XX.FT_OPEN_BY_INDEX, ctypes.byref(Device._Handle))
            Device.Handle = Device._Handle.value
        else:
            PyD3XX._Print("Open(), did not get expected int for index!", PyD3XX.PRINT_ERROR_MAJOR, False)
    elif(OpenFlag & PyD3XX.FT_OPEN_BY_SERIAL_NUMBER):
        if(isinstance(Identifier, str)):
            Status = _DLL.HS_Open(Identifier.encode("ascii"), PyD3XX.FT_OPEN_BY_SERIAL_NUMBER, ctypes.byref(Device._Handle))
            Device.Handle = Device._Handle.value
        else:
            PyD3XX._Print("Open(), did not get expected str for serial number!", PyD3XX.PRINT_ERROR_MAJOR, False)
    elif(OpenFlag & PyD3XX.FT_OPEN_BY_DESCRIPTION):
        if(isinstance(Identifier, str)):
            Status = _DLL.HS_Open(Identifier.encode("ascii"), PyD3XX.FT_OPEN_BY_DESCRIPTION, ctypes.byref(Device._Handle))
            Device.Handle = Device._Handle.value
        else:
            PyD3XX._Print("Open(), did not get expected str for description!", PyD3XX.PRINT_ERROR_MAJOR, False)
    else:
        PyD3XX._Print("Open(), given invalid open flag!", PyD3XX.PRINT_ERROR_MAJOR, False)
    return Status

def Close(Device: PyD3XX.FT_Device) -> int:
    return _DLL.HS_Close(Device._Handle)

def CreateQueue(Device: PyD3XX.FT_Device, Pipe: PyD3XX.FT_Pipe, StreamSize: int, QueueLength: int, Fixed: bool) -> int | Queue:
    if(Device.Handle == "FT_OTHER_ERROR"):
        PyD3XX._Print("CreateQueue(), was not given a valid FT_Device.", PyD3XX.PRINT_ERROR_MINOR)
        return PyD3XX.FT_INVALID_HANDLE
    NewQueue = Queue() #Create point to hold queue.
    Status = _DLL.HS_CreateQueue(Device._Handle, Pipe.PipeID, StreamSize, QueueLength, int(Fixed), ctypes.byref(NewQueue._HS_Queue))
    if(Status == PyD3XX.FT_OK):
        NewQueue._StreamSize = StreamSize
    return Status, NewQueue

def DestroyQueue(DQueue: Queue) -> int:
    Status = _DLL.HS_DestroyQueue(DQueue._HS_Queue)
    return Status

def ReadQueue(RQueue: Queue, Wait: bool) -> int | PyD3XX.FT_Buffer | int:
    Buffer = PyD3XX.FT_Buffer()
    Buffer._RawAddress = ctypes.c_buffer(RQueue._StreamSize)
    BytesTransferred = ctypes.c_ulong(0)
    Status = _DLL.HS_ReadQueue(ctypes.byref(RQueue._HS_Queue),
                               ctypes.byref(Buffer._RawAddress),
                               ctypes.byref(BytesTransferred),
                               int(Wait))
    if(Status != PyD3XX.FT_OK):
        Buffer = PyD3XX.FT_Buffer()
    return Status, Buffer, BytesTransferred.value

def WriteQueue(WQueue: Queue, Buffer: PyD3XX.FT_Buffer, Wait: bool) -> int:
    Status = PyD3XX.FT_OTHER_ERROR
    if(isinstance(Buffer._RawAddress, PyD3XX.FT_Buffer)):
        PyD3XX._Print("WriteQueue(), was not given expected FT_Buffer.", PyD3XX.PRINT_ERROR_MAJOR, False)
        return Status
    Status = _DLL.HS_WriteQueue(WQueue._HS_Queue,
                                ctypes.byref(Buffer._RawAddress),
                                int(Wait))
    return Status

def GetWriteStatus(GQueue, Wait: bool) -> int:
    BytesTransferred = ctypes.c_ulong(0)
    Status = _DLL.HS_GetWriteStatus(ctypes.byref(GQueue._HS_Queue),
                                    ctypes.byref(BytesTransferred),
                                    int(Wait))
    return Status

def FreeQueueD3XX() -> int:
    return _DLL.HS_FreeQueueD3XX()