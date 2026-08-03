# 6. System Architecture

## 6.1 System Architecture Overview

### 1. Design Philosophy

#### 1.1 Rationale for Architecture Choice

The chosen architecture is a **PC-controlled, embedded mixed-signal test station** in which:

- An **STM32F446/447-class MCU** provides:
  - Analog stimulus generation via on-chip 12-bit DACs.
  - Analog measurement via on-chip 12-bit ADCs.
  - High-speed data acquisition via DMA.
  - Serial communication to a host PC.
- A **laptop** provides:
  - Test orchestration and configuration.
  - Data analysis (histogram, FFT).
  - Visualization and reporting.
  - Storage and version-controlled documentation.

This architecture was selected because it:

- Leverages **existing hardware** (STM32 dev board and laptop) to minimize cost.
- Provides **real mixed-signal behavior** with non-idealities that are essential for learning.
- Separates **real-time, deterministic embedded tasks** (waveform generation, sampling) from **non-real-time, flexible host tasks** (analysis, UI, reporting).
- Supports **modular expansion** (additional channels, sensors, interfaces) without fundamental redesign.

#### 1.2 Educational Goals

The architecture is designed to support the following learning outcomes:

- **Mixed-signal fundamentals**: Direct experience with ADC/DAC operation, quantization, noise, and distortion.
- **Test and measurement theory**: Practical implementation of histogram-based DNL/INL and FFT-based THD/SNR.
- **Embedded systems design**: Use of timers, DMA, and UART/USB in a real data acquisition system.
- **Lab automation**: End-to-end test sequencing, data logging, and report generation.
- **Frugal engineering**: Achieving meaningful measurements with minimal budget and clever use of existing resources.
- **Systems engineering**: Clear decomposition, interface definition, and traceability from requirements to tests.

#### 1.3 Design Constraints

Key constraints shaping the architecture:

- **Budget**: No new expensive instruments; total additional hardware cost ≤ ₹1,000 (ideally ≤ ₹500).
- **Hardware availability**: Only an STM32F446/447-class board and a standard laptop are guaranteed.
- **No lab access**: No oscilloscope, function generator, or departmental test equipment.
- **Time**: Project must be completable within ~6 weeks of part-time effort.
- **Skill level**: Assumes basic C and Python proficiency; advanced topics must be learnable incrementally.
- **Safety**: All analog signals must remain within safe low-voltage ranges (< 5 V, ideally < 3.3 V).

#### 1.4 Budget Constraints

Budget constraints directly influence architectural decisions:

- **Reuse over purchase**: The STM32 board is the primary analog engine; no external high-end signal sources or analyzers are introduced.
- **Passive front-end only**: Analog front-end uses resistors, capacitors, and diodes; no active amplifiers or precision references are mandated.
- **Free software tools**: STM32CubeIDE, Python, and open-source plotting/analysis libraries are used exclusively.
- **Minimal external hardware**: Optional items (audio jack, multimeter) are non-essential and deferred.

These constraints enforce a **minimalist but educationally rich** architecture.

#### 1.5 Performance Goals

Although not intended as production-grade equipment, the system targets:

- **ADC sampling**:
  - Sustained capture of 10k–100k samples per test.
  - Effective sampling rates up to ~200 kSPS for initial tests, with potential extension toward 1 MSPS via interleaving as a stretch goal. [st](https://www.st.com/resource/en/datasheet/stm32f446re.pdf)
- **DAC waveform generation**:
  - Sine and ramp waveforms with update rates ≥ 50 kSPS.
  - Amplitudes within 0–3.3 V (or appropriately scaled).
- **Latency**:
  - End-to-end test (acquisition + analysis + report) under 60 seconds for typical configurations.
- **Throughput**:
  - UART streaming sufficient to transfer 10k–100k 16-bit samples within a few seconds.

These goals are aligned with educational needs rather than metrological certification.

#### 1.6 Scalability Goals

The architecture is designed to allow:

- **Channel expansion**:
  - Additional ADC channels for multi-signal testing.
  - Additional DAC channels for multi-tone or multi-stimulus scenarios.
- **Interface expansion**:
  - Future addition of SPI/I²C sensors.
  - Optional USB CDC or virtual COM for higher throughput.
- **Functional expansion**:
  - More complex test profiles (noise generation, multi-tone, swept frequency).
  - Automated calibration routines.
  - Integration with external instruments (if ever available) via PC-side control.

Scalability is achieved by:

- Clear separation of concerns (PC vs embedded).
- Modular firmware and software components.
- Well-defined interfaces (UART commands, data formats).

#### 1.7 Modularity Goals

Modularity is a core principle:

- **Embedded side**:
  - Separate modules for DAC waveform generation, ADC acquisition, DMA management, and UART communication.
- **PC side**:
  - Separate modules for serial communication, data analysis (histogram, FFT), visualization, and reporting.
- **Test profiles**:
  - Parameterized test definitions (waveform type, sample count, sampling rate).
  - Easy addition of new test types without modifying core infrastructure.

This modularity supports:

- Parallel development (e.g., one person works on ADC, another on analysis).
- Incremental testing and validation.
- Future reuse in other projects.

#### 1.8 Assumptions

The architecture assumes:

- The STM32F446/447 board has:
  - Functional 12-bit ADCs and DACs.
  - At least one UART port accessible (directly or via USB).
  - Sufficient RAM for buffers (≥ 16 kB recommended).
- The laptop has:
  - Python 3.10+ available.
  - USB ports and ability to install `pyserial`, `numpy`, `scipy`, `matplotlib`.
- The user has:
  - Basic soldering/breadboarding skills.
  - Access to basic passive components (resistors, capacitors, diodes).
- Analog signals are:
  - Low-voltage (< 3.3 V nominal, < 5 V absolute maximum).
  - Not connected to mains or hazardous sources.

***

### 2. Overall System Description

The μATE-STM system is a **two-tier architecture**:

1. **Embedded Tier (STM32F4)**:
   - Generates analog stimuli (DAC).
   - Samples analog signals (ADC) using DMA.
   - Streams digitized data to the host PC via UART/USB.
   - Executes simple self-tests and responds to commands.

2. **Host Tier (Laptop)**:
   - Provides a Python-based test application.
   - Sends configuration commands to the STM32.
   - Receives raw ADC data.
   - Performs histogram and FFT analysis.
   - Generates plots, metrics, and reports.
   - Stores data and documentation.

From the user’s perspective:

- The user runs a Python script or GUI on the laptop.
- The script configures the test, starts acquisition, and waits for data.
- After acquisition, the script analyzes the data and displays results.
- The user inspects plots, metrics, and optionally saves/export reports.

The system is **closed-loop in function** but **open-loop in control**:

- Closed-loop: DAC output can be fed back to ADC input for loopback tests.
- Open-loop: The PC controls the test sequence but does not form a real-time feedback control loop around the analog signals.

***

### 3. Functional Decomposition

The system is decomposed into the following major subsystems:

1. **Test Orchestration Subsystem (PC)**
2. **Analog Stimulus Subsystem (STM32 DAC)**
3. **Data Acquisition Subsystem (STM32 ADC + DMA)**
4. **Communication Subsystem (UART/USB)**
5. **Analysis & Metrics Subsystem (PC)**
6. **Visualization & Reporting Subsystem (PC)**
7. **Analog Front-End (AFE)**
8. **Self-Test & Diagnostics Subsystem (STM32)**

Each is described below.

#### 3.1 Test Orchestration Subsystem (PC)

**Purpose:**  
Coordinate the entire test process from the host side.

**Responsibilities:**

- Define test parameters (waveform type, sample count, sampling rate).
- Send configuration commands to the STM32.
- Trigger acquisition and wait for completion.
- Invoke analysis and reporting modules.
- Handle user errors (e.g., invalid parameters, communication failures).

**Inputs:**

- User-specified test configuration (CLI args, config file, or GUI inputs).
- Status/error messages from the STM32.

**Outputs:**

- Configuration commands to STM32.
- Raw data files (CSV/binary).
- Processed metrics (DNL/INL, THD/SNR).
- Plots and reports.

**Dependencies:**

- Communication Subsystem.
- Analysis & Metrics Subsystem.
- Visualization & Reporting Subsystem.

**Failure Conditions:**

- Unable to open serial port.
- STM32 does not respond within timeout.
- Corrupted or incomplete data frames.

**Future Expansion:**

- GUI-based test control.
- Batch test execution (multiple configurations).
- Integration with external instruments (e.g., power supply control).

#### 3.2 Analog Stimulus Subsystem (STM32 DAC)

**Purpose:**  
Generate analog test signals for characterization and loopback testing.

**Responsibilities:**

- Produce DC levels, ramps, and sine waves via DAC channels.
- Maintain stable amplitude and frequency under firmware control.
- Support multiple test profiles (e.g., low-frequency sine, full-scale ramp).

**Inputs:**

- Configuration commands from PC (waveform type, amplitude, frequency).
- Internal timing references (timers).

**Outputs:**

- Analog voltage on DAC output pins (0–3.3 V range).

**Dependencies:**

- Clocking infrastructure (timers, system clock).
- Configuration interface (UART command handler).

**Failure Conditions:**

- DAC not enabled or misconfigured.
- Clock/timer configuration errors.
- Overloading of DAC output (excessive current draw).

**Future Expansion:**

- Multi-tone or arbitrary waveform generation (via lookup tables).
- Synchronized multi-channel stimuli.

#### 3.3 Data Acquisition Subsystem (STM32 ADC + DMA)

**Purpose:**  
Capture analog signals with high fidelity and stream them to memory.

**Responsibilities:**

- Configure ADC channels and sampling parameters.
- Use DMA to transfer ADC results to RAM without CPU intervention.
- Ensure buffer integrity and completion notification.

**Inputs:**

- Analog signals on ADC input pins.
- Configuration commands (channels, sampling rate, sample count).

**Outputs:**

- Digital samples stored in RAM buffers.
- Completion flags/interrupts to signal end of acquisition.

**Dependencies:**

- ADC peripheral.
- DMA controller.
- Timer or trigger source for sampling.
- Configuration interface.

**Failure Conditions:**

- ADC not enabled or misconfigured.
- DMA misconfiguration leading to no data or corrupted data.
- Buffer overflow or underrun.

**Future Expansion:**

- Multi-channel simultaneous sampling.
- Interleaved ADC modes for higher effective sampling rates. [st](https://www.st.com/resource/en/datasheet/stm32f446re.pdf)

#### 3.4 Communication Subsystem (UART/USB)

**Purpose:**  
Provide a reliable channel for command and data exchange between STM32 and PC.

**Responsibilities:**

- Receive configuration commands from PC.
- Transmit ADC data buffers to PC.
- Provide status and error messages.
- Implement simple framing and error detection.

**Inputs:**

- Configuration commands and triggers from PC.
- ADC data buffers from Data Acquisition Subsystem.

**Outputs:**

- Acknowledgement and status messages to PC.
- Raw sample data streams to PC.

**Dependencies:**

- UART/USB peripheral on STM32.
- Serial interface on PC.

**Failure Conditions:**

- Baud rate mismatch.
- Framing or parity errors.
- Buffer underrun/overrun in UART/USB.

**Future Expansion:**

- Higher-speed interfaces (USB CDC, SPI-to-USB bridges).
- Binary protocols with CRC for robustness.

#### 3.5 Analysis & Metrics Subsystem (PC)

**Purpose:**  
Compute quantitative metrics from raw ADC data.

**Responsibilities:**

- Compute histograms and derive DNL/INL.
- Compute FFT and derive THD/SNR.
- Apply windowing, coherent sampling logic, and calibration factors.

**Inputs:**

- Raw ADC sample arrays.
- Test metadata (sampling rate, waveform type).

**Outputs:**

- DNL/INL arrays and summary statistics.
- THD/SNR values and spectral plots.

**Dependencies:**

- Data from Communication Subsystem.
- Numerical libraries (NumPy, SciPy).

**Failure Conditions:**

- Insufficient samples for meaningful analysis.
- Incorrect parameters (e.g., wrong sampling rate) leading to invalid results.

**Future Expansion:**

- ENOB (Effective Number of Bits) estimation.
- Advanced statistical analysis (e.g., jitter estimation).

#### 3.6 Visualization & Reporting Subsystem (PC)

**Purpose:**  
Present results to the user and persist them for documentation.

**Responsibilities:**

- Generate time-domain, histogram, DNL/INL, and FFT plots.
- Save plots and metrics to disk.
- Generate structured reports (CSV, HTML, or PDF).

**Inputs:**

- Metrics from Analysis Subsystem.
- Raw data (optional).

**Outputs:**

- PNG/SVG plots.
- CSV/HTML/PDF reports.

**Dependencies:**

- Matplotlib or similar.
- File system.

**Failure Conditions:**

- File permission errors.
- Plot generation failures due to invalid data.

**Future Expansion:**

- Interactive dashboards (e.g., Jupyter, web UI).
- Automated regression test reporting.

#### 3.7 Analog Front-End (AFE)

**Purpose:**  
Condition analog signals to ensure safe and accurate ADC/DAC operation.

**Responsibilities:**

- Scale DAC outputs if needed (e.g., divider for external circuits).
- Filter high-frequency noise (RC low-pass).
- Protect ADC inputs from overvoltage (diode clamps).

**Inputs:**

- DAC outputs.
- External test signals (if any).

**Outputs:**

- Conditioned signals to ADC inputs.

**Dependencies:**

- Passive components (resistors, capacitors, diodes).
- PCB/breadboard layout.

**Failure Conditions:**

- Incorrect component values leading to distortion.
- Open or short connections.
- Diodes installed backwards.

**Future Expansion:**

- Switched input ranges.
- Programmable gain stages (if budget allows).

#### 3.8 Self-Test & Diagnostics Subsystem (STM32)

**Purpose:**  
Provide basic health checks and error reporting.

**Responsibilities:**

- Perform DAC-to-ADC loopback tests.
- Check ADC/DAC configuration consistency.
- Report error codes to PC.

**Inputs:**

- Internal DAC outputs.
- ADC readings.

**Outputs:**

- Status/error codes to PC.
- Optional LED indicators.

**Dependencies:**

- DAC and ADC subsystems.
- Communication Subsystem.

**Failure Conditions:**

- Self-test logic errors.
- Inability to distinguish between hardware and configuration faults.

**Future Expansion:**

- Automated calibration routines.
- Extended diagnostics (e.g., temperature drift tests).

***

### 4. Context Diagram

The context diagram describes the system’s external entities and interactions.

**External Entities:**

1. **User/Operator**
   - Interactions:
     - Configures test parameters via Python script/GUI.
     - Initiates tests.
     - Reviews plots and reports.

2. **STM32F4 Board**
   - Note: Internally part of the system, but from the PC’s perspective it is an external entity providing analog I/O and data.
   - Interactions:
     - Receives configuration and trigger commands.
     - Sends raw ADC data and status messages.

3. **Power Source (USB)**
   - Interactions:
     - Supplies power to STM32 board.
     - May also provide data connectivity if USB-to-UART is integrated.

4. **Analog Test Environment**
   - Includes:
     - Breadboard with passive components.
     - Any external low-voltage signal sources (e.g., potentiometer, sensor).
   - Interactions:
     - Receives DAC outputs.
     - Provides signals to ADC inputs.

5. **File System / Storage**
   - Interactions:
     - Receives raw data, plots, and reports from PC.
     - Stores configuration files and logs.

**Interaction Summary:**

- User ↔ PC:
  - Provides test configuration.
  - Receives visual feedback and reports.
- PC ↔ STM32:
  - Sends commands and triggers.
  - Receives data and status.
- STM32 ↔ Analog Environment:
  - Drives analog signals.
  - Samples analog inputs.
- PC ↔ File System:
  - Writes data and reports.
  - Reads configuration.

**Diagram Description (for later drawing):**

- Central box: “μATE-STM System” (split into PC and STM32 sub-boxes).
- Surrounding boxes: User, Power (USB), Analog Environment, File System.
- Arrows:
  - User → PC: “Test config, Start command”.
  - PC → STM32: “Config, Trigger”.
  - STM32 → PC: “ADC data, Status”.
  - STM32 ↔ Analog Environment: “Analog signals”.
  - PC ↔ File System: “Data, Reports, Logs”.

***

### 5. High-Level Component Diagram

The high-level component diagram refines the context by showing internal major components and their connections.

**Major Components:**

1. **PC Test Application**
2. **STM32 Firmware**
   - Command Handler
   - DAC Waveform Generator
   - ADC + DMA Controller
   - UART/USB Driver
3. **Analog Front-End (AFE)**
4. **Data Storage & Reporting**

**Connections and Rationale:**

1. **PC Test Application ↔ STM32 Firmware (UART/USB)**
   - Purpose:
     - Command and control.
     - Data transfer.
   - Why it exists:
     - Separates real-time embedded tasks from flexible host-side analysis.
   - Characteristics:
     - Serial link (e.g., 115,200 baud or higher).
     - Simple ASCII or binary protocol.

2. **STM32 Firmware: Command Handler ↔ DAC Waveform Generator**
   - Purpose:
     - Translate high-level commands into DAC configurations.
   - Why it exists:
     - Encapsulates waveform generation logic.

3. **STM32 Firmware: Command Handler ↔ ADC + DMA Controller**
   - Purpose:
     - Configure acquisition parameters and trigger sampling.
   - Why it exists:
     - Centralizes ADC/DMA setup.

4. **DAC Waveform Generator ↔ AFE**
   - Purpose:
     - Deliver conditioned analog signals to the test environment.
   - Why it exists:
     - Ensures safe and appropriate signal levels.

5. **AFE ↔ ADC + DMA Controller**
   - Purpose:
     - Provide conditioned analog inputs to ADC.
   - Why it exists:
     - Protects ADC and improves measurement quality.

6. **ADC + DMA Controller ↔ UART/USB Driver**
   - Purpose:
     - Stream acquired data to PC.
   - Why it exists:
     - Enables host-side analysis.

7. **PC Test Application ↔ Data Storage & Reporting**
   - Purpose:
     - Persist raw data, metrics, plots, and reports.
   - Why it exists:
     - Documentation and traceability.

**Diagram Description (for later drawing):**

- Two main blocks: “PC” and “STM32”.
- Inside PC: “Test Application”, “Analysis & Metrics”, “Visualization & Reporting”, “Storage”.
- Inside STM32: “Command Handler”, “DAC Generator”, “ADC + DMA”, “UART/USB”.
- AFE shown as a separate block between DAC/ADC and “Analog Environment”.
- Arrows labeled with data types (commands, samples, analog signals).

***

### 6. Data Flow

The data flow describes how information moves through the system from physical signals to final reports.

#### 6.1 Acquisition Flow

1. **Analog Signal Generation**
   - DAC outputs analog voltage based on configured waveform.
   - AFE conditions the signal (scaling, filtering, protection).

2. **Analog-to-Digital Conversion**
   - ADC samples the conditioned analog signal at defined intervals.
   - Conversion results are 12-bit digital codes.

3. **DMA Transfer**
   - ADC results are automatically transferred to a RAM buffer by DMA.
   - Buffer size is predefined (e.g., 4k, 16k samples).

4. **Buffer Completion**
   - Upon filling the buffer, DMA triggers an interrupt or flag.
   - Firmware marks the buffer as ready for transmission.

**Data at this stage:**

- Raw 12-bit ADC codes in a contiguous memory buffer.

#### 6.2 Processing Flow

1. **Data Transmission**
   - Firmware sends the buffer over UART/USB to the PC.
   - Data may be framed with headers (e.g., length, test ID).

2. **Reception and Parsing**
   - PC application reads the byte stream.
   - Parses frames and reconstructs sample arrays.

3. **Preprocessing**
   - Optional steps:
     - Offset removal.
     - Scaling to voltage units using calibration factors.
     - Windowing for FFT.

**Data at this stage:**

- Arrays of samples (integer codes or scaled voltages).
- Metadata (sampling rate, test ID, timestamp).

#### 6.3 Storage Flow

1. **Raw Data Storage**
   - Raw sample arrays are saved to CSV or binary files.
   - Metadata stored alongside (e.g., in header or sidecar JSON).

2. **Processed Data Storage**
   - Metrics (DNL/INL arrays, THD/SNR values) saved to CSV.
   - Summary statistics saved to structured formats.

**Data at this stage:**

- Files in `data/raw/` and `data/processed/`.

#### 6.4 Visualization Flow

1. **Plot Generation**
   - Time-domain plot of samples.
   - Histogram of code occurrences.
   - DNL/INL vs code index.
   - FFT magnitude vs frequency.

2. **Display**
   - Plots shown in matplotlib windows or saved as images.

**Data at this stage:**

- PNG/SVG files in `data/plots/`.

#### 6.5 Reporting Flow

1. **Report Assembly**
   - Metrics, plots, and metadata combined into a structured report.
   - Optional HTML/PDF generation.

2. **Archival**
   - Reports saved to `data/reports/`.
   - Versioned alongside code and configuration.

**Data at this stage:**

- Final test reports for documentation and review.


### 6.7 Control Flow

This section describes the complete execution sequence from power-on until report generation. The description is structured to support creation of a UML sequence diagram and a state machine diagram for the embedded firmware.

#### 6.7.1 Power-On and Hardware Initialization

**Sequence:**

1. **Power Applied**
   - USB power applied to STM32 board and laptop.
   - On-board regulators stabilize; MCU reset released.

2. **STM32 Boot**
   - STM32 boots from flash; vector table loaded.
   - `SystemInit()` configures clocks (PLL, AHB, APB).
   - Default peripherals disabled; GPIOs in reset state.

3. **Firmware Initialization (STM32)**
   - **Clock tree configuration**:
     - System clock (e.g., 168 MHz for F446/447).
     - ADC clock derived from APB2 (subject to max ADC clock limit per datasheet). [st](https://www.st.com/resource/en/datasheet/stm32f446re.pdf)
     - Timer clocks for DAC/ADC triggers.
   - **Peripheral initialization order**:
     1. GPIO (for ADC/DAC pins, UART TX/RX, status LED).
     2. UART/USB (for debug and host communication).
     3. Timers (for DAC update and ADC trigger).
     4. DAC (in basic mode, disabled initially).
     5. ADC (in scan/continuous or triggered mode, disabled initially).
     6. DMA (associated with ADC stream, configured but not enabled).
     7. NVIC (interrupt priorities for DMA, UART, timers).
   - **Firmware state machine initialized**:
     - State: `IDLE`.
     - Buffers allocated in RAM.
     - Global flags cleared.

4. **PC Application Startup**
   - User launches Python test application.
   - Application enumerates serial ports; user selects COM port.
   - PC state: `WAITING_FOR_USER_COMMAND`.

**UML Lifelines:**

- `User`
- `PC_App`
- `STM32_Firmware`
- `STM32_HAL` (representing HAL/LL drivers)
- `Peripherals` (ADC, DAC, DMA, UART, Timers)

**Messages (Power-On Phase):**

- `User → PC_App`: “Launch application”
- `PC_App → PC_App`: “Enumerate serial ports”
- `STM32_Firmware → STM32_HAL`: “SystemInit()”
- `STM32_HAL → Peripherals`: “Configure clocks, GPIO, UART, Timers, DAC, ADC, DMA”

***

#### 6.7.2 Test Configuration and Command Parsing

**Sequence:**

1. **User Specifies Test**
   - User selects test type (e.g., “Ramp Histogram”, “Sine FFT”).
   - User sets parameters:
     - Sample count (e.g., 50,000).
     - Sampling rate (e.g., 100 kSPS).
     - DAC waveform parameters (amplitude, frequency).

2. **PC Sends Configuration Command**
   - PC constructs a configuration packet (see Section 6.9).
   - PC sends packet over UART/USB to STM32.
   - PC transitions to state: `WAITING_FOR_ACK`.

3. **STM32 Receives and Parses Command**
   - UART RX interrupt or polling receives bytes.
   - Command handler:
     - Validates packet (length, checksum/CRC).
     - Decodes command type and parameters.
   - If valid:
     - Update internal test configuration.
     - Transition state: `IDLE → CONFIGURED`.
     - Send ACK response to PC.
   - If invalid:
     - Send NACK with error code.
     - Remain in `IDLE`.

4. **PC Receives ACK**
   - PC validates ACK.
   - PC transitions to state: `READY_TO_START`.

**UML Messages (Configuration Phase):**

- `User → PC_App`: “Set test parameters”
- `PC_App → STM32_Firmware`: “SEND_CONFIG_CMD(params)”
- `STM32_Firmware → STM32_Firmware`: “Parse command, validate”
- `STM32_Firmware → PC_App`: “ACK / NACK(error_code)”

***

#### 6.7.3 Start Test and Acquisition Sequence

**Sequence:**

1. **User Starts Test**
   - User clicks “Start Test” or runs script.
   - PC sends `START_TEST` command to STM32.
   - PC transitions to state: `ACQUIRING`.

2. **STM32 Configures Peripherals for Test**
   - Based on stored configuration:
     - Configure timer for DAC update rate.
     - Configure timer for ADC trigger rate (or same timer in synchronized mode).
     - Configure DAC:
       - Load waveform LUT or enable ramp mode.
       - Enable DAC output.
     - Configure ADC:
       - Select channels, sample time, resolution (12-bit).
       - Enable continuous or triggered mode.
     - Configure DMA:
       - Set source (ADC data register), destination (RAM buffer), transfer count.
       - Enable DMA stream.
   - Enable ADC and start timer triggers.
   - Transition state: `CONFIGURED → ACQUIRING`.

3. **Data Acquisition**
   - Timer triggers ADC conversions at defined rate.
   - Each conversion complete event:
     - ADC data register updated.
     - DMA automatically transfers data to RAM buffer.
   - CPU remains free (except for interrupt handling if used).

4. **DMA Completion**
   - When transfer count reached, DMA triggers interrupt or sets flag.
   - DMA interrupt handler:
     - Disable ADC and DMA (or reconfigure for next buffer if multi-buffer).
     - Transition state: `ACQUIRING → DATA_READY`.
     - Optionally toggle status LED.

**UML Messages (Acquisition Phase):**

- `User → PC_App`: “Start test”
- `PC_App → STM32_Firmware`: “START_TEST”
- `STM32_Firmware → Peripherals`: “Configure Timers, DAC, ADC, DMA”
- `Peripherals → STM32_Firmware`: “DMA complete interrupt”
- `STM32_Firmware → STM32_Firmware`: “State: ACQUIRING → DATA_READY”

***

#### 6.7.4 Data Transmission to PC

**Sequence:**

1. **PC Polls or Waits for Data**
   - PC may:
     - Poll status via a `GET_STATUS` command, or
     - Wait for STM32 to autonomously send data after acquisition.

2. **STM32 Sends Data**
   - In `DATA_READY` state:
     - Firmware formats data into packets (with headers, length, test ID).
     - Sends packets over UART/USB.
   - After full buffer sent:
     - Send `END_OF_DATA` marker or final packet flag.
     - Transition state: `DATA_READY → IDLE` (or `WAITING_FOR_NEXT_CMD`).

3. **PC Receives and Assembles Data**
   - PC reads bytes, reassembles frames.
   - Validates checksum/CRC per packet.
   - On `END_OF_DATA`:
     - Transition state: `ACQUIRING → PROCESSING`.

**UML Messages (Transmission Phase):**

- `STM32_Firmware → PC_App`: “DATA_PACKET(n)”
- `PC_App → PC_App`: “Assemble buffer, validate CRC”
- `STM32_Firmware → PC_App`: “END_OF_DATA”

***

#### 6.7.5 PC Processing and Report Generation

**Sequence:**

1. **Preprocessing**
   - PC applies:
     - Scaling (codes to volts, if desired).
     - Windowing (for FFT).
     - Offset removal.

2. **Analysis**
   - Histogram analysis:
     - Build code histogram.
     - Compute DNL/INL.
   - FFT analysis:
     - Compute magnitude spectrum.
     - Identify fundamental and harmonics.
     - Compute THD/SNR.

3. **Visualization**
   - Generate plots:
     - Time-domain waveform.
     - Histogram.
     - DNL/INL vs code.
     - FFT magnitude vs frequency.

4. **Report Generation**
   - Assemble metrics and plots into report structure.
   - Save:
     - Raw data (CSV/binary).
     - Processed metrics (CSV).
     - Plots (PNG/SVG).
     - Report (HTML/PDF).

5. **User Notification**
   - Display “Test Complete” message.
   - Show key metrics and plots.
   - Transition state: `PROCESSING → COMPLETE`.

**UML Messages (Processing Phase):**

- `PC_App → PC_App`: “Compute histogram, DNL/INL”
- `PC_App → PC_App`: “Compute FFT, THD/SNR”
- `PC_App → Storage`: “Save data, plots, report”
- `PC_App → User`: “Test complete, show results”

***

#### 6.7.6 Shutdown Sequence

**Normal Shutdown:**

1. **User Exits Application**
   - User closes Python application or ends script.
   - PC sends optional `SHUTDOWN` or `RESET` command to STM32.

2. **STM32 Enters Safe State**
   - Firmware:
     - Disables DAC outputs (or sets to 0 V).
     - Disables ADC and timers.
     - Clears buffers.
     - Returns to `IDLE` or enters low-power mode.

3. **Power Removal**
   - User disconnects USB or leaves board powered.

**Abnormal Shutdown (PC Crash or Disconnect):**

- STM32:
  - Detects UART timeout or lack of activity.
  - After timeout, disables DAC/ADC and enters safe idle state.
  - LED pattern indicates fault or idle.

***

### 6.8 Timing Architecture

This section quantifies timing behavior and constraints. Calculations use typical STM32F446 parameters (system clock up to 168 MHz, ADC max clock ~36 MHz, 12-bit resolution). Exact values depend on specific MCU and configuration; these are representative for architectural planning. [st](https://www.st.com/resource/en/datasheet/stm32f446re.pdf)

#### 6.8.1 ADC Timing

**Key Parameters:**

- ADC resolution: 12 bits.
- ADC clock: ≤ 36 MHz (per datasheet).
- Sample time: configurable (e.g., 3, 15, 28, … cycles).
- Conversion time (12-bit):
$$
T_{\text{conv}} = T_{\text{sample}} + 12 \text{ cycles}
$$

**Example:**

- ADC clock = 36 MHz → \(T_{\text{clk}} = 27.78\) ns.
- Sample time = 15 cycles.
- Conversion cycles = 15 + 12 = 27 cycles.
- Conversion time:
$$
T_{\text{conv}} = 27 \times 27.78 \text{ ns} \approx 750 \text{ ns}
$$
- Maximum theoretical sampling rate:
$$
f_s = \frac{1}{T_{\text{conv}}} \approx 1.33 \text{ MSPS}
$$

In practice, due to timer overhead and DMA, a **sustainable rate of 200 kSPS–1 MSPS** is a realistic target for initial designs.

#### 6.8.2 DAC Timing

**Key Parameters:**

- DAC resolution: 12 bits.
- DAC update triggered by timer.
- Timer clock derived from APB1 (max 42 MHz for F446).

**Example:**

- Timer clock = 84 MHz (with APB1 prescaler).
- Desired update rate = 100 kSPS.
- Timer period:
$$
\text{ARR} = \frac{f_{\text{timer}}}{f_{\text{update}}} - 1 = \frac{84 \times 10^6}{100 \times 10^3} - 1 = 839
$$

This yields a 100 kSPS DAC update rate with ample CPU headroom.

#### 6.8.3 Timer Configuration Philosophy

- Use **one timer for DAC updates** and **one timer for ADC triggers**, optionally synchronized.
- For coherent sampling:
  - Ensure:
$$
f_{\text{signal}} = \frac{M}{N} f_s
$$
    where \(M\) is integer cycles, \(N\) is FFT size, \(f_s\) is sampling rate.
- Timer prescalers and auto-reload registers chosen to hit desired rates within integer constraints.

#### 6.8.4 DMA Timing

- DMA operates independently of CPU once configured.
- DMA transfer time per sample:
  - 16-bit transfer, DMA clock ~84 MHz.
  - Transfer time per sample ≈ tens of nanoseconds, negligible vs ADC conversion time.
- DMA ensures no sample loss up to high sampling rates, provided:
  - DMA stream priority is sufficient.
  - No bus contention bottlenecks.

#### 6.8.5 UART Throughput Calculations

**Example Configuration:**

- Baud rate: 115,200 bps.
- Frame: 1 start, 8 data, 1 stop = 10 bits per byte.
- Effective throughput:
$$
\frac{115,200}{10} = 11,520 \text{ bytes/s}
$$
- For 16-bit samples (2 bytes):
$$
\text{Max sample rate} \approx \frac{11,520}{2} \approx 5,760 \text{ samples/s}
$$

This is a bottleneck for high-speed acquisition.

**Mitigation Strategies:**

- Increase baud rate (e.g., 921,600 or 2 Mbps if supported and reliable).
- Use binary framing (no ASCII overhead).
- For very high rates, consider:
  - USB CDC (higher throughput).
  - On-board logging (e.g., SD card) as a stretch goal.

**Example at 921,600 baud:**

- Throughput:
$$
\frac{921,600}{10} = 92,160 \text{ bytes/s} \Rightarrow \approx 46,000 \text{ samples/s}
$$

Sufficient for 10k–50k sample tests in 1–2 seconds of streaming.

#### 6.8.6 Buffer Sizing Calculations

**Design Goals:**

- Capture 10k–100k samples per test.
- Fit within available RAM (STM32F446 has 128 kB SRAM).

**Example:**

- Sample size: 16 bits (2 bytes).
- Buffer for 50k samples:
$$
50,000 \times 2 = 100,000 \text{ bytes} \approx 97.7 \text{ kB}
$$

This leaves ~30 kB for stack, heap, and other variables, which is acceptable but tight.

**Architectural Choice:**

- Use **16k–32k sample buffers** as default.
- Support **multi-buffer acquisition** (e.g., 4 × 16k) if needed, with careful memory management.

#### 6.8.7 Latency and Throughput

**Worst-Case Latency:**

- From “Start Test” to first sample:
  - Timer setup + DAC/ADC enable ≈ few hundred microseconds.
- From last sample to PC receiving first byte:
  - DMA completion + UART framing ≈ milliseconds depending on baud rate.

**Best-Case Latency:**

- With high baud rate and small buffers, end-to-end test can complete in < 1 second.

**Throughput Bottlenecks:**

- UART speed is the dominant bottleneck for data transfer.
- ADC conversion time is the dominant bottleneck for sampling rate.

#### 6.8.8 Sampling Limitations

- Nyquist limit:
  - Maximum measurable signal frequency:
$$
f_{\text{max}} = \frac{f_s}{2}
$$
  - For \(f_s = 200\) kSPS → \(f_{\text{max}} = 100\) kHz.
- Anti-aliasing:
  - AFE should include low-pass filter with cutoff < \(f_s/2\).

#### 6.8.9 Clock Tree Assumptions

- System clock: 168 MHz (typical for F446/447).
- AHB: 168 MHz.
- APB2 (ADC): 84 MHz (with prescaler to keep ADC clock ≤ 36 MHz).
- APB1 (DAC, timers): 42–84 MHz depending on configuration.

Exact configuration must respect datasheet limits. [st](https://www.st.com/resource/en/datasheet/stm32f446re.pdf)

#### 6.8.10 Synchronization Strategy

- DAC and ADC triggered by **synchronized timers**:
  - Same timer clock source.
  - Optionally same timer with different channels.
- Ensures deterministic phase relationship between stimulus and sampling.
- Critical for coherent sampling and repeatable FFT results.

***

### 6.9 Communication Architecture

This section defines the UART-based communication protocol between PC and STM32.

#### 6.9.1 Physical Interface

- **Medium**:
  - USB-to-UART bridge (on-board or external).
  - TX, RX, GND lines.
- **Voltage**:
  - 3.3 V logic (typical for STM32).
- **Connector**:
  - USB Type-B/Micro for PC side.
  - Header or onboard USB for STM32.

#### 6.9.2 Transport Layer

- **Asynchronous serial**.
- **Parameters** (initial):
  - Baud: 115,200 (configurable up to 921,600 or higher).
  - Data: 8 bits.
  - Parity: None.
  - Stop: 1 bit.
  - Flow control: None (initially).

#### 6.9.3 Packet/Frame Format

**General Frame Structure:**

- `[SYNC][LENGTH][CMD/RESP][PAYLOAD][CRC16]`

Fields:

- `SYNC`: 1 byte (e.g., 0xAA) to identify frame start.
- `LENGTH`: 1 byte, payload length (0–254 bytes).
- `CMD/RESP`: 1 byte, command or response code.
- `PAYLOAD`: 0–254 bytes, command/response data.
- `CRC16`: 2 bytes, CRC over LENGTH, CMD/RESP, PAYLOAD.

**Byte Ordering:**

- Multi-byte fields: little-endian.
- CRC16: low byte first, then high byte.

#### 6.9.4 Command Structure

**Command Codes (Examples):**

- `0x01`: `CONFIG_TEST`
- `0x02`: `START_TEST`
- `0x03`: `GET_STATUS`
- `0x04`: `RESET`

**Example: CONFIG_TEST Payload:**

- Byte 0: Test type (0 = ramp, 1 = sine).
- Byte 1–2: Sample count (16-bit, little-endian).
- Byte 3–4: Sampling rate index (mapped to predefined rates).
- Byte 5: DAC amplitude index.
- Byte 6: DAC frequency index.

#### 6.9.5 Response Structure

**Response Codes:**

- `0x80`: `ACK`
- `0x81`: `NACK`
- `0x82`: `STATUS`
- `0x83`: `DATA_START`
- `0x84`: `DATA_PACKET`
- `0x85`: `END_OF_DATA`

**ACK Payload:**

- Empty or status byte.

**NACK Payload:**

- Byte 0: Error code (e.g., 0x01 = invalid command, 0x02 = invalid parameters).

**DATA_PACKET Payload:**

- Byte 0–1: Packet index (16-bit).
- Byte 2–N: Sample data (2 bytes per sample).

#### 6.9.6 Error Messages

- NACK with error codes:
  - `0x01`: Invalid command.
  - `0x02`: Invalid length.
  - `0x03`: CRC error.
  - `0x04`: Invalid parameters.
  - `0x05`: Hardware fault (ADC/DAC error).

#### 6.9.7 Timeouts

- PC timeouts:
  - Command ACK: 100 ms.
  - Data packet inter-arrival: 500 ms.
- STM32 timeouts:
  - Host inactivity: 5 s → enter safe idle.

#### 6.9.8 CRC Strategy

- CRC16-CCITT over frame (excluding SYNC and CRC itself).
- Detected CRC errors → NACK with error code `0x03`.
- PC retries failed packets up to 3 times.

#### 6.9.9 Recovery After Communication Failure

- PC:
  - On timeout or repeated NACK:
    - Retry command up to 3 times.
    - If still failing, prompt user to check connection and reset STM32.
- STM32:
  - On repeated bad frames:
    - Log error internally (optional).
    - Continue listening; no state change unless valid command received.

#### 6.9.10 Versioning Strategy

- Protocol version encoded in:
  - A `GET_VERSION` command/response.
  - Response includes:
    - Major, minor version.
    - Supported command set bitmap.
- PC checks version at startup; adapts behavior if needed.

#### 6.9.11 Example Command Packets

**Example 1: CONFIG_TEST (Ramp, 10k samples, rate index 3, amp index 2, freq index 0)**

- SYNC: `0xAA`
- LENGTH: `0x06` (6-byte payload)
- CMD: `0x01`
- PAYLOAD:
  - Test type: `0x00`
  - Sample count: `0x10 0x27` (10,000 = 0x2710, little-endian → 0x10 0x27)
  - Rate index: `0x03`
  - Amp index: `0x02`
  - Freq index: `0x00`
- CRC16: computed over `0x06 0x01 0x00 0x10 0x27 0x03 0x02 0x00`

**Example 2: ACK Response**

- SYNC: `0xAA`
- LENGTH: `0x00`
- RESP: `0x80`
- PAYLOAD: (none)
- CRC16: computed over `0x00 0x80`

***

### 6.10 Interface Specifications

This section defines interfaces for each subsystem using specification tables.

#### 6.10.1 Test Orchestration Subsystem (PC)

| Interface | Direction | Data Type | Units | Valid Range | Update Rate | Timing Req. | Error Conditions |
|----------|-----------|-----------|-------|-------------|-------------|-------------|------------------|
| User → Test Config | In | Struct (test type, params) | N/A | As per UI | On user action | < 1 s response | Invalid params |
| Test Config → Comm Subsystem | Out | Command packet | Bytes | 4–255 bytes/frame | As needed | < 100 ms to STM32 ACK | Comm failure |
| Comm Subsystem → Test Orch | In | Response packet | Bytes | 3–257 bytes/frame | As needed | Timeout 100 ms | NACK, timeout |
| Test Orch → Analysis | Out | Sample array | uint16 or float | 0–65535 or volts | Per test | N/A | Insufficient data |
| Test Orch → Reporting | Out | Metrics, plots | Struct, images | N/A | Per test | N/A | File I/O error |

#### 6.10.2 Analog Stimulus Subsystem (STM32 DAC)

| Interface | Direction | Data Type | Units | Valid Range | Update Rate | Timing Req. | Error Conditions |
|----------|-----------|-----------|-------|-------------|-------------|-------------|------------------|
| Command Handler → DAC Gen | In | Config (waveform, amp, freq) | N/A | Enum, indices | Per test | < 1 ms apply | Invalid config |
| DAC Gen → AFE | Out | Analog voltage | V | 0–3.3 V (nominal) | Up to ~100 kSPS | Deterministic | Overload, distortion |
| DAC Gen → Timers | In | Timer trigger | N/A | N/A | Configured rate | Jitter < 1% period | Timer misconfig |

#### 6.10.3 Data Acquisition Subsystem (STM32 ADC + DMA)

| Interface | Direction | Data Type | Units | Valid Range | Update Rate | Timing Req. | Error Conditions |
|----------|-----------|-----------|-------|-------------|-------------|-------------|------------------|
| Command Handler → ADC Ctrl | In | Config (channels, rate, count) | N/A | Enums, integers | Per test | < 1 ms apply | Invalid config |
| AFE → ADC Ctrl | In | Analog voltage | V | 0–3.3 V (safe range) | Up to fs | Sampling jitter | Overvoltage, noise |
| ADC Ctrl → DMA | Out | 12-bit codes | LSB | 0–4095 | fs | Deterministic | DMA error |
| DMA → RAM | Out | Sample buffer | uint16 | 0–65535 | fs | No loss up to design fs | Buffer overflow |

#### 6.10.4 Communication Subsystem (UART/USB)

| Interface | Direction | Data Type | Units | Valid Range | Update Rate | Timing Req. | Error Conditions |
|----------|-----------|-----------|-------|-------------|-------------|-------------|------------------|
| PC → UART Driver | In | Command packets | Bytes | 4–255 bytes | As needed | ACK < 100 ms | Framing, CRC error |
| UART Driver → PC | Out | Response/data packets | Bytes | 3–257 bytes | As needed | Inter-packet < 500 ms | Overrun, timeout |
| UART Driver ↔ ADC/DAC | Internal | Buffers, status | N/A | N/A | N/A | N/A | Driver fault |

#### 6.10.5 Analysis & Metrics Subsystem (PC)

| Interface | Direction | Data Type | Units | Valid Range | Update Rate | Timing Req. | Error Conditions |
|----------|-----------|-----------|-------|-------------|-------------|-------------|------------------|
| Test Orch → Analysis | In | Sample array | uint16/float | N/A | Per test | < 5 s for 50k samples | Invalid data |
| Analysis → Test Orch | Out | Metrics (DNL/INL, THD/SNR) | Float, arrays | N/A | Per test | N/A | Algorithm error |

#### 6.10.6 Visualization & Reporting Subsystem (PC)

| Interface | Direction | Data Type | Units | Valid Range | Update Rate | Timing Req. | Error Conditions |
|----------|-----------|-----------|-------|-------------|-------------|-------------|------------------|
| Analysis → Viz/Report | In | Metrics, samples | Float, arrays | N/A | Per test | < 2 s plot gen | Plot error |
| Viz/Report → Storage | Out | Files (CSV, PNG, HTML) | N/A | N/A | Per test | < 1 s write | File error |

***

### 6.11 Error Handling Architecture

This section defines a formal fault handling strategy across hardware, firmware, and PC software.

#### 6.11.1 Hardware Faults

**Types:**

- ADC peripheral fault (e.g., clock error, overtemperature).
- DAC fault (e.g., output short).
- UART/USB physical layer fault (disconnected, noise).
- Power fault (undervoltage, brownout).

**Detection:**

- STM32 hardware flags (e.g., ADC error flags).
- Voltage monitoring (brownout reset).
- UART framing/overrun errors.

**Response:**

- Set internal fault flag.
- Disable affected peripheral (ADC/DAC).
- Send fault status to PC (if comm available).
- Enter safe state (DAC off, ADC off).

#### 6.11.2 Firmware Faults

**Types:**

- Invalid configuration (e.g., unsupported sampling rate).
- DMA misconfiguration (e.g., wrong buffer address).
- Timer configuration error.

**Detection:**

- Parameter validation before applying config.
- HAL/LL error returns.
- DMA/ADC error interrupts.

**Response:**

- NACK command with error code.
- Log fault internally (optional).
- Remain in `IDLE` or `CONFIGURED` state; do not start acquisition.

#### 6.11.3 Communication Faults

**Types:**

- CRC errors.
- Framing/parity errors.
- Timeout (no response).

**Detection:**

- CRC check on each frame.
- UART error flags.
- PC-side timeout on expected responses.

**Response:**

- NACK with error code for CRC/framing errors.
- PC retries command up to 3 times.
- After repeated failures, PC prompts user to check connection and reset.

#### 6.11.4 User Errors

**Types:**

- Invalid test parameters (e.g., sample count too large).
- Wrong COM port selected.
- Incorrect wiring (e.g., DAC output not connected to ADC input).

**Detection:**

- Parameter range checks in PC.
- Comm failure on wrong COM port.
- Unexpected ADC readings (e.g., all zeros or constant).

**Response:**

- PC displays clear error message.
- Suggest corrective actions.
- Prevent test start until parameters are valid.

#### 6.11.5 Recovery Strategy

- **Transient faults** (e.g., single CRC error):
  - Retry packet/command.
- **Persistent faults** (e.g., repeated NACK):
  - Abort test.
  - Return to `IDLE`.
  - Prompt user intervention.
- **Hardware faults**:
  - Disable peripherals.
  - Require reset or power cycle.

#### 6.11.6 Logging

- STM32:
  - Optional internal fault log (last N error codes).
  - Exposed via `GET_STATUS` or debug command.
- PC:
  - Log all commands, responses, and errors to a text file.
  - Include timestamps and error codes.

#### 6.11.7 Retry Policy

- PC:
  - Max 3 retries per command/packet.
  - Exponential backoff (e.g., 100 ms, 200 ms, 400 ms).
- STM32:
  - No automatic retry; waits for new command.

#### 6.11.8 Safe-State Behavior

- Safe state defined as:
  - DAC outputs disabled or set to 0 V.
  - ADC and timers disabled.
  - UART active for status/reporting.
  - LED in known pattern (e.g., slow blink).

All fault paths lead to safe state unless a catastrophic hardware fault occurs.

#### 6.11.9 Fault Propagation

- Hardware fault → Firmware fault handler → Safe state → PC notification.
- Communication fault → PC retry → If persistent → User notification.
- User error → PC validation → No command sent → No fault in firmware.

***

### 6.12 Architectural Verification

Before implementation, the architecture itself must be verified for correctness, feasibility, and completeness.

#### 6.12.1 Architecture Review Checklist

- **Requirements coverage**:
  - Every functional requirement mapped to at least one subsystem.
  - Every non-functional requirement addressed (timing, reliability, cost).
- **Interface completeness**:
  - All subsystem interfaces defined (inputs, outputs, data types).
  - No orphaned signals or data flows.
- **Timing feasibility**:
  - ADC/DAC rates achievable within MCU limits.
  - UART throughput sufficient for target sample counts.
- **Error handling**:
  - All identified fault types have detection and recovery paths.
- **Scalability**:
  - Clear paths for adding channels or features.

#### 6.12.2 Interface Verification

- Simulate or walk through:
  - Command/response exchanges.
  - Data flow from ADC to PC.
- Check for:
  - Data type mismatches.
  - Missing error codes.
  - Inconsistent units or ranges.

#### 6.12.3 Timing Verification

- Analytical checks:
  - Confirm ADC conversion time and max sampling rate.
  - Confirm UART throughput vs required data volume.
- Identify:
  - Bottlenecks (e.g., UART).
  - Margins (e.g., CPU load during acquisition).

#### 6.12.4 Communication Verification

- Verify:
  - Protocol supports all required commands.
  - Error codes cover anticipated faults.
  - Timeout values are realistic given worst-case latencies.

#### 6.12.5 Scalability Verification

- Assess:
  - Memory headroom for larger buffers.
  - CPU headroom for additional features.
  - UART bandwidth limits and potential need for higher-speed interfaces.

#### 6.12.6 Design Review Criteria

- **Clarity**:
  - Can a new engineer understand the architecture from this document?
- **Feasibility**:
  - Are all performance targets achievable with given hardware?
- **Robustness**:
  - Are fault scenarios adequately addressed?
- **Maintainability**:
  - Is the decomposition modular and understandable?
- **Traceability**:
  - Can each requirement be traced to architecture elements?

***

### 6.13 Relevant Standards

This architecture aligns with or references the following standards and best practices:

- **ARM Cortex-M Architecture**:
  - ARMv7-M architecture for STM32F4.
  - NVIC, interrupt priorities, and exception model.
- **STM32 Reference Manual and Datasheet**:
  - ADC, DAC, DMA, UART, and timer configurations per ST documentation. [st](https://www.st.com/resource/en/datasheet/stm32f446re.pdf)
- **UART Standards**:
  - Asynchronous serial communication (8N1 typical).
  - Voltage levels per STM32 GPIO specs (3.3 V logic).
- **IEEE Terminology for Data Converters**:
  - Definitions of DNL, INL, THD, SNR, ENOB per IEEE standards (e.g., IEEE Std 1241 for ADC testing).
- **Software Architecture Best Practices**:
  - Layered architecture (embedded vs host).
  - Clear interface definitions and separation of concerns.
- **Systems Engineering Documentation Practices**:
  - Use of context diagrams, functional decomposition, interface tables.
  - Architecture Decision Records (ADRs).

Adherence to these standards ensures the project uses accepted terminology and methodologies, improving its credibility and transferability.

***

### 6.14 Architecture Decision Record (ADR)

This section records major architectural decisions in a formal ADR format.

***

#### ADR-001: Use STM32F4 as Primary Mixed-Signal Engine

**Decision:**  
Use the existing STM32F446/447-class MCU as the core analog stimulus and measurement engine.

**Alternatives Considered:**

- Arduino + sound card.
- Pure software simulation.
- External USB oscilloscope/function generator (if budget allowed).

**Advantages:**

- Real mixed-signal hardware with 12-bit ADC/DAC.
- High sampling rates (up to ~2.4 MSPS ADC). [st](https://www.st.com/resource/en/datasheet/stm32f446re.pdf)
- Deep embedded learning (timers, DMA, UART).
- Minimal additional cost.

**Disadvantages:**

- Limited to 3.3 V domain.
- Requires embedded firmware development.
- UART throughput limits data transfer.

**Risks:**

- Learning curve for STM32 peripherals.
- Potential misconfiguration of ADC/DAC.

**Justification:**

- Maximizes learning per rupee.
- Provides realistic non-ideal behavior for testing education.
- Fits within budget and hardware availability constraints.

**Future Implications:**

- Foundation for more advanced mixed-signal projects.
- Can be extended with additional sensors and interfaces.

***

#### ADR-002: PC-Based Analysis and Visualization

**Decision:**  
Perform all analysis (histogram, FFT) and visualization on the laptop using Python.

**Alternatives Considered:**

- On-MCU analysis with results-only transfer.
- Dedicated DSP or FPGA for analysis.

**Advantages:**

- Leverages powerful CPU and libraries (NumPy, SciPy, Matplotlib).
- Simplifies firmware (no need for complex math on MCU).
- Easy to extend and modify analysis algorithms.

**Disadvantages:**

- Requires reliable high-volume data transfer.
- Latency due to data streaming.

**Risks:**

- UART bottleneck for large datasets.
- Dependency on PC environment.

**Justification:**

- Aligns with educational goals (Python data analysis).
- Keeps firmware simple and focused on real-time tasks.

**Future Implications:**

- Easy to add advanced analysis (e.g., ENOB, jitter estimation).
- Can later migrate some analysis to MCU if needed.

***

#### ADR-003: UART-Based Communication Protocol

**Decision:**  
Use UART (via USB-to-UART) as the primary communication channel between PC and STM32.

**Alternatives Considered:**

- USB CDC (device-side).
- SPI-to-USB bridge.
- Wi-Fi/Bluetooth modules.

**Advantages:**

- Simple to implement (UART peripheral, `pyserial` on PC).
- Widely supported, low-cost.
- Sufficient for initial data rates (10k–50k samples).

**Disadvantages:**

- Limited throughput compared to USB CDC.
- Susceptible to noise and framing errors.

**Risks:**

- May become a bottleneck for high-speed, large-buffer tests.
- Requires careful framing and error handling.

**Justification:**

- Matches existing hardware (most STM32 boards have UART/USB).
- Adequate for educational-scale data volumes.

**Future Implications:**

- Can upgrade to USB CDC or other higher-speed interfaces later.
- Protocol designed to be transport-agnostic (can be adapted).

***

#### ADR-004: DMA-Based ADC Acquisition

**Decision:**  
Use DMA to transfer ADC conversion results directly to RAM without CPU intervention.

**Alternatives Considered:**

- Polling ADC data register.
- Interrupt-driven single-sample acquisition.

**Advantages:**

- Minimizes CPU load during acquisition.
- Enables high sampling rates without sample loss.
- Simplifies timing analysis.

**Disadvantages:**

- More complex initial configuration.
- Debugging DMA issues can be tricky.

**Risks:**

- Misconfiguration can lead to silent data loss.
- Buffer overflow if not properly managed.

**Justification:**

- Essential for achieving target sampling rates (100 kSPS+).
- Standard practice in embedded data acquisition.

**Future Implications:**

- Foundation for multi-buffer and interleaved ADC modes.
- Transferable skill to other high-speed acquisition projects.

***

#### ADR-005: Simple Binary Protocol with CRC16

**Decision:**  
Implement a simple binary framing protocol with CRC16 for command and data exchange.

**Alternatives Considered:**

- ASCII-based protocol (e.g., CSV over UART).
- Complex protocol stacks (e.g., custom TCP-like layers).

**Advantages:**

- Low overhead (binary vs ASCII).
- Robust error detection (CRC16).
- Simple to implement on both sides.

**Disadvantages:**

- Less human-readable than ASCII.
- Requires careful implementation of CRC and framing.

**Risks:**

- Bugs in CRC or framing can cause silent data corruption.
- Versioning needed if protocol evolves.

**Justification:**

- Balances simplicity and robustness.
- Suitable for educational project with potential for extension.

**Future Implications:**

- Can evolve to include compression, encryption, or more advanced features.
- Protocol versioning allows backward compatibility.

***

#### ADR-006: Modular Subsystem Decomposition

**Decision:**  
Decompose the system into clearly defined subsystems (Test Orchestration, Stimulus, Acquisition, Communication, Analysis, Visualization, AFE, Self-Test).

**Alternatives Considered:**

- Monolithic firmware and software.
- Different decomposition (e.g., by hardware vs software only).

**Advantages:**

- Clear responsibilities and interfaces.
- Facilitates parallel development and testing.
- Improves maintainability and extensibility.

**Disadvantages:**

- Slightly more upfront design effort.
- Requires disciplined interface management.

**Risks:**

- Over-engineering for a small project.
- Interface mismatches if not carefully documented.

**Justification:**

- Aligns with systems engineering best practices.
- Supports future expansion and reuse.

**Future Implications:**

- Easier to add new features (e.g., additional sensors).
- Clear structure for portfolio and documentation.

