# 8. Hardware Design

This chapter defines the hardware architecture and detailed design of the μATE-STM system. It is written as a professional Hardware Design Document (HDD) to support implementation, verification, and review. All analog signals are constrained to safe low-voltage ranges, and the design emphasizes frugality, modularity, and educational value.

***

## 8.1 Hardware Design Philosophy

### 8.1.1 Design Objectives

The hardware design targets:

- **Functional sufficiency**: Provide enough analog stimulus and measurement capability to perform histogram-based DNL/INL and FFT-based THD/SNR tests on 12-bit data converters.
- **Safety**: Ensure all user-accessible nodes remain at safe, low-voltage levels (< 5 V, nominally 0–3.3 V).
- **Reproducibility**: Enable another engineer to replicate the hardware using commonly available components and a breadboard.
- **Educational depth**: Expose key mixed-signal concepts (sampling, filtering, protection, grounding) without unnecessary complexity.

### 8.1.2 Cost Constraints

- **Budget ceiling**: Additional hardware cost ≤ ₹1,000 (ideally ≤ ₹500).
- **Reuse-first strategy**: Leverage the existing STM32F446/447 board; no external instruments or active analog ICs are required.
- **Passive-only front-end**: Use resistors, capacitors, and diodes; avoid op-amps and precision references unless absolutely necessary.

This constraint enforces a minimalist design that still meets learning objectives.

### 8.1.3 Learning Objectives

Hardware design decisions prioritize:

- **Hands-on analog design**: Resistor dividers, RC filters, and protection circuits.
- **Mixed-signal integration**: Understanding ADC input requirements and DAC output limitations.
- **Debugging skills**: Using a multimeter and logic analyzer (if available) to validate hardware behavior.

### 8.1.4 Reliability Goals

Although not production-grade, the hardware should:

- Withstand repeated connection/disconnection cycles.
- Tolerate minor misconfigurations (e.g., temporary overvoltage within diode clamp limits).
- Operate continuously for hours without thermal or electrical failure.

### 8.1.5 Safety Philosophy

- **Low-voltage domain**: All signals constrained to 0–3.3 V nominal, < 5 V absolute maximum.
- **Current limiting**: Series resistors limit fault current into ADC/DAC pins.
- **Protection diodes**: Clamp inputs to safe rails (GND and 3.3 V).
- **No mains connection**: The system is entirely USB-powered and isolated from hazardous voltages.

### 8.1.6 Modularity Philosophy

- **Breadboard-based AFE**: Analog front-end built on a separate breadboard section for easy modification.
- **Jumper-based configuration**: Allow easy changes to filter cutoff frequencies or divider ratios.
- **Test points**: Provide accessible nodes for measurement and debugging.

### 8.1.7 Maintainability Philosophy

- **Labeling**: Clearly label all nodes (e.g., “DAC_OUT”, “ADC_IN”, “GND”).
- **Documentation**: Schematic and BOM maintained alongside firmware and software.
- **Standard values**: Use common resistor/capacitor values for easy replacement.

### 8.1.8 Future Expansion Philosophy

The design supports:

- **Additional channels**: Extra ADC/DAC pins can be routed to the breadboard.
- **Active components**: Space and power budget allow future addition of op-amps if needed.
- **External interfaces**: Headers for SPI/I²C sensors or external signal sources.

***

## 8.2 Hardware Requirements

This section defines hardware requirements with unique IDs for traceability.

| ID | Requirement | Category | Description | Acceptance Criteria |
|----|-------------|----------|-------------|---------------------|
| HR-001 | Voltage Range | Electrical | All analog signals must remain within 0–3.3 V nominal. | Measured voltages at ADC/DAC pins within 0–3.3 V under all test conditions. |
| HR-002 | Absolute Maximum Voltage | Safety | No pin shall exceed 5 V absolute maximum. | No pin exceeds 5 V even under fault conditions (e.g., miswiring). |
| HR-003 | Current Limiting | Safety | Fault current into any pin ≤ 10 mA. | Series resistors limit current to ≤ 10 mA in worst-case short. |
| HR-004 | ADC Sampling Rate | Performance | Support sustained sampling ≥ 100 kSPS. | ADC configured for ≥ 100 kSPS with no sample loss. |
| HR-005 | DAC Update Rate | Performance | Support waveform update ≥ 50 kSPS. | DAC updates at ≥ 50 kSPS with stable output. |
| HR-006 | Input Impedance | Electrical | ADC source impedance ≤ 10 kΩ (recommended per STM32). | Measured or calculated source impedance ≤ 10 kΩ. |
| HR-007 | Overvoltage Protection | Safety | Clamp inputs to GND and 3.3 V using diodes. | Diodes conduct when input < GND − 0.3 V or > 3.3 V + 0.3 V. |
| HR-008 | Power Source | Electrical | System powered via USB (5 V). | Board operates stably from USB port. |
| HR-009 | Current Consumption | Electrical | Total current ≤ 200 mA from USB. | Measured current ≤ 200 mA under full load. |
| HR-010 | Grounding | Signal Integrity | Separate analog and digital ground returns where possible. | Grounding scheme minimizes noise coupling (validated by observation). |
| HR-011 | Component Availability | Maintainability | All components readily available in India. | All parts purchasable from common suppliers (e.g., Robu.in, Amazon.in). |
| HR-012 | Cost Limit | Cost | Total additional hardware cost ≤ ₹1,000. | BOM cost ≤ ₹1,000. |
| HR-013 | Operating Temperature | Environmental | Operate at room temperature (15–35 °C). | No thermal issues under normal lab conditions. |
| HR-014 | Mechanical Form Factor | Mechanical | Fit on standard breadboard alongside STM32 board. | All components fit without overcrowding. |
| HR-015 | Test Points | Maintainability | Provide test points for DAC_OUT, ADC_IN, GND, 3.3 V. | Test points accessible with multimeter probes. |

***

## 8.3 Complete Hardware Architecture

The hardware architecture comprises the following blocks:

1. **STM32F4 Core Board**
2. **Analog Front-End (AFE)**
   - DAC Output Conditioning
   - ADC Input Conditioning
   - Protection Circuitry
3. **Power Distribution**
4. **Communication Interface (UART/USB)**
5. **Test Points and Headers**

### 8.3.1 STM32F4 Core Board

**Purpose:**  
Provide mixed-signal peripherals (ADC, DAC), digital control, and communication.

**Responsibilities:**

- Generate analog stimuli via DAC.
- Sample analog signals via ADC.
- Stream data to PC via UART/USB.

**Interfaces:**

- GPIO pins for ADC/DAC/UART.
- USB connector for power and communication.

**Dependencies:**

- USB power source.
- AFE for signal conditioning.

**Failure Modes:**

- Overvoltage on ADC/DAC pins.
- Incorrect clock configuration.
- USB power instability.

### 8.3.2 DAC Output Conditioning

**Purpose:**  
Scale and filter DAC outputs for safe and accurate use.

**Responsibilities:**

- Attenuate DAC output if needed (e.g., for external circuits).
- Low-pass filter to reduce high-frequency noise.

**Interfaces:**

- Input: DAC output pin (PA4 or PA5).
- Output: Conditioned signal to AFE output node.

**Dependencies:**

- Resistor divider network.
- RC low-pass filter.

**Failure Modes:**

- Incorrect resistor values causing distortion.
- Open/short connections.

### 8.3.3 ADC Input Conditioning

**Purpose:**  
Condition external or loopback signals for ADC input.

**Responsibilities:**

- Scale signals to 0–3.3 V range.
- Filter high-frequency noise.
- Provide low-impedance source to ADC.

**Interfaces:**

- Input: External signal or DAC loopback.
- Output: ADC input pin (e.g., PA0–PA3).

**Dependencies:**

- Resistor dividers.
- RC filters.
- Protection diodes.

**Failure Modes:**

- High source impedance causing sampling errors.
- Overvoltage despite protection.

### 8.3.4 Protection Circuitry

**Purpose:**  
Protect STM32 pins from overvoltage and reverse polarity.

**Responsibilities:**

- Clamp voltages to safe rails.
- Limit fault current.

**Interfaces:**

- In series with all analog I/O.

**Dependencies:**

- Schottky or small-signal diodes.
- Series resistors.

**Failure Modes:**

- Diodes installed backwards.
- Resistor values too low (excessive current).

### 8.3.5 Power Distribution

**Purpose:**  
Distribute USB 5 V to STM32 board and AFE (if needed).

**Responsibilities:**

- Provide stable 3.3 V and 5 V rails.
- Decouple power pins.

**Interfaces:**

- USB input.
- 3.3 V and GND rails on breadboard.

**Dependencies:**

- On-board regulators (on STM32 board).
- External decoupling capacitors.

**Failure Modes:**

- Insufficient decoupling causing noise.
- Overloading USB port.

### 8.3.6 Communication Interface (UART/USB)

**Purpose:**  
Enable PC communication.

**Responsibilities:**

- Provide TX/RX lines for UART.
- Optionally use USB CDC.

**Interfaces:**

- UART pins (e.g., PA2/PA3).
- USB connector.

**Failure Modes:**

- Baud rate mismatch.
- Wiring errors.

### 8.3.7 Test Points and Headers

**Purpose:**  
Facilitate debugging and measurement.

**Responsibilities:**

- Provide accessible nodes for key signals.
- Allow easy reconfiguration.

**Interfaces:**

- Breadboard rows with labels.

**Failure Modes:**

- Loose connections.
- Mislabeling.

***

## 8.4 Component Selection

### 8.4.1 Resistors

**Choice:** 1/4 W carbon film or metal film resistors, 1% tolerance.

**Why:**

- Widely available and inexpensive.
- 1% tolerance sufficient for educational purposes.

**Alternatives:**

- 5% resistors (cheaper but less precise).
- SMD resistors (not suitable for breadboard).

**Cost:** ~₹100–₹150 for assorted kit.

**Future Upgrade:** Precision 0.1% resistors for calibration experiments.

### 8.4.2 Capacitors

**Choice:** Ceramic disc or multilayer ceramic capacitors (MLCC), 10–100 nF for decoupling; 100 nF–1 μF for filters.

**Why:**

- Low cost, good high-frequency performance.
- Suitable for breadboard use.

**Alternatives:**

- Electrolytic capacitors (higher capacitance but poorer high-frequency response).

**Cost:** ~₹50–₹100 for assorted kit.

### 8.4.3 Diodes

**Choice:** 1N4148 small-signal diodes or BAT54 Schottky diodes.

**Why:**

- Fast switching, low forward voltage.
- Widely available.

**Alternatives:**

- 1N4001 (slower, higher forward voltage).
- TVS diodes (more robust but costlier).

**Cost:** ~₹20–₹50 for 10–20 pieces.

### 8.4.4 Breadboard and Jumper Wires

**Choice:** Standard solderless breadboard and male-to-male jumper wires.

**Why:**

- Reusable and flexible.
- Ideal for prototyping.

**Cost:** Often already owned; ~₹100–₹200 if purchased.

***

## 8.5 STM32 Hardware Analysis

### 8.5.1 Peripheral Usage

**ADC:**

- Use ADC1 (or ADC2/3 if needed).
- Channels: PA0–PA3 (ADC1 IN0–IN3).
- Resolution: 12-bit.
- Clock: ≤ 36 MHz (per datasheet). [st](https://www.st.com/resource/en/datasheet/stm32f446re.pdf)

**DAC:**

- Use DAC1 channels 1 and 2 (PA4, PA5).
- Resolution: 12-bit.
- Trigger: Timer-based (e.g., TIM6 or TIM7).

**DMA:**

- Use DMA2 Stream0 (for ADC1).
- Circular mode for continuous acquisition.

**Timers:**

- TIM6/TIM7 for DAC updates.
- TIM2/TIM3 for ADC triggers (if external trigger needed).

**UART:**

- USART2 (PA2/PA3) for communication.
- Baud: 115,200–921,600.

**GPIO:**

- ADC pins: Analog mode.
- DAC pins: Analog mode.
- UART pins: Alternate function.

### 8.5.2 Memory Usage

- SRAM: 128 kB total.
- ADC buffer: 16k–32k samples (32–64 kB).
- Remaining SRAM for stack, heap, and variables.

### 8.5.3 Clock Resources

- System clock: 168 MHz.
- AHB: 168 MHz.
- APB2 (ADC): 84 MHz (prescaled to ≤ 36 MHz for ADC).
- APB1 (DAC, timers): 42–84 MHz.

***

## 8.6 Pin Assignment

| Function | STM32 Pin | Port/Line | Rationale | Alternatives |
|----------|-----------|-----------|-----------|--------------|
| DAC1_CH1 | PA4 | A4 | Dedicated DAC output | PA5 (DAC1_CH2) |
| DAC1_CH2 | PA5 | A5 | Second DAC channel | None if single channel |
| ADC1_IN0 | PA0 | A0 | ADC input, low channel | PA1–PA3 |
| ADC1_IN1 | PA1 | A1 | Optional second input | PA0, PA2, PA3 |
| USART2_TX | PA2 | A2 | UART TX | PB2 (if remapped) |
| USART2_RX | PA3 | A3 | UART RX | PB3 (if remapped) |
| 3.3 V | 3.3V pin | N/A | Analog reference | N/A |
| GND | GND pin | N/A | Ground | N/A |

**Rationale:**

- PA0–PA3 are contiguous ADC channels, simplifying configuration.
- PA4/PA5 are dedicated DAC outputs.
- PA2/PA3 are default USART2 pins, avoiding remapping.

***

## 8.7 Analog Front-End Design

### 8.7.1 Signal Conditioning

**DAC Output:**

- Direct connection to AFE if no scaling needed.
- RC low-pass filter to smooth steps.

**ADC Input:**

- Resistor divider if external signal exceeds 3.3 V.
- RC low-pass filter for anti-aliasing.

### 8.7.2 Voltage Scaling

**Example Divider:**

- Input: 0–5 V.
- Output: 0–3.3 V.
- Ratio: 3.3/5 = 0.66.
- Choose R1 = 10 kΩ, R2 = 20 kΩ:
  $
  V_{\text{out}} = V_{\text{in}} \cdot \frac{R2}{R1 + R2} = V_{\text{in}} \cdot \frac{20}{30} = 0.667 V_{\text{in}}
  $

### 8.7.3 Filter Design

**RC Low-Pass:**

- Cutoff frequency:
  $
  f_c = \frac{1}{2 \pi R C}
  $
- Example: R = 1 kΩ, C = 100 nF:
  $
  f_c = \frac{1}{2 \pi \cdot 1000 \cdot 100 \times 10^{-9}} \approx 1.59 \text{ kHz}
  $

### 8.7.4 Input/Output Impedance

- **ADC source impedance**: ≤ 10 kΩ recommended.
- **DAC load**: Avoid < 5 kΩ loads to prevent distortion.

### 8.7.5 Overvoltage Protection

- Diodes from ADC input to GND and 3.3 V.
- Series resistor (1 kΩ) limits current.

### 8.7.6 ESD Considerations

- Minimize exposed metal.
- Use grounded breadboard rails.

***

## 8.8 Power System

### 8.8.1 Power Source

- USB 5 V, ≤ 500 mA.

### 8.8.2 Current Consumption

- STM32 board: ~100–150 mA.
- AFE: negligible.

### 8.8.3 Decoupling

- 100 nF capacitors near each power pin.
- 10 μF bulk capacitor on breadboard.

### 8.8.4 Power Budget

- Total: < 200 mA → well within USB limits.

***

## 8.9 Signal Integrity

- **Grounding**: Single-point ground for analog and digital.
- **Return paths**: Keep analog and digital return paths separate.
- **Noise**: Minimize loop areas; use short jumper wires.
- **Breadboard limitations**: Parasitic capacitance and inductance may affect high-frequency performance.

***

## 8.10 Hardware Calculations

### 8.10.1 Resistor Values

- Divider: R1 = 10 kΩ, R2 = 20 kΩ (see Section 8.7.2).

### 8.10.2 RC Filters

- f_c = 1.59 kHz (see Section 8.7.3).

### 8.10.3 ADC Source Impedance

- Divider output impedance:
  $
  Z_{\text{out}} = \frac{R1 \cdot R2}{R1 + R2} = \frac{10k \cdot 20k}{30k} \approx 6.67 \text{ kΩ}
  $
  Acceptable (< 10 kΩ).

### 8.10.4 Current and Power

- Series resistor 1 kΩ, 3.3 V:
  $
  I = \frac{3.3}{1000} = 3.3 \text{ mA}, \quad P = I^2 R = 10.9 \text{ mW}
  $
  Well within 1/4 W rating.

***

## 8.11 Hardware Verification

- **Continuity testing**: Verify all connections with multimeter.
- **Voltage verification**: Measure 3.3 V and GND rails.
- **Peripheral verification**: Test DAC output with multimeter/oscilloscope.
- **ADC verification**: Apply known voltage and verify reading.
- **UART verification**: Loopback test (TX to RX).

***

## 8.12 Hardware Risks

- **Failure modes**: Open/short, wrong component values.
- **Tolerances**: 1% resistors acceptable; 5% may introduce error.
- **Breadboard issues**: Loose connections, parasitic effects.
- **Debugging**: Use multimeter, logic analyzer, and systematic testing.

***

## 8.13 Hardware Bring-up Procedure

1. **First Power-On**:
   - Connect USB; measure 3.3 V and 5 V rails.
2. **Voltage Measurements**:
   - Verify all power nodes.
3. **Firmware Loading**:
   - Load test firmware (e.g., blink LED, output DAC voltage).
4. **Peripheral Testing**:
   - Test DAC output, ADC input, UART communication.
5. **Validation Sequence**:
   - Run loopback test (DAC → ADC).
   - Verify data received on PC.

***

## 8.14 Hardware Design Review Checklist

| Item | Status | Notes |
|------|--------|-------|
| All HR requirements addressed | ☐ | |
| Schematic complete and reviewed | ☐ | |
| BOM verified for availability and cost | ☐ | |
| Protection circuitry included | ☐ | |
| Test points accessible | ☐ | |
| Power budget validated | ☐ | |
| Signal integrity considerations documented | ☐ | |
| Bring-up procedure defined | ☐ | |

***

### 8.15 Complete Circuit Schematics

This section provides a net-level description of the entire analog front-end (AFE) circuitry, sufficient to be drawn directly in KiCad or implemented on a breadboard. The STM32F4 board is treated as a pre-built module; only its external connections and the AFE are described.

#### 8.15.1 Global Net List and Power Nets

**Power Nets:**

- `USB_5V`: 5 V from USB (if accessible via header).
- `VDD_3V3`: 3.3 V rail (from STM32 board’s 3.3 V output pin).
- `GND`: Common ground (analog and digital tied at a single point near the STM32 board).

**Signal Nets:**

- `DAC1_OUT`: Raw DAC output from PA4.
- `DAC1_COND`: Conditioned DAC output (after filtering/scaling).
- `ADC1_IN0`: Signal fed to ADC input PA0.
- `EXT_SIG_IN`: Optional external signal input.
- `UART_TX`, `UART_RX`: USART2 lines (PA2, PA3).

#### 8.15.2 DAC Output Conditioning Circuit

**Purpose:**  
Smooth DAC output and optionally scale it for external use.

**Components:**

- `R_DAC_S`: Series resistor, 330 Ω (default).
- `C_DAC_LP`: Low-pass capacitor to GND, 100 nF (default).
- Optional divider: `R_DAC_H` (10 kΩ), `R_DAC_L` (20 kΩ).

**Connections:**

1. `DAC1_OUT` (PA4) → one end of `R_DAC_S`.
2. Other end of `R_DAC_S` → net `DAC1_COND`.
3. `C_DAC_LP` from `DAC1_COND` to `GND`.
4. Optional scaling (if needed):
   - `DAC1_COND` → `R_DAC_H` → `GND`.
   - Junction between `R_DAC_H` and `R_DAC_L` → scaled output net `DAC1_SCALED`.

**KiCad Representation:**

- Resistor `R_DAC_S` between nets `DAC1_OUT` and `DAC1_COND`.
- Capacitor `C_DAC_LP` between `DAC1_COND` and `GND`.
- Optional resistors `R_DAC_H`, `R_DAC_L` forming divider from `DAC1_COND` to `GND`.

#### 8.15.3 ADC Input Conditioning Circuit (Loopback Mode)

**Purpose:**  
Condition DAC output (or external signal) for safe ADC input.

**Components:**

- `R_ADC_S`: Series resistor, 1 kΩ (default).
- `D_ADC_GND`: Diode from ADC input to GND (cathode at ADC input, anode at GND).
- `D_ADC_3V3`: Diode from 3.3 V to ADC input (anode at 3.3 V, cathode at ADC input).
- `C_ADC_LP`: Low-pass capacitor to GND, 100 nF (default).
- Optional divider: `R_ADC_H`, `R_ADC_L`.

**Connections (Loopback from DAC1):**

1. `DAC1_COND` → `R_ADC_S` → net `ADC1_IN0_NET`.
2. `ADC1_IN0_NET` → PA0 (ADC1_IN0).
3. `D_ADC_GND`:
   - Anode → `GND`.
   - Cathode → `ADC1_IN0_NET`.
4. `D_ADC_3V3`:
   - Anode → `VDD_3V3`.
   - Cathode → `ADC1_IN0_NET`.
5. `C_ADC_LP` from `ADC1_IN0_NET` to `GND`.

**Optional External Input Path:**

- `EXT_SIG_IN` → series resistor (1 kΩ) → same `ADC1_IN0_NET` node (via jumper or switch to select source).

**KiCad Representation:**

- Resistor `R_ADC_S` between `DAC1_COND` and `ADC1_IN0_NET`.
- Diodes `D_ADC_GND`, `D_ADC_3V3` connected as described.
- Capacitor `C_ADC_LP` between `ADC1_IN0_NET` and `GND`.

#### 8.15.4 UART Interface Circuit

**Connections:**

- STM32 PA2 (USART2_TX) → net `UART_TX`.
- STM32 PA3 (USART2_RX) → net `UART_RX`.
- If using external USB-to-UART:
  - `UART_TX` → RX of USB-to-UART module.
  - `UART_RX` → TX of USB-to-UART module.
  - Common `GND`.

**Optional Series Resistors:**

- 100 Ω resistors in series with `UART_TX` and `UART_RX` for signal integrity.

#### 8.15.5 Power Distribution and Decoupling

**On Breadboard:**

- `VDD_3V3` rail connected to STM32 3.3 V pin.
- `GND` rail connected to STM32 GND pin.
- Decoupling:
  - 100 nF capacitor between `VDD_3V3` and `GND` near AFE.
  - Optional 10 μF electrolytic capacitor (positive to `VDD_3V3`, negative to `GND`).

#### 8.15.6 Connector Pinouts

**If using 2.54 mm headers for AFE:**

| Header | Pin | Net | Description |
|--------|-----|-----|-------------|
| J_DAC | 1 | DAC1_COND | Conditioned DAC output |
| J_DAC | 2 | GND | Ground |
| J_ADC | 1 | ADC1_IN0_NET | ADC input node |
| J_ADC | 2 | GND | Ground |
| J_PWR | 1 | VDD_3V3 | 3.3 V |
| J_PWR | 2 | GND | Ground |
| J_UART | 1 | UART_TX | TX |
| J_UART | 2 | UART_RX | RX |
| J_UART | 3 | GND | Ground |

#### 8.15.7 Breadboard Layout Recommendations

- Place STM32 board at one end of the breadboard.
- Use adjacent rows for power rails (`VDD_3V3`, `GND`).
- AFE components placed in a dedicated section:
  - DAC conditioning near DAC pin.
  - ADC conditioning near ADC pin.
- Keep analog signal paths short and away from digital lines (e.g., UART).
- Use color-coded wires:
  - Red for `VDD_3V3`.
  - Black for `GND`.
  - Blue/green for analog signals.
  - Yellow/white for UART.

***

### 8.16 PCB Design Considerations

Although the initial implementation uses a breadboard, transitioning to a PCB improves signal integrity, reliability, and repeatability. This section outlines key PCB design considerations.

#### 8.16.1 Component Placement

- **STM32 Module**:
  - Place at one edge to allow easy USB access.
  - Keep analog components close to ADC/DAC pins.
- **AFE Components**:
  - Group DAC conditioning components near DAC output pin.
  - Group ADC conditioning components near ADC input pin.
- **Decoupling Capacitors**:
  - Place 100 nF capacitors as close as possible to each power pin of the STM32 module (if accessible).
  - Place bulk decoupling (10 μF) near the power entry point.

#### 8.16.2 Analog vs Digital Routing

- **Analog Traces**:
  - Route DAC and ADC signals on one side of the board.
  - Keep traces short and direct.
- **Digital Traces**:
  - Route UART and other digital signals on the opposite side or layer.
  - Avoid crossing analog and digital traces.

#### 8.16.3 Ground Plane

- Use a solid ground plane on one layer (e.g., bottom layer).
- Split analog and digital ground planes only if necessary; otherwise, use a single continuous plane with careful component placement.
- Connect all grounds to the plane with short vias.

#### 8.16.4 Trace Width

- **Power Traces**:
  - 3.3 V and GND: ≥ 0.5 mm width for low resistance.
- **Signal Traces**:
  - Analog signals: 0.25–0.3 mm width.
  - Digital signals: 0.2 mm minimum.

#### 8.16.5 Return Current Paths

- Ensure return currents for analog signals flow directly under the signal trace (microstrip configuration).
- Avoid slots or cuts in the ground plane under analog traces.

#### 8.16.6 Vias

- Use multiple vias for ground connections to reduce inductance.
- Avoid vias on sensitive analog traces if possible; if required, use small vias (0.3 mm drill).

#### 8.16.7 Connector Placement

- Place USB connector at board edge for easy access.
- Place test point headers near AFE nodes (`DAC1_COND`, `ADC1_IN0_NET`, `VDD_3V3`, `GND`).
- Orient connectors consistently (e.g., all pin 1 at top).

***

### 8.17 Hardware Verification Procedures

This section provides detailed verification procedures for each hardware subsystem.

#### 8.17.1 Power System Verification

**Objective:**  
Verify correct voltage levels and stability.

**Required Equipment:**

- Digital multimeter (DMM).
- Optional oscilloscope.

**Setup:**

- Power the STM32 board via USB.
- Probe `VDD_3V3` and `GND` rails on the breadboard.

**Procedure:**

1. Measure DC voltage between `VDD_3V3` and `GND`.
2. Observe for noise or ripple (if oscilloscope available).

**Expected Measurements:**

- VDD_3V3: 3.28–3.32 V.
- Ripple: < 50 mV peak-to-peak.

**Acceptable Tolerances:**

- ±2% for DC level.
- Ripple within oscilloscope noise floor.

**Failure Diagnosis:**

- Low voltage: Check USB cable, STM32 regulator.
- High ripple: Add decoupling capacitors.

**Troubleshooting:**

- Replace USB cable.
- Add 10 μF bulk capacitor.

***

#### 8.17.2 DAC Output Verification

**Objective:**  
Verify DAC output voltage range and linearity.

**Required Equipment:**

- DMM.
- Optional oscilloscope.

**Setup:**

- Load firmware that outputs known DAC codes (e.g., 0, 2048, 4095).
- Probe `DAC1_COND` node.

**Procedure:**

1. Set DAC code to 0; measure voltage.
2. Set DAC code to 2048; measure voltage.
3. Set DAC code to 4095; measure voltage.

**Expected Measurements:**

- Code 0: ~0 V.
- Code 2048: ~1.65 V.
- Code 4095: ~3.3 V.

**Acceptable Tolerances:**

- ±5% of expected value.

**Failure Diagnosis:**

- No output: Check DAC configuration, pin mode.
- Clipped output: Check loading, short circuits.

**Troubleshooting:**

- Verify firmware DAC initialization.
- Disconnect load and re-measure.

***

#### 8.17.3 ADC Input Verification

**Objective:**  
Verify ADC reading accuracy.

**Required Equipment:**

- DMM.
- Variable voltage source (e.g., potentiometer or DAC).

**Setup:**

- Apply known voltage to `ADC1_IN0_NET`.
- Read ADC values via firmware/PC.

**Procedure:**

1. Apply 0 V; read ADC code.
2. Apply 1.65 V; read ADC code.
3. Apply 3.3 V; read ADC code.

**Expected Measurements:**

- 0 V → code ~0.
- 1.65 V → code ~2048.
- 3.3 V → code ~4095.

**Acceptable Tolerances:**

- ±2% of full scale.

**Failure Diagnosis:**

- Constant readings: Check ADC enable, channel selection.
- Noisy readings: Check decoupling, source impedance.

**Troubleshooting:**

- Verify ADC clock and sample time.
- Reduce source impedance.

***

#### 8.17.4 UART Verification

**Objective:**  
Verify serial communication.

**Required Equipment:**

- USB-to-UART adapter (if not using onboard USB).
- PC with terminal software.

**Setup:**

- Connect `UART_TX`, `UART_RX`, `GND` to adapter.
- Open terminal at configured baud rate.

**Procedure:**

1. Send known characters from STM32.
2. Verify reception on PC.
3. Send characters from PC; verify STM32 response.

**Expected Behavior:**

- Characters received without errors.

**Failure Diagnosis:**

- Garbage data: Check baud rate, wiring.
- No data: Check TX/RX swap, power.

**Troubleshooting:**

- Swap TX/RX.
- Verify baud rate configuration.

***

### 8.18 Hardware Debugging Guide

This section addresses common hardware failures.

#### 8.18.1 No Power on Breadboard

**Symptoms:**

- No voltage on `VDD_3V3` rail.

**Likely Causes:**

- Loose USB connection.
- Broken jumper from STM32 3.3 V pin.

**Diagnostic Procedure:**

1. Measure voltage at STM32 3.3 V pin.
2. Measure at breadboard rail.

**Corrective Action:**

- Re-seat USB cable.
- Replace jumper wire.

***

#### 8.18.2 DAC Output Stuck at 0 V or 3.3 V

**Symptoms:**

- DAC output does not change with code.

**Likely Causes:**

- DAC not enabled in firmware.
- Pin not configured as analog.
- Short to GND or 3.3 V.

**Diagnostic Procedure:**

1. Measure DAC pin voltage.
2. Check firmware DAC initialization.
3. Disconnect load and re-measure.

**Corrective Action:**

- Fix firmware configuration.
- Remove short circuit.

***

#### 8.18.3 ADC Readings Constant or Noisy

**Symptoms:**

- ADC codes do not change with input.
- Readings fluctuate wildly.

**Likely Causes:**

- ADC not enabled.
- High source impedance.
- Poor decoupling.

**Diagnostic Procedure:**

1. Verify ADC clock and channel.
2. Measure source impedance.
3. Check decoupling capacitors.

**Corrective Action:**

- Reduce source impedance (< 10 kΩ).
- Add decoupling capacitors.

***

#### 8.18.4 UART Communication Fails

**Symptoms:**

- No data received or garbage data.

**Likely Causes:**

- TX/RX swapped.
- Baud rate mismatch.
- Ground not common.

**Diagnostic Procedure:**

1. Check wiring.
2. Verify baud rate on both sides.
3. Measure common ground.

**Corrective Action:**

- Swap TX/RX.
- Match baud rates.
- Connect common GND.

***

### 8.19 Manufacturing Notes

This section provides guidance for assembling and maintaining the breadboard implementation.

#### 8.19.1 Breadboard Assembly Order

1. **Power Rails**:
   - Connect `VDD_3V3` and `GND` from STM32 to breadboard.
   - Install decoupling capacitors.
2. **DAC Conditioning**:
   - Place R_DAC_S and C_DAC_LP.
   - Connect to PA4.
3. **ADC Conditioning**:
   - Place R_ADC_S, diodes, and C_ADC_LP.
   - Connect to PA0.
4. **UART Wiring**:
   - Connect PA2/PA3 to UART header or USB-to-UART.

#### 8.19.2 Wiring Practices

- Use short, direct wires for analog signals.
- Color-code wires consistently.
- Avoid daisy-chaining power; use star topology where possible.

#### 8.19.3 Labeling

- Label all nets on the breadboard with tape or markers.
- Use a printed diagram pinned nearby.

#### 8.19.4 Connector Management

- Use right-angle headers to reduce cable strain.
- Secure cables with ties to prevent accidental disconnection.

#### 8.19.5 Cable Routing

- Route analog and digital cables separately.
- Avoid looping cables near sensitive nodes.

#### 8.19.6 Maintainability

- Leave space for modifications.
- Use sockets for components that may change (e.g., diodes).

***

### 8.20 Design for Future Expansion

This section describes how the hardware can evolve to support advanced features.

#### 8.20.1 Higher-Resolution ADCs

- Add footprint for external ADC (e.g., 16-bit SPI ADC).
- Route SPI pins (MOSI, MISO, SCK, CS) to a header.
- Provide separate analog supply and reference for external ADC.

#### 8.20.2 External DACs

- Similar to ADCs: route SPI/I²C pins.
- Add 3.3 V and GND pins on header.

#### 8.20.3 SPI Peripherals

- Reserve GPIO pins for SPI (PA5–PA7 or alternate).
- Add 2.54 mm header for SPI bus.

#### 8.20.4 I²C Sensors

- Use PB6/PB7 (I²C1) or other I²C-capable pins.
- Add pull-up resistors (4.7 kΩ) to 3.3 V.
- Provide 4-pin header (VDD, GND, SDA, SCL).

#### 8.20.5 SD Card Logging

- Add SPI-based SD card module.
- Route MOSI, MISO, SCK, CS, 3.3 V, GND.
- Consider level shifters if module is 5 V.

#### 8.20.6 USB CDC

- Use STM32’s built-in USB FS (PA11/PA12).
- Add USB connector and series resistors (22 Ω).
- Update firmware to support USB CDC.

#### 8.20.7 Ethernet

- Add Ethernet module (e.g., W5500) via SPI.
- Route SPI pins and provide 3.3 V/5 V as needed.

#### 8.20.8 Wi-Fi

- Add ESP-01 or similar module.
- Use UART interface (separate from debug UART if possible).
- Provide 3.3 V regulator capable of 200+ mA.

#### 8.20.9 FPGA Integration

- Reserve GPIO pins for parallel interface.
- Add 2.54 mm header for data and control lines.
- Consider voltage level translation if FPGA is 5 V.

***
