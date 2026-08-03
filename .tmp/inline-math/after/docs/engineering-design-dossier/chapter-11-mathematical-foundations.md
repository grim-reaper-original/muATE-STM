# 11. Mathematical Foundations

This chapter provides the complete mathematical foundation for the μATE-STM system. Every equation used in hardware design, firmware implementation, and host software analysis is derived, explained, and connected to its engineering application. The goal is to ensure that all mathematical models are understood, justified, and correctly implemented.

***

## 11.1 Mathematical Philosophy

### 11.1.1 Why Mathematical Modelling Is Required

Mathematical models serve three critical purposes in this project:

1. **Prediction:** Models allow us to predict system behavior before implementation (e.g., expected ADC codes for a given voltage).
2. **Design:** Equations guide component selection (e.g., resistor values for filters, timer prescalers for sampling rates).
3. **Validation:** Models provide expected results against which measurements are compared (e.g., theoretical vs. measured THD).

### 11.1.2 Relationship Between Mathematics and Implementation

Every mathematical concept in this chapter maps directly to implementation:

- **ADC transfer function** → Firmware ADC configuration and host voltage scaling.
- **Sampling theorem** → ADC sampling rate selection (Chapter 8).
- **FFT equations** → Host signal processing module (Chapter 9).
- **Uncertainty propagation** → Error budget and calibration (Chapter 10).

### 11.1.3 Approximations and Assumptions

Key approximations include:

- **Ideal ADC/DAC:** Initially assumed ideal; non-idealities (DNL, INL, noise) added later.
- **Linear time-invariant (LTI) systems:** Filters and signal paths treated as LTI for analysis.
- **Small-signal models:** Noise and distortion treated as small perturbations.
- **Negligible parasitics:** Breadboard parasitic capacitance/inductance ignored in first-order analysis.

**Justification:**

- These approximations simplify analysis while maintaining sufficient accuracy for educational purposes.
- Higher-order effects (e.g., parasitic capacitance) are characterized empirically in Chapter 10.

### 11.1.4 Numerical Precision Considerations

- **Firmware:** Integer arithmetic (16-bit, 32-bit) for efficiency; floating-point avoided in real-time paths.
- **Host:** Double-precision floating-point (IEEE-754 binary64) for analysis to minimize numerical errors.
- **Quantization:** Explicitly modeled; effects accounted for in SNR and ENOB calculations.

***

## 11.2 Number Systems

### 11.2.1 Binary and Hexadecimal

**Binary (Base-2):**

- Used internally by STM32 for all computations.
- ADC/DAC codes are binary (12-bit: 0 to 4095).

**Hexadecimal (Base-16):**

- Used for compact representation of binary values.
- Example: 12-bit code 4095 = 0xFFF.

**Usage:**

- Firmware: Register values, memory addresses.
- Host: Debug output, packet encoding.

***

### 11.2.2 Signed vs Unsigned Integers

**Unsigned Integers (`uint16_t`, `uint32_t`):**

- Used for ADC/DAC codes (0 to 4095).
- No negative values.

**Signed Integers (`int16_t`, `int32_t`):**

- Used for DNL/INL calculations (can be negative).
- FFT results (complex numbers with real/imaginary parts).

***

### 11.2.3 Fixed-Point Arithmetic

**Definition:**

- Numbers represented as integers with implicit binary point.
- Example: Q12.4 format (12 integer bits, 4 fractional bits).

**Usage:**

- Considered for firmware if floating-point is too slow.
- Not used in current design (floating-point on host only).

***

### 11.2.4 Floating-Point (IEEE-754)

**Format (Binary64):**

- 1 sign bit, 11 exponent bits, 52 mantissa bits.
- Precision: ~15–17 decimal digits.

**Usage:**

- Host software (Python `float` = 64-bit double).
- FFT, statistical calculations, report metrics.

**Why Not in Firmware:**

- STM32F4 has FPU, but integer arithmetic is faster and sufficient for ADC/DAC control.

***

## 11.3 ADC Mathematics

### 11.3.1 ADC Transfer Function

**Purpose:**  
Relates analog input voltage to digital output code.

**Derivation:**

An N-bit ADC divides the full-scale voltage range $V_{\text{FS}}$ into $2^N$ discrete levels.

**Ideal Transfer Function:**

$$
C = \left\lfloor \frac{V_{\text{in}}}{V_{\text{REF}}} \times (2^N - 1) \right\rfloor
$$

**Variables:**

- $C$: Digital output code (integer, 0 to $2^N - 1$).
- $V_{\text{in}}$: Analog input voltage (V).
- $V_{\text{REF}}$: Reference voltage (V), typically 3.3 V.
- $N$: ADC resolution (bits), $N = 12$ for STM32.
- $\lfloor \cdot \rfloor$: Floor function (round down to nearest integer).

**Assumptions:**

- Ideal ADC (no offset, gain, or linearity errors).
- Input range: $0 \leq V_{\text{in}} \leq V_{\text{REF}}$.

**Physical Meaning:**

- Each code represents a voltage range of $\frac{V_{\text{REF}}}{2^N - 1}$.

**Engineering Significance:**

- Used to convert ADC codes to voltages in host software.
- Basis for calibration (offset/gain correction).

**Numerical Example:**

- $V_{\text{REF}} = 3.3$ V, $N = 12$, $V_{\text{in}} = 1.65$ V.
- $C = \left\lfloor \frac{1.65}{3.3} \times 4095 \right\rfloor = \left\lfloor 0.5 \times 4095 \right\rfloor = 2047$.

**Implementation (Host Python):**

```python
def code_to_voltage(code, vref=3.3, n_bits=12):
    return code * vref / (2**n_bits - 1)
```

***

### 11.3.2 Code-to-Voltage Equation

**Equation:**

$$
V_{\text{out}} = C \times \frac{V_{\text{REF}}}{2^N - 1}
$$

**Variables:**

- $V_{\text{out}}$: Reconstructed voltage (V).
- $C$: ADC code (0–4095).

**Usage:**

- Host software converts raw ADC codes to voltages for plotting and analysis.

***

### 11.3.3 Voltage-to-Code Equation

**Equation:**

$$
C = \left\lfloor \frac{V_{\text{in}} \times (2^N - 1)}{V_{\text{REF}}} \right\rfloor
$$

**Usage:**

- Firmware: Determine DAC code for target voltage.
- Host: Generate synthetic test data.

***

### 11.3.4 Resolution and LSB

**Least Significant Bit (LSB) Voltage:**

$$
V_{\text{LSB}} = \frac{V_{\text{REF}}}{2^N - 1}
$$

**For STM32 (12-bit, 3.3 V):**

$$
V_{\text{LSB}} = \frac{3.3}{4095} \approx 0.806 \text{ mV}
$$

**Physical Meaning:**

- Smallest detectable voltage change.
- Quantization step size.

***

### 11.3.5 Quantization Error

**Definition:**

- Difference between actual voltage and quantized representation.

**Maximum Error:**

$$
\epsilon_{\text{quant}} = \pm \frac{V_{\text{LSB}}}{2} = \pm 0.403 \text{ mV}
$$

**Distribution:**

- Uniform distribution over $[-\frac{V_{\text{LSB}}}{2}, +\frac{V_{\text{LSB}}}{2}]$.

**Usage:**

- Uncertainty budget (Section 10.10).
- SNR calculation (Section 11.13).

***

## 11.4 DAC Mathematics

### 11.4.1 DAC Transfer Function

**Purpose:**  
Relates digital input code to analog output voltage.

**Ideal Transfer Function:**

$$
V_{\text{out}} = C \times \frac{V_{\text{REF}}}{2^N - 1}
$$

**Variables:**

- $C$: DAC code (0–4095).
- $V_{\text{out}}$: Output voltage (V).

**Physical Meaning:**

- DAC reconstructs analog voltage from digital code.

**Engineering Significance:**

- Used in firmware waveform generation (Section 9.12.1).
- Basis for DAC calibration (Section 10.9).

***

### 11.4.2 DAC Error Definitions

**Offset Error:**

- Output voltage when $C = 0$.
- Ideal: 0 V.
- Measured: $V_{\text{offset}}$.

**Gain Error:**

- Deviation of actual full-scale output from ideal.
- Ideal: $V_{\text{REF}}$ at $C = 4095$.
- Measured: $V_{\text{full}}$.
- Gain error: $\frac{V_{\text{REF}}}{V_{\text{full}}}$.

**Usage:**

- Calibration (Section 10.9).
- Error budget (Section 10.11).

***

## 11.5 Quantization Theory

### 11.5.1 Uniform Quantization

**Definition:**

- Quantization levels equally spaced by $V_{\text{LSB}}$.

**Rounding:**

- Code assigned to nearest level.
- Error: $\epsilon \in [-\frac{V_{\text{LSB}}}{2}, +\frac{V_{\text{LSB}}}{2}]$.

**Truncation:**

- Code assigned to lower level (floor).
- Error: $\epsilon \in [0, V_{\text{LSB}}]$.

**STM32 ADC:**

- Uses rounding (effective).

***

### 11.5.2 Quantization Noise Power

**Assumption:**

- Quantization error uniformly distributed.

**Noise Power (Variance):**

$$
P_{\text{quant}} = \frac{V_{\text{LSB}}^2}{12}
$$

**Derivation:**

- For uniform distribution over $[-\frac{V_{\text{LSB}}}{2}, +\frac{V_{\text{LSB}}}{2}]$:
$$
\sigma^2 = \frac{(b - a)^2}{12} = \frac{V_{\text{LSB}}^2}{12}
$$

**RMS Quantization Noise:**

$$
V_{\text{noise,rms}} = \sqrt{P_{\text{quant}}} = \frac{V_{\text{LSB}}}{\sqrt{12}}
$$

**For STM32:**

- $V_{\text{LSB}} = 0.806$ mV.
- $V_{\text{noise,rms}} = \frac{0.806}{\sqrt{12}} \approx 0.233$ mV.

***

### 11.5.3 Quantization SNR

**For Full-Scale Sine Wave:**

- Signal amplitude: $A = \frac{V_{\text{REF}}}{2}$.
- Signal power: $P_{\text{signal}} = \frac{A^2}{2} = \frac{V_{\text{REF}}^2}{8}$.

**SNR (dB):**

$$
\text{SNR}_{\text{quant}} = 10 \log_{10} \left( \frac{P_{\text{signal}}}{P_{\text{quant}}} \right) = 6.02 N + 1.76 \text{ dB}
$$

**For N = 12:**

$$
\text{SNR}_{\text{quant}} = 6.02 \times 12 + 1.76 \approx 74 \text{ dB}
$$

**Usage:**

- Theoretical maximum SNR for ADC/DAC.
- Comparison with measured SNR (Section 11.13).

***

## 11.6 Sampling Theory

### 11.6.1 Nyquist-Shannon Sampling Theorem

**Statement:**

A continuous-time signal with maximum frequency $f_{\text{max}}$ can be perfectly reconstructed from its samples if the sampling frequency $f_s$ satisfies:

$$
f_s > 2 f_{\text{max}}
$$

**Derivation (Intuitive):**

- A sine wave of frequency $f$ requires at least 2 samples per cycle to be uniquely identified.
- Fewer samples → aliasing (higher frequencies appear as lower frequencies).

**Nyquist Frequency:**

$$
f_{\text{Nyquist}} = \frac{f_s}{2}
$$

**Usage:**

- ADC sampling rate selection (Chapter 8).
- Anti-aliasing filter cutoff design.

***

### 11.6.2 Aliasing

**Definition:**

- Phenomenon where frequencies above $f_{\text{Nyquist}}$ appear as lower frequencies.

**Aliased Frequency:**

$$
f_{\text{alias}} = |f_{\text{in}} - k f_s|
$$

where $k$ is integer such that $f_{\text{alias}} \in [0, f_{\text{Nyquist}}]$.

**Example:**

- $f_s = 100$ kSPS, $f_{\text{in}} = 60$ kHz.
- $f_{\text{alias}} = |60 - 100| = 40$ kHz.

**Mitigation:**

- Anti-aliasing filter (RC low-pass) with cutoff < $f_{\text{Nyquist}}$.

***

### 11.6.3 Oversampling and Undersampling

**Oversampling:**

- $f_s \gg 2 f_{\text{max}}$.
- Benefits: Reduced quantization noise in band of interest, easier filtering.

**Undersampling:**

- $f_s < 2 f_{\text{max}}$ (intentional for bandpass signals).
- Not used in this project.

***

## 11.7 Timing Mathematics

### 11.7.1 Sampling Period and Frequency

**Definitions:**

- Sampling period: $T_s = \frac{1}{f_s}$.
- Sampling frequency: $f_s$.

**Example:**

- $f_s = 100$ kSPS → $T_s = 10$ µs.

***

### 11.7.2 Timer Configuration for DAC/ADC

**STM32 Timer Equation:**

$$
f_{\text{update}} = \frac{f_{\text{timer}}}{(\text{PSC} + 1) \times (\text{ARR} + 1)}
$$

**Variables:**

- $f_{\text{timer}}$: Timer clock frequency (e.g., 84 MHz for APB1).
- PSC: Prescaler (integer, 0 to 65535).
- ARR: Auto-reload value (integer, 0 to 65535).

**Example (DAC Sine at 100 kSPS):**

- $f_{\text{timer}} = 84$ MHz.
- Desired $f_{\text{update}} = 100$ kSPS.
- Choose PSC = 0 (no prescaling).
- Solve for ARR:
$$
\text{ARR} = \frac{84 \times 10^6}{100 \times 10^3} - 1 = 839
$$

**Implementation (Firmware):**

- Configure timer with PSC = 0, ARR = 839.
- Timer triggers DAC update every 10 µs.

***

### 11.7.3 ADC Conversion Time

**STM32 ADC:**

- Conversion time: $T_{\text{conv}} = T_{\text{sample}} + 12$ cycles (for 12-bit).
- ADC clock: $f_{\text{ADC}} \leq 36$ MHz.

**Example:**

- $f_{\text{ADC}} = 36$ MHz → $T_{\text{clk}} = 27.78$ ns.
- Sample time = 15 cycles.
- $T_{\text{conv}} = (15 + 12) \times 27.78 \text{ ns} \approx 750 \text{ ns}$.
- Maximum sampling rate: $f_s = \frac{1}{T_{\text{conv}}} \approx 1.33$ MSPS.

**Usage:**

- ADC configuration in firmware (Chapter 9).

***

### 11.7.4 UART Timing

**Baud Rate:**

$$
\text{Baud} = \frac{f_{\text{UART}}}{\text{DIV}}
$$

where DIV is integer divider.

**Throughput:**

- 10 bits per byte (1 start, 8 data, 1 stop).
- Effective throughput: $\frac{\text{Baud}}{10}$ bytes/s.

**Example (921,600 baud):**

- Throughput: $\frac{921,600}{10} = 92,160$ bytes/s.
- 16-bit samples: $\frac{92,160}{2} = 46,080$ samples/s.

***

### 11.8 Histogram Mathematics

#### 11.8.1 Probability Density Function (PDF)

**Purpose:**  
The Probability Density Function (PDF), $p(x)$, describes the likelihood of a continuous random variable $x$ taking a specific value. For a voltage signal $v(t)$, the PDF indicates how much time the signal spends at each voltage level.

**Normalization Condition:**
$$
\int_{-\infty}^{\infty} p(v) \, dv = 1
$$

**Probability in Interval:**
The probability that $v(t)$ lies between $V_1$ and $V_2$ is:
$$
P(V_1 \le v \le V_2) = \int_{V_1}^{V_2} p(v) \, dv
$$

**Engineering Significance:**  
In ADC testing, we use a known input signal (e.g., a ramp) with a known PDF to characterize the ADC. If the input PDF is uniform, deviations in the output histogram reveal ADC non-linearities.

***

#### 11.8.2 Code Density Testing

**Principle:**  
Apply an input signal that sweeps the entire ADC input range uniformly. Count the number of occurrences (hits) for each output code $k$.

**Ideal Input:**  
A linear ramp signal $v(t) = \alpha t$ has a uniform PDF:
$$
p(v) = \begin{cases} \frac{1}{V_{\text{FS}}} & 0 \le v \le V_{\text{FS}} \\ 0 & \text{otherwise} \end{cases}
$$
where $V_{\text{FS}}$ is the full-scale voltage range.

**Histogram Formation:**  
For an $N$-bit ADC, there are $2^N$ possible codes. Let $H[k]$ be the number of times code $k$ is observed out of $M$ total samples.

**Ideal Histogram:**  
For a uniform input, the expected count for every code is:
$$
H_{\text{ideal}}[k] = \frac{M}{2^N}
$$

**Non-Ideal Histogram:**  
If the ADC has non-uniform code widths (non-linearity), codes corresponding to wider voltage ranges will have higher counts, and vice versa.

**Missing Codes:**  
If $H[k] = 0$ for a code $k$ that should exist, it is a "missing code," indicating a severe non-linearity where the code width is effectively zero.

***

#### 11.8.3 Transition Levels and Code Widths

**Transition Levels ($T_k$):**  
The input voltage at which the ADC output transitions from code $k-1$ to code $k$.
- $T_1$: Transition from 0 to 1.
- $T_{2^N-1}$: Transition from $2^N-2$ to $2^N-1$.

**Code Width ($W_k$):**  
The voltage range corresponding to code $k$:
$$
W_k = T_{k+1} - T_k
$$
For an ideal ADC, $W_k = 1 \text{ LSB}$ for all $k$.

**Relation to Histogram:**  
The histogram count $H[k]$ is proportional to the code width $W_k$:
$$
H[k] \propto W_k
$$
Specifically, for a uniform input slope $\frac{dv}{dt}$ and sampling rate $f_s$:
$$
H[k] \approx \frac{W_k}{\text{slope}} \times f_s
$$

**Implementation (Host Software):**  
The `compute_histogram` function in `signal_processing.py` (Chapter 9) builds the array $H[k]$ from raw ADC samples. This array is the primary input for DNL/INL calculations.

***

### 11.9 Differential Non-Linearity (DNL)

#### 11.9.1 Derivation from First Principles

**Definition:**  
DNL measures the deviation of each code width from the ideal width (1 LSB). It indicates local linearity errors.

**Ideal Code Width:**
$$
W_{\text{ideal}} = 1 \text{ LSB} = \frac{V_{\text{REF}}}{2^N - 1}
$$

**Actual Code Width (Normalized):**  
Using the histogram method, the normalized code width for code $k$ is estimated as:
$$
\hat{W}_k = \frac{H[k]}{H_{\text{avg}}}
$$
where $H_{\text{avg}} = \frac{1}{2^N - 2} \sum_{k=1}^{2^N-2} H[k]$ is the average hit count (excluding first and last codes which are often distorted).

**DNL Equation:**
$$
\text{DNL}[k] = \hat{W}_k - 1 = \frac{H[k]}{H_{\text{avg}}} - 1
$$

**Variables:**
- $H[k]$: Histogram count for code $k$.
- $H_{\text{avg}}$: Average histogram count.
- $k$: Code index (typically $1 \le k \le 2^N-2$).

**Interpretation:**
- $\text{DNL}[k] = 0$: Ideal code width.
- $\text{DNL}[k] > 0$: Code is wider than ideal (ADC spends more time in this state).
- $\text{DNL}[k] < 0$: Code is narrower than ideal.
- $\text{DNL}[k] = -1$: **Missing Code** (width is zero).

**Monotonicity:**  
An ADC is monotonic if $T_{k+1} > T_k$ for all $k$. This requires $\text{DNL}[k] > -1$ for all $k$. If $\text{DNL} \le -1$, the ADC is non-monotonic (output decreases for increasing input).

***

#### 11.9.2 Numerical Example

**Setup:**
- 12-bit ADC, $M = 10,000$ samples.
- Ideal average count: $H_{\text{avg}} = \frac{10000}{4096} \approx 2.44$.
- Suppose for code $k=1000$, observed count $H[1000] = 4$.
- Suppose for code $k=1001$, observed count $H[1001] = 1$.

**Calculation:**
- $\text{DNL}[1000] = \frac{4}{2.44} - 1 \approx 1.64 - 1 = +0.64 \text{ LSB}$.
- $\text{DNL}[1001] = \frac{1}{2.44} - 1 \approx 0.41 - 1 = -0.59 \text{ LSB}$.

**Interpretation:**  
Code 1000 is 64% wider than ideal; Code 1001 is 59% narrower.

***

#### 11.9.3 Implementation in Software

**Algorithm (`adc_analysis.py`):**
1. Compute histogram $H$.
2. Calculate $H_{\text{avg}}$ (excluding endpoints).
3. Compute $\text{DNL}[k] = (H[k] / H_{\text{avg}}) - 1$.
4. Filter out endpoints (codes 0 and 4095).

**Numerical Stability:**  
- Ensure $H_{\text{avg}} > 0$ (sufficient samples).
- Use floating-point division to avoid integer truncation.

***

### 11.10 Integral Non-Linearity (INL)

#### 11.10.1 Derivation from DNL

**Definition:**  
INL measures the cumulative deviation of transition points from their ideal positions. It represents the "shape" of the transfer curve.

**Endpoint Method:**  
INL at code $k$ is the sum of DNL errors from code 1 up to $k-1$:
$$
\text{INL}[k] = \sum_{i=1}^{k-1} \text{DNL}[i]
$$
Boundary conditions: $\text{INL} = 0$, $\text{INL}[2^N-1] = 0$ (forced by definition). [study.iitm.ac](https://study.iitm.ac.in/es/course_pages/EE4108.html)

**Physical Interpretation:**  
INL represents the vertical distance between the actual transfer curve and the straight line connecting the first and last transition points.

**Best-Fit Method:**  
Instead of fixing endpoints, a straight line is fitted to the transfer curve (e.g., least-squares) to minimize the total INL error. This often yields smaller INL values but is computationally more complex. This project uses the **Endpoint Method** for simplicity and standard compliance.

***

#### 11.10.2 Numerical Example

**Given DNL:**
- $\text{DNL} = 0.1$ [study.iitm.ac](https://study.iitm.ac.in/es/course_pages/EE4108.html)
- $\text{DNL} = -0.2$ [analog](https://www.analog.com/media/en/training-seminars/design-handbooks/Data-Conversion-Handbook/Chapter5.pdf)
- $\text{DNL} = 0.5$ [ersaelectronics](https://www.ersaelectronics.com/blog/adc-inl-dnl-missing-codes)

**INL Calculation:**
- $\text{INL} = 0$ [study.iitm.ac](https://study.iitm.ac.in/es/course_pages/EE4108.html)
- $\text{INL} = \text{DNL} = 0.1$ [analog](https://www.analog.com/media/en/training-seminars/design-handbooks/Data-Conversion-Handbook/Chapter5.pdf)
- $\text{INL} = \text{DNL} + \text{DNL} = 0.1 - 0.2 = -0.1$ [study.iitm.ac](https://study.iitm.ac.in/es/course_pages/EE4108.html)
- $\text{INL} = 0.1 - 0.2 + 0.5 = 0.4$ [archive.nptel.ac](https://archive.nptel.ac.in/content/syllabus_pdf/106103016.pdf)

**Implementation:**  
`compute_inl(dnl)` in `adc_analysis.py` performs a cumulative sum (`numpy.cumsum`) of the DNL array.

***

### 11.11 Fourier Analysis

#### 11.11.1 From Fourier Series to DFT

**Fourier Series:**  
Any periodic signal $x(t)$ with period $T$ can be represented as a sum of sinusoids:
$$
x(t) = a_0 + \sum_{n=1}^{\infty} \left( a_n \cos(2\pi n f_0 t) + b_n \sin(2\pi n f_0 t) \right)
$$
where $f_0 = 1/T$.

**Discrete Fourier Transform (DFT):**  
For a discrete sequence $x[n]$ of length $N$:
$$
X[k] = \sum_{n=0}^{N-1} x[n] e^{-j 2\pi k n / N}, \quad k = 0, \dots, N-1
$$

**Variables:**
- $x[n]$: Input sample at index $n$.
- $X[k]$: Complex spectral component at bin $k$.
- $N$: Number of samples (FFT size).
- $k$: Frequency bin index.

**Frequency Resolution:**  
The frequency corresponding to bin $k$ is:
$$
f_k = k \cdot \frac{f_s}{N}
$$
where $f_s$ is the sampling frequency.

**Nyquist Limit:**  
Valid frequencies are up to $k = N/2$ (Nyquist frequency $f_s/2$).

***

#### 11.11.2 Fast Fourier Transform (FFT)

**Purpose:**  
The FFT is an efficient algorithm to compute the DFT.

**Complexity:**
- DFT: $O(N^2)$.
- FFT (Radix-2): $O(N \log_2 N)$.

**Example:**  
For $N = 10,000$:
- DFT operations $\approx 10^8$.
- FFT operations $\approx 1.3 \times 10^5$.
- **Speedup:** ~770x.

**Implementation:**  
`scipy.fft.fft` in `signal_processing.py` uses an optimized FFT algorithm (FFTPACK).

***

### 11.12 Window Functions

#### 11.12.1 Spectral Leakage

**Problem:**  
The DFT assumes the input signal is periodic with period $N$. If the signal is not exactly periodic in the window (non-coherent sampling), discontinuities occur at the edges, causing energy to "leak" into adjacent frequency bins.

**Solution:**  
Multiply the input signal $x[n]$ by a window function $w[n]$ that tapers to zero at the edges.

**Windowed Signal:**
$$
x_w[n] = x[n] \cdot w[n]
$$

***

#### 11.12.2 Common Windows

| Window | Equation \(w[n]\) | Main Lobe Width | Side Lobe Attenuation | Usage |
|--------|---------------------|-----------------|-----------------------|-------|
| **Rectangular** | $ 1 $ | Narrowest (1 bin) | -13 dB | Coherent sampling only |
| **Hann** | \(0.5 - 0.5 \cos(\frac{2\pi n}{N-1})\) | 2 bins | -31 dB | General purpose |
| **Hamming** | \(0.54 - 0.46 \cos(\frac{2\pi n}{N-1})\) | 2 bins | -41 dB | Better side lobe suppression |
| **Blackman** | \(0.42 - 0.5 \cos(\dots) + 0.08 \cos(\dots)\) | 3 bins | -58 dB | High dynamic range |
| **Flat-top** | Complex sum of cosines | Wide | -90 dB | Amplitude accuracy |

**Selection for This Project:**  
- **Hann Window:** Used for THD/SNR analysis.
- **Reason:** Good balance between frequency resolution and side lobe suppression. Adequate for educational THD measurements where exact amplitude calibration is secondary.

**Implementation:**  
`scipy.signal.windows.hann(N)` generates the window vector, which is multiplied element-wise with the input sample array before FFT.

***

### 11.13 Spectral Performance Metrics

#### 11.13.1 Total Harmonic Distortion (THD)

**Definition:**  
Ratio of the RMS sum of harmonics to the RMS value of the fundamental.

**Equation:**
$$
\text{THD} = \frac{\sqrt{\sum_{h=2}^{H} V_h^2}}{V_1}
$$
$$
\text{THD}_{\text{dB}} = 20 \log_{10}(\text{THD})
$$

**Variables:**
- $V_1$: RMS amplitude of fundamental frequency (bin $k_1$).
- $V_h$: RMS amplitude of $h$-th harmonic.
- $H$: Number of harmonics considered (typically 5–10).

**Implementation:**  
1. Identify fundamental bin $k_1$ (max magnitude).
2. Identify harmonic bins $k_h = h \cdot k_1$.
3. Sum squares of harmonic magnitudes.
4. Compute ratio.

***

#### 11.13.2 Signal-to-Noise Ratio (SNR)

**Definition:**  
Ratio of signal power to noise power (excluding harmonics).

**Equation:**
$$
\text{SNR} = 10 \log_{10} \left( \frac{P_{\text{signal}}}{P_{\text{noise}}} \right) \text{ dB}
$$

**Noise Power:**  
Sum of magnitudes of all bins excluding DC, fundamental, and harmonics.
$$
P_{\text{noise}} = \sum_{k \in \text{noise bins}} |X[k]|^2
$$

***

#### 11.13.3 Effective Number of Bits (ENOB)

**Definition:**  
The resolution of an ideal ADC that would produce the same SNR.

**Equation:**
$$
\text{ENOB} = \frac{\text{SNR}_{\text{measured}} - 1.76}{6.02}
$$

**Derivation:**  
From quantization noise SNR formula $\text{SNR} = 6.02 N + 1.76$, solve for $N$.

**Usage:**  
Key metric for ADC performance characterization in Chapter 10.

***

### 11.14 RC Filter Mathematics

#### 11.14.1 Transfer Function

**Circuit:**  
Series resistor $R$, shunt capacitor $C$.

**Transfer Function $H(s)$:**
$$
H(s) = \frac{V_{\text{out}}(s)}{V_{\text{in}}(s)} = \frac{1}{1 + sRC}
$$

**Cutoff Frequency** ($f_c$):
$$
f_c = \frac{1}{2\pi RC}
$$

**Magnitude Response:**
$$
|H(j\omega)| = \frac{1}{\sqrt{1 + (\omega RC)^2}}
$$

**Phase Response:**
$$
\phi(\omega) = -\arctan(\omega RC)
$$

**Example (Chapter 8 Values):**  
- $R = 1 \text{ k}\Omega$, $C = 100 \text{ nF}$.
- $f_c = \frac{1}{2\pi \cdot 1000 \cdot 100 \times 10^{-9}} \approx 1.59 \text{ kHz}$.

**Relevance:**  
This filter acts as an anti-aliasing filter for the ADC, attenuating frequencies above $f_c$.

***

### 11.15 Error Analysis

#### 11.15.1 Absolute and Relative Error

**Absolute Error:**
$$
\epsilon = V_{\text{measured}} - V_{\text{true}}
$$

**Relative Error:**
$$
\epsilon_{\text{rel}} = \frac{\epsilon}{V_{\text{true}}}
$$

**Percentage Error:**
$$
\epsilon_{\%} = \epsilon_{\text{rel}} \times 100\%
$$

**Usage:**  
Calibration (Chapter 10) uses these to quantify offset and gain errors.

***

### 11.16 Measurement Uncertainty

#### 11.16.1 Uncertainty Propagation

**Law of Propagation of Uncertainty:**  
If $y = f(x_1, x_2, \dots)$, the combined standard uncertainty $u_c(y)$ is:
$$
u_c(y) = \sqrt{ \sum_{i} \left( \frac{\partial f}{\partial x_i} u(x_i) \right)^2 }
$$
(Assuming uncorrelated inputs).

**Example (Voltage Measurement):**  
$V = C \cdot \frac{V_{\text{REF}}}{4095}$.
$$
u_c(V) = \sqrt{ \left( \frac{V_{\text{REF}}}{4095} u(C) \right)^2 + \left( \frac{C}{4095} u(V_{\text{REF}}) \right)^2 }
$$

**Expanded Uncertainty:**  
$$
U = k \cdot u_c(y)
$$
where $k$ is the coverage factor (typically $k=2$ for 95% confidence).

***

### 11.17 Statistical Foundations

#### 11.17.1 Mean and Variance

**Arithmetic Mean:**
$$
\bar{x} = \frac{1}{n} \sum_{i=1}^{n} x_i
$$

**Variance:**
$$
s^2 = \frac{1}{n-1} \sum_{i=1}^{n} (x_i - \bar{x})^2
$$

**Standard Deviation:**
$$
s = \sqrt{s^2}
$$

**Usage:**  
- Mean: Average ADC code for offset calibration.
- Standard Deviation: Noise estimation (RMS noise).

***

### 11.18 Computational Complexity

| Algorithm | Complexity | Notes |
|-----------|------------|-------|
| **FFT** | \(O(N \log N)\) | Dominant cost in host analysis |
| **Histogram** | \(O(N)\) | Linear scan of samples |
| **DNL/INL** | \(O(2^N)\) | Constant time (4096 iterations) |
| **Parser** | \(O(L)\) | Linear in packet length |
| **Plotting** | \(O(N)\) | Proportional to data points |

**Engineering Significance:**  
Ensures host software can process 50k samples in < 1 second (SR-011).

***

### 11.19 Numerical Stability

**Floating-Point Precision:**  
Python uses 64-bit floats (53 bits mantissa). Precision is ~15 decimal digits.

**Catastrophic Cancellation:**  
Occurs when subtracting nearly equal numbers (e.g., $\text{INL}$ calculation if DNL is small).
- **Mitigation:** Use compensated summation (Kahan summation) if necessary (not critical for 12-bit data).

**Overflow/Underflow:**  
- FFT magnitudes can be large; normalize by $N$.
- Squaring large numbers can overflow; use log-sum-exp tricks if needed (not critical here).

***

### 11.20 Engineering Approximations

| Approximation | Justification | Limitations |
|---------------|---------------|-------------|
| **Ideal Ramp** | Simple to generate with DAC | DAC non-linearity affects result |
| **Uniform Quantization Noise** | Valid for busy signals | Invalid for DC or low-frequency tones |
| **LTI System** | Filters are linear | Real components have tolerance/drift |
| **Negligible Parasitics** | Low frequency (< 100 kHz) | May affect high-speed edges |

***

### 11.21 Mathematical Validation

**Experimental Verification:**  
- **ADC Transfer Function:** Verified by applying known voltages (DMM) and comparing ADC codes (TC-012).
- **FFT:** Verified using synthetic sine waves with known frequency/amplitude (TC-021).
- **Filter Cutoff:** Verified by sweeping frequency and measuring attenuation (TC-005).

**Connection to Chapter 10:**  
Every equation derived here is tested in the Verification Plan (e.g., SNR formula tested against measured SNR).

***

### 11.22 Formula Summary

| Formula | Variables | Units | Purpose | Used In | Assumptions | Related Chapter |
|---------|-----------|-------|---------|---------|-------------|---------------|
| \(V_{\text{LSB}} = \frac{V_{\text{REF}}}{2^N - 1}\) | \(V_{\text{REF}}\): Ref Voltage, \(N\): Bits | Volts | ADC/DAC resolution | All | Ideal converter | 8, 9 |
| \(\text{SNR} = 6.02 N + 1.76\) | \(N\): Bits | dB | Theoretical max SNR | 10, 11 | Quantization noise only | 10 |
| \(\text{DNL}[k] = \frac{H[k]}{H_{\text{avg}}} - 1\) | \(H[k]\): Histogram count | LSB | Local linearity error | 9, 10 | Uniform input PDF | 10 |
| \(\text{INL}[k] = \sum_{i=1}^{k-1} \text{DNL}[i]\) | \(\text{DNL}\): Diff. Non-Linearity | LSB | Cumulative linearity error | 9, 10 | Endpoint method | 10 |
| \(f_c = \frac{1}{2\pi RC}\) | \(R\): Resistance, \(C\): Capacitance | Hz | RC filter cutoff | 8 | Ideal components | 8 |
| \(\text{THD} = \frac{\sqrt{\sum V_h^2}}{V_1}\) | \(V_h\): Harmonics, \(V_1\): Fundamental | Ratio | Distortion metric | 9, 10 | Sinusoidal input | 10 |
| \(\text{ENOB} = \frac{\text{SNR} - 1.76}{6.02}\) | \(\text{SNR}\): Measured SNR | Bits | Effective resolution | 10 | Sinusoidal input | 10 |

***
