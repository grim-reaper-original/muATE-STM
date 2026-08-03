# 15. Developer Manual

This chapter is intended for engineers who will understand, modify, extend, debug, maintain, or contribute to the μATE-STM project. It assumes familiarity with embedded C, Python, Git, and basic electronics. It describes the internal organization, design rationale, and safe extension practices to preserve existing functionality while enabling growth.

***

## 15.1 Developer Philosophy

### 15.1.1 Project Philosophy

μATE-STM is designed as an educational, reproducible, and extensible mixed-signal test instrument. The software architecture prioritizes clarity, modularity, and verifiability over cleverness. Every module has a single responsibility, well-defined interfaces, and testable behavior.

### 15.1.2 Modular Design

- **Firmware:** Peripherals are encapsulated in discrete modules (UART, ADC, DAC, DMA). Each module exposes a minimal API and hides implementation details.
- **Host:** Analysis, acquisition, reporting, and configuration are separated into independent packages with clear data contracts.

### 15.1.3 Separation of Concerns

- **Firmware:** Handles real-time I/O, timing, and command execution.
- **Host:** Handles data processing, visualization, reporting, and user interaction.
- **Protocol:** Defines a stable binary interface between firmware and host, enabling independent evolution.

### 15.1.4 Maintainability

- **Naming:** Consistent, descriptive names (e.g., `adc_acquire`, `compute_fft`).
- **Documentation:** Every module has a header comment explaining purpose, inputs, outputs, and side effects.
- **Logging:** Structured logs (firmware: UART debug prints; host: `logging` module) for traceability.

### 15.1.5 Scalability

- **Firmware:** New peripherals or commands are added without modifying existing modules (Open/Closed Principle).
- **Host:** New analysis modules are pluggable; reports are generated from a registry of metrics.

### 15.1.6 Readability

- **Code Style:** Follows MISRA-C-like discipline in firmware (no dynamic memory, minimal globals) and PEP 8 in Python.
- **Flow Control:** State machines and polling loops are preferred over complex interrupt nesting.

### 15.1.7 Reproducibility

- **Versioning:** Git tags mark releases; `requirements.txt` pins Python dependencies.
- **Configuration:** JSON configs ensure experiments are repeatable.
- **Testing:** Unit and integration tests verify behavior across changes.

**Engineering Principles for Future Development:**
- **Verify Before Merge:** No feature is complete without tests and documentation.
- **Backward Compatibility:** Protocol and config changes must be versioned and migratable.
- **Fail Safely:** Errors are logged, reported, and handled gracefully (no silent failures).

***

## 15.2 Overall Software Architecture

The software architecture is a client-server model with the STM32 firmware as the server (real-time I/O) and the Python host as the client (analysis, UI, reporting).

### 15.2.1 Firmware

- **Responsibilities:** Peripheral initialization, command parsing, real-time acquisition (ADC/DAC/DMA), calibration application.
- **Interfaces:** UART (command/response), ADC/DAC (analog I/O), GPIO (status LED).
- **Data Flow:** Host command → Parser → Action (e.g., start ADC) → DMA buffer → UART transmission → Host.

### 15.2.2 Host Software

- **Responsibilities:** Device communication, data parsing, signal processing (FFT, histogram), metrics (DNL, INL, THD, SNR, ENOB), reporting.
- **Interfaces:** Serial (UART), file system (configs, data, reports), plotting (matplotlib).
- **Data Flow:** Send command → Receive packets → Parse → Analyze → Plot → Report.

### 15.2.3 Communication Protocol

- **Structure:** Binary packets with header, command, length, payload, CRC (Chapter 13).
- **Versioning:** Protocol version byte enables future extensions while maintaining backward compatibility.
- **Error Handling:** ACK/NACK, timeouts, retries (Section 13.8).

### 15.2.4 Configuration

- **Firmware:** Compile-time constants (e.g., `BUFFER_SIZE`, `BAUD_RATE`) in `config.h`.
- **Host:** JSON configs (`configs/acquisition.json`, `configs/calibration.json`) for runtime parameters.

### 15.2.5 Reporting

- **Generation:** Host aggregates metrics, plots, and metadata into PDF/HTML.
- **Extensibility:** Report sections are registered modules; new metrics auto-appear in reports.

### 15.2.6 Analysis

- **Modules:** `signal_processing.py` (FFT, windows), `adc_analysis.py` (DNL, INL, ENOB), `metrics.py` (THD, SNR).
- **Data Contracts:** Functions accept numpy arrays; return dicts with metrics and plots.

**Reference:** See Chapters 9 (software architecture), 11 (mathematics), 13 (implementation).

***

## 15.3 Repository Structure

```
μATE-STM/
├── docs/                    # Documentation (reports, datasheets, diagrams)
├── firmware/                # STM32CubeIDE project, source, headers
│   ├── Src/                 # C source files (main.c, adc.c, uart.c, ...)
│   ├── Inc/                 # Headers (adc.h, uart.h, config.h, ...)
│   ├── STM32CubeMX/         # .ioc configuration
│   └── Debug/               # Build output (bin, hex)
├── hardware/                # Schematics, BOM, Gerbers (if PCB)
├── python/                  # Host software packages
│   ├── acquisition.py       # UART communication, data capture
│   ├── parser.py            # Binary packet parser
│   ├── signal_processing.py # FFT, windows, histogram
│   ├── adc_analysis.py      # DNL, INL, ENOB
│   ├── metrics.py           # THD, SNR, SINAD, SFDR
│   ├── report_generator.py  # PDF/HTML report generation
│   ├── config.py            # Configuration loading/validation
│   └── utils.py             # Logging, helpers
├── configs/                 # JSON configuration files
│   ├── acquisition.json     # Sampling rate, buffer size, window
│   ├── calibration.json     # Offset, gain constants
│   └── test_plans.json      # Pass/fail thresholds
├── scripts/                 # Automation (build, test, deploy)
├── tests/                   # Test suites
│   ├── unit/                # Unit tests (parser, analysis)
│   ├── integration/         # End-to-end tests (acquire + analyze)
│   └── verification/        # Chapter 10 test procedures
├── data/                    # Measurement data
│   ├── raw/                 # Raw ADC samples
│   ├── processed/           # FFT, histograms, DNL/INL
│   └── test_results/        # Verification logs
├── examples/                # Example workflows, sample data
└── README.md                # Project overview, quickstart
```

### 15.3.1 Directory Purposes

- **docs/:** Centralized documentation; avoids scattering PDFs.
- **firmware/:** Isolated embedded code; CubeMX project regenerates initialization.
- **python/:** Host logic; modular packages enable independent testing.
- **configs/:** Externalized settings; allows experimentation without code changes.
- **scripts/:** Automation; ensures consistent builds and tests.
- **tests/:** Verification; unit tests catch regressions, integration tests validate end-to-end.
- **data/:** Experimental data; versioned separately from code.
- **examples/:** Reproducible workflows; aids onboarding and debugging.

***

## 15.4 Firmware Architecture

Firmware is organized into modules with clear responsibilities. Dependencies flow upward: `main` depends on peripherals; peripherals depend on HAL.

### 15.4.1 main

- **Responsibility:** Top-level state machine, system initialization, idle loop.
- **Dependencies:** `system`, `uart`, `acquisition_controller`.
- **Flow:** Init → Wait for command → Execute → Loop.

### 15.4.2 system

- **Responsibility:** Clock configuration, NVIC setup, watchdog (if used).
- **Dependencies:** HAL, CMSIS.
- **Note:** Auto-generated by CubeMX; manual edits in designated sections only.

### 15.4.3 clock

- **Responsibility:** System clock (168 MHz), APB1/APB2 prescalers, timer clock sources.
- **Dependencies:** HAL RCC.
- **Configuration:** `SystemClock_Config()` in `main.c`.

### 15.4.4 gpio

- **Responsibility:** Pin configuration (LED, ADC, DAC, UART), speed, pull-up/down.
- **Dependencies:** HAL GPIO.
- **Note:** Auto-generated; manual changes via CubeMX or `MX_GPIO_Init()`.

### 15.4.5 uart

- **Responsibility:** UART2 initialization, transmit/receive, interrupt handling.
- **Dependencies:** HAL UART, NVIC.
- **API:** `uart_init()`, `uart_send()`, `uart_receive_it()`.
- **Interrupt:** `USART2_IRQHandler()` calls parser on byte received.

### 15.4.6 adc

- **Responsibility:** ADC1 configuration, single/DMA modes, calibration.
- **Dependencies:** HAL ADC, DMA, timer (trigger).
- **API:** `adc_start_single()`, `adc_start_dma()`, `adc_stop()`.
- **Trigger:** Timer 2 (100 kSPS); see Chapter 11 for timing math.

### 15.4.7 dac

- **Responsibility:** DAC1 configuration, single/DMA modes, waveform generation.
- **Dependencies:** HAL DAC, DMA, timer.
- **API:** `dac_set_value()`, `dac_start_dma()`, `dac_stop()`.

### 15.4.8 dma

- **Responsibility:** DMA2 (ADC), DMA1 (DAC) configuration, circular/normal modes, interrupt callbacks.
- **Dependencies:** HAL DMA.
- **Callbacks:** `HAL_ADC_ConvCpltCallback()`, `HAL_DAC_ConvCpltCallback()`.

### 15.4.9 interrupts

- **Responsibility:** NVIC prioritization, ISR stubs, deferred processing flags.
- **Dependencies:** CMSIS, HAL.
- **Policy:** ISRs set flags; main loop processes (minimize ISR complexity).

### 15.4.10 command parser

- **Responsibility:** Packet framing, CRC verification, command dispatch.
- **Dependencies:** `uart`, `acquisition_controller`, `calibration`.
- **State Machine:** WAIT_HEADER → READ_CMD → READ_LENGTH → READ_PAYLOAD → READ_CRC.
- **Commands:** `CMD_START_ACQ`, `CMD_STOP_ACQ`, `CMD_READ_ADC`, `CMD_WRITE_DAC`, `CMD_CALIBRATE`.

### 15.4.11 acquisition controller

- **Responsibility:** Coordinate ADC/DAC/DMA/UART, manage buffers, signal completion.
- **Dependencies:** `adc`, `dac`, `dma`, `uart`.
- **States:** IDLE, ACQUIRING, TRANSMITTING, COMPLETE.

### 15.4.12 calibration

- **Responsibility:** Apply offset/gain correction to ADC codes, store constants in flash.
- **Dependencies:** `config`, `adc`.
- **API:** `calibration_apply(raw_code) → corrected_code`.

### 15.4.13 configuration

- **Responsibility:** Compile-time constants (`BUFFER_SIZE`, `BAUD_RATE`), runtime defaults.
- **Location:** `Inc/config.h`.
- **Note:** Avoid runtime config changes in firmware; use host-driven commands.

**Dependencies Summary:**  
`main` → `system`, `uart`, `acquisition_controller`  
`acquisition_controller` → `adc`, `dac`, `dma`  
`command parser` → `uart`, `acquisition_controller`, `calibration`

***

## 15.5 Host Software Architecture

Host software is organized into packages with single responsibilities. Data flows from acquisition → parsing → analysis → reporting.

### 15.5.1 acquisition

- **Responsibility:** Open COM port, send commands, receive packets, reassemble buffers.
- **Dependencies:** `pyserial`, `parser`.
- **API:** `acquire_samples(n_samples, config) → numpy array`.

### 15.5.2 parser

- **Responsibility:** Decode binary packets, verify CRC, extract payload.
- **Dependencies:** `binascii` (CRC), `struct` (unpacking).
- **API:** `parse_packet(raw_bytes) → dict{command, payload, crc_ok}`.

### 15.5.3 analysis

- **Packages:**
  - `signal_processing.py`: FFT, window functions, histogram.
  - `adc_analysis.py`: DNL, INL, ENOB.
  - `metrics.py`: THD, SNR, SINAD, SFDR.
- **Dependencies:** `numpy`, `scipy`.
- **API:** `compute_fft(samples, fs, window)`, `compute_dnl_inl(histogram)`, `compute_thd_snr(fft)`.

### 15.5.4 calibration

- **Responsibility:** Load/save calibration constants, apply correction to raw data.
- **Dependencies:** `config`, `json`.
- **API:** `load_calibration()`, `apply_calibration(raw_data)`.

### 15.5.5 reports

- **Responsibility:** Aggregate metrics, plots, metadata; generate PDF/HTML.
- **Dependencies:** `matplotlib`, `reportlab`/`weasyprint`.
- **API:** `generate_report(metrics, plots, output_path)`.

### 15.5.6 visualization

- **Responsibility:** Plotting functions (time-domain, FFT, histogram, DNL/INL).
- **Dependencies:** `matplotlib`.
- **API:** `plot_time_domain(samples)`, `plot_fft(fft, fs)`.

### 15.5.7 configuration

- **Responsibility:** Load JSON configs, validate schema, provide defaults.
- **Dependencies:** `json`, `jsonschema` (optional).
- **API:** `load_config(path)`, `validate_config(config)`.

### 15.5.8 utilities

- **Responsibility:** Logging, path helpers, timing.
- **Dependencies:** `logging`, `os`, `time`.
- **API:** `setup_logging()`, `get_data_path()`.

### 15.5.9 testing

- **Responsibility:** Unit tests, integration tests, mock objects.
- **Dependencies:** `unittest`, `pytest`.
- **API:** `test_parser()`, `test_fft_sine()`.

**Module Interactions:**  
`acquisition` → `parser` → `analysis` → `visualization` → `reports`  
`configuration` → all modules (provides settings)  
`calibration` → `acquisition`/`analysis` (corrects data)

***

## 15.6 Communication Protocol

The protocol is a binary, packet-oriented interface optimized for simplicity and robustness.

### 15.6.1 Packet Structure

| Field | Size (bytes) | Description |
|-------|--------------|-------------|
| Header | 2 | Sync bytes: `0xAA 0x55` |
| Version | 1 | Protocol version (currently `0x01`) |
| Command | 1 | Command ID (e.g., `0x01` = START_ACQ) |
| Length | 2 | Payload length (little-endian) |
| Payload | N | Command-specific data |
| CRC | 2 | CRC-16-CCITT (little-endian) |

### 15.6.2 Headers

- **Sync:** `0xAA 0x55` ensures byte alignment.
- **Version:** Enables future extensions; receivers reject unknown versions.

### 15.6.3 Payload

- **Variable Length:** Defined by `Length` field.
- **Examples:**
  - `START_ACQ`: `{ count: uint32 }`.
  - `READ_ADC`: `{ channel: uint8 }`.
  - `WRITE_DAC`: `{ code: uint16 }`.

### 15.6.4 CRC

- **Algorithm:** CRC-16-CCITT (poly `0x1021`, init `0xFFFF`).
- **Coverage:** Header + Version + Command + Length + Payload.
- **Purpose:** Detect corruption; firmware sends NACK on mismatch.

### 15.6.5 Versioning

- **Current:** `0x01`.
- **Future:** Increment on breaking changes; maintain backward compatibility where possible.
- **Migration:** Host checks version; warns if mismatch.

### 15.6.6 Command IDs

| Command | ID | Direction | Description |
|---------|----|-----------|-------------|
| `PING` | `0x00` | Host→FW | Health check |
| `START_ACQ` | `0x01` | Host→FW | Start ADC acquisition |
| `STOP_ACQ` | `0x02` | Host→FW | Stop acquisition |
| `READ_ADC` | `0x03` | Host→FW | Single ADC read |
| `WRITE_DAC` | `0x04` | Host→FW | Single DAC write |
| `CALIBRATE` | `0x05` | Host→FW | Run calibration |
| `ACK` | `0x80` | FW→Host | Acknowledge |
| `NACK` | `0x81` | FW→Host | Negative acknowledge |
| `DATA` | `0x82` | FW→Host | ADC data packet |

### 15.6.7 Error Handling

- **CRC Fail:** Firmware discards packet, sends NACK.
- **Unknown Command:** Firmware sends NACK.
- **Timeout:** Host retries (max 3); then aborts.

### 15.6.8 Timeouts

- **Firmware:** 10 ms inter-byte timeout resets parser state.
- **Host:** 1 s command timeout; configurable.

### 15.6.9 Future Compatibility

- **Extension:** New commands added; old hosts ignore unknown IDs (safe).
- **Breaking Changes:** Increment version; provide migration scripts.

***

## 15.7 Configuration System

### 15.7.1 Configuration Files

- **Format:** JSON (human-readable, easy to parse).
- **Location:** `configs/` directory.
- **Files:**
  - `acquisition.json`: Sampling rate, buffer size, window.
  - `calibration.json`: Offset, gain constants.
  - `test_plans.json`: Pass/fail thresholds.

### 15.7.2 JSON Structure

**Example (`acquisition.json`):**
```json
{
  "version": "1.0",
  "sampling_rate": 100000,
  "buffer_size": 4096,
  "window_function": "hann",
  "averaging": 1
}
```

### 15.7.3 Default Configuration

- **Fallback:** If config missing, use hardcoded defaults in `config.py`.
- **Defaults:** Match Chapter 8/11 design (100 kSPS, 4096 samples, Hann window).

### 15.7.4 Validation

- **Schema:** Optional `jsonschema` for strict validation.
- **Checks:** Range (e.g., `sampling_rate` 1k–100k), type (int vs float).

### 15.7.5 Loading

- **Function:** `config.load_config(path)`.
- **Behavior:** Merge with defaults; log overrides.

### 15.7.6 Saving

- **Function:** `config.save_config(config, path)`.
- **Usage:** Calibration updates, user tweaks.

### 15.7.7 Version Compatibility

- **Field:** `version` in JSON.
- **Migration:** If version mismatch, apply migration script (e.g., rename fields).

***

## 15.8 Adding New Measurements

To add a new measurement (e.g., SFDR, IMD):

### 15.8.1 Firmware Modifications

- **If New Data Needed:** Add command (e.g., `CMD_START_SPECTRAL_ACQ`).
- **If Existing Data Suffices:** No firmware change (use existing ADC data).

### 15.8.2 Communication Changes

- **Command ID:** Assign new ID in `command_parser.c`.
- **Payload:** Define structure (e.g., `{ mode: uint8 }`).
- **Response:** Use `DATA` packet with metric payload.

### 15.8.3 Python Analysis Additions

- **Module:** Add function in `metrics.py` (e.g., `compute_sfdr(fft)`).
- **Integration:** Call from `analysis` pipeline; append to metrics dict.

### 15.8.4 Report Generation

- **Section:** Add to `report_generator.py` (e.g., "SFDR Metric").
- **Plot:** If applicable, add to `visualization.py`.

### 15.8.5 Verification

- **Unit Test:** Add test in `tests/unit/test_metrics.py`.
- **Integration Test:** Acquire known signal; verify metric value.

### 15.8.6 Documentation Updates

- **User Manual:** Add command/example in Chapter 14.
- **Developer Manual:** Update this chapter with new module.

***

## 15.9 Extending Firmware

### 15.9.1 New Peripherals

- **CubeMX:** Configure peripheral (e.g., SPI1); generate code.
- **Module:** Create `spi.c/h` with init, transfer functions.
- **Integration:** Call from `main` or new command.

### 15.9.2 New Commands

- **Parser:** Add case in `command_parser.c`.
- **Handler:** Implement function (e.g., `handle_spectral_acq()`).
- **Testing:** Send command via host; verify response.

### 15.9.3 DMA Transfers

- **Configuration:** CubeMX DMA settings; ensure no conflict with existing streams.
- **Callbacks:** Add `HAL_DMA_ConvCpltCallback()` handler.
- **Buffers:** Use separate buffers to avoid overwriting.

### 15.9.4 Interrupt Handlers

- **Priority:** Assign NVIC priority; avoid preemption conflicts.
- **ISR:** Minimal work; set flag for main loop.

### 15.9.5 Drivers

- **Abstraction:** Wrap HAL in driver API (e.g., `driver_spi_init()`).
- **Portability:** Isolate hardware-specific code.

### 15.9.6 Calibration Routines

- **New Routine:** Add function in `calibration.c` (e.g., `calibrate_temperature()`).
- **Storage:** Extend flash section; update `calibration.json`.

**Safety:**  
- **No Global State:** Minimize shared variables; use mutexes if needed.
- **Backward Compatibility:** Do not modify existing command behavior.

***

## 15.10 Extending Host Software

### 15.10.1 Analysis Modules

- **Add File:** `new_metric.py` in `python/`.
- **Function:** `compute_new_metric(data) → float`.
- **Registration:** Add to `analysis` pipeline.

### 15.10.2 Plots

- **Function:** `plot_new_metric(data)` in `visualization.py`.
- **Integration:** Call from report generator.

### 15.10.3 Metrics

- **Dict:** Append to metrics dict in `analysis.py`.
- **Report:** Auto-included via registry.

### 15.10.4 Report Sections

- **Template:** Add section in `report_generator.py`.
- **Condition:** Include if metric present.

### 15.10.5 Configuration Options

- **JSON:** Add field in `acquisition.json`.
- **Validation:** Update schema in `config.py`.

### 15.10.6 CLI Commands

- **Argparse:** Add argument in `main.py` (e.g., `--new-metric`).
- **Handler:** Call analysis function.

### 15.10.7 Future GUI Support

- **Abstraction:** Keep analysis separate from UI.
- **Framework:** PyQt/Tkinter; use existing analysis modules.

***

## 15.11 Coding Standards

### 15.11.1 Naming

- **Firmware:** `snake_case` for functions/variables; `UPPER_CASE` for constants.
- **Python:** `snake_case` for functions/variables; `PascalCase` for classes.

### 15.11.2 Formatting

- **Firmware:** 4-space indent; braces on same line.
- **Python:** PEP 8 (4-space indent, max 79 chars).

### 15.11.3 Documentation

- **Firmware:** Doxygen-style comments (`/** @brief ... */`).
- **Python:** Docstrings (triple quotes) for modules, functions, classes.

### 15.11.4 Comments

- **Purpose:** Explain "why," not "what."
- **Avoid:** Redundant comments (e.g., `i++ // increment i`).

### 15.11.5 Constants

- **Firmware:** `#define` in `config.h`; avoid magic numbers.
- **Python:** `UPPER_CASE` constants in module scope.

### 15.11.6 Magic Numbers

- **Prohibited:** Use named constants (e.g., `ADC_MAX_CODE = 4095`).

### 15.11.7 Error Handling

- **Firmware:** Return error codes; log via UART.
- **Python:** Raise exceptions; log via `logging` module.

### 15.11.8 Logging

- **Firmware:** `printf_debug("ADC started\n");`.
- **Python:** `logging.info("Acquisition complete")`.

***

## 15.12 Version Control

### 15.12.1 Branch Strategy

- **main:** Stable, release-ready.
- **develop:** Integration branch for features.
- **feature/xxx:** New features (e.g., `feature/sfdr-metric`).
- **bugfix/xxx:** Critical fixes (e.g., `bugfix/uart-timeout`).

### 15.12.2 Commit Message Conventions

- **Format:** `type: subject` (e.g., `feat: add SFDR metric`).
- **Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`.

### 15.12.3 Feature Branches

- **Lifecycle:** Branch from `develop`; merge via PR.
- **Testing:** All tests pass before merge.

### 15.12.4 Bug Fixes

- **Priority:** Hotfix to `main`; cherry-pick to `develop`.

### 15.12.5 Releases

- **Tagging:** `v1.0.0`, `v1.1.0` (semantic versioning).
- **Notes:** Update `CHANGELOG.md`.

### 15.12.6 Code Review Philosophy

- **Focus:** Correctness, clarity, test coverage.
- **Feedback:** Constructive, specific.

***

## 15.13 Testing Strategy

### 15.13.1 Unit Testing

- **Firmware:** Limited (HAL dependence); test logic in isolation.
- **Python:** `unittest`/`pytest` for parser, analysis, metrics.

### 15.13.2 Integration Testing

- **End-to-End:** Acquire known signal; verify metrics.
- **Automation:** `scripts/run_integration_tests.sh`.

### 15.13.3 Hardware Testing

- **Procedures:** Chapter 10 test cases.
- **Data:** Store in `data/test_results/`.

### 15.13.4 Regression Testing

- **Baseline:** Save expected metrics; compare on changes.
- **Tool:** `pytest --baseline`.

### 15.13.5 Continuous Verification

- **CI:** GitHub Actions (lint, test, build).
- **Trigger:** On push/PR.

### 15.13.6 Test Data

- **Synthetic:** Sine waves, ramps for analysis tests.
- **Real:** Captured ADC data for integration tests.

### 15.13.7 Mock Objects

- **Serial:** Mock `pyserial` for parser tests.
- **HAL:** Stub HAL functions for firmware logic tests.

***

## 15.14 Debugging Methodology

### 15.14.1 Firmware

- **LED:** Toggle on state changes.
- **UART:** Print debug messages.
- **Debugger:** STM32CubeIDE breakpoints.

### 15.14.2 UART

- **Logic Analyzer:** Capture TX/RX; verify timing.
- **Loopback:** TX→RX; test parser.

### 15.14.3 DMA

- **Buffers:** Inspect in debugger; check for overwrites.
- **Interrupts:** Verify callbacks fire.

### 15.14.4 ADC

- **Input:** Apply known voltage; compare code.
- **Timing:** Verify trigger (Timer 2).

### 15.14.5 DAC

- **Output:** Measure with multimeter/oscilloscope.
- **Settling:** Check waveform after code change.

### 15.14.6 Python

- **Logging:** Increase verbosity (`--verbose`).
- **Debugger:** `pdb` for step-through.

### 15.14.7 Communication

- **Packet Capture:** Log raw bytes; verify CRC.
- **Timeouts:** Increase for debugging.

### 15.14.8 Reports

- **Debug Mode:** Skip PDF generation; output JSON.
- **Logs:** Check `report_generator.py` errors.

### 15.14.9 Configuration

- **Validation:** Print loaded config; verify values.
- **Defaults:** Fallback if file missing.

***

## 15.15 Performance Optimization

### 15.15.1 Memory

- **Firmware:** Reuse buffers; avoid large stacks.
- **Python:** Use `numpy` arrays; avoid copies.

### 15.15.2 CPU

- **Firmware:** Minimize ISR work; use DMA.
- **Python:** Vectorize operations (`numpy`); avoid loops.

### 15.15.3 DMA

- **Circular Mode:** For continuous ADC; no CPU intervention.
- **Priority:** High priority for ADC/DMA.

### 15.15.4 FFT

- **Library:** `scipy.fft` (FFTPACK); power-of-2 sizes.
- **Window:** Precompute window array.

### 15.15.5 Buffer Management

- **Firmware:** Double buffering for UART transmission.
- **Python:** Stream processing for large datasets.

### 15.15.6 UART Throughput

- **Baud Rate:** 921600 (max reliable).
- **Packing:** Send raw bytes (no ASCII).

### 15.15.7 Python Performance

- **Profiling:** `cProfile` to identify bottlenecks.
- **Optimization:** Numba for critical loops (optional).

***

## 15.16 Documentation Standards

### 15.16.1 API Documentation

- **Firmware:** Doxygen-generated HTML.
- **Python:** Sphinx-generated docs.

### 15.16.2 Module Documentation

- **Header:** Purpose, inputs, outputs, side effects.
- **Example:** Usage snippet.

### 15.16.3 README Files

- **Root:** Overview, quickstart.
- **Subdirs:** Purpose, structure.

### 15.16.4 Diagrams

- **Tools:** Draw.io, Graphviz.
- **Types:** Block diagrams, flowcharts.

### 15.16.5 Change Logs

- **File:** `CHANGELOG.md`.
- **Format:** Date, version, changes.

### 15.16.6 Release Notes

- **Content:** New features, bug fixes, known issues.
- **Location:** `docs/releases/`.

***

## 15.17 Future Extensions

The architecture supports extension in several directions:

### 15.17.1 Higher-Resolution ADCs

- **Interface:** External ADC via SPI/I²C.
- **Firmware:** Add `adc_external.c`; new command.
- **Host:** New analysis for 16/24-bit data.

### 15.17.2 External DACs

- **Interface:** SPI (e.g., AD5662).
- **Firmware:** `dac_external.c`; waveform generation.
- **Host:** Extended DAC tests.

### 15.17.3 SPI Devices

- **Driver:** `spi_driver.c`; generic read/write.
- **Commands:** `CMD_SPI_READ`, `CMD_SPI_WRITE`.

### 15.17.4 I²C Devices

- **Driver:** `i2c_driver.c`; EEPROM, sensors.
- **Commands:** `CMD_I2C_READ`, `CMD_I2C_WRITE`.

### 15.17.5 Ethernet

- **Hardware:** STM32 with MAC (e.g., F427).
- **Protocol:** TCP/IP socket instead of UART.
- **Host:** Network client.

### 15.17.6 USB High-Speed

- **Hardware:** STM32 with HS PHY.
- **Protocol:** CDC or custom class.
- **Throughput:** >10 MSPS possible.

### 15.17.7 GUI

- **Framework:** PyQt, Tkinter, or web-based.
- **Integration:** Reuse analysis modules.

### 15.17.8 FPGA Acceleration

- **Role:** High-speed acquisition, real-time FFT.
- **Interface:** Parallel or high-speed serial.
- **Host:** Offload processing.

### 15.17.9 PCB Implementation

- **Design:** KiCad/Altium; integrate STM32, AFE, connectors.
- **Firmware:** Same; hardware abstraction layer.

### 15.17.10 Industrial Instruments

- **Certification:** CE, FCC.
- **Enclosure:** Rugged, isolated.
- **Software:** LabVIEW driver, SCPI commands.

***

## 15.18 Developer Checklist

Before submitting new functionality:

- [ ] **Code:** Follows naming, formatting standards.
- [ ] **Documentation:** Module header, API docs updated.
- [ ] **Tests:** Unit/integration tests added; all pass.
- [ ] **Config:** JSON schema updated; migration script if needed.
- [ ] **Protocol:** Command ID assigned; version incremented if breaking.
- [ ] **Report:** New metric/section included.
- [ ] **Changelog:** Entry added.
- [ ] **Review:** Code reviewed; feedback addressed.

***

## 15.19 Developer Workflow Summary

1. **Idea:** Define feature (e.g., "Add SFDR metric").
2. **Branch:** Create `feature/sfdr-metric` from `develop`.
3. **Implement:**
   - **Firmware:** Add command (if needed).
   - **Host:** Add `compute_sfdr()` in `metrics.py`.
   - **Report:** Add section in `report_generator.py`.
4. **Test:**
   - **Unit:** Test `compute_sfdr()` with synthetic data.
   - **Integration:** Acquire sine wave; verify SFDR value.
5. **Document:** Update API docs, User Manual, CHANGELOG.
6. **Review:** Submit PR; address feedback.
7. **Merge:** Into `develop`; test regression suite.
8. **Release:** Tag `v1.1.0`; publish release notes.

This workflow ensures safe, verifiable extension of μATE-STM while preserving existing functionality.

***