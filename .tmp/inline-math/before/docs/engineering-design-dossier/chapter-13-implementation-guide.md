# 13. Implementation Guide

This chapter provides a complete, step-by-step implementation manual for the μATE-STM system. Following this guide, an engineer with basic embedded systems and Python experience can reproduce the instrument from scratch. The implementation follows the incremental, verification-driven philosophy established in Chapters 1–12, with each stage validated before proceeding to the next.

***

## 13.1 Implementation Philosophy

### 13.1.1 Implementation Objectives

The primary objectives of implementation are:

1. **Functional Correctness:** The system must meet all design requirements (Chapter 5).
2. **Reproducibility:** Another engineer must be able to replicate the build using only this document.
3. **Incremental Verification:** Each subsystem is tested immediately after implementation to isolate faults.
4. **Risk Reduction:** High-risk components (ADC, communication) are implemented early to allow time for debugging.

### 13.1.2 Incremental Development Philosophy

The project is divided into stages to:

- **Limit Scope:** Each stage focuses on one subsystem (e.g., UART, ADC).
- **Enable Early Testing:** Firmware can be tested before hardware is complete (e.g., UART loopback).
- **Reduce Debugging Complexity:** If a fault appears, it must be in the most recently added code/hardware.

### 13.1.3 Verification After Every Stage

Every stage concludes with a verification checkpoint:

- **Hardware:** Measure voltages, continuity.
- **Firmware:** Use LED blink, UART print.
- **Host:** Run unit tests, plot data.

This aligns with the Verification Plan (Chapter 10) and ensures that no stage is considered complete until tested.

### 13.1.4 Recommended Development Workflow

1. **Read:** Understand the relevant design chapter (e.g., Chapter 8 for hardware).
2. **Implement:** Build the subsystem (hardware, firmware, or software).
3. **Test:** Run the corresponding verification procedure (Chapter 10).
4. **Document:** Update logs, commit code, note any deviations.
5. **Proceed:** Move to the next stage only after verification passes.

***

## 13.2 Development Environment

### 13.2.1 Operating System

- **Recommended:** Windows 10/11 or Ubuntu 20.04+.
- **Rationale:** Both STM32CubeIDE and Python tools are cross-platform.

### 13.2.2 Version Control (Git)

- **Purpose:** Track code changes, enable rollback, facilitate collaboration.
- **Setup:** Install Git from https://git-scm.com.
- **Configuration:**
  ```bash
  git config --global user.name "Your Name"
  git config --global user.email "your.email@example.com"
  ```

### 13.2.3 Repository Organization

The repository should be structured as follows (detailed in Section 13.3):

- **docs:** Documentation (this report, datasheets).
- **firmware:** STM32CubeIDE project, source code.
- **hardware:** Schematics, BOM, layout (if applicable).
- **python:** Host software modules.
- **scripts:** Build, test, and deployment scripts.
- **configs:** Configuration files (JSON, YAML).
- **data:** Raw measurement data, test results.
- **tests:** Unit tests, integration tests.

### 13.2.4 Python Version and Virtual Environments

- **Python Version:** 3.9 or later (required for `scipy`, `numpy` compatibility).
- **Virtual Environment:** Isolate dependencies.
  ```bash
  python -m venv venv
  source venv/bin/activate  # Linux/macOS
  venv\Scripts\activate     # Windows
  ```
- **Dependencies:** Install from `requirements.txt`:
  ```
  numpy>=1.21
  scipy>=1.7
  matplotlib>=3.4
  pyserial>=3.5
  ```

### 13.2.5 STM32CubeIDE

- **Purpose:** Integrated development environment for STM32 firmware.
- **Download:** https://www.st.com/en/development-tools/stm32cubeide.html.
- **Features:** Includes STM32CubeMX for peripheral configuration.

### 13.2.6 STM32CubeMX

- **Purpose:** Graphical tool for MCU configuration and code generation.
- **Usage:** Configure clocks, GPIO, UART, ADC, DAC, DMA; generate initialization code.

### 13.2.7 Required Python Packages

| Package | Purpose |
|---------|---------|
| `numpy` | Numerical arrays, FFT, statistics |
| `scipy` | Signal processing, window functions |
| `matplotlib` | Plotting (time-domain, FFT, histograms) |
| `pyserial` | UART communication with STM32 |
| `json` | Configuration file parsing |
| `unittest` | Unit testing framework |

### 13.2.8 Documentation Tools

- **LaTeX:** For report writing (e.g., TeX Live, Overleaf).
- **Draw.io:** For diagrams (hardware architecture, flowcharts).
- **Markdown:** For README files, quick notes.

### 13.2.9 Recommended Editors

- **VS Code:** Python, Markdown, Git integration.
- **STM32CubeIDE:** Firmware development.

### 13.2.10 Debugging Tools

- **ST-Link/V2:** Hardware debugger/programmer (often onboard Nucleo).
- **Logic Analyzer:** Optional (e.g., Saleae, DSView) for UART/SPI timing.
- **Oscilloscope:** For analog signal verification (Chapter 10).

***

## 13.3 Repository Structure

```
μATE-STM/
├── docs/                    # Documentation
│   ├── datasheets/          # MCU, ADC, DAC, passive components
│   ├── reports/             # Draft chapters, final report
│   └── diagrams/            # Block diagrams, schematics
├── firmware/                # STM32 firmware
│   ├── STM32CubeMX/         # .ioc configuration file
│   ├── Src/                 # C source files
│   ├── Inc/                 # Header files
│   └── Debug/               # Build output
├── hardware/                # Hardware design
│   ├── schematics/          # PDF, source files
│   ├── bom/                 # Bill of Materials (CSV)
│   └── gerber/              # PCB files (if applicable)
├── python/                  # Host software
│   ├── acquisition.py       # UART communication, data capture
│   ├── parser.py            # Binary packet parser
│   ├── signal_processing.py # FFT, histogram, DNL/INL
│   ├── adc_analysis.py      # DNL, INL, ENOB calculation
│   ├── report_generator.py  # PDF/HTML report generation
│   └── config.py            # Configuration management
├── scripts/                 # Automation scripts
│   ├── build_firmware.sh    # Firmware build script
│   ├── run_tests.sh         # Run unit/integration tests
│   └── deploy.sh            # Deployment to host
├── configs/                 # Configuration files
│   ├── acquisition.json     # Sampling rate, buffer size
│   ├── calibration.json     # Offset, gain correction
│   └── test_plans.json      # Verification test parameters
├── data/                    # Measurement data
│   ├── raw/                 # Raw ADC/DAC samples
│   ├── processed/           # FFT, histogram results
│   └── test_results/        # Verification test logs
├── tests/                   # Test suites
│   ├── unit/                # Unit tests (parser, analysis)
│   ├── integration/         # Integration tests (end-to-end)
│   └── verification/        # Chapter 10 test procedures
└── README.md                # Project overview, quickstart
```

**File Organization Conventions:**

- **Lowercase with underscores:** `adc_analysis.py`, not `AdcAnalysis.py`.
- **Descriptive names:** `signal_processing.py`, not `utils.py`.
- **Comments:** Every module starts with a docstring explaining purpose.

***

## 13.4 Hardware Preparation

### 13.4.1 STM32 Board

- **Component:** Nucleo-F401RE (or equivalent STM32F4 board).
- **Purpose:** MCU, ADC, DAC, UART, USB.
- **Preparation:**
  - Inspect for physical damage.
  - Verify USB connector is secure.
  - Check that ST-Link drivers are installed (Windows: Device Manager).
- **Verification:**
  - Connect via USB; LED should blink (default firmware).
  - Program a simple LED blink test (Section 13.9).

### 13.4.2 Breadboard

- **Component:** Standard solderless breadboard (400–800 points).
- **Purpose:** Prototype analog front-end, passive components.
- **Preparation:**
  - Inspect for broken clips, debris.
  - Verify power rails are continuous (multimeter continuity test).
- **Verification:**
  - Insert jumper wire; measure continuity across rows.

### 13.4.3 Jumper Wires

- **Component:** Male-to-male, male-to-female jumper wires.
- **Purpose:** Connect STM32 to breadboard, components.
- **Preparation:**
  - Inspect for broken insulation, loose connections.
  - Organize by color (red = 3.3V, black = GND, etc.).
- **Verification:**
  - Test continuity of each wire (multimeter).

### 13.4.4 USB Cable

- **Component:** USB-A to Micro-USB (data-capable, not charging-only).
- **Purpose:** Power and UART communication.
- **Preparation:**
  - Verify cable is not damaged.
  - Test with known-working device.
- **Verification:**
  - Connect to STM32; check for COM port enumeration.

### 13.4.5 Passive Components

- **Resistors:**
  - 1 kΩ (×10), 10 kΩ (×10), 100 kΩ (×2).
  - 1% tolerance, 1/4 W.
  - **Verification:** Measure resistance with multimeter (expect ±1%).
- **Capacitors:**
  - 100 nF (×10), 10 µF (×2).
  - Ceramic (X7R), 16 V rating.
  - **Verification:** Visual inspection; capacitance meter (if available).

### 13.4.6 Optional Equipment

- **Multimeter:** For voltage, resistance, continuity.
- **Oscilloscope:** For analog signal verification.
- **Logic Analyzer:** For UART timing analysis.
- **Function Generator:** For DAC/ADC testing (can be emulated with DAC).

***

## 13.5 Firmware Project Creation

### 13.5.1 Creating a New STM32CubeMX Project

1. **Open STM32CubeMX.**
2. **File → New Project.**
3. **Select MCU:** Search for `STM32F401RE`; select `STM32F401RETx`.
4. **Project Name:** `μATE-STM-Firmware`.
5. **Toolchain/IDE:** `STM32CubeIDE`.
6. **Code Generator:**
   - **Check:** "Generate peripheral initialization as a pair of '.c/.h' files per peripheral".
   - **Uncheck:** "Delete previously generated files".

### 13.5.2 Clock Configuration

1. **Go to `Clock Configuration` tab.**
2. **HSE (High-Speed External):** Select `Crystal/Ceramic Resonator`.
3. **PLL Settings:**
   - **PLL M:** 8 (HSE = 8 MHz).
   - **PLL N:** 336.
   - **PLL P:** 4.
   - **System Clock:** 168 MHz (auto-calculated).
4. **Verify:** No warnings (red indicators).

**Rationale:** 168 MHz provides sufficient performance for ADC/DAC control and UART.

### 13.5.3 GPIO Configuration

1. **Pinout View:**
   - **PC13:** GPIO_Output (User LED).
   - **PA0:** ADC1_IN0 (ADC input).
   - **PA4:** DAC1_OUT1 (DAC output).
   - **PA2:** USART2_TX.
   - **PA3:** USART2_RX.
2. **GPIO Settings:**
   - **PC13:** Output Push-Pull, Pull-up, High speed.

**Rationale:** Default GPIO settings are sufficient; high speed ensures fast switching.

### 13.5.4 UART Configuration

1. **Connectivity → USART2.**
2. **Mode:** Asynchronous.
3. **Parameters:**
   - **Baud Rate:** 921600.
   - **Word Length:** 8.
   - **Stop Bits:** 1.
   - **Parity:** None.
4. **NVIC Settings:**
   - **Enable USART2 global interrupt.**
   - **Preemption Priority:** 1.

**Rationale:** 921600 baud provides ~92 kB/s throughput, sufficient for 50 kSPS 16-bit data.

### 13.5.5 ADC Configuration

1. **Analog → ADC1.**
2. **Parameters:**
   - **Resolution:** 12 Bits.
   - **Data Alignment:** Right.
   - **Scan Conversion Mode:** Disabled (single channel).
   - **Continuous Conversion Mode:** Disabled (triggered).
   - **External Trigger Conversion Source:** Timer 2 (configured later).
   - **External Trigger Conversion Edge:** Rising Edge.
   - **Sampling Time:** 15 Cycles (minimum for low source impedance).
3. **DMA Settings:**
   - **Add DMA Request:** ADC1.
   - **DMA Stream:** DMA2 Stream 0.
   - **Direction:** Peripheral to Memory.
   - **Data Width:** Word (32-bit).
   - **Mode:** Circular.

**Rationale:** Timer-triggered ADC ensures precise sampling intervals; DMA minimizes CPU overhead.

### 13.5.6 DAC Configuration

1. **Analog → DAC1.**
2. **Parameters:**
   - **Output Buffer:** Enable (reduces output impedance).
   - **Trigger:** Timer 2 (same as ADC).
   - **Data Alignment:** Right.
   - **DMA:** Enable (DMA1 Stream 5).

**Rationale:** Synchronized DAC/ADC via Timer 2 enables closed-loop testing.

### 13.5.7 Timer Configuration

1. **Timers → TIM2.**
2. **Parameters:**
   - **Prescaler:** 0 (no division).
   - **Counter Mode:** Up.
   - **Counter Period (ARR):** 839 (for 100 kSPS at 84 MHz).
   - **Auto-Reload Preload:** Enable.
3. **DMA Settings:**
   - **Add DMA Request:** DAC1.

**Rationale:** Timer 2 clocked at 84 MHz (APB1); ARR = 839 gives 100 kHz update rate.

### 13.5.8 Interrupt Configuration

1. **System Core → NVIC.**
2. **Enable:**
   - **USART2 global interrupt.**
   - **DMA2 Stream 0 global interrupt (for ADC).**
   - **DMA1 Stream 5 global interrupt (for DAC).**

**Rationale:** Interrupts signal completion of UART reception, DMA buffer transfers.

### 13.5.9 Code Generation

1. **Project Manager → Generate Code.**
2. **Open in STM32CubeIDE.**

***

## 13.6 Firmware Architecture Implementation

### 13.6.1 Implementation Order

Implement modules in the following order to minimize dependencies:

1. **System Initialization:** Clocks, GPIO (auto-generated).
2. **UART:** Basic transmit/receive.
3. **Command Parser:** Interpret UART commands.
4. **ADC:** Single conversion, then DMA.
5. **DAC:** Single conversion, then DMA.
6. **Timer:** Trigger ADC/DAC.
7. **Acquisition Controller:** Coordinate ADC/DMA/UART.
8. **Calibration Module:** Apply offset/gain correction.

### 13.6.2 System Initialization

- **Auto-Generated:** `SystemClock_Config()`, `MX_GPIO_Init()`, `MX_USART2_UART_Init()`, etc.
- **Verification:** LED blink test (toggle PC13 in `main()` loop).

### 13.6.3 UART Implementation

- **Transmit:** `HAL_UART_Transmit(&huart2, data, len, timeout)`.
- **Receive:** `HAL_UART_Receive_IT(&huart2, &rx_byte, 1)` (interrupt-driven).
- **Verification:** Echo received bytes back; test with host terminal.

### 13.6.4 Command Parser

- **Structure:**
  - **State Machine:** IDLE → HEADER → CMD → PAYLOAD → CRC.
  - **Commands:** `START_ACQ`, `STOP_ACQ`, `READ_ADC`, `WRITE_DAC`.
- **Verification:** Send known commands; verify actions (e.g., LED toggle).

### 13.6.5 ADC Implementation

- **Single Conversion:**
  ```c
  HAL_ADC_Start(&hadc1);
  HAL_ADC_PollForConversion(&hadc1, timeout);
  uint32_t adc_value = HAL_ADC_GetValue(&hadc1);
  ```
- **DMA (Continuous):**
  ```c
  HAL_ADC_Start_DMA(&hadc1, &adc_buffer, BUFFER_SIZE);
  ```
- **Verification:** Capture ADC values; compare with multimeter.

### 13.6.6 DAC Implementation

- **Single Conversion:**
  ```c
  HAL_DAC_SetValue(&hdac1, DAC_CHANNEL_1, DAC_ALIGN_12B_R, value);
  HAL_DAC_Start(&hdac1, DAC_CHANNEL_1);
  ```
- **DMA (Waveform):**
  ```c
  HAL_DAC_Start_DMA(&hdac1, DAC_CHANNEL_1, &waveform, BUFFER_SIZE, DAC_ALIGN_12B_R);
  ```
- **Verification:** Measure output with oscilloscope/multimeter.

### 13.6.7 DMA Implementation

- **ADC DMA:** Circular mode; interrupt on half/full transfer.
- **DAC DMA:** Normal mode; reload waveform on completion.
- **Verification:** Check buffer contents; verify no data loss.

### 13.6.8 Acquisition Controller

- **State Machine:**
  - **IDLE:** Wait for `START_ACQ`.
  - **ACQUIRING:** ADC/DAC running; DMA filling buffer.
  - **TRANSMITTING:** Send buffer via UART.
  - **COMPLETE:** Notify host.
- **Verification:** End-to-end acquisition test (Chapter 10, TC-020).

### 13.6.9 Calibration Module

- **Storage:** Flash or EEPROM (e.g., `uint16_t cal_offset, cal_gain`).
- **Application:**
  ```c
  int32_t corrected = (raw_adc - cal_offset) * cal_gain / 4096;
  ```
- **Verification:** Apply known voltage; verify corrected value.

***

## 13.7 Host Software Implementation

### 13.7.1 Project Structure

- **Modules:** `acquisition.py`, `parser.py`, `signal_processing.py`, `adc_analysis.py`, `report_generator.py`, `config.py`.
- **Entry Point:** `main.py` (CLI or GUI).

### 13.7.2 Acquisition Module

- **Function:** Open COM port, send commands, receive data.
- **Implementation:**
  - Use `serial.Serial(port, baudrate, timeout=1)`.
  - Send binary commands (Section 13.8).
  - Receive binary packets; parse with `parser.py`.
- **Verification:** Acquire known data (e.g., DC voltage); plot.

### 13.7.3 Parser Module

- **Function:** Decode binary packets.
- **Structure:**
  - **Header:** `0xAA 0x55`.
  - **Command:** 1 byte.
  - **Length:** 2 bytes.
  - **Payload:** N bytes.
  - **CRC:** 2 bytes (CRC-16-CCITT).
- **Verification:** Send known packets; verify parsed output.

### 13.7.4 Analysis Module

- **Functions:**
  - `compute_fft(samples, fs, window)`: FFT with windowing.
  - `compute_histogram(samples)`: Code density.
  - `compute_dnl_inl(histogram)`: DNL, INL.
  - `compute_thd_snr(fft)`: THD, SNR, ENOB.
- **Verification:** Use synthetic data (e.g., sine wave); compare with theoretical values.

### 13.7.5 Plotting Module

- **Functions:**
  - `plot_time_domain(samples)`.
  - `plot_fft(fft, fs)`.
  - `plot_histogram(histogram)`.
  - `plot_dnl_inl(dnl, inl)`.
- **Verification:** Visual inspection; compare with expected shapes.

### 13.7.6 Reporting Module

- **Function:** Generate PDF/HTML report with metrics, plots.
- **Implementation:** Use `matplotlib` for plots, `reportlab` or `weasyprint` for PDF.
- **Verification:** Generate report; check all sections are populated.

### 13.7.7 Configuration Management

- **Function:** Load/save settings (sampling rate, buffer size, calibration).
- **Implementation:** Use JSON files (`configs/acquisition.json`, `configs/calibration.json`).
- **Verification:** Modify config; verify software uses new values.

### 13.7.8 Testing Module

- **Unit Tests:** `unittest` for parser, analysis functions.
- **Integration Tests:** End-to-end acquisition with known input.
- **Verification:** Run `python -m unittest discover tests/`; all tests pass.

***

## 13.8 Communication Protocol Implementation

### 13.8.1 Packet Structure

| Field | Size (bytes) | Description |
|-------|--------------|-------------|
| Header | 2 | `0xAA 0x55` (sync) |
| Command | 1 | Command ID (e.g., `0x01` = START_ACQ) |
| Length | 2 | Payload length (little-endian) |
| Payload | N | Command-specific data |
| CRC | 2 | CRC-16-CCITT (little-endian) |

### 13.8.2 Framing

- **Host:** Construct packet; append CRC.
- **Firmware:** State machine waits for header, then reads length, payload, CRC.

### 13.8.3 CRC Calculation

- **Algorithm:** CRC-16-CCITT (polynomial `0x1021`, init `0xFFFF`).
- **Implementation:**
  - **Host:** Python `binascii.crc_hqx` or custom function.
  - **Firmware:** STM32 hardware CRC or software lookup table.

### 13.8.4 Parser

- **Firmware:**
  - **State Machine:**
    - **WAIT_HEADER:** Check for `0xAA 0x55`.
    - **READ_CMD:** Read command byte.
    - **READ_LENGTH:** Read 2 bytes.
    - **READ_PAYLOAD:** Read N bytes.
    - **READ_CRC:** Read 2 bytes; verify.
  - **Error Handling:** If CRC fails, discard packet; send NACK.

### 13.8.5 Acknowledgements

- **ACK:** `0xAA 0x55 0x80 0x00 0x00 <CRC>`.
- **NACK:** `0xAA 0x55 0x81 0x00 0x00 <CRC>`.

### 13.8.6 Timeout Handling

- **Firmware:** If no byte received within 10 ms, reset state to WAIT_HEADER.
- **Host:** If no response within 1 s, retry (max 3 times); then report error.

### 13.8.7 Error Recovery

- **Host:** On timeout/NACK:
  1. Retry command.
  2. If 3 retries fail, abort; report error.
- **Firmware:** On CRC error:
  1. Send NACK.
  2. Reset state to WAIT_HEADER.

***

## 13.9 Incremental Bring-Up

### 13.9.1 Bring-Up Sequence

Follow this exact order to minimize debugging complexity:

1. **Verify Board Powers Correctly:**
   - **Action:** Connect USB; measure 3.3V, 5V pins.
   - **Expected:** 3.3V ±5%, 5V ±5%.
   - **Common Failures:** No power → check USB cable, board fuse.

2. **Verify Clock:**
   - **Action:** Toggle GPIO at known frequency (e.g., 1 Hz).
   - **Expected:** LED blinks at 1 Hz.
   - **Common Failures:** Wrong clock → check `SystemClock_Config()`.

3. **Blink LED:**
   - **Action:** Toggle PC13 in `main()` loop.
   - **Expected:** Visible blink.
   - **Common Failures:** GPIO not configured → check `MX_GPIO_Init()`.

4. **Verify UART:**
   - **Action:** Send "Hello" via UART; receive on host terminal.
   - **Expected:** "Hello" appears.
   - **Common Failures:** Wrong baud rate → check `huart2.Init.BaudRate`.

5. **Receive Commands:**
   - **Action:** Send command from host; echo back.
   - **Expected:** Host receives echo.
   - **Common Failures:** Parser error → check state machine.

6. **Transmit Responses:**
   - **Action:** Send ACK/NACK.
   - **Expected:** Host receives ACK.
   - **Common Failures:** CRC mismatch → verify CRC algorithm.

7. **Verify ADC:**
   - **Action:** Single ADC conversion; send to host.
   - **Expected:** ADC code matches multimeter.
   - **Common Failures:** Wrong channel → check `ADC1_IN0`.

8. **Verify DAC:**
   - **Action:** Set DAC code; measure output.
   - **Expected:** Voltage matches code.
   - **Common Failures:** Output buffer disabled → check `DAC1_OUT1`.

9. **Verify DMA:**
   - **Action:** Continuous ADC/DAC with DMA.
   - **Expected:** No data loss; buffer fills correctly.
   - **Common Failures:** DMA not enabled → check `HAL_ADC_Start_DMA()`.

10. **Acquire First Samples:**
    - **Action:** Start acquisition; capture 1000 samples.
    - **Expected:** Host receives 1000 samples.
    - **Common Failures:** Buffer overflow → check UART throughput.

11. **Transfer Samples to Host:**
    - **Action:** Send buffer via UART.
    - **Expected:** All samples received.
    - **Common Failures:** Packet loss → check CRC, timeout.

12. **Analyse Samples:**
    - **Action:** Compute FFT, histogram.
    - **Expected:** Plots appear.
    - **Common Failures:** Wrong parsing → check `parser.py`.

13. **Generate First Report:**
    - **Action:** Generate PDF report.
    - **Expected:** Report contains all sections.
    - **Common Failures:** Missing data → check `report_generator.py`.

### 13.9.2 Why This Order Minimizes Debugging Complexity

- **Hardware First:** Power, clock, LED verify basic hardware.
- **Communication Next:** UART is independent of ADC/DAC; isolates communication issues.
- **Peripherals Last:** ADC/DAC depend on UART for debugging output.

***

## 13.10 Integration

### 13.10.1 Hardware-Firmware Integration

- **Verification:**
  - **ADC:** Apply known voltage; verify ADC code.
  - **DAC:** Set code; measure output voltage.
  - **UART:** Loopback test; verify data integrity.

### 13.10.2 Firmware-Host Integration

- **Verification:**
  - **Command/Response:** Send all commands; verify responses.
  - **Data Acquisition:** Acquire known signal; verify host receives correct data.

### 13.10.3 End-to-End Integration

- **Verification:**
  - **Full Workflow:** Acquire, analyse, report.
  - **Test Case:** TC-050 (Chapter 10).

***

## 13.11 Calibration Implementation

### 13.11.1 Storage

- **Firmware:** Store calibration constants in flash (e.g., `__attribute__((section(".calibration")))`).
- **Host:** Store in `configs/calibration.json`.

### 13.11.2 Loading

- **Firmware:** Load constants at startup; apply to ADC readings.
- **Host:** Load at startup; apply to received data.

### 13.11.3 Application

- **Firmware:**
  ```c
  int32_t corrected = (raw_adc - cal_offset) * cal_gain / 4096;
  ```
- **Host:**
  ```python
  corrected = (raw_adc - offset) * gain
  ```

### 13.11.4 Verification

- **Procedure:** Apply known voltage; verify corrected value matches.
- **Test Case:** TC-040 (Chapter 10).

***

## 13.12 Verification During Development

### 13.12.1 After Hardware Preparation

- **Test:** Measure all component values.
- **Expected:** Within tolerance.
- **Corrective Action:** Replace out-of-tolerance components.

### 13.12.2 After Firmware Module Implementation

- **Test:** Run unit test for module.
- **Expected:** Test passes.
- **Corrective Action:** Debug module; re-test.

### 13.12.3 After Host Module Implementation

- **Test:** Run unit test for module.
- **Expected:** Test passes.
- **Corrective Action:** Debug module; re-test.

### 13.12.4 After Integration

- **Test:** Run integration test (end-to-end).
- **Expected:** System meets requirements.
- **Corrective Action:** Debug integration issues; re-test.

***

## 13.13 Debugging Workflow

### 13.13.1 Hardware Debugging

1. **Visual Inspection:** Check for shorts, cold solder joints.
2. **Power:** Measure voltages at key points (3.3V, 5V).
3. **Continuity:** Check connections with multimeter.
4. **Signals:** Use oscilloscope to verify analog/digital signals.

### 13.13.2 Firmware Debugging

1. **LED Indicators:** Use LED to signal state (e.g., error, success).
2. **UART Print:** Send debug messages via UART.
3. **Breakpoints:** Use STM32CubeIDE debugger to step through code.
4. **Logic Analyzer:** Capture UART, SPI, I2C timing.

### 13.13.3 Communication Debugging

1. **Loopback Test:** Connect TX to RX; verify echo.
2. **Packet Capture:** Use host software to log raw bytes.
3. **CRC Verification:** Manually calculate CRC; compare with received.

### 13.13.4 Software Debugging

1. **Unit Tests:** Isolate module failures.
2. **Logging:** Add debug prints to host software.
3. **Debugger:** Use `pdb` (Python debugger) to step through code.

### 13.13.5 Recommended Order

1. **Hardware:** Verify power, clock, basic I/O.
2. **Firmware:** Verify UART, ADC, DAC independently.
3. **Communication:** Verify packet integrity.
4. **Host:** Verify parsing, analysis, plotting.
5. **Integration:** Verify end-to-end operation.

***

## 13.14 Milestones

### Milestone 1: Development Environment Setup

- **Objective:** All tools installed, repository created.
- **Prerequisites:** None.
- **Duration:** 1 week.
- **Deliverables:** Git repository, README, `requirements.txt`.
- **Verification:** Clone repository; install dependencies; run `python --version`.

### Milestone 2: Hardware Assembly

- **Objective:** Breadboard populated, components verified.
- **Prerequisites:** Milestone 1.
- **Duration:** 1 week.
- **Deliverables:** Assembled hardware, BOM, photos.
- **Verification:** Measure power, continuity.

### Milestone 3: Firmware Basic I/O

- **Objective:** LED blink, UART echo.
- **Prerequisites:** Milestone 2.
- **Duration:** 1 week.
- **Deliverables:** `main.c` with LED, UART.
- **Verification:** LED blinks; UART echo works.

### Milestone 4: Firmware Peripherals

- **Objective:** ADC, DAC, DMA operational.
- **Prerequisites:** Milestone 3.
- **Duration:** 2 weeks.
- **Deliverables:** `adc.c`, `dac.c`, `dma.c`.
- **Verification:** ADC reads correct voltage; DAC outputs correct voltage.

### Milestone 5: Host Basic Acquisition

- **Objective:** Acquire, plot ADC data.
- **Prerequisites:** Milestone 4.
- **Duration:** 1 week.
- **Deliverables:** `acquisition.py`, `parser.py`.
- **Verification:** Host plots ADC data correctly.

### Milestone 6: Host Analysis

- **Objective:** FFT, histogram, DNL/INL, THD/SNR.
- **Prerequisites:** Milestone 5.
- **Duration:** 2 weeks.
- **Deliverables:** `signal_processing.py`, `adc_analysis.py`.
- **Verification:** Analysis matches theoretical values.

### Milestone 7: Integration and Testing

- **Objective:** End-to-end system operational.
- **Prerequisites:** Milestone 6.
- **Duration:** 2 weeks.
- **Deliverables:** Integrated system, test results.
- **Verification:** All Chapter 10 test cases pass.

### Milestone 8: Documentation and Report

- **Objective:** Final report complete.
- **Prerequisites:** Milestone 7.
- **Duration:** 2 weeks.
- **Deliverables:** Final report, presentation.
- **Verification:** Report submitted; presentation delivered.

***

## 13.15 Risk Management During Implementation

### Risk 1: Hardware Damage

- **Cause:** Overvoltage, short circuit.
- **Probability:** Medium.
- **Impact:** High (board replacement needed).
- **Mitigation:** Use current-limited USB hub; inspect before powering.
- **Contingency:** Have spare board available.

### Risk 2: Firmware Bugs

- **Cause:** Logic errors, race conditions.
- **Probability:** High.
- **Impact:** Medium (debugging time).
- **Mitigation:** Incremental testing, unit tests.
- **Contingency:** Use debugger, logic analyzer.

### Risk 3: Communication Failures

- **Cause:** Baud rate mismatch, CRC errors.
- **Probability:** Medium.
- **Impact:** Medium (data loss).
- **Mitigation:** Verify baud rate; test CRC independently.
- **Contingency:** Lower baud rate for debugging.

### Risk 4: Time Overrun

- **Cause:** Underestimation, other commitments.
- **Probability:** High.
- **Impact:** High (missed deadline).
- **Mitigation:** Weekly milestones, buffer time.
- **Contingency:** Prioritize critical features; defer non-essential.

***

## 13.16 Build Checklist

### Hardware

- [ ] STM32 board inspected, powered.
- [ ] Breadboard continuity verified.
- [ ] Jumper wires tested.
- [ ] Resistors measured (1 kΩ, 10 kΩ).
- [ ] Capacitors inspected.
- [ ] RC filter assembled.
- [ ] Power rails verified (3.3V, GND).

### Firmware

- [ ] STM32CubeMX project created.
- [ ] Clock configured (168 MHz).
- [ ] GPIO (LED, ADC, DAC, UART) configured.
- [ ] UART (921600 baud) configured.
- [ ] ADC (12-bit, DMA) configured.
- [ ] DAC (12-bit, DMA) configured.
- [ ] Timer (100 kSPS) configured.
- [ ] Code generated, compiled without errors.
- [ ] LED blink test passed.
- [ ] UART echo test passed.
- [ ] ADC single conversion test passed.
- [ ] DAC single conversion test passed.
- [ ] DMA continuous acquisition test passed.

### Host Software

- [ ] Python virtual environment created.
- [ ] Dependencies installed (`requirements.txt`).
- [ ] `acquisition.py` implemented, tested.
- [ ] `parser.py` implemented, tested.
- [ ] `signal_processing.py` implemented, tested.
- [ ] `adc_analysis.py` implemented, tested.
- [ ] `report_generator.py` implemented, tested.
- [ ] `config.py` implemented, tested.
- [ ] Unit tests pass (`unittest`).
- [ ] Integration test passes (end-to-end).

### Integration

- [ ] Firmware uploads to board.
- [ ] Host connects to board.
- [ ] Commands sent/received.
- [ ] ADC data acquired, plotted.
- [ ] DAC waveform generated, measured.
- [ ] FFT, histogram, DNL/INL computed.
- [ ] Report generated.

***

## 13.17 Implementation Timeline

Assume a single engineering student working part-time (10–15 hours/week) alongside university coursework.

| Week | Milestone | Tasks | Deliverables |
|------|-----------|-------|--------------|
| 1 | Development Environment | Install tools, create repo, write README | Git repo, `requirements.txt` |
| 2 | Hardware Assembly | Purchase components, assemble breadboard | Assembled hardware, BOM |
| 3 | Firmware Basic I/O | STM32CubeMX, LED blink, UART echo | `main.c` with LED, UART |
| 4 | Firmware Peripherals | ADC, DAC, DMA, Timer | `adc.c`, `dac.c`, `dma.c` |
| 5 | Host Basic Acquisition | `acquisition.py`, `parser.py` | Data acquisition working |
| 6 | Host Analysis | `signal_processing.py`, `adc_analysis.py` | FFT, histogram, DNL/INL |
| 7 | Integration | End-to-end testing, debugging | Integrated system |
| 8 | Verification | Run Chapter 10 test cases | Test results |
| 9 | Documentation | Write report chapters | Draft report |
| 10 | Finalization | Polish report, prepare presentation | Final report, slides |

**Buffer:** Add 2 weeks buffer for unexpected delays (total 12 weeks).

***

## 13.18 Lessons Learned

### 13.18.1 Good Engineering Practices

1. **Incremental Development:** Implement one module at a time; test immediately.
2. **Version Control:** Commit frequently; use descriptive messages.
3. **Documentation:** Write comments, update README as you go.
4. **Testing:** Write unit tests before implementing modules (TDD).
5. **Debugging:** Use LED, UART prints, debugger systematically.
6. **Backup:** Regularly backup code, data (e.g., GitHub, cloud).

### 13.18.2 Common Pitfalls to Avoid

1. **Skipping Verification:** Never proceed to next stage without testing.
2. **Over-Engineering:** Start simple; add complexity only when needed.
3. **Ignoring Datasheets:** Always consult MCU, component datasheets.
4. **Poor Grounding:** Ensure solid ground connections; avoid ground loops.
5. **Rushing:** Allocate buffer time for debugging, documentation.

***
