# 12. Physics of Mixed-Signal Systems

This chapter explains the physical principles underlying the μATE-STM system. While Chapter 11 provided the mathematical models, this chapter explains *why* those models work by discussing the physics of charge, fields, semiconductors, and noise. Understanding these principles is essential for debugging, optimization, and future design improvements.

***

## 12.1 Physical Modelling Philosophy

### 12.1.1 Why Physical Modelling Matters

Mathematics describes *what* a system does; physics explains *why*. For example:
- **Math:** An RC filter has a transfer function $$ H(s) = \frac{1}{1+sRC} $$.
- **Physics:** Capacitors store energy in electric fields; resistors dissipate energy as heat. The interplay creates frequency-dependent behavior.

Physical understanding allows engineers to:
- **Predict non-idealities:** Math models often assume ideal components; physics reveals parasitics (e.g., wire inductance).
- **Debug effectively:** When measurements deviate from theory, physical insight identifies root causes (e.g., ground loops, thermal drift).
- **Optimize design:** Trade-offs (speed vs. power, bandwidth vs. noise) are fundamentally physical.

### 12.1.2 Relationship Between Physics, Mathematics, and Engineering

- **Physics:** Fundamental laws (Maxwell's equations, quantum mechanics).
- **Mathematics:** Abstractions (differential equations, Fourier transforms).
- **Engineering:** Practical application (component selection, layout, testing).

**Example:**  
- **Physics:** Electrons drift in a conductor under an electric field.
- **Math:** $$ I = V/R $$ (Ohm's Law).
- **Engineering:** Choose 1% resistors to minimize gain error.

### 12.1.3 Assumptions and Approximations

- **First-Order Models:** Ignore parasitics (e.g., ideal wires, zero inductance). Valid for low-frequency (< 100 kHz) designs like this project.
- **Higher-Order Models:** Include parasitics (trace inductance, capacitor ESR). Necessary for RF or high-speed digital.

**Educational Scope:**  
This project uses first-order models to teach core concepts. Higher-order effects (e.g., skin effect, dielectric loss) are acknowledged but not analyzed in depth.

***

## 12.2 Electric Charge and Current

### 12.2.1 Electric Charge

**Physical Principle:**  
Charge ($$ Q $$, coulombs) is a fundamental property of matter. Electrons carry negative charge ($$ -1.6 \times 10^{-19} $$ C).

**Relevance:**  
ADC/DAC operation involves moving charge onto/off capacitors. The amount of charge determines the voltage ($$ V = Q/C $$).

### 12.2.2 Electric Field

**Physical Principle:**  
A charge creates an electric field ($$ \mathbf{E} $$, V/m) that exerts force on other charges ($$ \mathbf{F} = q\mathbf{E} $$).

**Relevance:**  
- **Capacitors:** Electric field stores energy between plates.
- **MOSFETs:** Gate electric field controls channel conductivity.

### 12.2.3 Current and Drift Velocity

**Physical Principle:**  
Current ($$ I $$, amperes) is the flow of charge. In conductors, electrons drift at slow velocities ($$ \sim 1 $$ mm/s) but the electric field propagates near light speed.

**Current Density:**
$$
\mathbf{J} = \sigma \mathbf{E}
$$
where $$ \sigma $$ is conductivity.

**Engineering Implication:**  
PCB trace width determines current-carrying capacity. For μATE-STM (low current, < 10 mA), standard breadboard wires are sufficient.

***

## 12.3 Voltage and Electric Potential

### 12.3.1 Electric Potential

**Physical Principle:**  
Voltage ($$ V $$, volts) is electric potential difference. It represents energy per unit charge ($$ 1 \text{ V} = 1 \text{ J/C} $$).

**Reference Node (Ground):**  
Voltage is always measured *relative* to a reference. In μATE-STM:
- **Analog Ground (AGND):** Reference for ADC/DAC.
- **Digital Ground (DGND):** Reference for logic.
- **Single-Point Ground:** Tied together to avoid ground loops.

**Floating Systems:**  
If no reference is shared (e.g., battery-powered STM32 and laptop), communication fails. UART requires common ground.

**Common-Mode vs Differential Voltage:**  
- **Differential:** Signal of interest ($$ V_+ - V_- $$).
- **Common-Mode:** Average voltage relative to ground. ADCs reject common-mode noise (within limits).

***

## 12.4 Resistive Physics

### 12.4.1 Microscopic Origin of Resistance

**Physical Principle:**  
Electrons collide with atoms in the conductor lattice, losing energy as heat. Resistance ($$ R $$) quantifies this opposition.

**Ohm's Law (Physical View):**
$$
V = I R
$$
Voltage drives current; resistance dissipates energy ($$ P = I^2 R $$).

### 12.4.2 Temperature Dependence

**Physical Principle:**  
Higher temperature → more lattice vibrations → more collisions → higher resistance.

**Temperature Coefficient:**  
For carbon/metal film resistors: $$ \alpha \approx 50–100 $$ ppm/°C.

**Engineering Implication:**  
- **Gain Error:** Resistor divider ratio drifts with temperature.
- **Mitigation:** Use low-TC resistors for precision applications.

### 12.4.3 Johnson-Nyquist Thermal Noise

**Physical Principle:**  
Thermal agitation of electrons creates random voltage fluctuations.

**RMS Noise Voltage:**
$$
V_{\text{noise,rms}} = \sqrt{4 k_B T R \Delta f}
$$
where $$ k_B $$ is Boltzmann's constant, $$ T $$ is temperature (K), $$ \Delta f $$ is bandwidth.

**Example (1 kΩ, 10 kHz BW, 300 K):**
$$
V_{\text{noise}} \approx \sqrt{4 \times 1.38 \times 10^{-23} \times 300 \times 1000 \times 10^4} \approx 400 \text{ nV}
$$

**Relevance:**  
Negligible compared to ADC quantization noise (0.8 mV), but important for high-gain amplifiers.

***

## 12.5 Capacitance

### 12.5.1 Electric Field Storage

**Physical Principle:**  
A capacitor stores energy in the electric field between two conductive plates separated by a dielectric.

**Capacitance:**
$$
C = \frac{\varepsilon A}{d}
$$
where $$ \varepsilon $$ is permittivity, $$ A $$ is area, $$ d $$ is separation.

**Charging/Discharging:**  
Current flows only when voltage changes ($$ I = C \frac{dV}{dt} $$).

### 12.5.2 Displacement Current

**Physical Principle:**  
Changing electric field in the dielectric acts like a current (Maxwell's correction to Ampere's Law).

**Relevance:**  
- **Decoupling Capacitors:** Provide high-frequency current to ICs, bypassing inductive power traces.
- **RC Filters:** Capacitor impedance $$ Z_C = \frac{1}{j\omega C} $$ decreases with frequency, shunting high-frequency noise to ground.

### 12.5.3 Parasitic Capacitance

**Physical Principle:**  
Any two conductors separated by an insulator form a capacitor. Breadboard rows have ~2–5 pF parasitic capacitance.

**Impact:**  
- **High-Frequency Roll-off:** Parasitic capacitance with trace resistance forms unintended low-pass filters.
- **Mitigation:** Keep traces short; use ground planes.

***

## 12.6 Inductance

### 12.6.1 Magnetic Fields and Inductance

**Physical Principle:**  
Current flowing through a conductor creates a magnetic field. Changing current induces voltage (Faraday's Law):
$$
V = L \frac{dI}{dt}
$$
where $$ L $$ is inductance (henries).

**Self-Inductance:**  
A wire has inductance (~1 nH/mm for breadboard wires).

**Engineering Implication:**  
- **Switching Noise:** Rapid current changes (e.g., MCU clock) induce voltage spikes.
- **Mitigation:** Decoupling capacitors placed close to ICs minimize loop area.

### 12.6.2 Mutual Inductance

**Physical Principle:**  
Magnetic field from one wire induces voltage in a nearby wire (crosstalk).

**Impact:**  
- **Analog-Digital Coupling:** Digital signals (UART) can couple into analog lines (ADC input).
- **Mitigation:** Separate analog/digital routing; use ground shielding.

***

## 12.7 Electromagnetic Noise

### 12.7.1 EMI and RFI

**Physical Principle:**  
Electromagnetic interference (EMI) and radio-frequency interference (RFI) are external fields that induce currents in circuits.

**Coupling Mechanisms:**
1. **Conducted:** Noise travels via power/ground connections.
2. **Radiated:** Noise couples through air (antenna effect).

**Loop Area:**  
Induced voltage is proportional to the area of the current loop ($$ V \propto \frac{d\Phi}{dt} $$).

**Mitigation in μATE-STM:**
- **Small Loops:** Keep analog signal paths short.
- **Ground Plane:** Provides low-impedance return path.

***

## 12.8 Semiconductor Physics

### 12.8.1 Band Theory

**Physical Principle:**  
Electrons occupy energy bands: valence band (bound) and conduction band (free). The gap between them is the bandgap ($$ E_g $$).

**Semiconductors:**  
- **Intrinsic:** Pure silicon; few free carriers.
- **Doped:** Impurities add carriers (n-type: extra electrons; p-type: extra holes).

### 12.8.2 PN Junction

**Physical Principle:**  
Joining p-type and n-type creates a depletion region. Forward bias reduces barrier (current flows); reverse bias increases it (no current).

**Relevance:**  
- **Diodes:** Protection clamps in AFE (Chapter 8).
- **ESD Diodes:** Internal to STM32 pins.

### 12.8.3 MOSFET Operation

**Physical Principle:**  
Gate voltage creates an electric field that attracts carriers, forming a conductive channel.

**CMOS Logic:**  
- **NMOS:** Conducts when gate is high.
- **PMOS:** Conducts when gate is low.
- **Low Power:** Current flows only during switching.

**Relevance:**  
- **STM32 GPIO:** MOSFETs drive pins.
- **ADC Switches:** MOSFETs connect input to sampling capacitor.

***

## 12.9 Analog-to-Digital Conversion Physics

### 12.9.1 Sample-and-Hold (S/H)

**Physical Principle:**  
A switch connects the input to a capacitor for a fixed time (acquisition). The capacitor holds the voltage during conversion.

**Acquisition Time:**  
Must be long enough for the capacitor to charge to within ½ LSB of the input voltage.
$$
t_{\text{acq}} \geq R_{\text{source}} C_{\text{sample}} \ln(2^N)
$$

**Engineering Implication:**  
- **Source Impedance:** High source resistance (e.g., 10 kΩ divider) increases acquisition time.
- **STM32 ADC:** Requires source impedance < 10 kΩ (datasheet spec).

### 12.9.2 SAR ADC Operation

**Successive Approximation Register (SAR):**
1. **Sample:** Input voltage stored on capacitor.
2. **Compare:** Comparator checks if $$ V_{\text{in}} > V_{\text{DAC}} $$.
3. **Binary Search:** DAC tries codes from MSB to LSB.

**Physical Limitations:**  
- **Comparator Offset:** Introduces gain/offset error.
- **DAC Linearity:** Internal DAC non-linearity affects ADC linearity.
- **Noise:** Thermal noise during sampling adds uncertainty.

***

## 12.10 Digital-to-Analog Conversion Physics

### 12.10.1 Resistor-String DAC

**Physical Principle:**  
A string of equal resistors divides $$ V_{\text{REF}} $$. Switches select the tap corresponding to the digital code.

**Advantages:**  
- Monotonic by design.
- Low glitch energy.

**STM32 DAC:**  
Likely uses a resistor-string architecture (typical for 12-bit MCUs).

### 12.10.2 Output Settling

**Physical Principle:**  
After a code change, the output takes time to settle due to:
- **Switch Resistance:** RC time constant with load capacitance.
- **Slew Rate:** Maximum rate of voltage change.

**Glitch Energy:**  
Transient spike during code transitions (e.g., 0111 → 1000).

**Mitigation:**  
- **RC Filter:** Smooths glitches (Chapter 8).
- **Sampling After Settling:** ADC samples DAC output only after settling time.

***

## 12.11 Clock Physics

### 12.11.1 Crystal Oscillators

**Physical Principle:**  
Quartz crystal vibrates at a resonant frequency when electric field is applied (piezoelectric effect).

**Stability:**  
- **Frequency Tolerance:** ±20–50 ppm.
- **Temperature Drift:** ±30 ppm/°C.

**Phase-Locked Loop (PLL):**  
Multiplies reference frequency to higher system clocks (e.g., 8 MHz → 168 MHz).

### 12.11.2 Clock Jitter

**Physical Principle:**  
Random variation in clock edge timing.

**Impact on ADC:**  
Jitter causes sampling time uncertainty ($$ \Delta t $$), leading to voltage error:
$$
\Delta V = \frac{dV}{dt} \Delta t
$$
For high-frequency signals ($$ \frac{dV}{dt} $$ is large), jitter significantly degrades SNR.

**Engineering Implication:**  
- **STM32:** Internal PLL jitter is low enough for 100 kSPS sampling.
- **High-Speed Designs:** Use external low-jitter clocks.

***

## 12.12 Sampling Physics

### 12.12.1 Aliasing

**Physical Principle:**  
If a signal changes faster than the sampling rate, the samples cannot uniquely represent the frequency.

**Frequency Folding:**  
Frequencies above $$ f_s/2 $$ appear as lower frequencies:
$$
f_{\text{alias}} = |f_{\text{in}} - k f_s|
$$

**Anti-Aliasing Filter:**  
RC low-pass filter attenuates frequencies above $$ f_s/2 $$ before sampling.

### 12.12.2 Aperture Uncertainty

**Physical Principle:**  
The exact moment of sampling is not instantaneous; there is a small window (aperture time).

**Impact:**  
Similar to jitter; limits effective resolution for high-frequency signals.

***

## 12.13 Noise Physics

### 12.13.1 Thermal Noise (Johnson Noise)

**Source:**  
Random thermal motion of electrons in resistors.

**Spectrum:**  
White noise (flat power spectral density).

**Magnitude:**  
~400 nV/√Hz for 1 kΩ at 300 K.

### 12.13.2 Shot Noise

**Source:**  
Discrete nature of charge carriers crossing a potential barrier (e.g., PN junction).

**Magnitude:**  
$$
I_{\text{noise,rms}} = \sqrt{2 q I \Delta f}
$$
Negligible in low-current CMOS circuits.

### 12.13.3 Flicker Noise (1/f Noise)

**Source:**  
Traps in semiconductor material releasing carriers randomly.

**Spectrum:**  
Power increases at low frequencies.

**Impact:**  
Dominates at low frequencies (< 100 Hz); mitigated by AC coupling or chopper stabilization.

### 12.13.4 Quantization Noise

**Source:**  
Rounding error in ADC/DAC.

**Spectrum:**  
Approximately white (for busy signals).

**Magnitude:**  
~0.8 mV RMS for 12-bit, 3.3 V (Chapter 11).

***

## 12.14 Signal Integrity

### 12.14.1 Transmission Lines

**Physical Principle:**  
At high frequencies, traces behave as transmission lines with characteristic impedance ($$ Z_0 $$).

**Reflections:**  
Impedance mismatch causes reflections (ringing).

**Relevance to μATE-STM:**  
- **Low Frequency:** Traces are lumped elements (no transmission line effects).
- **Future Designs:** For > 10 MHz, impedance matching is critical.

### 12.14.2 Crosstalk

**Physical Principle:**  
Capacitive/inductive coupling between adjacent traces.

**Mitigation:**  
- **Spacing:** Increase distance between analog/digital lines.
- **Guard Traces:** Ground traces between sensitive signals.

***

## 12.15 Filters

### 12.15.1 Energy Storage

**Physical Principle:**  
- **Capacitor:** Stores energy in electric field ($$ E = \frac{1}{2} C V^2 $$).
- **Inductor:** Stores energy in magnetic field ($$ E = \frac{1}{2} L I^2 $$).

**Frequency-Dependent Behavior:**  
- **Capacitor:** Low impedance at high frequency (shunts noise).
- **Resistor:** Constant impedance.

**RC Low-Pass Filter:**  
- **Cutoff:** $$ f_c = \frac{1}{2\pi RC} $$.
- **Phase Shift:** Output lags input by up to 90°.

**Transient Response:**  
Step input causes exponential rise: $$ V(t) = V_0 (1 - e^{-t/RC}) $$.

**Settling Time:**  
Time to reach within 1% of final value: $$ t_s \approx 5 RC $$.

***

## 12.16 Thermal Physics

### 12.16.1 Self-Heating

**Physical Principle:**  
Power dissipation ($$ P = I^2 R $$) raises component temperature.

**Thermal Resistance:**  
$$
\Delta T = P \times \theta_{\text{JA}}
$$
where $$ \theta_{\text{JA}} $$ is junction-to-ambient thermal resistance.

**Impact:**  
- **Resistor Drift:** Resistance changes with temperature.
- **ADC Reference:** Internal VREF may drift with chip temperature.

**Mitigation:**  
- **Low Power:** Keep currents low.
- **Ventilation:** Allow air flow.

***

## 12.17 Power Integrity

### 12.17.1 Decoupling

**Physical Principle:**  
Decoupling capacitors provide local energy storage to supply transient currents.

**Why Needed:**  
- **Inductive Traces:** Power traces have inductance; rapid current changes cause voltage droop ($$ V = L \frac{dI}{dt} $$).
- **Solution:** Place 100 nF capacitor close to IC power pins.

### 12.17.2 Ground Bounce

**Physical Principle:**  
Inductance in ground path causes voltage spikes when digital circuits switch.

**Impact:**  
- **ADC Reference:** Ground bounce modulates ADC reference, causing noise.
- **Mitigation:** Separate analog/digital grounds; single-point tie.

***

## 12.18 Error Sources

### 12.18.1 Offset Error

**Physical Origin:**  
- **Comparator Offset:** Internal mismatch in ADC comparator.
- **Amplifier Offset:** Input stage mismatch.

**Manifestation:**  
All codes shifted by a constant value.

### 12.18.2 Gain Error

**Physical Origin:**  
- **Resistor Mismatch:** DAC/feedback network tolerance.
- **VREF Error:** Reference voltage deviation.

**Manifestation:**  
Slope of transfer curve differs from ideal.

### 12.18.3 DNL/INL

**Physical Origin:**  
- **Resistor Mismatch:** In DAC string or ADC ladder.
- **Capacitor Mismatch:** In charge-redistribution ADCs.

**Manifestation:**  
Non-uniform code widths (DNL); curved transfer function (INL).

### 12.18.4 Distortion

**Physical Origin:**  
- **Non-Linearity:** Active devices (transistors) have non-linear I-V curves.
- **Clipping:** Signal exceeds supply rails.

**Manifestation:**  
Harmonics in FFT spectrum.

***

## 12.19 Physical Limitations

### 12.19.1 Finite Bandwidth

**Physical Origin:**  
Parasitic capacitance and inductance limit frequency response.

**Impact:**  
- **ADC:** Cannot sample signals above Nyquist frequency.
- **DAC:** Output slew rate limits maximum frequency.

### 12.19.2 Finite Resolution

**Physical Origin:**  
Quantization is fundamental; cannot represent infinite precision.

**Impact:**  
- **Quantization Noise:** Sets theoretical SNR limit (74 dB for 12-bit).

### 12.19.3 Finite Settling

**Physical Origin:**  
RC time constants prevent instantaneous changes.

**Impact:**  
- **DAC:** Must wait for settling before ADC samples.

***

## 12.20 Engineering Trade-offs

### 12.20.1 Speed vs Accuracy

- **High Speed:** Requires wide bandwidth → more noise, higher power.
- **High Accuracy:** Requires narrow bandwidth, low noise → slower settling.

**Example:**  
- **ADC Sampling Time:** Longer sample time → higher accuracy (more charging time) but lower max sampling rate.

### 12.20.2 Power vs Noise

- **Low Power:** Lower currents → higher thermal noise (for same resistance).
- **Low Noise:** Higher currents → more power dissipation.

**Example:**  
- **Resistor Values:** Higher resistance → lower power but higher thermal noise.

### 12.20.3 Cost vs Precision

- **Precision:** 0.1% resistors, low-noise op-amps → expensive.
- **Cost:** 1% resistors, basic components → sufficient for educational use.

**Decision:**  
μATE-STM uses 1% resistors (cost-effective, adequate for 12-bit).

***

## 12.21 Experimental Observation

### 12.21.1 Demonstrating Thermal Noise

**Experiment:**  
- Measure ADC input with grounded input.
- Observe histogram spread (should be ~1–2 codes wide due to noise).

**Reference:**  
Chapter 10, TC-012 (ADC Acquisition Test).

### 12.21.2 Demonstrating Aliasing

**Experiment:**  
- Generate sine wave at 60 kHz.
- Sample at 100 kSPS.
- Observe 40 kHz peak in FFT (alias).

**Reference:**  
Chapter 10, TC-030 (Sampling Rate Test).

### 12.21.3 Demonstrating Ground Bounce

**Experiment:**  
- Run heavy digital switching (e.g., GPIO toggling at 10 MHz).
- Measure ADC noise floor increase.

**Mitigation Verification:**  
- Add decoupling capacitor; observe noise reduction.

***

## 12.22 Physics Summary

| Physical Phenomenon | Governing Equation | Engineering Implication | Affected Subsystem | Mitigation Strategy | Related Chapter |
|---------------------|--------------------|------------------------|--------------------|---------------------|-----------------|
| **Thermal Noise** | $$ V_{\text{rms}} = \sqrt{4 k_B T R \Delta f} $$ | Sets noise floor | ADC, AFE | Use low R, limit BW | 8, 11 |
| **Quantization Noise** | $$ \text{SNR} = 6.02 N + 1.76 $$ | Limits resolution | ADC, DAC | Oversampling, dithering | 11 |
| **RC Filtering** | $$ f_c = \frac{1}{2\pi RC} $$ | Anti-aliasing | AFE | Select R, C for $$ f_c < f_s/2 $$ | 8, 11 |
| **Clock Jitter** | $$ \Delta V = \frac{dV}{dt} \Delta t $$ | Degrades SNR | ADC, Clock | Low-jitter oscillator | 11 |
| **Ground Bounce** | $$ V = L \frac{dI}{dt} $$ | Adds noise | ADC, Power | Decoupling, ground plane | 8 |
| **Aliasing** | $$ f_{\text{alias}} = |f_{\text{in}} - k f_s| $$ | False frequencies | ADC | Anti-aliasing filter | 11 |
| **Resistor Drift** | $$ \Delta R = R \alpha \Delta T $$ | Gain error | AFE, DAC | Low-TC resistors | 8 |
| **Capacitor Charging** | $$ V(t) = V_0 (1 - e^{-t/RC}) $$ | Settling time | ADC S/H | Ensure $$ t_{\text{acq}} \gg RC $$ | 8 |

***
