# 14. User Manual

## 14.1 Introduction

### 14.1.1 Purpose of the Instrument

The **μATE-STM (Micro Automated Test Equipment for STM32)** is a portable, USB-powered instrument designed for characterizing and verifying mixed-signal embedded systems. It provides precision analog stimulus (DAC) and measurement (ADC) capabilities controlled via a host computer, enabling comprehensive testing of analog-to-digital converters, digital-to-analog converters, and analog front-ends without requiring expensive benchtop equipment.

### 14.1.2 Intended Users

This instrument is designed for:
- **Engineering Students:** Learning ADC/DAC characterization, signal processing, and embedded systems.
- **Researchers:** Prototyping and validating analog circuits in resource-constrained environments.
- **Laboratory Technicians:** Quick verification of embedded board analog performance.

### 14.1.3 Capabilities

- **ADC Testing:** Code density histograms, DNL, INL, ENOB, THD, SNR, SINAD.
- **DAC Testing:** Linearity verification, settling time, glitch energy (via ADC feedback).
- **Signal Generation:** Sine, triangle, square, ramp waveforms (1 Hz to 50 kHz).
- **Data Acquisition:** Continuous sampling up to 100 kSPS, 12-bit resolution.
- **Spectral Analysis:** FFT with configurable window functions (Rectangular, Hann, Hamming, Blackman).
- **Automated Reporting:** PDF/HTML reports with metrics, plots, and pass/fail indicators.

### 14.1.4 Limitations

- **Input Voltage Range:** 0 V to 3.3 V (do not exceed; see Section 14.2).
- **Bandwidth:** Effective analog bandwidth limited to ~50 kHz (RC filter cutoff).
- **Absolute Accuracy:** ±1% (suitable for relative characterization, not metrology-grade measurements).
- **Isolation:** No galvanic isolation between USB and analog grounds.

### 14.1.5 Supported Measurements

| Measurement | Description | Typical Use Case |
|-------------|-------------|------------------|
| **DC Voltage** | Average ADC code converted to voltage | Power supply verification |
| **AC Waveform** | Time-domain capture | Signal integrity analysis |
| **FFT Spectrum** | Frequency-domain analysis | Harmonic distortion measurement |
| **Histogram** | Code density distribution | ADC linearity testing |
| **DNL/INL** | Differential/Integral Non-Linearity | ADC/DAC linearity characterization |
| **THD** | Total Harmonic Distortion | DAC/ADC distortion analysis |
| **SNR** | Signal-to-Noise Ratio | Noise performance evaluation |
| **ENOB** | Effective Number of Bits | Overall ADC performance metric |

***

## 14.2 Safety Information

### 14.2.1 Electrical Safety

**WARNING:** The μATE-STM is powered exclusively via USB (5 V). Do not connect external power supplies to the board.

- **Maximum Input Voltage:** 3.3 V on analog input pins (PA0). Voltages exceeding 3.6 V may permanently damage the STM32 MCU.
- **Current Limit:** USB port current is limited to 500 mA (USB 2.0 spec). Do not connect high-current loads.

**Rationale:** The STM32F401RE operates at 3.3 V logic; exceeding this voltage causes latch-up or junction breakdown.

### 14.2.2 USB Safety

- **Use Data-Capable Cables:** Charging-only cables lack data lines and will prevent communication.
- **Avoid Hot-Plugging Analog Signals:** Connect analog signals before powering USB to minimize ESD risk.

### 14.2.3 ESD Precautions

**WARNING:** The analog input (PA0) and DAC output (PA4) pins are not protected against electrostatic discharge (ESD).

- **Handling:** Always discharge yourself (touch grounded metal) before touching the breadboard or STM32 pins.
- **Storage:** Store the instrument in an anti-static bag when not in use.

**Rationale:** CMOS inputs have thin gate oxides that can be punctured by ESD voltages (>1 kV).

### 14.2.4 Operating Environment

- **Temperature:** 10°C to 40°C (0°C to 50°C non-operating).
- **Humidity:** 20% to 80% non-condensing.
- **Environment:** Indoor use only; avoid dust, moisture, and direct sunlight.

**Rationale:** Component values (especially capacitors) drift with temperature; condensation can cause short circuits.

### 14.2.5 Handling Precautions

- **Breadboard:** Do not bend component leads excessively; this can damage breadboard contacts.
- **Jumper Wires:** Pull by the connector, not the wire, to avoid breakage.
- **STM32 Board:** Avoid placing conductive objects on the board while powered.

***

## 14.3 Package Contents

Verify all items are present before use.

| Item | Quantity | Purpose |
|------|----------|---------|
| **STM32 Nucleo-F401RE Board** | 1 | Main processing unit (ADC, DAC, UART, USB) |
| **Breadboard (Pre-assembled)** | 1 | Analog front-end (RC filter, voltage dividers) |
| **USB-A to Micro-USB Cable** | 1 | Power and communication |
| **Jumper Wires (Assorted)** | 10 | Signal connections |
| **Resistor Kit (1 kΩ, 10 kΩ)** | 1 set | Calibration, voltage division |
| **Capacitor Kit (100 nF, 10 µF)** | 1 set | Filtering, decoupling |
| **Quick Start Guide** | 1 | This manual (abridged) |
| **Software Download Card** | 1 | URL to GitHub repository |

**Optional Accessories (Not Included):**
- **Multimeter:** For DC voltage verification.
- **Oscilloscope:** For waveform visualization.
- **Function Generator:** For external signal testing.

***

## 14.4 System Overview

### 14.4.1 External Hardware

The μATE-STM consists of two main hardware sections:

1. **STM32 Nucleo Board:** Provides digital processing, ADC, DAC, and USB interface.
2. **Analog Front-End (Breadboard):** Provides signal conditioning (RC filter, protection).

### 14.4.2 Connectors and Indicators

| Connector/Indicator | Location | Function |
|---------------------|----------|----------|
| **USB Micro-USB (CN1)** | STM32 Board | Power (5 V) and UART communication |
| **User LED (LD2)** | STM32 Board (PC13) | Status indicator (blinks during acquisition) |
| **Analog Input (PA0)** | Breadboard (Row 1) | Signal input for ADC (0–3.3 V) |
| **DAC Output (PA4)** | Breadboard (Row 10) | Signal output from DAC (0–3.3 V) |
| **GND Rails** | Breadboard (Blue) | Common ground reference |
| **3.3V Rail** | Breadboard (Red) | Power supply for analog circuits |

### 14.4.3 Analog Inputs

- **Label:** `AIN` (Analog Input).
- **Connector:** Breadboard row connected to STM32 pin PA0.
- **Range:** 0 V to 3.3 V.
- **Impedance:** ~10 kΩ (due to voltage divider for protection).
- **Protection:** Series resistor (1 kΩ) and clamping diodes (internal to STM32).

### 14.4.4 Analog Outputs

- **Label:** `AOUT` (Analog Output).
- **Connector:** Breadboard row connected to STM32 pin PA4.
- **Range:** 0 V to 3.3 V (12-bit resolution).
- **Drive Capability:** Up to 10 mA (sufficient for high-impedance loads).

### 14.4.5 Indicators

- **LD2 (User LED):**
  - **Solid On:** Device powered, idle.
  - **Blinking (1 Hz):** Acquisition in progress.
  - **Rapid Blink (5 Hz):** Error state (check logs).

***

## 14.5 Installation

### 14.5.1 Hardware Setup

1. **Inspect:** Verify no loose wires or components on the breadboard.
2. **Connect USB:** Plug the Micro-USB end into the STM32 board, USB-A end into your computer.
3. **Verify Power:** The STM32 board should power on (green LED lit).

### 14.5.2 Software Installation

**Requirements:**
- **Operating System:** Windows 10/11, macOS 10.15+, or Ubuntu 20.04+.
- **Python:** Version 3.9 or later (https://www.python.org).
- **Git:** For repository cloning (optional; ZIP download available).

**Steps:**

1. **Clone Repository:**
   ```bash
   git clone https://github.com/your-username/uate-stm.git
   cd uate-stm
   ```

2. **Create Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify Installation:**
   ```bash
   python -m pytest tests/unit
   ```

### 14.5.3 Required Drivers

- **Windows:** STM32 ST-Link drivers are typically auto-installed. If not, download from https://www.st.com.
- **macOS/Linux:** No additional drivers required (CDC ACM class device).

### 14.5.4 First Startup

1. **Activate Virtual Environment:** (See above).
2. **Run Host Software:**
   ```bash
   python main.py --help
   ```
3. **Verify COM Port:**
   - **Windows:** Check Device Manager → Ports (COM & LPT) for `STMicroelectronics STLink Virtual COM Port`.
   - **macOS:** `/dev/tty.usbmodem*`.
   - **Linux:** `/dev/ttyACM*`.

### 14.5.5 Verification

Run the self-test:
```bash
python main.py --self-test
```
Expected output: `All tests passed.`

***

## 14.6 First-Time Setup

### 14.6.1 Connecting the Instrument

1. **Power:** Ensure USB is connected.
2. **Analog Input:** Connect a known voltage source (e.g., 1.5 V battery) to `AIN` and `GND`.
3. **Host Software:** Open terminal/Command Prompt.

### 14.6.2 Verifying Communication

```bash
python main.py --ping
```
Expected: `Device responded: OK`.

### 14.6.3 Loading Configuration

Default configuration is loaded automatically. To customize:
```bash
python main.py --load-config configs/default.json
```

### 14.6.4 Performing First Calibration

**Note:** Calibration is required only if absolute accuracy is critical. For relative measurements (DNL/INL), factory defaults are sufficient.

```bash
python main.py --calibrate
```
Follow on-screen prompts to apply known voltages (0 V, 1.65 V, 3.3 V).

### 14.6.5 Running First Measurement

```bash
python main.py --acquire --samples 1000 --plot
```
Expected: Time-domain plot of 1000 samples appears.

***

## 14.7 User Interface

The μATE-STM host software provides both a **Command-Line Interface (CLI)** and a **Graphical User Interface (GUI)** (planned for future releases). This section describes the CLI workflow.

### 14.7.1 Command Structure

All commands follow the pattern:
```bash
python main.py [OPTIONS] [COMMAND]
```

### 14.7.2 Common Commands

| Command | Description | Example |
|---------|-------------|---------|
| `--ping` | Check device connectivity | `python main.py --ping` |
| `--acquire` | Capture ADC samples | `python main.py --acquire --samples 1000` |
| `--fft` | Perform FFT analysis | `python main.py --fft --samples 4096` |
| `--histogram` | Generate code density histogram | `python main.py --histogram --samples 10000` |
| `--dnl-inl` | Compute DNL and INL | `python main.py --dnl-inl` |
| `--thd-snr` | Measure THD, SNR, ENOB | `python main.py --thd-snr` |
| `--report` | Generate PDF report | `python main.py --report --output test_report.pdf` |
| `--calibrate` | Run calibration procedure | `python main.py --calibrate` |
| `--help` | Show help message | `python main.py --help` |

### 14.7.3 Configuration Panels

Configuration is managed via JSON files in the `configs/` directory.

**Example (`configs/acquisition.json`):**
```json
{
  "sampling_rate": 100000,
  "buffer_size": 4096,
  "window_function": "hann",
  "averaging": 1
}
```

### 14.7.4 Plots

Plots are generated using `matplotlib` and displayed interactively or saved to files.

- **Time-Domain:** Voltage vs. sample index.
- **FFT:** Magnitude (dB) vs. frequency (Hz).
- **Histogram:** Count vs. ADC code.
- **DNL/INL:** Error (LSB) vs. ADC code.

### 14.7.5 Status Indicators

- **Console Output:** Real-time status messages (e.g., `Acquiring 1000 samples...`).
- **Log File:** `logs/uate_stm.log` contains detailed debug information.

### 14.7.6 Log Window

View logs:
```bash
tail -f logs/uate_stm.log  # Linux/macOS
Get-Content logs/uate_stm.log -Wait  # Windows PowerShell
```

***

## 14.8 Performing Measurements

### 14.8.1 ADC Characterization (DC)

**Purpose:** Verify ADC accuracy at DC voltages.

**Setup:**
- Connect a stable DC voltage (e.g., 1.5 V from a battery) to `AIN` and `GND`.

**Procedure:**
```bash
python main.py --acquire --samples 100 --average
```

**Expected Results:**
- Average voltage within ±1% of multimeter reading.

**Interpretation:**
- Large deviation → Check calibration (Section 14.9).

### 14.8.2 DAC Characterization (DC)

**Purpose:** Verify DAC output accuracy.

**Setup:**
- Connect multimeter to `AOUT` and `GND`.

**Procedure:**
```bash
python main.py --dac-set --code 2048
```
(Outputs ~1.65 V).

**Expected Results:**
- Multimeter reads 1.65 V ±1%.

**Interpretation:**
- Deviation → DAC gain/offset error; calibrate.

### 14.8.3 FFT Analysis

**Purpose:** Analyze frequency content of input signal.

**Setup:**
- Connect sine wave generator (1 kHz, 1 Vpp) to `AIN`.

**Procedure:**
```bash
python main.py --fft --samples 4096 --window hann
```

**Expected Results:**
- Peak at 1 kHz; harmonics at 2 kHz, 3 kHz, etc.

**Interpretation:**
- High harmonics → Distortion in signal source or ADC.

### 14.8.4 Histogram Analysis

**Purpose:** Evaluate ADC code density.

**Setup:**
- Connect low-frequency ramp signal (0–3.3 V, ~10 Hz) to `AIN`.

**Procedure:**
```bash
python main.py --histogram --samples 10000
```

**Expected Results:**
- Uniform histogram (all codes have similar counts).

**Interpretation:**
- Peaks/valleys → ADC non-linearity (DNL/INL).

### 14.8.5 DNL/INL Measurement

**Purpose:** Quantify ADC linearity errors.

**Setup:**
- Same as histogram (ramp input).

**Procedure:**
```bash
python main.py --dnl-inl --samples 10000
```

**Expected Results:**
- DNL/INL plots saved to `data/processed/`.
- Max DNL < ±1 LSB (ideal ADC).

**Interpretation:**
- DNL > ±1 LSB → Missing codes possible.
- INL trend → Gain/offset error.

### 14.8.6 THD Measurement

**Purpose:** Measure harmonic distortion.

**Setup:**
- Connect pure sine wave (1 kHz) to `AIN`.

**Procedure:**
```bash
python main.py --thd-snr --samples 4096 --window hann
```

**Expected Results:**
- THD < -60 dB (typical for 12-bit ADC).

**Interpretation:**
- High THD → Distortion in signal chain.

### 14.8.7 SNR Measurement

**Purpose:** Evaluate noise performance.

**Setup:**
- Same as THD.

**Procedure:**
```bash
python main.py --thd-snr
```

**Expected Results:**
- SNR ~70–74 dB (theoretical max for 12-bit).

**Interpretation:**
- Low SNR → Excessive noise (check grounding, shielding).

### 14.8.8 ENOB Calculation

**Purpose:** Determine effective resolution.

**Setup:**
- Same as SNR.

**Procedure:**
- ENOB is automatically calculated in `--thd-snr` output.

**Expected Results:**
- ENOB ~11–11.5 bits (realistic for 12-bit ADC).

**Interpretation:**
- ENOB < 10 bits → Significant noise/distortion.

***

## 14.9 Calibration

### 14.9.1 When Calibration Is Required

- **Initial Setup:** After first assembly.
- **Periodic:** Every 6 months (or if measurements drift).
- **After Component Replacement:** If resistors/capacitors are changed.

### 14.9.2 Calibration Procedure

**DC Offset Calibration:**
1. **Short AIN to GND** (0 V input).
2. **Run:**
   ```bash
   python main.py --calibrate --offset
   ```
3. **Software:** Computes average ADC code; stores as offset.

**DC Gain Calibration:**
1. **Apply 3.3 V** to AIN (use 3.3V rail).
2. **Run:**
   ```bash
   python main.py --calibrate --gain
   ```
3. **Software:** Computes gain factor; stores.

### 14.9.3 Verification

After calibration, verify:
```bash
python main.py --acquire --samples 100 --average
```
Compare with multimeter.

### 14.9.4 Storing Calibration Constants

- **Host:** Saved to `configs/calibration.json`.
- **Firmware:** Stored in flash (if implemented; see Chapter 13).

### 14.9.5 Restoring Factory Defaults

```bash
python main.py --calibrate --reset
```
Deletes `configs/calibration.json`; reloads defaults.

***

## 14.10 Reports

### 14.10.1 Report Generation

```bash
python main.py --report --output my_report.pdf
```

### 14.10.2 Report Contents

- **Header:** Instrument ID, date, operator.
- **Configuration:** Sampling rate, buffer size, window.
- **Measurements:**
  - Time-domain plot.
  - FFT spectrum.
  - Histogram, DNL, INL plots.
  - THD, SNR, ENOB metrics.
- **Pass/Fail:** Based on thresholds in `configs/test_plans.json`.

### 14.10.3 Exporting

- **PDF:** `--output report.pdf`.
- **HTML:** `--output report.html`.
- **CSV:** Raw data exported to `data/processed/`.

### 14.10.4 Saving

Reports are automatically saved to `reports/` directory.

### 14.10.5 Supported Formats

- **PDF:** Portable Document Format (recommended for sharing).
- **HTML:** Interactive (plots embedded as images).
- **CSV:** Comma-separated values (for further analysis).

***

## 14.11 Configuration

### 14.11.1 Sampling Frequency

- **Parameter:** `sampling_rate` (Hz).
- **Range:** 1000 to 100000.
- **Default:** 100000 (100 kSPS).
- **Effect:** Higher rates capture faster signals but increase data volume.

### 14.11.2 Buffer Size

- **Parameter:** `buffer_size` (samples).
- **Range:** 256 to 65535.
- **Default:** 4096.
- **Effect:** Larger buffers improve FFT resolution but increase acquisition time.

### 14.11.3 Averaging

- **Parameter:** `averaging` (integer).
- **Range:** 1 to 100.
- **Default:** 1.
- **Effect:** Reduces noise by averaging multiple acquisitions; slows measurement.

### 14.11.4 Window Function

- **Parameter:** `window_function`.
- **Options:** `rectangular`, `hann`, `hamming`, `blackman`, `flat-top`.
- **Default:** `hann`.
- **Effect:** Reduces spectral leakage in FFT; `hann` is recommended for general use.

### 14.11.5 UART Settings

- **Parameter:** `baud_rate`.
- **Default:** 921600.
- **Effect:** Higher rates increase throughput but may cause errors on long cables.

### 14.11.6 Report Options

- **Parameter:** `report_format`, `include_plots`.
- **Default:** PDF with plots.
- **Effect:** Customize report content.

***

## 14.12 Troubleshooting

| Problem | Possible Causes | Diagnostic Procedure | Corrective Action |
|---------|-----------------|----------------------|-------------------|
| **No Power** | USB cable faulty, port dead | Try different USB cable/port | Replace cable; use powered USB hub |
| **No UART Communication** | Wrong COM port, baud rate mismatch | Check Device Manager; run `--ping` | Select correct port; verify baud rate |
| **Incorrect ADC Values** | Calibration drift, wrong input range | Measure input with multimeter | Recalibrate; ensure input < 3.3 V |
| **Noisy Measurements** | Poor grounding, EMI | Check ground connections; use shielded cables | Improve grounding; add decoupling |
| **Failed Calibration** | Unstable voltage source | Verify voltage source with multimeter | Use stable reference (e.g., 3.3V rail) |
| **Report Generation Fails** | Missing dependencies, disk full | Check `pip list`; verify disk space | Install `reportlab`; free disk space |
| **FFT Shows Aliasing** | Input frequency > Nyquist | Check input frequency; reduce sampling rate | Add anti-aliasing filter; lower input frequency |
| **DAC Output Distorted** | Load too heavy, settling time | Measure DAC output with oscilloscope | Reduce load; increase settling delay |

***

## 14.13 Frequently Asked Questions

**Q: Can I measure voltages above 3.3 V?**  
A: No. Exceeding 3.3 V may damage the STM32. Use a voltage divider for higher voltages.

**Q: Why is my SNR lower than 74 dB?**  
A: Real-world noise (power supply, EMI) reduces SNR. Ensure proper grounding and shielding.

**Q: Can I use this with a Raspberry Pi?**  
A: Yes. Install Python 3.9+ and dependencies; connect via USB.

**Q: How often should I calibrate?**  
A: Every 6 months, or if measurements drift significantly.

**Q: What if the device is not detected?**  
A: Check USB cable, drivers, and COM port. Run `python main.py --ping` to verify.

**Q: Can I generate arbitrary waveforms?**  
A: Currently, only sine, triangle, square, and ramp are supported. Custom waveforms require firmware modification.

***

## 14.14 Best Practices

### 14.14.1 Measurement Techniques

- **Averaging:** Use `--average` for DC measurements to reduce noise.
- **Windowing:** Always use a window function (e.g., `hann`) for FFT to reduce leakage.
- **Buffer Size:** Use power-of-2 sizes (e.g., 4096) for efficient FFT.

### 14.14.2 Cable Routing

- **Keep Analog Wires Short:** Minimize pickup of EMI.
- **Separate Analog/Digital:** Route analog signals away from USB cable.

### 14.14.3 Grounding

- **Single-Point Ground:** Connect all grounds to the STM32 GND pin.
- **Avoid Ground Loops:** Do not connect multiple ground paths.

### 14.14.4 Calibration Frequency

- **Initial:** After assembly.
- **Periodic:** Every 6 months.
- **After Shock:** If the instrument is dropped or exposed to extreme temperatures.

### 14.14.5 Operating Conditions

- **Temperature:** Operate at room temperature (20–25°C) for best accuracy.
- **Humidity:** Avoid high humidity (>80%) to prevent condensation.

### 14.14.6 Data Management

- **Backup:** Regularly backup `data/` and `reports/` directories.
- **Naming:** Use descriptive filenames (e.g., `adc_test_2026-08-02.pdf`).

***

## 14.15 Maintenance

### 14.15.1 Cleaning

- **Exterior:** Wipe with a dry, lint-free cloth.
- **Breadboard:** Use compressed air to remove dust; do not use liquids.

### 14.15.2 Storage

- **Environment:** Cool, dry place (10–30°C, <60% humidity).
- **Packaging:** Store in anti-static bag; avoid bending jumper wires.

### 14.15.3 Inspection

- **Monthly:** Check for loose wires, corrosion, or damaged components.
- **Before Use:** Verify USB cable integrity.

### 14.15.4 Firmware Updates

- **Check:** https://github.com/your-username/uate-stm/releases.
- **Update:** Follow instructions in `firmware/README.md`.

### 14.15.5 Recalibration

- **Schedule:** Every 6 months.
- **Procedure:** See Section 14.9.

### 14.15.6 Periodic Verification

- **Quarterly:** Run `--self-test` and compare with baseline results.

***

## 14.16 Technical Specifications

| Parameter | Specification | Notes |
|-----------|---------------|-------|
| **Supply Voltage** | 5 V (USB) | 500 mA max |
| **ADC Resolution** | 12 bits | 0 to 4095 codes |
| **ADC Input Range** | 0 to 3.3 V | Do not exceed 3.6 V |
| **DAC Resolution** | 12 bits | 0 to 4095 codes |
| **DAC Output Range** | 0 to 3.3 V | 10 mA max drive |
| **Sampling Rate** | 1 kSPS to 100 kSPS | Configurable |
| **Communication** | USB CDC (UART) | 921600 baud default |
| **Operating Temperature** | 10°C to 40°C | Indoor use only |
| **Accuracy (DC)** | ±1% | After calibration |
| **Bandwidth** | 50 kHz (analog) | RC filter cutoff |
| **Dimensions** | Nucleo: 70×75 mm; Breadboard: 160×50 mm | Portable |
| **Weight** | ~150 g | Including cables |

***

## 14.17 Quick Start Checklist

Use this checklist for first-time setup.

- [ ] **Unpack:** Verify all items from Section 14.3 are present.
- [ ] **Inspect:** Check for loose wires or damaged components.
- [ ] **Install Software:**
  - [ ] Install Python 3.9+.
  - [ ] Clone repository or download ZIP.
  - [ ] Create virtual environment.
  - [ ] Install dependencies (`pip install -r requirements.txt`).
- [ ] **Connect Hardware:**
  - [ ] Plug USB cable into STM32 board and computer.
  - [ ] Verify green LED on STM32 board lights up.
- [ ] **Verify Communication:**
  - [ ] Run `python main.py --ping`.
  - [ ] Confirm `Device responded: OK`.
- [ ] **Run Self-Test:**
  - [ ] Run `python main.py --self-test`.
  - [ ] Confirm `All tests passed`.
- [ ] **First Measurement:**
  - [ ] Connect 1.5 V battery to `AIN` and `GND`.
  - [ ] Run `python main.py --acquire --samples 100 --average`.
  - [ ] Verify voltage reading matches multimeter.
- [ ] **Generate Report:**
  - [ ] Run `python main.py --report --output quick_start.pdf`.
  - [ ] Open `quick_start.pdf`; verify plots and metrics.

***

## 14.18 User Manual Summary

The μATE-STM instrument provides a complete workflow for mixed-signal testing:

1. **Setup:** Install software, connect hardware (Section 14.5).
2. **Calibrate:** Perform DC offset/gain calibration (Section 14.9).
3. **Measure:** Acquire data, perform FFT, histogram, DNL/INL, THD/SNR (Section 14.8).
4. **Analyze:** Review plots, metrics, pass/fail indicators.
5. **Report:** Generate PDF/HTML report for documentation (Section 14.10).
6. **Maintain:** Periodic recalibration, inspection, software updates (Section 14.15).

For detailed technical background, refer to Chapters 1–13 of the project report. For troubleshooting, see Section 14.12.

***