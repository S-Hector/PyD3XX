import PyD3XX
import PyD3XX.Queue
import time
import threading # Using solely for input.
import queue # Using solely for input.
import random # Generate random data.

CHANNEL_COUNT = 4 # How many channels we're streaming.
STREAM_SIZE = 98*1024 # How many bytes each read pipe call is.
VALUE_SIZE = 4 # How many bytes each counter value is.
FIXED_TRANSFER_SIZE = False # Fix the transfer size. DO NOT enable unless STREAM_SIZE is a multiple of MaxPacketSize.
QUEUE_SIZE = 50 # How large our read/write pipe call queues should be.
WRITE_OUT = False # If true, a write queue will write random data out.
CHECK_DATA = False # If true, data received will be compared with data sent.

if((STREAM_SIZE < (VALUE_SIZE*2)) or ((STREAM_SIZE % VALUE_SIZE) != 0)):
    print("ERROR: STREAM_SIZE must be divisible by " + str(VALUE_SIZE) + " and " + str(VALUE_SIZE*2) + " or greater.")
    exit()
if(CHANNEL_COUNT > 4):
    print("ERROR: CHANNEL_COUNT must be 4 or less.")
    exit()

def GetValue(Buffer: PyD3XX.FT_Buffer, Index: int) -> int:
    Value = 0
    for i in range(VALUE_SIZE):
        Value += (Buffer.Value()[Index + i]) << (i*8)
    return Value

def CheckInput(Input: queue.SimpleQueue):
    input("Press anything to stop reading.\n")
    Input.put([True]) # Tell main thread we're done reading if user inputs anything.
    print("CheckInput thread has ended")
    return

# ---| Main Code Starts Here |---
Status, DeviceCount = PyD3XX.FT_CreateDeviceInfoList() # Create a device info list.
if Status != PyD3XX.FT_OK:
    print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO CREATE DEVICE INFO LIST: ABORTING")
    exit()
print(str(DeviceCount) + " Devices detected.")
if (DeviceCount == 0):
    print("NO DEVICES DETECTED: ABORTING")
    exit()

Status, Device = PyD3XX.FT_GetDeviceInfoDetail(0) # Get info of a device at index 0.
Status = PyD3XX.Queue.Open(0, PyD3XX.FT_OPEN_BY_INDEX, Device) # Open the device we're using.
if Status != PyD3XX.FT_OK:
    print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO OPEN DEVICE: ABORTING")
    exit()

if(Device.Flags == PyD3XX.FT_FLAGS_SUPERSPEED):
    print("Operating at SuperSpeed.")
elif(Device.Flags == PyD3XX.FT_FLAGS_HISPEED):
    print("Operating at High speed.")
else:
    print("Operating at Full speed.")

Pipes = {}
for i in range(CHANNEL_COUNT * 2): # Get pipes.
    Status, Pipes[i] = PyD3XX.FT_GetPipeInformation(Device, 1, i)
    if Status != PyD3XX.FT_OK:
        print("FAILED TO GET PIPE INFO OF [1," + str(i) +"]: ABORTING")
        exit()

# Main thread starts here.
Latency = queue.SimpleQueue() # Use to store latency between read pipe requests.
InputQueue = queue.SimpleQueue() # Use to get user input.
InputThread = threading.Thread(target=CheckInput, args=(InputQueue,))
InputThread.start() # Start taking in input.

CallQueue = {}
if(WRITE_OUT): # Create Write queues and initiate writing out QUEUE_SIZE times.
    WriteBuffer = PyD3XX.FT_Buffer.from_bytes(random.randbytes(STREAM_SIZE))
    for i in range(0, (CHANNEL_COUNT * 2), 2): # Write pipes, 0, 2, 4, 6
        Status, CallQueue[i] = PyD3XX.Queue.CreateQueue(Device, Pipes[i], STREAM_SIZE, QUEUE_SIZE, FIXED_TRANSFER_SIZE)
        if(Status != PyD3XX.FT_OK):
            print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO CREATE WRITE QUEUE!")
            exit()
        for j in range(QUEUE_SIZE): # Issue writes.
            Status = PyD3XX.Queue.WriteQueue(CallQueue[i], WriteBuffer, True)
            if(Status != PyD3XX.FT_OK):
                print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO WRITE TO QUEUE!")
                exit()

# Create read queues to continuously read.
for i in range(1, (CHANNEL_COUNT * 2), 2): # Read pipes 1, 3, 5, 7.
    Status, CallQueue[i] = PyD3XX.Queue.CreateQueue(Device, Pipes[i], STREAM_SIZE, QUEUE_SIZE, FIXED_TRANSFER_SIZE)
    if(Status != PyD3XX.FT_OK):
            print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO CREATE READ QUEUE!")
            exit()

DataTransferred = 0 # Data transferred each second.
ReadBuffer = {}
EndTranValue = {} # Value at end of transaction.
StartTime = time.perf_counter() # Get start time of second.
while(True):
    if(InputQueue.qsize()): # We received user input.
        if(InputQueue.get()[0]): # Quit if we get True.
            break # Exit while loop early.
    for i in range(1, (CHANNEL_COUNT * 2), 2): # Read pipes 1, 3, 5, 7.
        Status = PyD3XX.FT_IO_PENDING
        #while(Status != PyD3XX.FT_OK):
        #    Status, ReadBuffer[i], BytesTransferred = PyD3XX.Queue.ReadQueue(CallQueue[i], False)
        #    if(Status != PyD3XX.FT_OK) and (Status != PyD3XX.FT_IO_INCOMPLETE) and (Status != PyD3XX.FT_IO_PENDING) and (Status != PyD3XX.FT_NO_MORE_ITEMS):
        #        print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO READ PIPE " + str(i))
        #        exit()
        Status, ReadBuffer[i], BytesTransferred = PyD3XX.Queue.ReadQueue(CallQueue[i], True)
        if(Status != PyD3XX.FT_OK) and (Status != PyD3XX.FT_IO_INCOMPLETE) and (Status != PyD3XX.FT_IO_PENDING) and (Status != PyD3XX.FT_NO_MORE_ITEMS):
            print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO READ PIPE " + str(i))
            exit()
        if(WRITE_OUT): # Queue another write call to replace what we just read.
            # Write queue does not gain space until we get the status of a write.
            Status = PyD3XX.Queue.GetWriteStatus(CallQueue[i-1], True) # Get status of the oldest write request
            if(Status != PyD3XX.FT_OK):
                print(PyD3XX.FT_STATUS_STR[Status] + " | A WRITE REQUEST FAILED!")
            Status = PyD3XX.Queue.WriteQueue(CallQueue[i-1], WriteBuffer, True)
            if(Status != PyD3XX.FT_OK):
                print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO WRITE TO QUEUE!")
            if(CHECK_DATA): # Check data.
                for j in range(STREAM_SIZE):
                    if(WriteBuffer.Value()[j] != ReadBuffer[i].Value()[j]):
                        print("EP" + str(i) + " MISMATCH: WB=" + str(WriteBuffer.Value()[j]) + "\t | RB=" + str(ReadBuffer[i].Value()[j]))
                        exit()
        StartTranValue = {} # Value at start of transaction.
        if not(i in EndTranValue): # Get value at end of transaction.
            EndTranValue[i] = GetValue(ReadBuffer[i], STREAM_SIZE - VALUE_SIZE)
        else: # Last transaction value exists.
            StartTranValue[i] = GetValue(ReadBuffer[i], 0) # Get first value in current transaction.
            Latency.put([StartTranValue[i] - EndTranValue[i]]) # We're storing the latencies of all separate channels.
            # ^ Latency between end of last transaction and start of this transaction.
            EndTranValue[i] = GetValue(ReadBuffer[i], STREAM_SIZE - VALUE_SIZE) # Get end value of current transaction.
    EndTime = time.perf_counter() # Get end time of loop.
    DataTransferred += CHANNEL_COUNT * STREAM_SIZE # Add how much data we transferred/processed (assuming no errors).
    ElapsedTime = EndTime - StartTime
    if(ElapsedTime >= 1): # If 1 second or more has passed.
        StartTime = EndTime
        MB = str(round(DataTransferred / 1000000 / ElapsedTime, 2))
        MiB = str(round(DataTransferred / 1048576 / ElapsedTime, 2))
        print("Performance = " + MiB + " MiB/s\t| " + MB + " MB/s\t| " + str(Latency.qsize()) + " Inbetweens") # Print MiB/s.
        DataTransferred = 0 # Reset data transferred counter.

InputThread.join()

# Find highest latency and calculate average latency.
# THIS ONLY WORKS FOR A SPECIFIC FIFO MASTER IMPLEMENTATION
if False:
    MaxLatency = 0
    AverageLatency = 0
    TotalBetweens = Latency.qsize() 
    while(Latency.qsize()):
        LV = Latency.get()[0]
        AverageLatency += LV
        if(LV > MaxLatency):
            MaxLatency = LV
    AverageLatency = AverageLatency / TotalBetweens
    AverageLatency = str(round(AverageLatency, 2))
    MaxLatency = str(round(MaxLatency, 2))
    print("Max Latency = " + MaxLatency + " us\t| Average Latency = " + AverageLatency + " us")

Status = PyD3XX.Queue.Close(Device)
if(Status == PyD3XX.FT_OK):
    print("Program ended and device closed successfully.")