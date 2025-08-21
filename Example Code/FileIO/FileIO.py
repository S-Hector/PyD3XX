import PyD3XX
import time
PyD3XX.SetPrintLevel(PyD3XX.PRINT_NONE) # Make PyD3XX not print anything.

GEN_INPUT_FILE = 0 # If non-zero a new input file will be created.
GEN_INPUT_FILE_SIZE = 1600000 # Size of new input file in bytes if GEN_INPUT_FILE is non-zero.
INPUT_FILE_NAME = "HD_Test_Video" # Name of input file without extensions.
FILE_EXTENSION = ".mp4" # File extension for both the input and output files.
INPUT_FILE = INPUT_FILE_NAME + FILE_EXTENSION # Entire name of input file we're using/creating.

if(GEN_INPUT_FILE): # Create input file.
    InputFile = open(INPUT_FILE, "wb")
    BytesWritten = 0
    for i in range(GEN_INPUT_FILE_SIZE): # Write bytes in ascending order. Values will repeat.
        BytesWritten += InputFile.write((i & int("0x00FF", 16)).to_bytes())
    InputFile.close() # Close the file.
    print("Bytes Written to '" + INPUT_FILE + "': " + str(BytesWritten))

try:
    InputFile = open(INPUT_FILE, "rb")
    InputData = InputFile.read() # Read in file as bytes.
    DataSize = len(InputData) # Get length of input file.
    InputData = PyD3XX.FT_Buffer.from_bytes(InputData) # Put file bytes into an FT_Buffer.
    InputFile.close()
except:
    print("FAILED TO READ '" + INPUT_FILE + "': ENDING PROGRAM")
    exit()

Status, DeviceCount = PyD3XX.FT_CreateDeviceInfoList() # Create a device info list.
if Status != PyD3XX.FT_OK:
    print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO CREATE DEVICE INFO LIST: ABORTING")
    exit()
if(DeviceCount < 1):
    print("NO DEVICES DETECTED: ENDING PROGRAM")
    exit()

print(str(DeviceCount) + " Devices detected.")

Status, Device = PyD3XX.FT_GetDeviceInfoDetail(0) # Get info of device at index 0.
if Status != PyD3XX.FT_OK:
    print(PyD3XX.FT_STATUS_STR[Status] + " | WARNING: FAILED TO GET INFO FOR DEVICE 0")
    exit()
if(Device.Flags & PyD3XX.FT_FLAGS_OPENED):
    print("Device 0 is opened by another process: ENDING PROGRAM")
    exit()

Status = PyD3XX.FT_Create(0, PyD3XX.FT_OPEN_BY_INDEX, Device) # Open the device we're using.
if Status != PyD3XX.FT_OK:
    print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO OPEN DEVICE: ABORTING")
    exit()

Pipes = {} # Pipes we're reading/writing to.
Overlaps = {} # Overlaps to handle asynchronous reads & writes.
for i in range(8): # Get in and out pipes for channels 1-4.
    Status, Pipes[i] = PyD3XX.FT_GetPipeInformation(Device, 1, i)
    if Status != PyD3XX.FT_OK:
        print("FAILED TO GET PIPE INFO OF [1," + str(i) +"]: ABORTING")
        exit()
    Status, Overlaps[i] = PyD3XX.FT_InitializeOverlapped(Device) # Create overlaps.
    if(Status != PyD3XX.FT_OK):
        print("FAILED TO CREATE OVERLAP FOR PIPE " + str(i) + ": ABORTING")
        exit()

for i in range (0, 7, 2): # Write data to all four channels.
    if(PyD3XX.Platform == "linux") or (PyD3XX.Platform == "darwin"):
        Status, BytesWrote = PyD3XX.FT_WritePipeAsync(Device, round(i/2), InputData, DataSize, Overlaps[i])
    else:
        Status, BytesWrote = PyD3XX.FT_WritePipe(Device, Pipes[i], InputData, DataSize, Overlaps[i])
    if(Status != PyD3XX.FT_OK) and (Status != PyD3XX.FT_IO_PENDING):
        print(PyD3XX.FT_STATUS_STR[Status] + " | ERROR: Async write failed!")
        print("ENDING PROGRAM")
        exit()

# At this point we have issued an asynchronous write request for the whole file to all four channels.
# The write requests either completed with FT_OK or are in-progress with FT_IO_PENDING.

ReadBuffer = {} # Buffers to hold data for each channel.
for i in range (1, 8, 2): # Read data from all four channels.
    if(PyD3XX.Platform == "linux") or (PyD3XX.Platform == "darwin"):
        Status, ReadBuffer[i], BytesRead = PyD3XX.FT_ReadPipeAsync(Device, round((i - 1)/2), DataSize, Overlaps[i])
    else:
        Status, ReadBuffer[i], BytesRead = PyD3XX.FT_ReadPipe(Device, Pipes[i], DataSize, Overlaps[i])
    if(Status != PyD3XX.FT_OK) and (Status != PyD3XX.FT_IO_PENDING):
        print(PyD3XX.FT_STATUS_STR[Status] + " | ERROR: Async read failed!")
        print("ENDING PROGRAM")

# At this point we have issued an asynchronous read request for the whole file to all four channels.
# The read requests either completed with FT_OK or are in-progress with FT_IO_PENDING.

for i in range (1, 8, 2): # Wait for read request to complete for all four channels.
    Status = PyD3XX.FT_IO_INCOMPLETE
    while(Status == PyD3XX.FT_IO_INCOMPLETE):
        Status, BytesTransferred = PyD3XX.FT_GetOverlappedResult(Device, Overlaps[i], False)
        time.sleep(0.5)
        print(str(BytesTransferred) + "/" + str(DataSize) + " bytes transferred so far at pipe index " + str(i) + "!")
        if(Status == PyD3XX.FT_OK):
            print("Successfully read " + str(BytesTransferred) + " bytes at pipe index " + str(i) + "!")

# At this point we have received all data from all of the channels!

OutputFile = {}
for i in range (1, 8, 2): # Write output file for each channel.
    OutputFile[i] = open("Output_PI_" + str(i) + FILE_EXTENSION, "wb")
    try:
        OutputFile[i].write(ReadBuffer[i].Value())
    except:
        print("Failed to write output file for pipe index " + str(i) + "!")
        print("ENDING PROGRAM")
        exit()
    OutputFile[i].close()
    print("Successfully wrote file '" + "Output_PI_" + str(i) + FILE_EXTENSION + "'!")

for i in range(8): # Release overlaps since we're done using them.
    Status = PyD3XX.FT_ReleaseOverlapped(Device, Overlaps[i])
    if Status != PyD3XX.FT_OK:
        print(PyD3XX.FT_STATUS_STR[Status] + " | WARNING: FAILED TO RELEASE OVERLAP " + str(i))

PyD3XX.FT_Close(Device)