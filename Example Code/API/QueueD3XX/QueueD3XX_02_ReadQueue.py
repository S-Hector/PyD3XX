import PyD3XX
import PyD3XX.Queue

QUEUE_SIZE = 30 # How large our read/write pipe call queues should be.

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

Status, Pipe = PyD3XX.FT_GetPipeInformation(Device, 1, 1)
if Status != PyD3XX.FT_OK:
    print("FAILED TO GET PIPE INFO OF [1,1]: ABORTING")
    exit()
# PipeIndex is 1, which is channel 1 IN/read endpoint.
# Following queue will automatically queue up read requests.
Status, ReadQueue = PyD3XX.Queue.CreateQueue(Device, Pipe, 1, QUEUE_SIZE, False)
if(Status != PyD3XX.FT_OK):
    print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO CREATE READ QUEUE!")
    exit()

print("Successfully made read queue!")
while True:
    Status, Buffer, BytesTransferred = PyD3XX.Queue.ReadQueue(ReadQueue, True)
    if(Status != PyD3XX.FT_OK) and (Status != PyD3XX.FT_IO_INCOMPLETE) and (Status != PyD3XX.FT_IO_PENDING) and (Status != PyD3XX.FT_NO_MORE_ITEMS):
        print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO READ CHANNEL 1 PIPE!")
        exit()
    ReadValue = int.from_bytes(Buffer.Value(), "little")
    print("Data In = " + str(ReadValue))
    if ReadValue >= 3:
         print("Reached value 3, ending streaming!")
         break

Status = PyD3XX.Queue.DestroyQueue(ReadQueue)
if(Status != PyD3XX.FT_OK):
    print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO DESTROY READ QUEUE!")
    exit()

Status = PyD3XX.Queue.FreeQueueD3XX() # Automatically destroys all queues and cleans up.
if(Status != PyD3XX.FT_OK):
    print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO FREE QueueD3XX!")
    exit()

Status = PyD3XX.FT_Close(Device)
if(Status == PyD3XX.FT_OK):
    print("Program ended and device closed successfully.")
