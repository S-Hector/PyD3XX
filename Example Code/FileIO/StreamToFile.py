# Created By: Hector Soto (hector.soto@ftdichip.com)
# Streams incoming data from a FIFO master to disk.
# Expects FIFO master to never have a session underrun or throws an error otherwise.

import PyD3XX
import time
import threading
import queue
PyD3XX.SetPrintLevel(PyD3XX.PRINT_NONE) # Make PyD3XX not print anything.

CHANNEL_COUNT = 1 # How many channels we're streaming.
STREAM_SIZE = 98*1024 # How many bytes each read pipe call is.
OUTPUT_FILE_NAME = "Output"
OUTPUT_FILE_EXTENSION = ".txt"
# File name will be OUTPUT_FILE_NAME + Channel + OUTPUT_FILE_EXTENSION

FIXED_TRANSFER_SIZE = False # Fix the transfer size. DO NOT enable unless STREAM_SIZE is a multiple of MaxPacketSize.
QUEUE_SIZE = 200 # How many read pipe calls should we have queued up?

if(CHANNEL_COUNT > 4):
    print("ERROR: CHANNEL_COUNT must be 4 or less.")
    exit()

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

OutputFiles = {}
for i in range(CHANNEL_COUNT):
    # Set the buffering value to 20 MiB so disk writes only occur when 20MiB is in memory.
    # By default without doing that ^, small writes happen more frequently which destroys disk performance.
    # For disks, larger writes ~= greater performance.
    # Just like USB, larger data transfers ~= greater performance.
    OutputFiles[i] = open(OUTPUT_FILE_NAME + str(i) + OUTPUT_FILE_EXTENSION, "wb", buffering=1024*1024*20)

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
QR_Thread = threading.Thread(target=QueueReads, args=(ReadQueue, StopQueue))
InputThread = threading.Thread(target=CheckInput, args=(InputQueue,))
QR_Thread.start() # Start queueing up read pipe calls.
InputThread.start() # Start taking in input.

# Start reading overlaps.
StartTime = time.perf_counter() # Get start time of second.
DataTransferred = 0 # Data transferred each second.
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
    j = 0
    for i in range(1, (CHANNEL_COUNT * 2), 2): # Wait for reads to finish.
        Status = PyD3XX.FT_IO_INCOMPLETE
        while(Status != PyD3XX.FT_OK):
            Status, BytesTransferred = PyD3XX.FT_GetOverlappedResult(Device, Overlaps[i], False)
        Status = PyD3XX.FT_ReleaseOverlapped(Device, Overlaps[i]) # Free overlaps.
        if(BytesTransferred != STREAM_SIZE):
            print("ERROR: Read " + str(BytesTransferred) + " bytes, when " + str(STREAM_SIZE) + " bytes were expected!")
        OutputFiles[j].write(bytes(ReadBuffer[i].Value()))
        j = j + 1
    # ONE read pipe call for ALL channels finished.
    # We wait for one read pipe call to complete for EVERY channel before checking the next wave of data.
    EndTime = time.perf_counter() # Get end time of loop.
    DataTransferred += CHANNEL_COUNT * STREAM_SIZE # Add how much data we transferred/processed (assuming no errors).
    ElapsedTime = EndTime - StartTime
    if(ElapsedTime >= 1): # If 1 second or more has passed.
        StartTime = EndTime
        MB = str(round(DataTransferred / 1000000 / ElapsedTime, 2))
        MiB = str(round(DataTransferred / 1048576 / ElapsedTime, 2))
        print("Performance = " + MiB + " MiB/s\t| " + MB + " MB/s") # Print MiB/s.
        DataTransferred = 0 # Reset data transferred counter.

QR_Thread.join()
InputThread.join()

# Clean up any leftover by chance overlaps.
while(ReadQueue.qsize() > 0):
    QR_Data = ReadQueue.get()
    Overlaps = QR_Data[2]
    for i in range(1, (CHANNEL_COUNT * 2), 2): # Free overlaps.
        Status = PyD3XX.FT_ReleaseOverlapped(Device, Overlaps[i])

for i in range(CHANNEL_COUNT):
    OutputFiles[i].close()

Status = PyD3XX.FT_Close(Device)
if(Status == PyD3XX.FT_OK):
    print("Program ended and device closed successfully.")