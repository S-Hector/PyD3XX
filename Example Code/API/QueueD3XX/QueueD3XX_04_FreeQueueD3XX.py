import PyD3XX
import PyD3XX.Queue

Status = PyD3XX.Queue.FreeQueueD3XX() # Automatically destroys all queues and cleans up.
if(Status != PyD3XX.FT_OK):
    print(PyD3XX.FT_STATUS_STR[Status] + " | FAILED TO FREE QueueD3XX!")
    exit()
print("Successfully freed QueueD3XX!")