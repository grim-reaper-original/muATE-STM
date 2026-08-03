# 10. Verification, Validation, Testing, and Calibration

This chapter defines the complete Verification & Validation Plan (VVP) for the μATE-STM system. It is written to support engineering design reviews and to provide another engineer with repeatable, objective procedures to verify that all hardware, firmware, host software, and integrated system requirements are satisfied.

***

## 10.1 Verification Philosophy

### 10.1.1 Verification vs Validation

**Verification** answers: *"Did we build the product right?"*

- Confirms that each component and subsystem meets its specified requirements.
- Uses inspections, analyses, demonstrations, and tests.
- Traceable to requirement IDs (HR-xxx, SR-xxx).

**Validation** answers: *"Did we build the right product?"*

- Confirms that the complete system satisfies user needs and intended use.
- Focuses on end-to-end functionality and educational objectives.
- Often involves stakeholder review and real-world scenario testing.

**Why Both Are Necessary:**

- Verification ensures technical correctness at each level.
- Validation ensures the system fulfills its purpose (educational mixed-signal testing).
- A system can be verified (meets specs) but not validated (doesn't solve the right problem).

### 10.1.2 Related Concepts

| Term | Definition | Purpose |
|------|------------|---------|
| **Verification** | Confirmation that outputs meet input requirements | Ensure correctness of design and implementation |
| **Validation** | Confirmation that the system meets user needs | Ensure the right system was built |
| **Calibration** | Adjustment or characterization to correct systematic errors | Improve measurement accuracy |
| **Characterization** | Measurement of system behavior under various conditions | Understand performance limits and non-idealities |
| **Qualification** | Formal demonstration that system meets all requirements | Readiness for deployment or production |
| **Acceptance Testing** | Final testing to confirm readiness for delivery | Customer/stakeholder sign-off |

### 10.1.3 Engineering Quality Objectives

- **Objectivity:** All tests have measurable, binary pass/fail criteria.
- **Repeatability:** Tests produce consistent results across multiple runs.
- **Traceability:** Every test maps to specific requirements.
- **Completeness:** All requirements (hardware, firmware, software) are verified.
- **Efficiency:** Tests are automated where possible to reduce manual effort.

### 10.1.4 Acceptance Philosophy

- **Progressive Acceptance:**
  - Unit tests → Module tests → Integration tests → System tests.
  - Each level must pass before proceeding.
- **Zero Critical Defects:**
  - No open critical or high-severity bugs at acceptance.
- **Documented Evidence:**
  - Test reports with raw data, plots, and analysis.

### 10.1.5 Requirement Traceability Philosophy

- **Bidirectional Traceability:**
  - Requirements → Tests (forward traceability).
  - Tests → Requirements (backward traceability).
- **RTM (Requirements Traceability Matrix):**
  - Living document updated as requirements or tests change.
- **Coverage Goal:** 100% of requirements verified by at least one test.

***

## 10.2 Requirement Traceability Matrix

This section provides a Requirements Traceability Matrix (RTM) linking all hardware (HR-xxx) and software (SR-xxx) requirements to verification methods and test procedures.

| Req ID | Description | Verification Method | Test Procedure | Expected Result | Acceptance Criteria | Status |
|--------|-------------|---------------------|----------------|-----------------|---------------------|--------|
| HR-001 | Voltage Range 0–3.3 V | Measurement | DMM measurement at DAC/ADC pins | 0–3.3 V under all conditions | ±2% of nominal | ☐ |
| HR-002 | Absolute Max < 5 V | Measurement | Apply 5 V input; measure clamped voltage | < 5 V at pin | < 5 V absolute | ☐ |
| HR-003 | Current Limiting ≤ 10 mA | Calculation/Measurement | Measure fault current with 5 V applied | ≤ 10 mA | ≤ 10 mA | ☐ |
| HR-004 | ADC Sampling ≥ 100 kSPS | Measurement | Configure 100 kSPS; measure actual rate | ≥ 100 kSPS | ±5% of target | ☐ |
| HR-005 | DAC Update ≥ 50 kSPS | Measurement | Configure 50 kSPS sine; measure output | ≥ 50 kSPS | ±5% of target | ☐ |
| HR-006 | ADC Source Impedance ≤ 10 kΩ | Calculation | Compute divider output impedance | ≤ 10 kΩ | ≤ 10 kΩ | ☐ |
| HR-007 | Overvoltage Protection | Demonstration | Apply 5 V to ADC input; verify clamping | Diodes conduct; pin < 5 V | Pin voltage < 5 V | ☐ |
| HR-008 | USB Power | Measurement | Measure current draw from USB | ≤ 200 mA | ≤ 200 mA | ☐ |
| HR-009 | Cost ≤ ₹1,000 | Inspection | Sum BOM costs | ≤ ₹1,000 | ≤ ₹1,000 | ☐ |
| SR-001 | Test Configuration | Demonstration | Run CLI with config file | Test starts with specified params | Config applied correctly | ☐ |
| SR-002 | Waveform Generation | Measurement | Measure DAC output with oscilloscope | Ramp/sine as configured | Waveform matches expected | ☐ |
| SR-003 | ADC Acquisition | Demonstration | Capture 10k samples; verify buffer | 10k samples in buffer | No sample loss | ☐ |
| SR-004 | UART Communication | Demonstration | Send/receive packets | ACKs received; data intact | No CRC errors | ☐ |
| SR-005 | Histogram Analysis | Demonstration | Run ramp test; verify DNL/INL plots | Plots generated | DNL/INL within expected range | ☐ |
| SR-006 | FFT Analysis | Demonstration | Run sine test; verify FFT/THD/SNR | Metrics computed | THD/SNR reasonable | ☐ |
| SR-007 | Data Logging | Inspection | Check output files | CSV/HTML/PDF saved | Files present and valid | ☐ |
| SR-008 | Sampling Rate 1–200 kSPS | Measurement | Test at 1, 10, 100, 200 kSPS | Actual rate matches config | ±5% | ☐ |
| SR-009 | Buffer Size 1k–50k | Demonstration | Test with 1k, 10k, 50k samples | No overflow | All samples captured | ☐ |
| SR-010 | UART Throughput | Measurement | Time 50k sample transfer at 921600 baud | < 10 s | < 10 s | ☐ |
| SR-011 | End-to-End Latency < 60 s | Measurement | Time full test (10k samples) | < 60 s | < 60 s | ☐ |
| SR-012 | Error Recovery | Demonstration | Induce UART timeout; verify recovery | Test aborts gracefully | User notified | ☐ |
| SR-013 | CLI Usability | Inspection | Run `--help`; check error messages | Clear help/errors | User can operate | ☐ |
| SR-014 | Code Maintainability | Inspection | Check documentation coverage | > 80% functions documented | Pass | ☐ |
| SR-015 | Extensibility | Demonstration | Add new test profile via config | New test runs without code change | Pass | ☐ |

***

## 10.3 Test Strategy

The testing strategy follows a **V-model** approach, progressing from unit tests to system acceptance.

### 10.3.1 Unit Testing

**Purpose:** Verify individual modules in isolation.

- **Firmware:** ADC driver, DAC driver, UART driver, DMA driver, command parser.
- **Host:** Parser, FFT, histogram, DNL/INL, plotting, report generator, config manager.
- **Why:** Catch bugs early; ensure module correctness before integration.

### 10.3.2 Module Testing

**Purpose:** Verify subsystems (e.g., ADC+DMA, DAC+Timer).

- **Examples:** ADC acquisition with DMA, DAC waveform generation with timer.
- **Why:** Ensure modules work together before full integration.

### 10.3.3 Integration Testing

**Purpose:** Verify interactions between subsystems.

- **Examples:** Firmware ↔ Host communication, Acquisition ↔ Processing.
- **Why:** Detect interface mismatches and protocol errors.

### 10.3.4 System Testing

**Purpose:** Verify end-to-end functionality.

- **Examples:** Ramp histogram test, sine FFT test, loopback test.
- **Why:** Confirm the complete system meets user requirements.

### 10.3.5 Acceptance Testing

**Purpose:** Final validation against all requirements.

- **Procedure:** Execute RTM tests; review test reports.
- **Why:** Stakeholder sign-off.

### 10.3.6 Regression Testing

**Purpose:** Ensure changes do not break existing functionality.

- **Automated:** Unit and integration tests run on each commit.
- **Why:** Maintain stability during development.

### 10.3.7 Performance Testing

**Purpose:** Measure timing, throughput, and resource usage.

- **Metrics:** Sampling rate, UART throughput, FFT time, memory usage.
- **Why:** Verify performance requirements (SR-008 to SR-011).

### 10.3.8 Stress Testing

**Purpose:** Verify behavior under extreme conditions.

- **Scenarios:** Max sample count, continuous operation, corrupted packets.
- **Why:** Ensure robustness.

### 10.3.9 Fault Injection Testing

**Purpose:** Verify error handling and recovery.

- **Faults:** Invalid CRC, UART timeout, ADC failure, memory overflow.
- **Why:** Confirm graceful degradation.

### 10.3.10 Long-Duration Testing

**Purpose:** Verify stability over extended operation.

- **Procedure:** Run continuous acquisition for 1–2 hours.
- **Why:** Detect memory leaks, thermal issues, or drift.

***

## 10.4 Test Environment

### 10.4.1 Hardware Configuration

- **STM32 Board:** STM32F446RE Nucleo or equivalent.
- **AFE:** Breadboard with resistors, capacitors, diodes as per Chapter 8.
- **Power:** USB from laptop or USB hub.
- **Wiring:** As per Section 8.15 (DAC → AFE → ADC loopback).

### 10.4.2 Firmware Version

- **Version:** v1.0 (as per this document).
- **Build:** STM32CubeIDE, optimization level `-O2`.
- **Debug:** Serial debug output enabled (115200 baud on separate UART).

### 10.4.3 Host Software Version

- **Python:** 3.10+.
- **Libraries:** `numpy`, `scipy`, `matplotlib`, `pyserial`.
- **Version:** v1.0 (as per this document).

### 10.4.4 Operating System

- **Primary:** Windows 10/11 or Ubuntu 22.04 LTS.
- **Secondary:** macOS (for portability testing).

### 10.4.5 Measurement Equipment

| Equipment | Purpose |
|-----------|---------|
| DMM (e.g., UNI-T UT33A) | Voltage measurements |
| Oscilloscope (or PC soundcard) | Waveform verification |
| USB-to-UART adapter (if needed) | Serial communication |

### 10.4.6 Environmental Assumptions

- **Temperature:** 15–35 °C (room temperature).
- **Humidity:** < 80% non-condensing.
- **Power:** Stable USB 5 V supply.

***

## 10.5 Test Equipment

| Equipment | Purpose | Required Accuracy | Calibration Requirement | Low-Cost Alternative | Why Sufficient |
|-----------|---------|-------------------|-------------------------|----------------------|----------------|
| DMM (e.g., UNI-T UT33A) | Voltage/current measurements | ±1% for DC voltage | Annual calibration or verification against known reference | Basic multimeter (₹300–400) | Adequate for 3.3 V range verification |
| Oscilloscope (or PC soundcard) | Waveform visualization | Bandwidth ≥ 10 MHz | N/A (qualitative) | PC soundcard + software (e.g., SoundCard) | Sufficient for < 100 kHz signals |
| USB-to-UART adapter | Serial communication | N/A | N/A | CH340/CP2102 module (₹100) | Standard UART interface |
| Stopwatch (or Python `time`) | Timing measurements | ±1 ms | N/A | Python `time` module | Sufficient for latency tests |
| Temperature sensor (optional) | Thermal monitoring | ±1 °C | N/A | LM35 module (₹50) | Detect thermal drift |

***

## 10.6 Unit Testing

### 10.6.1 Firmware Unit Tests

#### ADC Driver Test

- **Objective:** Verify ADC initialization and single conversion.
- **Inputs:** Configuration (channel, sample time).
- **Procedure:**
  1. Call `ADC_Driver_Init()`.
  2. Trigger single conversion.
  3. Read result.
- **Expected Outputs:** Valid 12-bit code (0–4095).
- **Pass Criteria:** Code within expected range for known input voltage.

#### DAC Driver Test

- **Objective:** Verify DAC output for known codes.
- **Inputs:** DAC code (0, 2048, 4095).
- **Procedure:**
  1. Call `DAC_Driver_SetValue(code)`.
  2. Measure output with DMM.
- **Expected Outputs:** 0 V, 1.65 V, 3.3 V (±5%).
- **Pass Criteria:** Measured voltage within ±5% of expected.

#### UART Driver Test

- **Objective:** Verify UART TX/RX.
- **Inputs:** Test string ("Hello").
- **Procedure:**
  1. Send string via UART.
  2. Loopback TX to RX.
  3. Verify received string.
- **Expected Outputs:** "Hello" received correctly.
- **Pass Criteria:** No character errors.

#### DMA Driver Test

- **Objective:** Verify DMA transfer to buffer.
- **Inputs:** ADC trigger, buffer pointer.
- **Procedure:**
  1. Configure DMA for ADC.
  2. Trigger 100 conversions.
  3. Check buffer contents.
- **Expected Outputs:** 100 samples in buffer.
- **Pass Criteria:** Buffer filled without gaps.

#### Command Parser Test

- **Objective:** Verify packet parsing.
- **Inputs:** Valid/invalid packets.
- **Procedure:**
  1. Feed packet to parser.
  2. Check response (ACK/NACK).
- **Expected Outputs:** ACK for valid, NACK for invalid.
- **Pass Criteria:** Correct response for all test vectors.

***

### 10.6.2 Host Unit Tests

#### Parser Test

- **Objective:** Verify binary packet decoding.
- **Inputs:** Known byte sequences.
- **Procedure:**
  1. Pass bytes to `data_parser.parse()`.
  2. Check parsed fields.
- **Expected Outputs:** Correct sync, length, cmd, payload, CRC.
- **Pass Criteria:** All fields match expected.

#### FFT Test

- **Objective:** Verify FFT correctness.
- **Inputs:** Synthetic sine wave (numpy).
- **Procedure:**
  1. Generate sine (f=1 kHz, fs=100 kSPS, N=10k).
  2. Call `signal_processing.compute_fft()`.
  3. Check peak frequency.
- **Expected Outputs:** Peak at 1 kHz.
- **Pass Criteria:** Frequency error < 1%.

#### Histogram Test

- **Objective:** Verify histogram computation.
- **Inputs:** Ramp data (0–4095).
- **Procedure:**
  1. Generate ramp.
  2. Call `signal_processing.compute_histogram()`.
- **Expected Outputs:** Uniform histogram (±10% variation).
- **Pass Criteria:** Histogram flatness within 10%.

#### DNL/INL Test

- **Objective:** Verify DNL/INL calculation.
- **Inputs:** Histogram from ideal ramp.
- **Procedure:**
  1. Compute DNL/INL.
- **Expected Outputs:** DNL ≈ 0, INL ≈ 0.
- **Pass Criteria:** |DNL| < 0.1, |INL| < 0.5.

#### Plotting Test

- **Objective:** Verify plot generation.
- **Inputs:** Sample data.
- **Procedure:**
  1. Call `plotting.plot_time()`, `plot_fft()`, etc.
- **Expected Outputs:** PNG files saved.
- **Pass Criteria:** Files non-empty, correct format.

#### Report Generator Test

- **Objective:** Verify report creation.
- **Inputs:** Metrics, plot paths.
- **Procedure:**
  1. Call `report_generator.generate()`.
- **Expected Outputs:** CSV/HTML files saved.
- **Pass Criteria:** Files valid and complete.

#### Configuration Manager Test

- **Objective:** Verify config loading/validation.
- **Inputs:** Valid/invalid JSON.
- **Procedure:**
  1. Load config.
- **Expected Outputs:** Valid config or error.
- **Pass Criteria:** Correct behavior for valid/invalid inputs.

***

## 10.7 Integration Testing

### 10.7.1 ADC + DMA Integration

- **Objective:** Verify continuous ADC sampling with DMA.
- **Setup:** ADC connected to potentiometer; DMA buffer configured.
- **Procedure:**
  1. Start ADC+DMA.
  2. Wait for buffer full.
  3. Read buffer.
- **Expected Behavior:** Buffer filled with sequential samples.
- **Acceptance Criteria:** No sample loss; correct count.

### 10.7.2 DAC + Timer Integration

- **Objective:** Verify timer-triggered DAC updates.
- **Setup:** DAC output to oscilloscope.
- **Procedure:**
  1. Configure timer for 50 kSPS.
  2. Load sine LUT.
  3. Measure output frequency.
- **Expected Behavior:** Sine wave at expected frequency.
- **Acceptance Criteria:** Frequency within ±5%.

### 10.7.3 UART + Parser Integration

- **Objective:** Verify end-to-end packet handling.
- **Setup:** STM32 UART connected to PC via USB-to-UART.
- **Procedure:**
  1. Host sends `CONFIG_TEST`.
  2. Firmware responds with ACK.
- **Expected Behavior:** ACK received, parsed correctly.
- **Acceptance Criteria:** No CRC errors; correct response.

### 10.7.4 Firmware + Host Integration

- **Objective:** Verify full command/response cycle.
- **Setup:** Loopback (DAC → ADC).
- **Procedure:**
  1. Host sends config + start.
  2. Firmware acquires and sends data.
  3. Host receives and parses.
- **Expected Behavior:** Data received, plots generated.
- **Acceptance Criteria:** End-to-end success.

### 10.7.5 Acquisition + Processing Integration

- **Objective:** Verify raw data → metrics pipeline.
- **Setup:** Sine test.
- **Procedure:**
  1. Acquire 10k samples.
  2. Compute FFT, THD, SNR.
- **Expected Behavior:** Metrics reasonable (THD < 5%, SNR > 50 dB).
- **Acceptance Criteria:** Metrics within expected range.

### 10.7.6 Plotting + Report Integration

- **Objective:** Verify plots embedded in reports.
- **Setup:** Completed test.
- **Procedure:**
  1. Generate report.
  2. Open HTML/PDF.
- **Expected Behavior:** Plots visible, metrics listed.
- **Acceptance Criteria:** Report complete and valid.

***

## 10.8 System Testing

### 10.8.1 Ramp Histogram Test

- **Objective:** Verify DNL/INL measurement.
- **Setup:** DAC ramp → ADC.
- **Procedure:**
  1. Configure ramp test (10k samples, 100 kSPS).
  2. Run test.
  3. Generate DNL/INL plots.
- **Expected Behavior:** DNL/INL within ±0.5 LSB.
- **Acceptance Criteria:** Plots show expected pattern; no missing codes.

### 10.8.2 Sine FFT Test

- **Objective:** Verify THD/SNR measurement.
- **Setup:** DAC sine (1 kHz) → ADC.
- **Procedure:**
  1. Configure sine test (10k samples, 100 kSPS).
  2. Run test.
  3. Generate FFT, THD, SNR.
- **Expected Behavior:** Single peak at 1 kHz; harmonics visible.
- **Acceptance Criteria:** THD < 5%, SNR > 50 dB.

### 10.8.3 Loopback Test

- **Objective:** Verify full signal chain.
- **Setup:** DAC → AFE → ADC.
- **Procedure:**
  1. Run ramp and sine tests.
  2. Compare input/output.
- **Expected Behavior:** Waveforms match (within noise).
- **Acceptance Criteria:** Correlation > 0.95.

### 10.8.4 Continuous Acquisition Test

- **Objective:** Verify sustained operation.
- **Setup:** Continuous trigger.
- **Procedure:**
  1. Run 100 acquisitions back-to-back.
- **Expected Behavior:** No crashes, no data loss.
- **Acceptance Criteria:** All 100 tests complete successfully.

### 10.8.5 Long Duration Stability Test

- **Objective:** Verify thermal/temporal stability.
- **Setup:** Continuous operation for 1 hour.
- **Procedure:**
  1. Run sine test repeatedly.
  2. Monitor THD/SNR drift.
- **Expected Behavior:** Metrics stable (±5%).
- **Acceptance Criteria:** No significant drift.

***

### 10.9 Calibration Procedures

This section defines engineering calibration procedures to correct systematic errors in ADC and DAC measurements. Calibration is performed at initial bring-up and periodically thereafter (e.g., every 6 months or after hardware modifications).

#### 10.9.1 ADC Offset Calibration

**Objective:**  
Determine and correct ADC zero-scale offset error.

**Equipment:**

- DMM (accuracy ±1%).
- Shorting wire or 0 V reference.

**Setup:**

- Connect ADC input (PA0) to GND via shorting wire.
- Ensure no external voltage sources.

**Procedure:**

1. Configure ADC for 12-bit single-channel mode.
2. Capture N = 1000 samples.
3. Compute mean code: \(\bar{C}_{\text{zero}} = \frac{1}{N} \sum_{i=1}^{N} C_i\).
4. Ideal zero code = 0.
5. Offset error (LSB): \(\text{Offset}_{\text{ADC}} = \bar{C}_{\text{zero}}\).

**Equation:**

- Corrected code: \(C_{\text{corr}} = C_{\text{raw}} - \text{Offset}_{\text{ADC}}\).

**Acceptance Limits:**

- |Offset_ADC| < 5 LSB (typical for 12-bit ADC).

**Documentation:**

- Record in `calibration.json`:
  ```json
  {
    "adc_offset_lsb": 2.3,
    "calibration_date": "2026-08-02",
    "temperature_c": 25.0
  }
  ```

***

#### 10.9.2 ADC Gain Calibration

**Objective:**  
Determine and correct ADC gain (scale factor) error.

**Equipment:**

- DMM.
- Precision voltage reference or calibrated DAC output (e.g., 3.3 V).

**Setup:**

- Connect ADC input to known voltage \(V_{\text{ref\_actual}}\) (e.g., 3.3 V measured by DMM).

**Procedure:**

1. Capture N = 1000 samples.
2. Compute mean code: \(\bar{C}_{\text{full}}\).
3. Ideal full-scale code: \(C_{\text{ideal}} = 4095\).
4. Expected code for \(V_{\text{ref\_actual}}\):
$$
C_{\text{expected}} = \frac{V_{\text{ref\_actual}}}{V_{\text{REF\_nominal}}} \times 4095
$$
   where \(V_{\text{REF\_nominal}} = 3.3\) V.
5. Gain error: \(\text{Gain}_{\text{ADC}} = \frac{C_{\text{expected}}}{\bar{C}_{\text{full}}}\).

**Equation:**

- Corrected code: \(C_{\text{corr}} = (C_{\text{raw}} - \text{Offset}_{\text{ADC}}) \times \text{Gain}_{\text{ADC}}\).

**Acceptance Limits:**

- 0.95 < Gain_ADC < 1.05 (±5% gain error).

**Documentation:**

- Update `calibration.json`:
  ```json
  {
    "adc_gain": 1.023,
    "vref_actual_v": 3.312
  }
  ```

***

#### 10.9.3 DAC Offset Calibration

**Objective:**  
Determine DAC zero-scale offset.

**Equipment:**

- DMM.

**Setup:**

- Configure DAC to output code 0.

**Procedure:**

1. Measure output voltage \(V_{\text{out\_zero}}\).
2. Ideal = 0 V.
3. Offset error (V): \(\text{Offset}_{\text{DAC}} = V_{\text{out\_zero}}\).

**Equation:**

- Corrected voltage: \(V_{\text{corr}} = V_{\text{raw}} - \text{Offset}_{\text{DAC}}\).

**Acceptance Limits:**

- |Offset_DAC| < 10 mV.

***

#### 10.9.4 DAC Gain Calibration

**Objective:**  
Determine DAC gain error.

**Equipment:**

- DMM.

**Setup:**

- Configure DAC to output code 4095 (full scale).

**Procedure:**

1. Measure output voltage \(V_{\text{out\_full}}\).
2. Ideal = \(V_{\text{REF\_actual}}\) (e.g., 3.312 V).
3. Gain error: \(\text{Gain}_{\text{DAC}} = \frac{V_{\text{REF\_actual}}}{V_{\text{out\_full}}}\).

**Equation:**

- Corrected code for target voltage \(V_{\text{target}}\):
$$
C_{\text{target}} = \frac{V_{\text{target}}}{V_{\text{REF\_actual}} \times \text{Gain}_{\text{DAC}}} \times 4095
$$

**Acceptance Limits:**

- 0.95 < Gain_DAC < 1.05.

***

#### 10.9.5 Reference Voltage Verification

**Objective:**  
Verify actual VREF against nominal 3.3 V.

**Equipment:**

- Calibrated DMM.

**Procedure:**

1. Measure STM32 3.3 V pin.
2. Record as `vref_actual_v`.

**Acceptance Limits:**

- 3.2 V < VREF < 3.4 V.

***

#### 10.9.6 Calibration Frequency

- **Initial:** At first bring-up.
- **Periodic:** Every 6 months or after hardware changes.
- **On-Demand:** If measurement accuracy degrades.

***

#### 10.9.7 Calibration Records

- Stored in `calibration.json`.
- Includes:
  - All offset/gain values.
  - Date, temperature, operator.
  - Equipment used (DMM serial number).

***

### 10.10 Measurement Uncertainty

This section estimates uncertainty contributions from all sources and combines them using standard uncertainty propagation.

#### 10.10.1 Uncertainty Sources

| Source | Estimated Magnitude | Distribution | Type |
|--------|---------------------|--------------|------|
| ADC quantization | ±0.5 LSB = ±0.4 mV | Uniform | B |
| DAC quantization | ±0.5 LSB = ±0.4 mV | Uniform | B |
| Resistor tolerance (1%) | ±1% of divider ratio | Uniform | B |
| Capacitor tolerance (10%) | ±10% of filter cutoff | Uniform | B |
| VREF uncertainty (DMM ±1%) | ±33 mV (for 3.3 V) | Normal | B |
| Sampling jitter (timer ±100 ppm) | ±10 µs at 100 kSPS | Normal | B |
| Timer uncertainty | ±1 tick (≈12 ns at 84 MHz) | Uniform | B |
| Thermal drift (50 ppm/°C) | ±165 ppm over 10°C | Normal | B |
| Electrical noise (RMS) | ±2 mV (measured) | Normal | A |
| Numerical processing (FFT leakage) | ±0.5 dB | Normal | B |

**Type A:** Evaluated by statistical methods (e.g., noise).  
**Type B:** Evaluated by other means (e.g., datasheets).

***

#### 10.10.2 Uncertainty Propagation

For voltage measurement \(V = C \times \frac{V_{\text{REF}}}{4095}\):

- **Combined standard uncertainty:**
$$
u_c(V) = \sqrt{ \left( \frac{\partial V}{\partial C} u(C) \right)^2 + \left( \frac{\partial V}{\partial V_{\text{REF}}} u(V_{\text{REF}}) \right)^2 }
$$

**Example Calculation:**

- \(C = 2048\), \(V_{\text{REF}} = 3.3\) V.
- \(u(C) = 0.5\) LSB (quantization).
- \(u(V_{\text{REF}}) = 33\) mV (DMM).

$$
\frac{\partial V}{\partial C} = \frac{3.3}{4095} \approx 0.806 \text{ mV/LSB}
$$
$$
\frac{\partial V}{\partial V_{\text{REF}}} = \frac{2048}{4095} \approx 0.5
$$
$$
u_c(V) = \sqrt{ (0.806 \times 0.5)^2 + (0.5 \times 33)^2 } \approx \sqrt{ 0.16 + 272 } \approx 16.5 \text{ mV}
$$

**Dominant term:** VREF uncertainty.

***

### 10.11 Error Budget

| Source | Estimated Error | Distribution | Impact | Mitigation | Residual Error |
|--------|-----------------|--------------|--------|------------|----------------|
| ADC quantization | ±0.4 mV | Uniform | Low | None (fundamental) | ±0.4 mV |
| DAC quantization | ±0.4 mV | Uniform | Low | None | ±0.4 mV |
| Resistor tolerance | ±1% of ratio | Uniform | Medium | Use 1% resistors | ±1% |
| VREF uncertainty | ±33 mV | Normal | High | Calibrate VREF | ±5 mV (after calibration) |
| Electrical noise | ±2 mV (RMS) | Normal | Medium | Filtering, averaging | ±1 mV (averaged) |
| Thermal drift | ±0.5 mV/10°C | Normal | Low | Room temp operation | ±0.5 mV |
| **Total (RSS)** | — | — | — | — | **±35 mV (worst-case)** |

**RSS (Root Sum Square):**
$$
\text{Total} = \sqrt{0.4^2 + 0.4^2 + 33^2 + 2^2 + 0.5^2} \approx 33.2 \text{ mV}
$$

***

### 10.12 Performance Testing

| Metric | Procedure | Acceptance Criteria |
|--------|-----------|---------------------|
| Maximum sampling rate | Configure ADC for increasing rates; verify no sample loss | ≥ 200 kSPS (HR-004) |
| UART throughput | Time 50k sample transfer at 921600 baud | < 10 s (SR-010) |
| FFT execution time | Time `compute_fft()` for 10k samples | < 100 ms |
| Histogram execution time | Time `compute_histogram()` for 10k samples | < 50 ms |
| Report generation time | Time from analysis completion to file save | < 2 s |
| CPU usage (Host) | Monitor during test (Task Manager/top) | < 50% |
| RAM usage (Host) | Peak memory during 50k sample test | < 50 MB |
| Storage usage | Size of raw data + plots + report for 10k samples | < 10 MB |
| End-to-end latency | Time from "Start" to report saved | < 60 s (SR-011) |

***

### 10.13 Stress Testing

| Test | Objective | Expected Behavior |
|------|-----------|-------------------|
| Maximum sample count (50k) | Verify buffer handling | No overflow; all samples captured |
| Continuous acquisition (100 runs) | Verify stability | No crashes; consistent results |
| Corrupted packets (random bit flips) | Verify CRC detection | NACK sent; packet discarded |
| Invalid configuration (out-of-range params) | Verify validation | NACK with error code 0x04 |
| Repeated resets (power cycle 10x) | Verify robustness | System boots correctly each time |
| USB disconnect during transfer | Verify recovery | Host detects disconnect; retries or aborts gracefully |
| Power interruption (mid-test) | Verify safe state | Firmware enters idle; no damage |
| Memory exhaustion (allocate until failure) | Verify handling | Graceful error message; no crash |
| Malformed packets (wrong SYNC, length) | Verify parser robustness | Packets discarded; no hang |

***

### 10.14 Fault Injection

| Fault | Objective | Method | Expected Response | Recovery | Verification |
|-------|-----------|--------|-------------------|----------|--------------|
| Invalid CRC | Verify CRC check | Flip bit in CRC field | NACK (0x03) | Retry up to 3x | Log shows CRC error |
| UART timeout | Verify timeout handling | Disconnect UART mid-transfer | Host timeout after 100 ms | Retry or abort | Error message displayed |
| ADC failure (disable clock) | Verify fault detection | Modify firmware to disable ADC | Firmware logs error; sends NACK | Safe state | LED blinks error pattern |
| DMA interruption (disable stream) | Verify DMA fault handling | Stop DMA mid-transfer | Buffer incomplete; flag set | Abort test | Partial data discarded |
| Incorrect configuration (negative sample count) | Verify validation | Send invalid config | NACK (0x04) | Ignore command | Error logged |
| Memory overflow (allocate beyond RAM) | Verify protection | Modify buffer size to 200k | Firmware hangs or resets | Watchdog reset | Reset observed |
| Corrupted config file (invalid JSON) | Verify host validation | Edit `config.json` with syntax error | Host displays error; aborts | User fixes file | Error message shown |

***

### 10.15 Repeatability and Reproducibility

#### 10.15.1 Repeatability Plan

- **Number of Trials:** 10 repeated tests under identical conditions.
- **Metrics:** THD, SNR, DNL_max, INL_max.
- **Repeatability Metric:** Standard deviation (σ) of metric across trials.
- **Acceptance Threshold:** σ < 5% of mean for THD/SNR; σ < 0.1 LSB for DNL/INL.

#### 10.15.2 Reproducibility Plan

- **Conditions:** Different operators, different days, different USB ports.
- **Number of Trials:** 5 trials per condition.
- **Reproducibility Metric:** ANOVA or pooled standard deviation.
- **Acceptance Threshold:** No statistically significant difference (p > 0.05).

#### 10.15.3 Confidence Intervals

- **95% Confidence Interval:**
$$
\text{CI} = \bar{x} \pm t_{0.975, n-1} \times \frac{s}{\sqrt{n}}
$$
  where \(\bar{x}\) = mean, \(s\) = std dev, \(n\) = 10.

***

### 10.16 Statistical Analysis

| Statistic | Formula | Usage |
|-----------|---------|-------|
| Mean | \(\bar{x} = \frac{1}{n} \sum x_i\) | Central tendency of metrics |
| Variance | \(s^2 = \frac{1}{n-1} \sum (x_i - \bar{x})^2\) | Spread of data |
| Standard Deviation | \(s = \sqrt{s^2}\) | Repeatability metric |
| 95% CI | \(\bar{x} \pm 1.96 \frac{s}{\sqrt{n}}\) (large n) | Uncertainty in mean |
| Outlier Detection | Z-score > 3 or IQR method | Identify anomalous tests |
| Uncertainty Estimation | RSS of Type A + Type B | Combined measurement uncertainty |

***

### 10.17 Acceptance Criteria

| Subsystem | Criterion | Pass/Fail |
|-----------|-----------|-----------|
| Hardware (HR-001 to HR-015) | All requirements verified; no critical defects | ☐ Pass / ☐ Fail |
| Firmware (SR-002 to SR-004, SR-008 to SR-012) | All tests pass; no crashes | ☐ Pass / ☐ Fail |
| Host Software (SR-001, SR-005 to SR-007, SR-013 to SR-015) | All tests pass; documentation complete | ☐ Pass / ☐ Fail |
| System (SR-011) | End-to-end latency < 60 s | ☐ Pass / ☐ Fail |
| Calibration | All offsets/gains within limits | ☐ Pass / ☐ Fail |
| Performance | All benchmarks meet criteria | ☐ Pass / ☐ Fail |
| Stress/Fault | All stress/fault tests pass | ☐ Pass / ☐ Fail |

***

### 10.18 Test Documentation

#### 10.18.1 Required Documents

| Document | Purpose | Owner |
|----------|---------|-------|
| Unit Test Report | Results of all unit tests | Developer |
| Integration Report | Results of integration tests | Integration Engineer |
| Calibration Certificate | Calibration data and uncertainty | Calibration Engineer |
| Validation Report | End-to-end system validation | QA Engineer |
| Regression Report | Results of automated regression tests | CI/CD System |
| Performance Report | Benchmark results | Performance Engineer |
| Issue Log | All defects and resolutions | Project Manager |
| Deviation Report | Requirements not met and justification | Systems Engineer |

#### 10.18.2 Standard Report Template

```markdown
# Test Report: [Test Name]

**Test ID:** TC-XXX  
**Date:** YYYY-MM-DD  
**Operator:** [Name]  
**Equipment:** [List]  
**Setup:** [Description]  

## Procedure
1. [Step 1]
2. [Step 2]

## Results
| Metric | Expected | Measured | Pass/Fail |
|--------|----------|----------|-----------|
| ... | ... | ... | ... |

## Conclusion
[Pass/Fail with justification]

## Attachments
- Raw data files
- Plots
- Logs
```

***

### 10.19 Verification Checklist

| Verification ID | Requirement | Test Case | Status |
|-----------------|-------------|-----------|--------|
| V-001 | HR-001 (Voltage Range) | TC-001 | ☐ |
| V-002 | HR-002 (Absolute Max) | TC-002 | ☐ |
| V-003 | HR-003 (Current Limiting) | TC-003 | ☐ |
| V-004 | HR-004 (ADC Sampling) | TC-004 | ☐ |
| V-005 | HR-005 (DAC Update) | TC-005 | ☐ |
| V-006 | SR-001 (Test Configuration) | TC-010 | ☐ |
| V-007 | SR-002 (Waveform Generation) | TC-011 | ☐ |
| V-008 | SR-003 (ADC Acquisition) | TC-012 | ☐ |
| V-009 | SR-004 (UART Communication) | TC-013 | ☐ |
| V-010 | SR-005 (Histogram Analysis) | TC-020 | ☐ |
| V-011 | SR-006 (FFT Analysis) | TC-021 | ☐ |
| V-012 | SR-007 (Data Logging) | TC-022 | ☐ |
| V-013 | SR-008 (Sampling Rate) | TC-030 | ☐ |
| V-014 | SR-009 (Buffer Size) | TC-031 | ☐ |
| V-015 | SR-010 (UART Throughput) | TC-032 | ☐ |
| V-016 | SR-011 (Latency) | TC-033 | ☐ |
| V-017 | SR-012 (Error Recovery) | TC-040 | ☐ |
| V-018 | SR-013 (CLI Usability) | TC-041 | ☐ |
| V-019 | SR-014 (Maintainability) | TC-042 | ☐ |
| V-020 | SR-015 (Extensibility) | TC-043 | ☐ |

***

### 10.20 Future Validation

#### 10.20.1 Industrial Deployment

- **Requirements:**
  - Environmental testing (temperature, humidity, vibration).
  - EMC/EMI compliance.
  - Long-term reliability (MTBF > 10,000 hours).
- **Validation:**
  - Accelerated life testing.
  - Field trials in target environment.

#### 10.20.2 Research Laboratories

- **Requirements:**
  - Higher accuracy (external reference, 16-bit ADC).
  - Traceability to national standards.
- **Validation:**
  - Comparison with calibrated instruments.
  - Uncertainty budget < 0.1%.

#### 10.20.3 Commercial Instrumentation

- **Requirements:**
  - Safety certifications (CE, FCC, UL).
  - Manufacturing test procedures.
  - User documentation and support.
- **Validation:**
  - Pre-compliance testing.
  - Production line qualification.

#### 10.20.4 Regulatory Certification

- **Standards:**
  - IEC 61010 (safety for measurement equipment).
  - FCC Part 15 (EMI).
- **Validation:**
  - Third-party testing laboratory.
  - Certification documentation.

***

### 10.21 Test Automation

#### 10.21.1 Automated Test Execution

- **Framework:** `pytest` for host software; custom C test harness for firmware.
- **Trigger:** On each Git commit (CI/CD).
- **Environment:** Docker container with Python dependencies.

#### 10.21.2 Automated Report Generation

- **Tool:** `pytest-html` or custom Sphinx reports.
- **Output:** HTML report with pass/fail summary, plots, logs.

#### 10.21.3 Regression Testing

- **Scope:** All unit and integration tests.
- **Frequency:** Every commit.
- **Pass Criteria:** 100% pass rate.

#### 10.21.4 Continuous Integration

- **Platform:** GitHub Actions or GitLab CI.
- **Pipeline:**
  1. Lint (flake8, clang-tidy).
  2. Unit tests.
  3. Integration tests (with STM32 emulator or hardware-in-loop).
  4. Build artifacts (firmware .hex, Python package).

#### 10.21.5 Nightly Testing

- **Extended Tests:**
  - Stress tests.
  - Long-duration tests.
  - Performance benchmarks.

#### 10.21.6 Result Archival

- **Storage:** Cloud storage (e.g., AWS S3) or on-premise server.
- **Retention:** 1 year minimum.
- **Metadata:** Commit hash, date, environment.

***

### 10.22 Test Case Catalogue

| Test ID | Objective | Related Req | Equipment | Setup | Procedure | Expected Result | Pass Criteria |
|---------|-----------|-------------|-----------|-------|-----------|-----------------|---------------|
| TC-001 | Verify voltage range 0–3.3 V | HR-001 | DMM | Probe DAC/ADC pins | Measure min/max voltages | 0–3.3 V | ±2% of nominal |
| TC-002 | Verify absolute max < 5 V | HR-002 | DMM | Apply 5 V to ADC input | Measure clamped voltage | < 5 V | < 5 V absolute |
| TC-003 | Verify current limiting ≤ 10 mA | HR-003 | DMM (current mode) | Apply 5 V via 1 kΩ | Measure current | ≤ 10 mA | ≤ 10 mA |
| TC-004 | Verify ADC sampling ≥ 100 kSPS | HR-004 | Oscilloscope | Configure 100 kSPS | Measure sample period | ≥ 100 kSPS | ±5% |
| TC-005 | Verify DAC update ≥ 50 kSPS | HR-005 | Oscilloscope | Configure 50 kSPS sine | Measure frequency | ≥ 50 kSPS | ±5% |
| TC-010 | Verify test configuration | SR-001 | PC | Run CLI with config | Test starts | Config applied | No errors |
| TC-011 | Verify waveform generation | SR-002 | Oscilloscope | Configure sine/ramp | Measure output | Waveform correct | ±5% amplitude |
| TC-012 | Verify ADC acquisition | SR-003 | PC | Capture 10k samples | Buffer filled | 10k samples | No loss |
| TC-013 | Verify UART communication | SR-004 | PC + STM32 | Send/receive packets | ACKs received | No CRC errors | 100% success |
| TC-020 | Verify histogram analysis | SR-005 | PC | Run ramp test | DNL/INL plots | Plots generated | DNL/INL reasonable |
| TC-021 | Verify FFT analysis | SR-006 | PC | Run sine test | FFT/THD/SNR | Metrics computed | THD < 5%, SNR > 50 dB |
| TC-022 | Verify data logging | SR-007 | PC | Check output files | CSV/HTML saved | Files present | Valid format |
| TC-030 | Verify sampling rate range | SR-008 | Oscilloscope | Test 1, 10, 100, 200 kSPS | Measure rates | Within ±5% | All pass |
| TC-031 | Verify buffer size range | SR-009 | PC | Test 1k, 10k, 50k | No overflow | All samples captured | Pass |
| TC-032 | Verify UART throughput | SR-010 | PC (time) | 50k samples at 921600 | Time transfer | < 10 s | Pass |
| TC-033 | Verify end-to-end latency | SR-011 | PC (time) | Full test (10k samples) | Time start to report | < 60 s | Pass |
| TC-040 | Verify error recovery | SR-012 | PC | Induce UART timeout | Recovery | Graceful abort | User notified |
| TC-041 | Verify CLI usability | SR-013 | PC | Run `--help` | Help displayed | Clear messages | User can operate |
| TC-042 | Verify maintainability | SR-014 | Inspection | Check docs coverage | > 80% functions | Pass |
| TC-043 | Verify extensibility | SR-015 | PC | Add new test profile | New test runs | No code change | Pass |

***

This completes Chapter 10: Verification, Validation, Testing, and Calibration.