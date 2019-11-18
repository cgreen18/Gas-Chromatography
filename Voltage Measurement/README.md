# Thermal Conductivity Sensing via Diodes
![Total Sensing Circuit Diagram](https://github.com/cgreen18/Gas-Chromatography/blob/master/Voltage%20Measurement/images/GC_ForwardVoltageDiffAmp.png)

## Breakdown of the System
![Total Diagram Illustrated](https://github.com/cgreen18/Gas-Chromatography/blob/master/Voltage%20Measurement/images/GC_ForwardVoltageDiffAmp_Illustrated.png)

### Diode Biasing
The core operation of our GC is to measure the difference in forward voltage between the dependent and control diodes, D1 and D2 in the figure below. Both the dependent and control diodes are in the detector, at the same temperature, and have inert gas flowing over them; however, the substance being tested does not flow over the control. The diodes are biased with an AC voltage (CITE PAPER) and set in parallel with a current limiting 1kOHM resistor in series as seen in the figure below.

![Diode Biasing Setup](https://github.com/cgreen18/Gas-Chromatography/blob/master/Voltage%20Measurement/images/GC_DiodeBiasing.png)

### Differential Amplifier
In order to find the difference in the forward voltage between diodes one and two, the low power [AD620AN Instrumental Amplifier](https://www.analog.com/en/products/ad620.html#product-overview) was used for it's low noise, high accuracy, and self-contained pre-amplification. The IC should be drift stable and accurate even without an intelligent processor that zeros and therefore, perfect for this GC application focused on simplicity and economics. The gain is determined by the resistance between the R<sub>g</sub> pins and set to ~1000 in this application. The differential amplification stage is given in the figure below.

![AD620AN Configuration](https://github.com/cgreen18/Gas-Chromatography/blob/master/Voltage%20Measurement/images/GC_AD620ANConfiguration.png)
