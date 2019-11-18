# Oven, Injector, and Detector Heating Control

![Increasing Delay gif](https://github.com/cgreen18/Gas-Chromatography/blob/master/Heating/images/GC_TriacClipping_Oscilloscope_IncreasingDelay.gif)
Example of Reducing Power Delivered to Element.

## Breakdown of the System

#### Triac Dimmer
Two [RoboDyn AC Light Dimmer](https://robotdyn.com/ac-light-dimmer-module-1-channel-3-3v-5v-logic-ac-50-60hz-220v-110v.html) were used to heat the elements: one dimmer for the oven and the other for the injector and detector together. This modules are triac based and as such, can clip the positive and negative waveforms

The method of operation is illustrated in the oscilloscope reading in the figure below.
![Example Clip Oscilloscope](https://github.com/cgreen18/Gas-Chromatography/blob/master/Heating/images/GC_TriacClipping_Oscilloscope.png)
Legend:
* Yellow - Wall voltage = 120V @ 60Hz
* Blue - Load (heating element) voltage
* Purple - Zero-cross
* Green - Trigger square pulse

#### Estimating Temperature
The voltage across the thermocouples is amplified by ~250 by an [LM358N](http://www.ti.com/product/LM358-N) as seen in the figure below.

![Non-inverting_amp](https://github.com/cgreen18/Gas-Chromatography/blob/master/Heating/images/GC_ThermoAmp_SimpleCircuit_Snippet.png)




#### PID Control

![PID_Diagram](https://github.com/cgreen18/Gas-Chromatography/blob/master/Heating/images/PID_en.svg)
Credit: Wikipedia @ [PID_Diagram_Link](https://en.wikipedia.org/wiki/PID_controller)


