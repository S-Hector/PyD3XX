import PyD3XX
import PyD3XX.Queue

STREAM_SIZE = 1024 # How many bytes each read pipe call is.
FIXED_TRANSFER_SIZE = False # Fix the transfer size. DO NOT enable unless STREAM_SIZE is a multiple of MaxPacketSize.
QUEUE_SIZE = 5 # How large our read/write pipe call queues should be.

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

Status, Pipe = PyD3XX.FT_GetPipeInformation(Device, 1, 0)
if Status != PyD3XX.FT_OK:
    print("FAILED TO GET PIPE INFO OF [1,0]: ABORTING")
    exit()
# PipeIndex is 0, which is channel 0 OUT/write endpoint.
# Following queue will automatically queue up write requests when given data.
Status, WriteQueue = PyD3XX.Queue.CreateQueue(Device, Pipe, STREAM_SIZE, QUEUE_SIZE, FIXED_TRANSFER_SIZE)
if(Status != PyD3XX.FT_OK):
    print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO CREATE WRITE QUEUE!")
    exit()

print("Successfully made write queue!")
print("Size of Requests = " + str(STREAM_SIZE) + " bytes")
print("Max Requests = " + str(QUEUE_SIZE))
print("Stream size is " + ("FIXED" if FIXED_TRANSFER_SIZE else "NOT FIXED"))

Status = PyD3XX.Queue.DestroyQueue(WriteQueue)
if(Status != PyD3XX.FT_OK):
    print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO DESTROY WRITE QUEUE!")
    exit()
print("Successfully destroyed write queue!")

Status = PyD3XX.Queue.FreeQueueD3XX() # Automatically destroys all queues and cleans up.
if(Status != PyD3XX.FT_OK):
    print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO FREE QueueD3XX!")
    exit()

Status = PyD3XX.FT_Close(Device)
if(Status == PyD3XX.FT_OK):
    print("Program ended and device closed successfully.")
