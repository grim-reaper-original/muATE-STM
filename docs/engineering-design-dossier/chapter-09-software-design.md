# 9. Software Design

This chapter defines the complete software architecture for the μATE-STM system, including both STM32F4 embedded firmware and host PC Python application. It is written as a professional Software Design Document (SDD) suitable for Preliminary Design Review (PDR) and Critical Design Review (CDR).

***

## 9.1 Software Design Philosophy

### 9.1.1 Software Objectives

The software architecture targets:

- **Functional completeness**: Support all test modes (ramp histogram, sine FFT, loopback) defined in Chapter 6.
- **Real-time performance**: Firmware must handle ADC/DAC timing deterministically; host software must process data efficiently.
- **Educational clarity**: Code structure should be understandable to students learning embedded systems and data analysis.
- **Extensibility**: Architecture must support future features (additional test types, GUI, remote operation).

### 9.1.2 Modularity Philosophy

The software is decomposed into **loosely coupled, highly cohesive modules**:

- **Firmware layers**: HAL/drivers, middleware (DMA, UART), services (waveform generation, acquisition), application (test manager).
- **Host modules**: Serial communication, data parsing, signal processing, visualization, reporting.

**Rationale:**

- Enables parallel development (e.g., one engineer works on FFT, another on UART protocol).
- Facilitates unit testing and debugging.
- Supports future replacement or enhancement of individual modules without system-wide changes.

### 9.1.3 Maintainability Philosophy

- **Clear naming conventions** (see Section 9.16).
- **Comprehensive inline documentation** for complex algorithms.
- **Centralized configuration** (JSON/YAML for host, header files for firmware).
- **Version control** with meaningful commit messages and branch strategy.

### 9.1.4 Portability Philosophy

- **Firmware**:
  - Use STM32 HAL/LL for peripheral access (not direct register manipulation).
  - Avoid hardware-specific assumptions beyond STM32F446/447 family.
- **Host**:
  - Pure Python 3.10+ with standard libraries (`numpy`, `scipy`, `matplotlib`, `pyserial`).
  - Cross-platform (Windows, Linux, macOS).

### 9.1.5 Scalability Philosophy

- **Firmware**:
  - Modular test profiles allow adding new waveforms without modifying core acquisition logic.
  - Buffer sizes and sampling rates are parameterized.
- **Host**:
  - Plugin-style architecture for analysis modules (e.g., add ENOB calculation without changing core).
  - Configuration-driven test sequences.

### 9.1.6 Testability Philosophy

- **Firmware**:
  - Self-test modes (e.g., internal loopback, known-pattern generation).
  - Logging of critical events (UART errors, DMA faults).
- **Host**:
  - Unit tests for analysis algorithms (histogram, FFT).
  - Synthetic data generation for offline testing.
  - Mock serial interface for integration testing.

### 9.1.7 Reliability Philosophy

- **Defensive programming**:
  - Validate all inputs (configuration, packets).
  - Use timeouts and retries for communication.
- **Graceful degradation**:
  - On error, return to safe state rather than crashing.
  - Log errors for post-mortem analysis.

### 9.1.8 Coding Philosophy

- **Firmware**:
  - C99 standard.
  - Minimal use of global variables.
  - ISR (interrupt service routine) minimalism: set flags, defer processing to main loop.
- **Host**:
  - Pythonic style (PEP 8).
  - Type hints for function signatures.
  - Docstrings for all public functions.

### 9.1.9 Error Handling Philosophy

- **Firmware**:
  - Error codes returned from functions.
  - Centralized error handler that logs and enters safe state.
- **Host**:
  - Exceptions for unrecoverable errors.
  - Try-except blocks around I/O and numerical operations.
  - User-friendly error messages.

### 9.1.10 Documentation Philosophy

- **Firmware**:
  - Doxygen-style comments for all public APIs.
  - Architecture overview in README.
- **Host**:
  - Sphinx documentation for public modules.
  - Inline comments for complex algorithms.

### 9.1.11 Rationale for Firmware/Host Split

The architecture divides responsibilities based on **real-time requirements** and **computational complexity**:

- **Firmware (STM32)**:
  - Handles time-critical tasks: DAC waveform generation, ADC sampling, DMA management.
  - Must be deterministic and low-latency.
  - Limited computational resources (CPU, memory).
- **Host (PC)**:
  - Handles computationally intensive tasks: FFT, histogram analysis, plotting, report generation.
  - No real-time constraints.
  - Abundant resources (CPU, memory, storage).

**Alternative Considered:**

- All processing on STM32 with results-only transfer.
- **Rejected because**:
  - STM32 lacks resources for large FFTs and complex analysis.
  - Would complicate firmware and reduce sampling performance.
  - Defeats educational goal of Python-based data analysis.

***

## 9.2 Software Requirements

This section defines software requirements with unique IDs for traceability.

| ID | Requirement | Category | Description | Acceptance Criteria |
|----|-------------|----------|-------------|---------------------|
| SR-001 | Test Configuration | Functional | Host shall allow user to specify test type, sample count, sampling rate, DAC parameters. | User can configure and start a test via CLI or config file. |
| SR-002 | Waveform Generation | Functional | Firmware shall generate ramp and sine waveforms via DAC. | DAC output measured on oscilloscope matches expected waveform. |
| SR-003 | ADC Acquisition | Functional | Firmware shall capture ADC samples using DMA. | ADC buffer filled with expected number of samples at configured rate. |
| SR-004 | UART Communication | Functional | Firmware and host shall exchange commands and data via UART. | Commands acknowledged; data received without corruption. |
| SR-005 | Histogram Analysis | Functional | Host shall compute code histogram and DNL/INL. | DNL/INL plots generated for synthetic and real data. |
| SR-006 | FFT Analysis | Functional | Host shall compute FFT and THD/SNR metrics. | FFT magnitude plot and THD/SNR values generated. |
| SR-007 | Data Logging | Functional | Host shall save raw data, metrics, and reports to disk. | Files saved in specified directory structure. |
| SR-008 | Sampling Rate | Performance | Firmware shall support sampling rates from 1 kSPS to 200 kSPS. | Measured sampling rate within ±5% of configured value. |
| SR-009 | Buffer Size | Performance | Firmware shall support buffer sizes from 1k to 50k samples. | No buffer overflow or sample loss. |
| SR-010 | UART Throughput | Performance | Host shall receive 50k samples in < 10 seconds at 921,600 baud. | Measured transfer time < 10 s. |
| SR-011 | Latency | Timing | End-to-end test (acquisition + analysis + report) shall complete in < 60 s. | Measured latency < 60 s for 10k samples. |
| SR-012 | Error Recovery | Reliability | System shall recover from UART timeout or invalid packet. | Test resumes or aborts gracefully with error message. |
| SR-013 | CLI Usability | Usability | Host shall provide clear CLI help and error messages. | `--help` displays usage; errors are descriptive. |
| SR-014 | Code Maintainability | Maintainability | All modules shall have documentation and unit tests. | Doxygen/Sphinx coverage > 80%; unit tests pass. |
| SR-015 | Extensibility | Extensibility | New test types shall be addable without modifying core modules. | New test profile added via config file. |

***

## 9.3 Overall Software Architecture

### 9.3.1 Architectural Overview

The software architecture is a **two-tier client-server model**:

- **Server (STM32 Firmware)**:
  - Real-time embedded system.
  - Manages hardware peripherals (ADC, DAC, DMA, UART).
  - Executes test sequences.
- **Client (Host PC Application)**:
  - Non-real-time application.
  - Provides user interface (CLI initially, GUI as future expansion).
  - Performs data analysis and visualization.

**Communication:**

- UART serial link (asynchronous, binary protocol with CRC16).
- Request-response pattern for commands.
- Streaming for data transfer.

### 9.3.2 Architectural Components

**Host Software:**

- **CLI/GUI**: User interaction.
- **Configuration Manager**: Loads/saves test parameters.
- **Serial Communication**: UART protocol implementation.
- **Data Acquisition**: Receives and buffers ADC samples.
- **Data Parser**: Decodes binary packets.
- **Signal Processing**: FFT, histogram, DNL/INL, THD/SNR.
- **Plotting**: Matplotlib-based visualization.
- **Report Generator**: CSV/HTML/PDF output.
- **Logging**: System and debug logs.

**Firmware:**

- **Startup**: Clock, peripheral initialization.
- **HAL/LL**: STM32 hardware abstraction.
- **Drivers**: ADC, DAC, DMA, UART.
- **Middleware**: Buffer management, timing.
- **Services**: Waveform generation, acquisition control.
- **Application**: Test manager, command handler.
- **Communication**: UART protocol stack.

### 9.3.3 Rationale for Architecture Selection

**Alternatives Considered:**

1. **Monolithic firmware** (all processing on STM32):
   - **Rejected**: Limited resources, complex firmware, no Python learning.
2. **Pure simulation** (no hardware):
   - **Rejected**: Loses real-world mixed-signal experience.
3. **Hybrid with external DSP**:
   - **Rejected**: Adds cost and complexity.

**Selected Architecture Advantages:**

- Leverages STM32 for real-time I/O.
- Leverages PC for complex analysis.
- Clear separation of concerns.
- Educational value (embedded + data science).

***

## 9.4 Firmware Architecture

The firmware is organized into **layers** to promote modularity and maintainability.

### 9.4.1 Startup Layer

**Responsibilities:**

- System clock configuration.
- Vector table initialization.
- Jump to main().

**Interfaces:**

- None (entry point).

**Dependencies:**

- CMSIS startup files.

**Failure Modes:**

- Clock misconfiguration → system hang.

### 9.4.2 HAL/LL Layer

**Responsibilities:**

- Provide hardware abstraction for peripherals.
- GPIO, RCC, ADC, DAC, DMA, UART initialization.

**Interfaces:**

- HAL/LL API (e.g., `HAL_ADC_Start()`, `HAL_DAC_SetValue()`).

**Dependencies:**

- STM32CubeF4 HAL library.

**Failure Modes:**

- Incorrect peripheral handle → undefined behavior.

### 9.4.3 Drivers Layer

**Responsibilities:**

- Encapsulate peripheral-specific logic.
- ADC driver: configure channels, sample time, trigger.
- DAC driver: configure output, trigger source.
- DMA driver: configure stream, circular mode.
- UART driver: configure baud, interrupts.

**Interfaces:**

- `ADC_Driver_Init()`, `DAC_Driver_SetWaveform()`, etc.

**Dependencies:**

- HAL/LL layer.

**Failure Modes:**

- DMA misconfiguration → data loss.

### 9.4.4 Middleware Layer

**Responsibilities:**

- Buffer management (circular buffers for ADC).
- Timing services (delays, timestamps).
- Error logging.

**Interfaces:**

- `Buffer_Init()`, `Buffer_Push()`, `Timer_Delay()`.

**Dependencies:**

- Drivers layer.

**Failure Modes:**

- Buffer overflow → data corruption.

### 9.4.5 Services Layer

**Responsibilities:**

- **Waveform Generation Service**:
  - Generate ramp, sine, DC levels.
  - Use lookup tables or formulas.
- **Acquisition Service**:
  - Configure ADC/DMA for test.
  - Start/stop acquisition.
- **Self-Test Service**:
  - Internal loopback tests.

**Interfaces:**

- `Waveform_Generate()`, `Acquisition_Start()`.

**Dependencies:**

- Drivers, middleware.

**Failure Modes:**

- Waveform distortion due to timer misconfiguration.

### 9.4.6 Application Layer

**Responsibilities:**

- **Test Manager**:
  - Orchestrate test sequence.
  - Parse commands from host.
  - Coordinate services.
- **Command Handler**:
  - Interpret host commands.
  - Validate parameters.
  - Send responses.

**Interfaces:**

- `Test_Manager_Run()`, `Command_Handler_Parse()`.

**Dependencies:**

- Services, communication.

**Failure Modes:**

- Invalid command → NACK response.

### 9.4.7 Communication Layer

**Responsibilities:**

- UART protocol implementation.
- Packet framing, CRC16.
- TX/RX state machines.

**Interfaces:**

- `Comm_Send()`, `Comm_Receive()`.

**Dependencies:**

- UART driver.

**Failure Modes:**

- CRC error → packet discarded.

***

## 9.5 Host Software Architecture

### 9.5.1 CLI/GUI Module

**Purpose:**  
Provide user interface for test configuration and control.

**Responsibilities:**

- Parse command-line arguments.
- Display help and error messages.
- (Future) GUI widgets for test control.

**Interfaces:**

- `argparse` for CLI.
- (Future) `tkinter` or `PyQt` for GUI.

**Dependencies:**

- Configuration Manager, Serial Communication.

**Inputs:**

- User command-line arguments.

**Outputs:**

- Test configuration, start/stop commands.

### 9.5.2 Configuration Manager

**Purpose:**  
Load and validate test parameters.

**Responsibilities:**

- Read JSON/YAML config files.
- Validate parameter ranges.
- Provide defaults.

**Interfaces:**

- `json` or `yaml` module.

**Dependencies:**

- None.

**Inputs:**

- Config file path.

**Outputs:**

- Validated configuration dictionary.

### 9.5.3 Serial Communication Module

**Purpose:**  
Implement UART protocol.

**Responsibilities:**

- Open/close serial port.
- Send commands.
- Receive data packets.
- Handle timeouts and retries.

**Interfaces:**

- `pyserial` library.

**Dependencies:**

- Configuration Manager.

**Inputs:**

- Commands to send.

**Outputs:**

- Received packets.

### 9.5.4 Data Acquisition Module

**Purpose:**  
Buffer incoming ADC samples.

**Responsibilities:**

- Call Serial Communication to receive data.
- Assemble packets into sample array.
- Detect end-of-data marker.

**Interfaces:**

- Serial Communication, Data Parser.

**Dependencies:**

- `numpy` for arrays.

**Inputs:**

- Raw bytes from UART.

**Outputs:**

- Numpy array of samples.

### 9.5.5 Data Parser Module

**Purpose:**  
Decode binary packets.

**Responsibilities:**

- Validate SYNC byte.
- Check length and CRC.
- Extract payload.

**Interfaces:**

- Serial Communication.

**Dependencies:**

- CRC16 implementation.

**Inputs:**

- Raw packet bytes.

**Outputs:**

- Parsed packet structure.

### 9.5.6 Signal Processing Module

**Purpose:**  
Compute metrics from samples.

**Responsibilities:**

- Histogram computation.
- DNL/INL calculation.
- FFT, THD, SNR.

**Interfaces:**

- `numpy`, `scipy.fft`.

**Dependencies:**

- Data Acquisition.

**Inputs:**

- Sample array.

**Outputs:**

- Histogram, DNL/INL arrays, FFT spectrum, metrics.

### 9.5.7 Plotting Module

**Purpose:**  
Generate visualizations.

**Responsibilities:**

- Time-domain plot.
- Histogram plot.
- DNL/INL plot.
- FFT magnitude plot.

**Interfaces:**

- `matplotlib.pyplot`.

**Dependencies:**

- Signal Processing.

**Inputs:**

- Metrics and samples.

**Outputs:**

- PNG/SVG files.

### 9.5.8 Report Generator Module

**Purpose:**  
Create test reports.

**Responsibilities:**

- Assemble metrics and plots.
- Generate CSV/HTML/PDF.

**Interfaces:**

- `csv`, `jinja2` (for HTML), `reportlab` (for PDF).

**Dependencies:**

- Signal Processing, Plotting.

**Inputs:**

- Metrics, plots, metadata.

**Outputs:**

- Report files.

### 9.5.9 Configuration Files Module

**Purpose:**  
Store default and user-defined parameters.

**Responsibilities:**

- Provide schema for config files.
- Load defaults if no file provided.

**Interfaces:**

- `json`.

**Dependencies:**

- None.

**Inputs:**

- File path.

**Outputs:**

- Configuration dictionary.

### 9.5.10 Logging Module

**Purpose:**  
Record system events.

**Responsibilities:**

- Log INFO, WARNING, ERROR messages.
- Timestamp entries.
- Write to file.

**Interfaces:**

- `logging` module.

**Dependencies:**

- None.

**Inputs:**

- Log messages.

**Outputs:**

- Log file entries.

***

## 9.6 Directory Structure

The project directory is organized as follows:

```
muate_stm32/
├── README.md
├── LICENSE
├── requirements.txt
├── firmware/
│   ├── Inc/
│   │   ├── main.h
│   │   ├── adc_driver.h
│   │   ├── dac_driver.h
│   │   ├── dma_driver.h
│   │   ├── uart_driver.h
│   │   ├── waveform_service.h
│   │   ├── acquisition_service.h
│   │   ├── test_manager.h
│   │   └── comm_protocol.h
│   ├── Src/
│   │   ├── main.c
│   │   ├── adc_driver.c
│   │   ├── dac_driver.c
│   │   ├── dma_driver.c
│   │   ├── uart_driver.c
│   │   ├── waveform_service.c
│   │   ├── acquisition_service.c
│   │   ├── test_manager.c
│   │   └── comm_protocol.c
│   ├── startup/
│   ├── STM32CubeMX/
│   └── .ioc
├── hardware/
│   ├── schematics/
│   ├── bom.csv
│   └── README.md
├── python/
│   ├── muate/
│   │   ├── __init__.py
│   │   ├── cli.py
│   │   ├── config_manager.py
│   │   ├── serial_comm.py
│   │   ├── data_acquisition.py
│   │   ├── data_parser.py
│   │   ├── signal_processing.py
│   │   ├── plotting.py
│   │   ├── report_generator.py
│   │   └── logging.py
│   ├── tests/
│   │   ├── test_histogram.py
│   │   ├── test_fft.py
│   │   └── test_serial.py
│   └── setup.py
├── analysis/
│   ├── synthetic_data.py
│   └── validation.py
├── plots/
│   └── (generated plots)
├── reports/
│   └── (generated reports)
├── configs/
│   ├── default.json
│   └── user_config.json
├── tests/
│   ├── firmware_tests/
│   └── host_tests/
├── docs/
│   ├── architecture.md
│   ├── api_reference.md
│   └── user_manual.md
├── scripts/
│   ├── run_ramp_test.py
│   └── run_sine_test.py
└── examples/
    ├── ramp_test_config.json
    └── sine_test_config.json
```

**Folder Purposes:**

- `firmware/`: STM32 C source and headers.
- `hardware/`: Schematics, BOM, assembly notes.
- `python/`: Host application source.
- `analysis/`: Offline analysis and validation scripts.
- `plots/`: Generated visualization outputs.
- `reports/`: Generated test reports.
- `configs/`: JSON configuration files.
- `tests/`: Unit and integration tests.
- `docs/`: Documentation (Markdown, Sphinx).
- `scripts/`: One-click test runners.
- `examples/`: Example configurations.

***

## 9.7 Module Specifications

### 9.7.1 CLI Module (`cli.py`)

**Objective:**  
Provide command-line interface for test execution.

**Inputs:**

- Command-line arguments (`--config`, `--port`, `--baud`).

**Outputs:**

- Test configuration passed to Configuration Manager.

**Algorithms:**

- Argument parsing using `argparse`.

**Data Structures:**

- `argparse.Namespace` object.

**Dependencies:**

- `argparse`, `config_manager`.

**Configuration Parameters:**

- Config file path, serial port, baud rate.

**Exceptions:**

- `ArgumentError` if invalid arguments.

**Logging:**

- Log CLI startup and arguments.

***

### 9.7.2 Signal Processing Module (`signal_processing.py`)

**Objective:**  
Compute histogram, DNL/INL, FFT, THD/SNR.

**Inputs:**

- Sample array (numpy).
- Sampling rate, test type.

**Outputs:**

- Histogram array, DNL/INL arrays.
- FFT magnitude, THD, SNR values.

**Algorithms:**

- Histogram: `numpy.histogram`.
- DNL/INL: See Chapter 10 (mathematical basis).
- FFT: `scipy.fft.fft`.
- THD/SNR: Harmonic extraction, power calculation.

**Data Structures:**

- Numpy arrays for samples, histograms, spectra.

**Dependencies:**

- `numpy`, `scipy`.

**Configuration Parameters:**

- FFT window type, number of harmonics.

**Exceptions:**

- `ValueError` if insufficient samples.

**Logging:**

- Log processing start/end times.

***

### 9.8 Data Structures

This section defines the core data structures used across firmware and host software. Each structure is described with purpose, fields, memory considerations, and lifecycle.

#### 9.8.1 Configuration Structures

**Firmware: `TestConfig_t`**

| Field | Type | Description | Range/Units |
|-------|------|-------------|-------------|
| `test_type` | `uint8_t` | Test profile identifier (0=Ramp, 1=Sine) | Enum |
| `sample_count` | `uint16_t` | Number of ADC samples to capture | 1000–50000 |
| `sampling_rate_idx` | `uint8_t` | Index into predefined rate table | 0–7 |
| `dac_amplitude_idx` | `uint8_t` | DAC amplitude setting index | 0–3 |
| `dac_frequency_idx` | `uint8_t` | DAC frequency setting index | 0–5 |
| `reserved` | `uint8_t[3]` | Alignment padding | N/A |

- **Memory Layout:** 12 bytes total (4-byte aligned).
- **Ownership:** Test Manager module.
- **Lifetime:** Persistent throughout test execution.
- **Validation:** Range checks on all indices during command parsing.

**Host: `TestConfig` (Python dataclass)**

```python
@dataclass
class TestConfig:
    test_type: str          # "ramp" or "sine"
    sample_count: int       # 1000–50000
    sampling_rate: int      # Hz
    dac_amplitude: float    # Volts
    dac_frequency: float    # Hz
    serial_port: str        # COM port
    baud_rate: int          # e.g., 921600
```

- **Serialization:** JSON for config files.
- **Validation:** Type and range checks in `config_manager.py`.

***

#### 9.8.2 Communication Packet Structures

**Firmware: `UART_Packet_t`**

| Field | Type | Description |
|-------|------|-------------|
| `sync` | `uint8_t` | SYNC byte (0xAA) |
| `length` | `uint8_t` | Payload length (0–254) |
| `cmd_resp` | `uint8_t` | Command or response code |
| `payload` | `uint8_t[254]` | Variable-length data |
| `crc16` | `uint16_t` | CRC over length, cmd_resp, payload |

- **Memory Layout:** Packed structure (no padding).
- **Ownership:** Communication Layer.
- **Lifetime:** Transient (stack-allocated during TX/RX).
- **Alignment:** 1-byte packing to match wire format.

**Host: `UARTPacket` (Python class)**

```python
@dataclass
class UARTPacket:
    sync: int           # 0xAA
    length: int         # 0–254
    cmd_resp: int       # Command/response code
    payload: bytes      # Variable-length
    crc16: int          # CRC value
```

- **Serialization:** `struct.pack/unpack` for binary encoding.
- **Validation:** CRC check, length consistency.

***

#### 9.8.3 ADC Buffer Structures

**Firmware: `ADC_Buffer_t`**

| Field | Type | Description |
|-------|------|-------------|
| `data` | `uint16_t[32768]` | Sample buffer (max 32k samples) |
| `count` | `uint16_t` | Actual number of samples captured |
| `overflow` | `uint8_t` | Overflow flag |
| `reserved` | `uint8_t` | Padding |

- **Memory Usage:** 64 kB + 4 bytes ≈ 65.5 kB.
- **Placement:** Placed in `.data` or `.bss` section (SRAM).
- **Alignment:** 4-byte aligned for DMA efficiency.
- **Ownership:** Acquisition Service.
- **Lifetime:** Reused across tests; cleared before each acquisition.

**Host: Numpy Array**

- **Type:** `numpy.ndarray` of `uint16`.
- **Shape:** `(sample_count,)`.
- **Ownership:** Data Acquisition Module.
- **Lifetime:** Lives until processed and saved.

***

#### 9.8.4 DMA Buffer Descriptors

**Firmware: `DMA_Desc_t`**

| Field | Type | Description |
|-------|------|-------------|
| `buffer_ptr` | `void*` | Pointer to ADC buffer |
| `size` | `uint16_t` | Buffer size in samples |
| `head` | `uint16_t` | Current write index (for circular mode) |
| `flags` | `uint8_t` | Status flags (complete, half-complete) |

- **Usage:** Manages double-buffering or circular DMA.
- **Ownership:** DMA Driver.

***

#### 9.8.5 Waveform Lookup Tables

**Firmware: `Waveform_LUT_t`**

| Field | Type | Description |
|-------|------|-------------|
| `table` | `uint16_t[256]` | 8-bit resolution sine/ramp table |
| `size` | `uint16_t` | Table size (256) |
| `type` | `uint8_t` | Waveform type (sine, ramp) |

- **Memory:** 512 bytes + metadata.
- **Placement:** Flash (`const` qualifier).
- **Usage:** DAC waveform generation via timer-triggered indexing.

***

#### 9.8.6 FFT Results Structure

**Host: `FFTResult` (Python dataclass)**

```python
@dataclass
class FFTResult:
    frequencies: np.ndarray   # Hz
    magnitudes: np.ndarray    # dB or linear
    fundamental_freq: float   # Hz
    fundamental_mag: float    # dB
    harmonics: List[float]    # Harmonic frequencies
    harmonic_mags: List[float] # Harmonic magnitudes
    thd: float                # % or dB
    snr: float                # dB
```

- **Ownership:** Signal Processing Module.
- **Lifetime:** Lives until report generation.

***

#### 9.8.7 Report Structure

**Host: `TestReport` (Python dataclass)**

```python
@dataclass
class TestReport:
    timestamp: datetime
    config: TestConfig
    metrics: dict           # DNL_max, INL_max, THD, SNR, etc.
    plot_files: List[str]   # Paths to PNG files
    raw_data_file: str      # Path to CSV
    status: str             # "PASS", "FAIL", "WARNING"
```

- **Serialization:** JSON metadata + separate CSV/HTML/PDF.

***

#### 9.8.8 Calibration Data Structure

**Host: `CalibrationData` (Python dataclass)**

```python
@dataclass
class CalibrationData:
    adc_offset: float       # LSB
    adc_gain: float         # LSB/V
    dac_offset: float       # LSB
    dac_gain: float         # LSB/V
    vref_actual: float      # Volts
    timestamp: datetime
```

- **Storage:** JSON file (`calibration.json`).
- **Usage:** Applied to raw ADC/DAC codes for voltage scaling.

***

#### 9.8.9 Log Entry Structure

**Host: `LogEntry` (Python dataclass)**

```python
@dataclass
class LogEntry:
    timestamp: datetime
    level: str              # INFO, WARNING, ERROR
    module: str             # e.g., "serial_comm"
    message: str
    details: dict           # Optional context
```

- **Storage:** Rotating log file (e.g., `muate.log`).

***

### 9.9 Communication Software

This section details the UART protocol implementation on both firmware and host sides.

#### 9.9.1 Protocol Overview

- **Physical Layer:** UART (asynchronous, 8N1).
- **Baud Rates:** 115200–921600 (configurable).
- **Framing:** SYNC-length-command-payload-CRC.
- **Direction:** Full-duplex (TX and RX independent).

#### 9.9.2 Transmitter State Machine (Firmware)

**States:**

1. `TX_IDLE`:
   - Waiting for packet to send.
2. `TX_SYNC`:
   - Sending SYNC byte (0xAA).
3. `TX_HEADER`:
   - Sending length and command bytes.
4. `TX_PAYLOAD`:
   - Sending payload bytes (if any).
5. `TX_CRC`:
   - Sending CRC16 (low byte, then high byte).
6. `TX_COMPLETE`:
   - Packet sent; return to IDLE.

**Triggers:**

- `Comm_Send()` called → `TX_IDLE` → `TX_SYNC`.
- UART TX complete interrupt → advance state.

**Timeout Behavior:**

- Not applicable (TX is interrupt-driven).

**Failure States:**

- UART error (overrun, framing) → log error, abort TX, return to `TX_IDLE`.

***

#### 9.9.3 Receiver State Machine (Firmware)

**States:**

1. `RX_IDLE`:
   - Waiting for SYNC byte.
2. `RX_SYNC`:
   - Received SYNC; expecting length byte.
3. `RX_HEADER`:
   - Received length; expecting command byte.
4. `RX_PAYLOAD`:
   - Receiving payload bytes (count = length).
5. `RX_CRC_LOW`:
   - Expecting CRC low byte.
6. `RX_CRC_HIGH`:
   - Expecting CRC high byte.
7. `RX_VALIDATE`:
   - Compute CRC; compare with received.
8. `RX_COMPLETE`:
   - Packet valid; dispatch to command handler.

**Triggers:**

- UART RX interrupt → advance state.
- Timeout (inter-byte > 10 ms) → reset to `RX_IDLE`.

**Timeout Behavior:**

- Inter-byte timeout resets state machine to `RX_IDLE`.
- Prevents desynchronization from noise.

**Failure States:**

- CRC mismatch → discard packet, send NACK (0x81) with error code 0x03.
- Invalid length → discard, send NACK with error code 0x02.

***

#### 9.9.4 Host Receiver State Machine

Similar to firmware receiver but implemented in Python:

- Uses `pyserial.read()` with timeout.
- State machine in `data_parser.py`.
- Raises `ProtocolError` on invalid packets.

***

#### 9.9.5 Buffering Strategy

**Firmware:**

- **TX Buffer:** Circular buffer (256 bytes) for outgoing packets.
  - Written by command handler.
  - Read by UART TX interrupt.
- **RX Buffer:** Circular buffer (256 bytes) for incoming bytes.
  - Written by UART RX interrupt.
  - Read by state machine.

**Host:**

- **RX Buffer:** `pyserial` internal buffer + application-level byte array.
- **TX Buffer:** Application constructs packet, sends in one `write()` call.

***

#### 9.9.6 Synchronization

- **SYNC Byte (0xAA):** Unique value not expected in payload.
- **Resynchronization:** If state machine loses sync, scan for next 0xAA.
- **Inter-Byte Timeout:** 10 ms (firmware), 100 ms (host).

***

#### 9.9.7 CRC Implementation

- **Algorithm:** CRC16-CCITT (polynomial 0x1021, initial 0xFFFF).
- **Coverage:** Length, command/response, payload.
- **Implementation:**
  - Firmware: Lookup table (256 entries) for speed.
  - Host: `binascii.crc_hqx` or custom implementation.

***

#### 9.9.8 Retries and Timeouts

**Host:**

- **Command Timeout:** 100 ms for ACK/NACK.
- **Data Timeout:** 500 ms between data packets.
- **Retry Policy:**
  - Retry command up to 3 times on timeout or NACK.
  - Abort after 3 failures; notify user.

**Firmware:**

- No retries (passive responder).
- Timeouts on host inactivity (5 s → enter safe idle).

***

#### 9.9.9 Protocol Versioning

- **Version Field:** Included in `GET_VERSION` response.
- **Format:** `MAJOR.MINOR` (e.g., 1.0).
- **Host Behavior:**
  - Check version at startup.
  - Warn if incompatible.

***

#### 9.9.10 Command Dispatch

**Firmware:**

- **Command Table:**
  ```c
  typedef struct {
      uint8_t cmd;
      void (*handler)(uint8_t* payload, uint8_t length);
  } CommandEntry_t;
  ```
- **Dispatch:** Linear search or switch-case.

**Host:**

- **Command Methods:**
  - `send_config_test()`, `send_start_test()`, etc.
  - Each constructs packet and calls `serial_comm.send()`.

***

#### 9.9.11 Packet Validation

**Checks:**

1. SYNC byte = 0xAA.
2. Length ≤ 254.
3. CRC matches.
4. Command code valid.

**Actions:**

- Invalid → discard, log error, send NACK (firmware).
- Host raises `ProtocolError`.

***

### 9.10 Memory Management

#### 9.10.1 STM32 Memory Layout

**Flash (1 MB typical):**

- **0x0800 0000:** Vector table (first 1 kB).
- **0x0800 0400:** Firmware code (`.text`).
- **0x0800 XX00:** Constant data (`.rodata`, e.g., waveform LUTs).

**SRAM (128 kB):**

- **0x2000 0000:** `.data` (initialized globals).
- **0x2000 XX00:** `.bss` (zero-initialized globals, e.g., ADC buffer).
- **0x2000 YY00:** Stack (grows downward, 8–16 kB typical).
- **0x2000 ZZ00:** Heap (grows upward, minimal use).

**Memory Estimates:**

| Region | Usage | Size |
|--------|-------|------|
| Flash | Code + constants | ~64–128 kB |
| SRAM (.data + .bss) | Globals, ADC buffer | ~80–100 kB |
| Stack | Local variables, ISR | 8–16 kB |
| Heap | Dynamic allocation (minimal) | 1–4 kB |

**DMA Buffers:**

- ADC buffer: 64 kB (32k samples × 2 bytes).
- Placed in `.bss` for zero-initialization.

**Circular Buffers:**

- UART TX/RX: 256 bytes each (`.data`).

**Memory Fragmentation:**

- Minimal (no `malloc` in critical paths).
- Stack and heap grow toward each other; linker script ensures no overlap.

***

#### 9.10.2 Python Memory Management

**Numpy Arrays:**

- **ADC Buffer:** 50k samples × 2 bytes = 100 kB.
- **FFT Spectrum:** 50k complex floats = 800 kB.
- **Plots:** Matplotlib figure objects (few MB).

**Memory Ownership:**

- Arrays created in `data_acquisition.py`, passed to `signal_processing.py`.
- No deep copies (pass by reference).

**Temporary Buffers:**

- Intermediate arrays (e.g., windowed samples) created as needed.
- Garbage collected when references drop.

**Garbage Collection:**

- Python GC handles cyclic references.
- Large arrays explicitly deleted (`del`) after use if memory is tight.

**Large Dataset Handling:**

- For >100k samples:
  - Use memory-mapped files (`numpy.memmap`).
  - Process in chunks.

***

### 9.11 Software State Machines

#### 9.11.1 Firmware State Machine

**States:**

1. `FW_INIT`:
   - Hardware initialization.
   - Transition: `FW_INIT` → `FW_IDLE` (on success).
2. `FW_IDLE`:
   - Waiting for commands.
   - Transitions:
     - `FW_IDLE` → `FW_CONFIGURED` (on `CONFIG_TEST` ACK).
     - `FW_IDLE` → `FW_ERROR` (on fault).
3. `FW_CONFIGURED`:
   - Test parameters loaded.
   - Transitions:
     - `FW_CONFIGURED` → `FW_ACQUIRING` (on `START_TEST`).
     - `FW_CONFIGURED` → `FW_IDLE` (on timeout or reset).
4. `FW_ACQUIRING`:
   - ADC/DMA active.
   - Transitions:
     - `FW_ACQUIRING` → `FW_DATA_READY` (on DMA complete).
     - `FW_ACQUIRING` → `FW_ERROR` (on ADC/DMA fault).
5. `FW_DATA_READY`:
   - Buffer filled; sending data.
   - Transitions:
     - `FW_DATA_READY` → `FW_IDLE` (on transmission complete).
6. `FW_ERROR`:
   - Fault detected.
   - Transitions:
     - `FW_ERROR` → `FW_IDLE` (on reset or recovery).

**Timeout Behavior:**

- `FW_CONFIGURED` → `FW_IDLE` after 5 s inactivity.

**Recovery States:**

- `FW_ERROR` → safe peripherals off → `FW_IDLE`.

***

#### 9.11.2 Host Application State Machine

**States:**

1. `HOST_INIT`:
   - Load config, open serial port.
   - Transition: `HOST_INIT` → `HOST_IDLE`.
2. `HOST_IDLE`:
   - Waiting for user command.
   - Transitions:
     - `HOST_IDLE` → `HOST_CONFIGURING` (on test start).
3. `HOST_CONFIGURING`:
   - Sending `CONFIG_TEST`.
   - Transitions:
     - `HOST_CONFIGURING` → `HOST_READY` (on ACK).
     - `HOST_CONFIGURING` → `HOST_ERROR` (on NACK/timeout).
4. `HOST_READY`:
   - Sending `START_TEST`.
   - Transitions:
     - `HOST_READY` → `HOST_ACQUIRING` (on ACK).
5. `HOST_ACQUIRING`:
   - Receiving data packets.
   - Transitions:
     - `HOST_ACQUIRING` → `HOST_PROCESSING` (on `END_OF_DATA`).
6. `HOST_PROCESSING`:
   - Running analysis.
   - Transitions:
     - `HOST_PROCESSING` → `HOST_REPORTING`.
7. `HOST_REPORTING`:
   - Generating plots/reports.
   - Transitions:
     - `HOST_REPORTING` → `HOST_IDLE`.
8. `HOST_ERROR`:
   - Fault detected.
   - Transitions:
     - `HOST_ERROR` → `HOST_IDLE` (on user retry).

**Timeout Behavior:**

- Each state has associated timeout (e.g., 100 ms for ACK).
- Timeout → `HOST_ERROR`.

***

### 9.12 Algorithms

#### 9.12.1 Waveform Generation (Firmware)

**Mathematical Basis:**

- **Ramp:**
  $
  y[n] = \left\lfloor \frac{n}{N} \cdot 4095 \right\rfloor
  $
  where $ N $ = waveform period in samples.
- **Sine:**
  $
  y[n] = 2048 + 2047 \cdot \sin\left( \frac{2\pi n}{N} \right)
  $

**Implementation:**

- **Lookup Table (LUT):**
  - 256-entry sine table in Flash.
  - Index incremented by timer.
- **Computational Complexity:** O(1) per sample (table lookup).

**Assumptions:**

- Timer triggers DAC at exact rate.
- LUT resolution sufficient (8-bit → 12-bit via scaling).

**Edge Cases:**

- Frequency too high → timer overflow.
- Mitigation: Limit frequency range in config.

***

#### 9.12.2 DMA Acquisition (Firmware)

**Algorithm:**

1. Configure ADC for continuous/triggered mode.
2. Configure DMA:
   - Source: ADC data register.
   - Destination: RAM buffer.
   - Transfer count = `sample_count`.
3. Enable DMA and ADC.
4. Wait for DMA complete interrupt.
5. Disable ADC/DMA.

**Complexity:** O(N) for N samples (hardware-driven).

**Assumptions:**

- DMA priority high enough to avoid data loss.
- Buffer large enough.

**Edge Cases:**

- Buffer overflow → flag set, data truncated.

***

#### 9.12.3 Histogram Computation (Host)

**Algorithm:**

```python
hist, bin_edges = np.histogram(samples, bins=4096, range=(0, 4096))
```

**Complexity:** O(N) for N samples.

**Numerical Stability:**

- Integer bins avoid floating-point errors.

**Assumptions:**

- Samples are 12-bit (0–4095).

**Edge Cases:**

- Empty bins → DNL undefined (skip in calculation).

***

#### 9.12.4 DNL Calculation (Host)

**Mathematical Basis:**

$
\text{DNL}(k) = \frac{N_k}{N_{\text{ideal}}} - 1
$

where $ N_k $ = count for code $ k $, $ N_{\text{ideal}} = \frac{\text{total samples}}{4096} $.

**Algorithm:**

1. Compute $ N_{\text{ideal}} $.
2. For each code $ k $:
   - $ \text{DNL}(k) = (N_k / N_{\text{ideal}}) - 1 $.

**Complexity:** O(4096) = O(1).

**Assumptions:**

- Uniform input distribution (ramp).

**Edge Cases:**

- $ N_{\text{ideal}} = 0 $ → skip.

***

#### 9.12.5 INL Calculation (Host)

**Mathematical Basis:**

$
\text{INL}(m) = \sum_{i=1}^{m-1} \text{DNL}(i)
$

**Algorithm:**

- Cumulative sum of DNL array.

**Complexity:** O(4096).

***

#### 9.12.6 FFT Computation (Host)

**Mathematical Basis:**

- Cooley-Tukey FFT algorithm.

**Implementation:**

```python
spectrum = scipy.fft.fft(windowed_samples)
magnitudes = np.abs(spectrum)
```

**Complexity:** O(N log N) for N samples.

**Numerical Stability:**

- Double-precision FFT (`scipy.fft` uses float64).

**Assumptions:**

- Coherent sampling (integer cycles in buffer).

**Edge Cases:**

- N not power of two → zero-pad or use bluestein.

***

#### 9.12.7 THD Calculation (Host)

**Mathematical Basis:**

$
\text{THD} = \frac{\sqrt{\sum_{n=2}^{H} V_n^2}}{V_1}
$

where $ V_1 $ = fundamental magnitude, $ V_n $ = harmonic magnitudes.

**Algorithm:**

1. Identify fundamental bin (peak near expected frequency).
2. Identify harmonic bins (integer multiples).
3. Compute RMS of harmonics.
4. Divide by fundamental.

**Complexity:** O(H) where H = number of harmonics (typically 5–10).

***

#### 9.12.8 SNR Calculation (Host)

**Mathematical Basis:**

$
\text{SNR} = 20 \cdot \log_{10}\left( \frac{P_{\text{signal}}}{P_{\text{noise}}} \right)
$

where $ P_{\text{signal}} $ = power in fundamental bin, $ P_{\text{noise}} $ = power in all other bins (excluding harmonics).

**Algorithm:**

1. Sum squares of magnitudes in fundamental bin.
2. Sum squares in noise bins.
3. Compute ratio in dB.

***

#### 9.12.9 Report Generation (Host)

**Algorithm:**

1. Gather metrics (DNL_max, INL_max, THD, SNR).
2. Generate plots (Matplotlib).
3. Save plots to PNG.
4. Write CSV for raw data and metrics.
5. (Optional) Generate HTML/PDF report.

**Complexity:** O(N) for N samples (dominated by I/O).

***

### 9.13 Error Handling

#### 9.13.1 Firmware Fault Model

| Fault | Detection | Logging | Recovery | User Notification |
|-------|-----------|---------|----------|-------------------|
| ADC timeout | ADC not complete after expected time | Log to UART | Reset ADC, retry | NACK with error code |
| DMA error | DMA error flag | Log | Disable DMA, reset | NACK |
| UART overrun | UART ORE flag | Log | Clear flag, continue | N/A |
| Invalid command | Command code not in table | Log | Ignore | NACK (0x01) |
| CRC error | CRC mismatch | Log | Discard packet | NACK (0x03) |

***

#### 9.13.2 Host Fault Model

| Fault | Detection | Logging | Recovery | User Notification |
|-------|-----------|---------|----------|-------------------|
| Serial timeout | `pyserial` timeout exception | Log to file | Retry up to 3x | Error message |
| Invalid packet | CRC/length check fail | Log | Discard, retry | Warning |
| File I/O error | `IOError` exception | Log | Abort test | Error message |
| Numerical error | NaN/Inf in FFT | Log | Skip metric | Warning |

***

### 9.14 Configuration Management

#### 9.14.1 JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "test_type": {"type": "string", "enum": ["ramp", "sine"]},
    "sample_count": {"type": "integer", "minimum": 1000, "maximum": 50000},
    "sampling_rate": {"type": "integer", "minimum": 1000},
    "dac_amplitude": {"type": "number", "minimum": 0.1, "maximum": 3.3},
    "dac_frequency": {"type": "number", "minimum": 10, "maximum": 10000},
    "serial_port": {"type": "string"},
    "baud_rate": {"type": "integer"}
  },
  "required": ["test_type", "sample_count", "serial_port"]
}
```

#### 9.14.2 Parameter Validation

- Host validates against schema before sending to firmware.
- Firmware performs secondary validation (range checks).

#### 9.14.3 Defaults

- `default.json`:
  ```json
  {
    "test_type": "ramp",
    "sample_count": 10000,
    "sampling_rate": 100000,
    "dac_amplitude": 3.3,
    "dac_frequency": 1000,
    "baud_rate": 921600
  }
  ```

#### 9.14.4 Versioning and Migration

- Config files include `"version": "1.0"`.
- Host checks version; migrates old configs if schema changes.

***

### 9.15 Logging

#### 9.15.1 Log Levels

- `DEBUG`: Detailed internal state.
- `INFO`: Normal operation (test start/end).
- `WARNING`: Recoverable errors (retries).
- `ERROR`: Unrecoverable errors (test abort).

#### 9.15.2 Formatting

```
[2026-08-02 14:30:15.123] [INFO] [serial_comm] Opened COM3 at 921600 baud
```

#### 9.15.3 Log Rotation

- Max file size: 10 MB.
- Backup count: 5 files.

#### 9.15.4 Debugging vs Production Logs

- **Debugging:** `DEBUG` level, console + file.
- **Production:** `INFO` level, file only.

***

### 9.16 Coding Standards

#### 9.16.1 Naming Conventions

- **Firmware (C):**
  - Types: `TestConfig_t`, `UART_Packet_t`.
  - Functions: `ADC_Driver_Init()`, `Waveform_Generate()`.
  - Globals: `g_adc_buffer`, `g_test_config`.
- **Host (Python):**
  - Classes: `TestConfig`, `FFTResult`.
  - Functions: `compute_histogram()`, `send_config_test()`.
  - Variables: `snake_case`.

#### 9.16.2 Documentation

- **Firmware:** Doxygen comments.
  ```c
  /**
   * @brief Initialize ADC driver
   * @param config Pointer to configuration
   * @return HAL status
   */
  ```
- **Host:** Sphinx docstrings.
  ```python
  def compute_fft(samples: np.ndarray, fs: int) -> FFTResult:
      """Compute FFT and extract metrics."""
  ```

#### 9.16.3 Commits and Branching

- **Branches:** `main`, `dev`, `feature/xxx`.
- **Commits:** Conventional Commits (`feat:`, `fix:`, `docs:`).

***

### 9.17 Software Testing

#### 9.17.1 Unit Testing

- **Host:** `pytest` for `signal_processing.py`, `data_parser.py`.
- **Firmware:** CMock or custom test harness for drivers.

#### 9.17.2 Integration Testing

- Firmware + Host:
  - Loopback test (DAC → ADC).
  - Verify end-to-end data flow.

#### 9.17.3 Regression Testing

- Automated test suite run on each commit (CI/CD).
- Synthetic data tests for FFT/histogram.

#### 9.17.4 Performance Testing

- Measure:
  - UART throughput.
  - FFT computation time.
  - End-to-end latency.

***

### 9.18 Software Bring-up

1. **Firmware Flashing:**
   - Load blinky test; verify LED.
2. **Peripheral Testing:**
   - DAC: Output constant voltage; measure with DMM.
   - ADC: Read potentiometer; verify values.
3. **UART Testing:**
   - Loopback TX/RX; verify characters.
4. **DMA Testing:**
   - Fill buffer with ADC samples; verify via debug.
5. **Host Communication:**
   - Run `python -m muate.cli --help`.
   - Send `GET_VERSION`; verify response.
6. **End-to-End Test:**
   - Run ramp test; verify DNL/INL plots.

***

### 9.19 Software Debugging Guide

| Symptom | Cause | Diagnosis | Solution |
|---------|-------|-----------|----------|
| No UART response | Wrong baud/port | Check `pyserial` config | Correct port/baud |
| ADC reads constant | ADC not enabled | Check firmware init | Enable ADC clock |
| FFT shows noise | Non-coherent sampling | Check signal frequency | Adjust to coherent frequency |
| CRC errors | Noise on UART | Check wiring, ground | Add series resistors, improve ground |

***

### 9.20 Future Expansion

- **GUI:** `PyQt` or `tkinter` for interactive control.
- **Plugins:** Dynamic loading of analysis modules.
- **Remote Operation:** WebSocket or REST API.
- **Cloud Sync:** Upload reports to cloud storage.
- **CI/CD:** GitHub Actions for automated testing.
- **FPGA Support:** Offload FFT to FPGA (via SPI).
- **Multiple Devices:** Address multiple STM32 boards.

***

### 9.21 Software Design Patterns

| Pattern | Usage | Justification |
|---------|-------|---------------|
| **State** | Firmware state machine | Clear state transitions |
| **Strategy** | Test profiles (ramp, sine) | Swap algorithms without changing core |
| **Command** | Host command dispatch | Encapsulate requests |
| **Observer** | Future GUI updates | Notify views of data changes |
| **Factory** | Waveform generation | Create waveform objects |
| **Dependency Injection** | Testing (mock serial) | Decouple dependencies |

***

### 9.22 UML Documentation

#### 9.22.1 Class Diagram

- **Host:**
  - Classes: `TestConfig`, `SerialComm`, `DataAcquisition`, `SignalProcessing`, `Plotting`, `ReportGenerator`.
  - Relationships: `DataAcquisition` → `SerialComm`, `SignalProcessing` → `DataAcquisition`.

#### 9.22.2 Sequence Diagrams

- **Test Execution:**
  - Lifelines: `User`, `CLI`, `SerialComm`, `Firmware`, `ADC`, `DAC`.
  - Messages: `send_config()`, `ack()`, `start_test()`, `send_data()`.

#### 9.22.3 State Diagrams

- **Firmware:** States from Section 9.11.1.
- **Host:** States from Section 9.11.2.

#### 9.22.4 Activity Diagrams

- **Test Workflow:**
  - Start → Configure → Acquire → Process → Report → End.

***
