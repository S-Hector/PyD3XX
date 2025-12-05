import PyD3XX

CHANNEL_COUNT = 4 # How many channels we're streaming.
STREAM_SIZE = 100000 # How many bytes each read pipe call is.
VALUE_SIZE = 2 # How many bytes each counter value is.
# Total counter values = STREAM_SIZE / VALUE_SIZE
FIXED_TRANSFER_SIZE = False # Fix the transfer size. DO NOT enable unless STREAM_SIZE is a multiple of MaxPacketSize.
LOOP_COUNT = 1 # Set to True to loop forever. Set to an integer X value to loop X times.
CHECK_INCREMENT = True # Stop streaming if a counter value is not greater than the previous by 1.
PRINT_COUNT = True # Set to true if you want to print every single value.

def GetValue(Buffer: PyD3XX.FT_Buffer, Index: int) -> int:
    Value = 0
    for i in range(VALUE_SIZE):
        Value += (Buffer.Value()[Index + i]) << (i*8)
    return Value

if(CHECK_INCREMENT) and ((STREAM_SIZE < (VALUE_SIZE*2)) or ((STREAM_SIZE % VALUE_SIZE) != 0)):
    print("ERROR: STREAM_SIZE must be divisible by " + str(VALUE_SIZE) + " and " + str(VALUE_SIZE*2) + " or greater.")
    exit()
if(CHANNEL_COUNT > 4):
    print("ERROR: CHANNEL_COUNT must be 4 or less.")
    exit()

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
Overlaps = {}
for i in range(1, (CHANNEL_COUNT * 2), 2): # Get IN pipes.
    Status, Pipes[i] = PyD3XX.FT_GetPipeInformation(Device, 1, i)
    if Status != PyD3XX.FT_OK:
        print("FAILED TO GET PIPE INFO OF [1," + str(i) +"]: ABORTING")
        exit()
    Status, Overlaps[i] = PyD3XX.FT_InitializeOverlapped(Device)
    if(Status != PyD3XX.FT_OK):
        print("FAILED TO CREATE OVERLAP FOR PIPE " + str(i) + ": ABORTING")
        exit()

if(FIXED_TRANSFER_SIZE):
    Status = PyD3XX.FT_SetStreamPipe(Device, False, True, PyD3XX.NULL, STREAM_SIZE)
    if Status != PyD3XX.FT_OK:
        print("FAILED TO SET STREAM SIZE FOR ALL IN PIPES. " + PyD3XX.FT_STATUS_STR[Status])
        exit()

ReadBuffer = {}

print("Input streaming is starting now...")
Loop = 0
while LOOP_COUNT: # Read IN pipes.
    if(PRINT_COUNT):
        print("---| Loop " + str(Loop) + " |---")
    for i in range(1, (CHANNEL_COUNT * 2), 2): # Issue reads.
        if(PyD3XX.Platform == "linux") or (PyD3XX.Platform == "darwin"):
            Status, ReadBuffer[i], BytesRead = PyD3XX.FT_ReadPipeAsync(Device, round((i - 1)/2), STREAM_SIZE, Overlaps[i])
        else:
            Status, ReadBuffer[i], BytesRead = PyD3XX.FT_ReadPipe(Device, Pipes[i], STREAM_SIZE, Overlaps[i])
    for i in range(1, (CHANNEL_COUNT * 2), 2): # Wait for reads to finish.
        Status = PyD3XX.FT_IO_INCOMPLETE
        while(Status == PyD3XX.FT_IO_INCOMPLETE):
            Status, BytesTransferred = PyD3XX.FT_GetOverlappedResult(Device, Overlaps[i], False)
            if(Status == PyD3XX.FT_OK): break
    if CHECK_INCREMENT:
        for i in range(1, (CHANNEL_COUNT * 2), 2): # Check values read.
            if(PRINT_COUNT): # Print first value.
                    CurrentValue = GetValue(ReadBuffer[i], 0)
                    print("CH" + str(round((i+1)/2)) + "[" + str(0) + "]: " + str(CurrentValue))
            for j in range(VALUE_SIZE, STREAM_SIZE, VALUE_SIZE):
                LastValue = GetValue(ReadBuffer[i], j - VALUE_SIZE)
                CurrentValue = GetValue(ReadBuffer[i], j)
                if(PRINT_COUNT):
                    print("CH" + str(round((i+1)/2)) + "[" + str(j) + "]: " + str(CurrentValue))
                if(CurrentValue != (LastValue + 1)): # Value is not bigger by 1.
                    if((CurrentValue == 0) and (LastValue == ((2 ** (VALUE_SIZE*8)) - 1))): # Account for counter overflow.
                        continue # There is no error if the counter just overflowed.
                    print("ERROR Loop " + str(Loop) + " CH" + str(round((i+1)/2)) + "[" + str(j) + "]: LV = " + str(LastValue) + " CV = " + str(CurrentValue))
                    exit()
    
    if not(isinstance(LOOP_COUNT, bool)): # Decrement LOOP_COUNT if it is an integer.
        LOOP_COUNT -= 1
    Loop += 1

print("Input streaming ended!")