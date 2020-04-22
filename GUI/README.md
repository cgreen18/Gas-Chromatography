# GUI
Main folder for the software supporting the GC instrument.
This folder will probably moved to a folder with a better name in the final version.

### Versions
|Version     | Date | Features |
|:-----------|:--------|:--------|
| 1.0 | 24 November 2019 | Initial Creation. |
| 1.1 | 24 November 2019 | Implements numpy and plotting to window. Uses random numbers. |
| 1.2 | 31 March 2020 | gc_gui.py defines the frame and panel classes that are put together in gas_chromatography.py. As of currently, it plots an example sin curve in the plotter but interfacing with the ADS1115 will be implemented when this is tested on a Raspberry Pi. |
| 1.3 | 30 March 2020 | Added images to buttons. Added more menu options. Complete overhaul. Utilizes frame and panel classes created in gc_gui and smashes them together using the SplitterWindow. |
| 1.4 | 31 March 2020 | Added Open window, similar to Save As. Both inherit new window class. Save current figure as .png or .jpg |
| [2.0](https://github.com/cgreen18/Gas-Chromatography/tree/master/GUI/2.0_version_stable) | 21 April 2020 | Successfully graphs live data with play button, graphs it live, saves images and .gc files, and clears. Basic, minimum GC supporting software. |
| 2.1 | __future__ | Arduino serial interface. Temperature control and feedback thread. |
