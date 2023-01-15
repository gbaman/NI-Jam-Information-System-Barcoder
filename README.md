# NI Jam Information System Barcoder
A clientside application that links to a NIJIS (NI Jam Information System) server, to print barcoded labels using a Brother QL-570 label printer.   
The main use of the application is generating and printing equipment labels.   

The following is required for the application to work:
- Copy the `config_example.py` file in secrets to `config.py` and fill in the required details.
- A reel of 29mm wide continuous label paper loaded in the printer (recommended) or a reel of 29x90mm labels in the printer.
- If on Windows, the Brother driver may be required.
- If on Windows (straight from [the brother_ql Github README.md](https://github.com/pklaus/brother_ql)) : Download [libusb-win32-devel-filter-1.2.6.0.exe](https://sourceforge.net/projects/libusb-win32/files/libusb-win32-releases/1.2.6.0/) from sourceforge and install it. After installing, you have to use the "Filter Wizard" to setup a "device filter" for the label printer.
