import PyD3XX
import time
import threading
import queue

CHANNEL_COUNT = 4 # How many channels we're streaming.
STREAM_SIZE = 98 * 1024 # How many bytes each read pipe call is.
VALUE_SIZE = 4 # How many bytes each counter value is.
# Total counter values = STREAM_SIZE / VALUE_SIZE
FIXED_TRANSFER_SIZE = False # Fix the transfer size. DO NOT enable unless STREAM_SIZE is a multiple of MaxPacketSize.
QUEUE_SIZE = 100 # How many read pipe calls should we have queued up?
# ^ Note on Linux/macOS having too many calls queued can lead to libusb/memory errors.
# QUEUE_SIZE does affect performance and tops out. A larger QUEUE_SIZE does improve performance.
# The FT600/FT601 top out at half the maximum performance.
# Max performance in a compiled language = 200 MiB/s for the FT600. 400 MiB/s for the FT601.
# Max performance in Python = about 100 MiB/s for the FT600. 200 MiB/s for the FT601.

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
Status = PyD3XX.FT_Create(0, PyD3XX.FT_OPEN_BY_INDEX, Device) # Open the device we're using.
if Status != PyD3XX.FT_OK:
    print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO OPEN DEVICE: ABORTING")
    exit()

if(Device.Flags == PyD3XX.FT_FLAGS_SUPERSPEED):
    print("Operating at SUPERSPEED")

Pipes = {}
for i in range(1, (CHANNEL_COUNT * 2), 2): # Get IN pipes.
    Status, Pipes[i] = PyD3XX.FT_GetPipeInformation(Device, 1, i)
    if Status != PyD3XX.FT_OK:
        print("FAILED TO GET PIPE INFO OF [1," + str(i) +"]: ABORTING")
        exit()

if(FIXED_TRANSFER_SIZE):
    Status = PyD3XX.FT_SetStreamPipe(Device, False, True, PyD3XX.NULL, STREAM_SIZE)
    if Status != PyD3XX.FT_OK:
        print("FAILED TO SET STREAM SIZE FOR ALL IN PIPES. " + PyD3XX.FT_STATUS_STR[Status])
        exit()

def CheckInput(Input: queue.SimpleQueue):
    input("Press anything to stop reading.\n")
    Input.put([True]) # Tell main thread we're done reading if user inputs anything.
    print("CheckInput thread has ended")
    return

def QueueReads(ReadQueue: queue.SimpleQueue, StopQueue: queue.SimpleQueue): # Keeps read pipe calls queued up.
    while(True):
        if(StopQueue.qsize()): # If main thread sent us something.
            if(StopQueue.get()[0] == True): # Return/quit if main thread tells us to.
                StopQueue.put([False]) # Indicate to main thread we stopped by making queue larger than one.
                StopQueue.put([False])
                print("QueueReads thread has ended.")
                return
        while(ReadQueue.qsize() < QUEUE_SIZE): # Issue a read pipe call until we've reached our target queue size.
            ReadBuffer = {}
            Overlaps = {}
            # Issue read pipe call for EVERY channel.
            for i in range(1, (CHANNEL_COUNT * 2), 2): # Issue reads.
                Status, Overlaps[i] = PyD3XX.FT_InitializeOverlapped(Device) # Create overlaps.
                if(Status != PyD3XX.FT_OK):
                    print("FAILED TO CREATE OVERLAP FOR PIPE " + str(i) + ": ABORTING")
                    exit()
                if(PyD3XX.Platform == "linux") or (PyD3XX.Platform == "darwin"): # Issue read pipe calls.
                    Status, ReadBuffer[i], BytesRead = PyD3XX.FT_ReadPipeAsync(Device, round((i - 1)/2), STREAM_SIZE, Overlaps[i])
                else:
                    Status, ReadBuffer[i], BytesRead = PyD3XX.FT_ReadPipe(Device, Pipes[i], STREAM_SIZE, Overlaps[i])
            ReadQueue.put([Status, ReadBuffer, Overlaps]) # Send overlaps for all channels.

# Create QueueReads thread to queue up read pipe calls.
ReadQueue = queue.SimpleQueue() # Use to transfer buffers and overlaps from read pipe calls.
StopQueue = queue.SimpleQueue() # Use to indicate we're done reading.
InputQueue = queue.SimpleQueue() # Use to get user input.
Latency = queue.SimpleQueue() # Use to store latency between read pipe requests.
QR_Thread = threading.Thread(target=QueueReads, args=(ReadQueue, StopQueue))
InputThread = threading.Thread(target=CheckInput, args=(InputQueue,))
QR_Thread.start() # Start queueing up read pipe calls.
InputThread.start() # Start taking in input.

# Start reading overlaps.
DataTransferred = 0 # Data transferred each second.
EndTranValue = {} # Value at end of transaction.
StartTime = time.perf_counter() # Get start time of second.
while(True):
    if(InputQueue.qsize()): # We received user input.
        if(InputQueue.get()[0]): # Quit if we get True.
            StopQueue.put([True]) # Indicate to QR_Thread we want to stop reading.
            while(StopQueue.qsize() != 2): # Wait for QR_Thread to confirm it has stopped.
                pass # Wait for QR_Thread to confirm it has stopped.
            break # Exit while loop early.
    QR_Data = ReadQueue.get()
    Status = QR_Data[0]
    ReadBuffer = QR_Data[1]
    Overlaps = QR_Data[2]
    for i in range(1, (CHANNEL_COUNT * 2), 2): # Wait for reads to finish.
        Status = PyD3XX.FT_IO_INCOMPLETE
        while(Status == PyD3XX.FT_IO_INCOMPLETE):
            Status, BytesTransferred = PyD3XX.FT_GetOverlappedResult(Device, Overlaps[i], False)
        Status = PyD3XX.FT_ReleaseOverlapped(Device, Overlaps[i]) # Free overlaps.
    # ONE read pipe call for ALL channels finished.
    # We wait for one read pipe call to complete for EVERY channel before checking the next wave of data.
    StartTranValue = {} # Value at start of transaction.
    for i in range(1, (CHANNEL_COUNT * 2), 2): # Check values read.
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

QR_Thread.join()
InputThread.join()

# Clean up any leftover by chance overlaps.
while(ReadQueue.qsize() > 0):
    QR_Data = ReadQueue.get()
    Overlaps = QR_Data[2]
    for i in range(1, (CHANNEL_COUNT * 2), 2): # Free overlaps.
        Status = PyD3XX.FT_ReleaseOverlapped(Device, Overlaps[i])

# Find highest latency and calculate average latency.
# THIS ONLY WORKS FOR A SPECIFIC FIFO MASTER IMPLEMENTATION
if False:
    MaxLatency = 0
    AverageLatency = 0
    TotalBetweens = Latency.qsize() 
    while(Latency.qsize()):
        LV = Latency.get()[0]
        if((LV > 95109324) or (LV < 0)):
            TotalBetweens = TotalBetweens - 1
            print("Removed inbetween")
            continue
        AverageLatency += LV
        if(LV > MaxLatency):
            MaxLatency = LV
    AverageLatency = AverageLatency / TotalBetweens
    AverageLatency = str(round(AverageLatency, 2))
    MaxLatency = str(round(MaxLatency, 2))
    print("Max Latency = " + MaxLatency + " us\t| Average Latency = " + AverageLatency + " us")

Status = PyD3XX.FT_Close(Device)
if(Status == PyD3XX.FT_OK):
    print("Program ended and device closed successfully.")