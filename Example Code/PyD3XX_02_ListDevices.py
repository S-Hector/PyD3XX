import PyD3XX

PyD3XX.SetPrintLevel(PyD3XX.PRINT_NONE) # Make PyD3XX not print anything.

print("---| Testing ListDevices() Calls |---")
Status, Count = PyD3XX.FT_ListDevices(PyD3XX.NULL, PyD3XX.FT_LIST_NUMBER_ONLY)
print("Device Count: " + str(Count))
Status, SerialNumber = PyD3XX.FT_ListDevices(0, PyD3XX.FT_LIST_BY_INDEX | PyD3XX.FT_OPEN_BY_SERIAL_NUMBER)
print("Device 0 Serial Number: " + str(SerialNumber))
Status, Description = PyD3XX.FT_ListDevices(0, PyD3XX.FT_LIST_BY_INDEX | PyD3XX.FT_OPEN_BY_DESCRIPTION)
print("Device 0 Description: " + str(Description))
Status, SerialNumbers = PyD3XX.FT_ListDevices(Count, PyD3XX.FT_LIST_ALL | PyD3XX.FT_OPEN_BY_SERIAL_NUMBER)
for i in range(Count):
    print("Device " + str(i) + " Serial Number: " + str(SerialNumbers[i]))
Status, Descriptions = PyD3XX.FT_ListDevices(Count, PyD3XX.FT_LIST_ALL | PyD3XX.FT_OPEN_BY_DESCRIPTION)
for i in range(Count):
    print("Device " + str(i) + " Description: " + str(Descriptions[i]))