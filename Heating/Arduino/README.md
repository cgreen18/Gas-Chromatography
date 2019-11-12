# Oven, Injector, and Detector Heating Control
three_element_heat_control.ino measures the temperature of the oven, injector, and detector via thermocouples. Two [RoboDyn AC Light Dimmer](https://robotdyn.com/ac-light-dimmer-module-1-channel-3-3v-5v-logic-ac-50-60hz-220v-110v.html) were used to heat the elements: one dimmer for the oven and the other for the injector and detector together.

### Estimating Temperature
The voltage across the thermocouples is amplified by ~250 by an [LM358N](http://www.ti.com/product/LM358-N) as seen in the figure below.

![Non-inverting_amp](https://github.com/cgreen18/Gas-Chromatography/blob/master/Triac%20Heating/Arduino/images/GC_ThermoAmp_SimpleCircuit_Snippet.png)




### PID Control


![PID_Diagram](https://github.com/cgreen18/Gas-Chromatography/blob/master/Triac%20Heating/Arduino/PID_en.svg)
[PID_Diagram_Link](https://en.wikipedia.org/wiki/PID_controller)