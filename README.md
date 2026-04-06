# PyD3XX
A Python wrapper for FTDI's D3XX library.  

PyD3XX supports Windows, Linux, and MacOS.  
Most D3XX dynamic library variants are included in this package, so you don't need to include them directly in your project!  
^You don't need and should not have any D3XX .dll, .dylib, or .so file in your script's directory.  
This was designed so the user needs zero ctypes knowledge and not need to import anything besides PyD3XX to interact with D3XX (FT600 & FT601) devices. The user should never have to interact with a ctypes object or method.

## Install
If you have Python installed simply run a pip install command to install PyD3XX like one of the below examples.
* "pip install PyD3XX"
* "py -m pip install PyD3XX"
* "python -m pip install PyD3XX"
* "python3 -m pip install PyD3XX"
### DO NOT manually copy files from the GitHub repository to your Python install/s.

## Issues, Requests, or Questions
If you encounter issues, have a request, and/or have any questions, it's better to send them directly to hector.soto@ftdichip.com or us.support@ftdichip.com. Me & the rest of FTDI's support team get immediate notifications of emails sent to us, so you'll receive responses far faster.

## PyPi Links
Official Package: https://pypi.org/project/PyD3XX/  
^ This is the official package.  

Test Package: https://test.pypi.org/project/PyD3XX/  
^ This is the test package which will contain early, experimental, and unstable changes.
