# Chapter 5 — Non-Functional Requirements

## 5.1 Introduction

Non-functional requirements (NFRs) define how well the μATE-STM system must perform, rather than what it must do. While Chapter 4 (Functional Requirements) specifies the capabilities and behaviors the system shall provide, this chapter specifies the quality attributes, performance targets, and constraints that the system must satisfy. Non-functional requirements are essential in systems engineering because they define the measurable criteria by which system quality is evaluated.

This chapter bridges the gap between functional requirements (Chapter 4) and system architecture (Chapter 6). Functional requirements define what the system must do; non-functional requirements define how well it must do it. The architecture must be designed to satisfy both functional and non-functional requirements simultaneously. Verification (Chapter 10) will demonstrate that each non-functional requirement is satisfied through testing, analysis, or inspection.

**Functional Requirements vs. Non-Functional Requirements:**  
Functional requirements answer the question "What shall the system do?" Examples include "The system shall acquire ADC samples" or "The software shall compute FFT." Non-functional requirements answer the question "How well shall the system do it?" Examples include "The system shall acquire samples at a minimum rate of X samples per second" or "The FFT computation shall complete within Y milliseconds."

Non-functional requirements are critical because they:
- Define measurable quality targets that guide architectural decisions
- Enable objective evaluation of system performance
- Provide criteria for trade-off analysis between competing design options
- Ensure that the system meets user expectations for performance, reliability, and usability
- Support verification by providing testable acceptance criteria

This chapter presents the complete set of non-functional requirements for μATE-STM, organized by quality attribute category. Each requirement is uniquely identified, traceable to objectives and functional requirements, and accompanied by a verification method.

***

## 5.2 Quality Attribute Framework

The μATE-STM project uses a structured quality attribute framework to organize non-functional requirements. The selected attributes reflect the educational mission, resource constraints, and technical scope of the project.

**Table 5.1 — Quality Attributes and Rationale**

| Quality Attribute | Description | Rationale for Selection |
|-------------------|-------------|-------------------------|
| **Performance** | Timing, throughput, latency, responsiveness | Ensures the system meets user expectations for acquisition speed and analysis responsiveness |
| **Reliability** | Repeatability, fault tolerance, recovery, robustness | Ensures consistent operation and graceful handling of error conditions |
| **Accuracy** | Measurement repeatability, calibration, computational correctness | Ensures measurement results are trustworthy and educationally meaningful |
| **Maintainability** | Modularity, documentation, build reproducibility | Enables future development, extension, and community contribution |
| **Usability** | Installation, configuration, learning curve, error messages | Enables students and engineers to use the system effectively |
| **Portability** | Operating system compatibility, compiler independence, Python compatibility | Enables use across different development environments |
| **Scalability** | Support for future enhancements, hardware revisions | Enables evolution of the system without complete redesign |
| **Safety** | Electrical safety, connector protection, safe operation | Protects users and equipment from harm |
| **Security** | Command validation, input validation, repository integrity | Protects against accidental or malicious misuse |
| **Environmental** | Operating temperature, humidity, storage | Ensures operation in typical student/home laboratory environments |

These quality attributes were selected to balance the educational mission (learnability, maintainability, portability) with technical rigor (performance, reliability, accuracy) and practical constraints (safety, environmental, security).

***

## 5.3 Performance Requirements

Performance requirements define measurable timing, throughput, and responsiveness targets for the system.

**Table 5.2 — Performance Requirements**

| ID | Requirement Name | Requirement Statement | Rationale | Source Obj. | Verification | Priority | Status |
|----|-----------------|----------------------|-----------|-------------|--------------|----------|--------|
| **NFR-001** | Minimum Sampling Rate | The system shall support a minimum sampling rate meeting the design target for audio-frequency signal analysis. | Enables capture of signals within the intended measurement bandwidth. | OBJ-002 | Functional Test | Mandatory | Planned |
| **NFR-002** | Maximum Sampling Rate | The system shall support a maximum sampling rate meeting the design target for the selected acquisition hardware. | Enables capture of higher-frequency signals within hardware capabilities. | OBJ-002 | Functional Test | Highly Desirable | Planned |
| **NFR-003** | Acquisition Latency | The time from acquisition command to first sample availability shall meet the design target for responsive user experience. | Ensures responsive user experience during measurement initiation. | OBJ-003 | Functional Test | Highly Desirable | Planned |
| **NFR-004** | Data Transfer Throughput | The system shall transfer acquired data to the host at a rate sufficient to support the maximum sampling rate without data loss. | Ensures continuous acquisition without buffer overflow. | OBJ-002, OBJ-007 | Analysis | Mandatory | Planned |
| **NFR-005** | FFT Computation Time | The FFT computation for a typical dataset shall complete within the design target for responsive analysis on a typical host computer. | Ensures responsive analysis without excessive delay. | OBJ-004 | Functional Test | Highly Desirable | Planned |
| **NFR-006** | Spectral Metrics Computation Time | All spectral metrics (THD, SNR, SINAD, SFDR, ENOB) shall be computed and displayed within the design target after FFT completion. | Ensures timely presentation of analysis results. | OBJ-004 | Functional Test | Highly Desirable | Planned |
| **NFR-007** | Report Generation Time | A measurement report with plots and metrics shall be generated within the design target for timely documentation. | Ensures timely documentation without excessive delay. | OBJ-008 | Functional Test | Highly Desirable | Planned |
| **NFR-008** | Command Response Time | The firmware shall respond to host commands within the design target under normal operating conditions. | Ensures responsive host-firmware interaction. | OBJ-002 | Functional Test | Highly Desirable | Planned |
| **NFR-009** | Startup Time | The system shall complete initialization and be ready for operation within the design target for acceptable startup delay. | Ensures acceptable startup delay for users. | OBJ-001, OBJ-002 | Functional Test | Highly Desirable | Planned |
| **NFR-010** | Histogram Acquisition Time | Acquisition of sufficient samples for code-density histogram shall complete within the design target at maximum sampling rate. | Ensures practical acquisition time for linearity analysis. | OBJ-005 | Functional Test | Highly Desirable | Planned |

These performance requirements establish targets for acquisition speed, analysis responsiveness, and overall system throughput. Actual achieved performance will be documented in Chapter 10 (Verification & Validation).

### 5.3.1 Resource Utilization Requirements

Resource utilization requirements define constraints on memory usage, processor utilization, and storage efficiency for the system.

**Table 5.3 — Resource Utilization Requirements**

| ID | Requirement Name | Requirement Statement | Rationale | Source Obj. | Verification | Priority | Status |
|----|-----------------|----------------------|-----------|-------------|--------------|----------|--------|
| **NFR-073** | Firmware Memory Usage | The firmware shall operate within the available memory resources of the selected microcontroller without exceeding the design target for memory utilization. | Ensures reliable operation within hardware constraints. | OBJ-002 | Analysis | Mandatory | Planned |
| **NFR-074** | Processor Utilization | The firmware shall operate with processor utilization meeting the design target to allow headroom for error handling and future enhancements. | Ensures stable operation and accommodates future features. | OBJ-002 | Analysis | Highly Desirable | Planned |
| **NFR-075** | Host Memory Usage | The host software shall operate within typical memory resources of a standard host computer without exceeding the design target for memory consumption. | Ensures compatibility with common host computers. | OBJ-003 | Analysis | Highly Desirable | Planned |
| **NFR-076** | Storage Efficiency | The system shall store measurement data and reports using efficient file formats meeting the design target for storage utilization. | Minimizes storage requirements and facilitates data sharing. | OBJ-003 | Analysis | Highly Desirable | Planned |

These resource utilization requirements ensure that the system operates efficiently within the constraints of the selected hardware and typical host computer resources.

***

## 5.4 Reliability Requirements

Reliability requirements define the system's ability to operate consistently, recover from errors, and maintain robust operation.

**Table 5.4 — Reliability Requirements**

| ID | Requirement Name | Requirement Statement | Rationale | Source Obj. | Verification | Priority | Status |
|----|-----------------|----------------------|-----------|-------------|--------------|----------|--------|
| **NFR-011** | Measurement Repeatability | Repeated measurements of the same input signal shall produce results within the design target for repeatability under identical conditions. | Ensures measurement consistency for educational purposes. | OBJ-004, OBJ-005 | Analysis | Highly Desirable | Planned |
| **NFR-012** | Fault Tolerance | The system shall detect and report communication errors without crashing or data corruption. | Ensures robust operation during communication failures. | OBJ-002, OBJ-003 | Functional Test | Mandatory | Planned |
| **NFR-013** | Error Recovery | The system shall recover from transient communication errors within the design target without user intervention. | Minimizes disruption from temporary communication issues. | OBJ-002, OBJ-003 | Functional Test | Highly Desirable | Planned |
| **NFR-014** | Startup Reliability | The system shall successfully initialize and enter operational state on all power-on attempts under normal conditions. | Ensures predictable startup behavior. | OBJ-001, OBJ-002 | Functional Test | Mandatory | Planned |
| **NFR-015** | Communication Robustness | The communication protocol shall detect transmission errors with a probability meeting the design target for data integrity. | Ensures high confidence in data integrity. | OBJ-007 | Analysis | Mandatory | Planned |
| **NFR-016** | Long-Duration Operation | The system shall operate continuously for the design target duration without degradation in performance or data loss. | Ensures suitability for extended measurement sessions. | OBJ-002, OBJ-003 | Functional Test | Highly Desirable | Planned |
| **NFR-017** | Buffer Overflow Protection | The system shall prevent data loss due to buffer overflow through appropriate flow control or error reporting. | Ensures data integrity during high-rate acquisition. | OBJ-002 | Analysis | Highly Desirable | Planned |
| **NFR-018** | Graceful Degradation | The system shall degrade gracefully (e.g., reduced sampling rate) rather than fail catastrophically when resources are constrained. | Ensures continued operation under suboptimal conditions. | OBJ-002, OBJ-003 | Functional Test | Highly Desirable | Planned |

These reliability requirements ensure that the system operates consistently, handles errors gracefully, and maintains data integrity during normal and abnormal conditions.

***

## 5.5 Accuracy Requirements

Accuracy requirements define the measurement precision, calibration capability, and computational correctness targets for the system.

**Table 5.5 — Accuracy Requirements**

| ID | Requirement Name | Requirement Statement | Rationale | Source Obj. | Verification | Priority | Status |
|----|-----------------|----------------------|-----------|-------------|--------------|----------|--------|
| **NFR-019** | DC Measurement Repeatability | Repeated DC voltage measurements of a stable input shall produce results within the design target for repeatability. | Ensures measurement consistency for calibration and verification. | OBJ-001, OBJ-006 | Analysis | Highly Desirable | Planned |
| **NFR-020** | Calibration Accuracy Improvement | After calibration, DC measurement accuracy shall improve relative to uncalibrated measurements, meeting the design target for calibration effectiveness. | Demonstrates effectiveness of calibration procedure. | OBJ-006 | Analysis | Highly Desirable | Planned |
| **NFR-021** | Numerical Consistency | Mathematical computations (FFT, DNL, INL, spectral metrics) shall produce consistent results across repeated executions with identical input data. | Ensures computational reproducibility. | OBJ-004, OBJ-005 | Analysis | Mandatory | Planned |
| **NFR-022** | Computational Correctness | All mathematical algorithms shall produce results within the design target for accuracy compared to reference implementations (e.g., MATLAB, NumPy) for identical input data. | Ensures algorithmic accuracy for educational purposes. | OBJ-004, OBJ-005 | Analysis | Highly Desirable | Planned |
| **NFR-023** | Timestamp Accuracy | Measurement timestamps shall be accurate to within the design target for traceability and reproducibility. | Enables traceability and reproducibility of measurements. | OBJ-003 | Inspection | Highly Desirable | Planned |
| **NFR-024** | Configuration Persistence Accuracy | Stored configuration settings shall be restored with complete accuracy after power cycle. | Ensures reliable configuration retention. | OBJ-002 | Functional Test | Highly Desirable | Planned |

These accuracy requirements establish targets for measurement repeatability, calibration effectiveness, and computational correctness. Actual achieved accuracy will be documented in Chapter 10 (Verification & Validation).

***

## 5.6 Maintainability Requirements

Maintainability requirements define the system's ease of modification, extension, and long-term maintenance.

**Table 5.6 — Maintainability Requirements**

| ID | Requirement Name | Requirement Statement | Rationale | Source Obj. | Verification | Priority | Status |
|----|-----------------|----------------------|-----------|-------------|--------------|----------|--------|
| **NFR-025** | Modular Code Structure | Firmware and software code shall be organized into distinct modules with well-defined interfaces. | Enables independent development and testing of components. | OBJ-009, OBJ-013 | Inspection | Mandatory | Planned |
| **NFR-026** | Code Documentation | All source code files shall include comments explaining purpose, inputs, outputs, and key algorithms. | Enables understanding and modification by future developers. | OBJ-009, OBJ-013, OBJ-015 | Inspection | Mandatory | Planned |
| **NFR-027** | Repository Organization | The project repository shall follow a standard structure with separate directories for hardware, firmware, software, and documentation. | Enables easy navigation and contribution by others. | OBJ-015 | Inspection | Mandatory | Planned |
| **NFR-028** | Build Reproducibility | The firmware and software shall be buildable from source code using documented procedures on a clean system. | Enables reproduction and verification by others. | OBJ-009, OBJ-015 | Functional Test | Mandatory | Planned |
| **NFR-029** | Configuration Management | All source code, documentation, and configuration files shall be version-controlled with clear commit history. | Enables tracking of changes and collaboration. | OBJ-015 | Inspection | Mandatory | Planned |
| **NFR-030** | Automated Testing | The software shall include automated tests for critical functions (e.g., FFT, DNL/INL, spectral metrics). | Enables regression testing and verification of changes. | OBJ-010 | Inspection | Highly Desirable | Planned |
| **NFR-031** | Dependency Documentation | All external dependencies (libraries, tools, packages) shall be documented with version numbers and installation instructions. | Enables reproducible builds and troubleshooting. | OBJ-009, OBJ-013 | Inspection | Mandatory | Planned |
| **NFR-032** | Code Review Readiness | The code shall be structured and documented to facilitate peer review by other developers. | Enables community contribution and quality improvement. | OBJ-015 | Inspection | Highly Desirable | Planned |

These maintainability requirements ensure that the system can be understood, modified, and extended by the original developer and by others in the future.

***

## 5.7 Usability Requirements

Usability requirements define the system's ease of use, installation, configuration, and learning curve.

**Table 5.7 — Usability Requirements**

| ID | Requirement Name | Requirement Statement | Rationale | Source Obj. | Verification | Priority | Status |
|----|-----------------|----------------------|-----------|-------------|--------------|----------|--------|
| **NFR-033** | Installation Time | A new user shall be able to install the host software and dependencies within the design target for reasonable installation effort. | Ensures reasonable installation effort for users. | OBJ-003, OBJ-013 | Demonstration | Highly Desirable | Planned |
| **NFR-034** | Configuration Simplicity | Basic configuration (sampling rate, number of samples) shall require minimal user actions for common use cases. | Minimizes configuration complexity for common use cases. | OBJ-003 | Demonstration | Highly Desirable | Planned |
| **NFR-035** | Learning Curve | A new user shall be able to perform a basic measurement (DC voltage or waveform capture) within the design target for learning time after reading the User Manual. | Ensures accessibility for students and hobbyists. | OBJ-013, OBJ-014 | Demonstration | Highly Desirable | Planned |
| **NFR-036** | Error Message Clarity | Error messages shall clearly indicate the nature of the problem and suggest corrective action. | Enables users to troubleshoot issues independently. | OBJ-003 | Inspection | Highly Desirable | Planned |
| **NFR-037** | Documentation Completeness | The User Manual shall include step-by-step instructions for all major features (acquisition, analysis, calibration, reporting). | Enables independent use without developer assistance. | OBJ-013, OBJ-014 | Inspection | Mandatory | Planned |
| **NFR-038** | Reporting Usability | Generated reports shall be readable and understandable by someone unfamiliar with the system. | Enables sharing of results with instructors or colleagues. | OBJ-008 | Demonstration | Highly Desirable | Planned |
| **NFR-039** | User Feedback | The system shall provide visual or textual feedback within the design target for responsive user experience after user actions (e.g., button clicks, command execution). | Ensures responsive user experience. | OBJ-003 | Functional Test | Highly Desirable | Planned |
| **NFR-040** | Help System | The host software shall provide context-sensitive help or documentation links for key features. | Enables users to access help when needed. | OBJ-003 | Inspection | Optional | Planned |

These usability requirements ensure that the system is accessible to students and engineers with varying levels of experience, and that users can operate the system effectively with minimal training.

***

## 5.8 Portability Requirements

Portability requirements define the system's ability to operate across different platforms, compilers, and environments.

**Table 5.8 — Portability Requirements**

| ID | Requirement Name | Requirement Statement | Rationale | Source Obj. | Verification | Priority | Status |
|----|-----------------|----------------------|-----------|-------------|--------------|----------|--------|
| **NFR-041** | Operating System Compatibility | The host software shall run on Windows, macOS, and Linux operating systems. | Enables use across different user environments. | OBJ-003 | Functional Test | Highly Desirable | Planned |
| **NFR-042** | Python Compatibility | The host software shall be compatible with Python 3.8 or later. | Ensures compatibility with widely available Python versions. | OBJ-003 | Functional Test | Mandatory | Planned |
| **NFR-043** | Compiler Independence (Firmware) | The firmware shall be compilable using at least one freely available compiler toolchain (e.g., GCC-based). | Enables reproduction without proprietary tools. | OBJ-002 | Functional Test | Mandatory | Planned |
| **NFR-044** | IDE Independence | The firmware shall be buildable from command line without requiring a specific IDE. | Enables automation and integration with CI/CD pipelines. | OBJ-002 | Functional Test | Highly Desirable | Planned |
| **NFR-045** | Repository Portability | The project repository shall be hostable on common platforms (e.g., GitHub, GitLab, Bitbucket). | Enables flexible hosting and collaboration. | OBJ-015 | Inspection | Mandatory | Planned |
| **NFR-046** | Hardware Abstraction | The firmware shall abstract hardware-specific code to facilitate porting to different microcontroller platforms. | Enables future hardware revisions or platform changes. | OBJ-002 | Inspection | Optional | Planned |
| **NFR-047** | Dependency Minimization | The host software shall minimize external dependencies to reduce installation complexity. | Simplifies installation and reduces compatibility issues. | OBJ-003 | Inspection | Highly Desirable | Planned |

These portability requirements ensure that the system can be used across different development environments and that future platform changes are feasible.

***

## 5.9 Scalability Requirements

Scalability requirements define the system's architectural ability to accommodate future enhancements, hardware revisions, and expanded capabilities without requiring complete redesign.

**Table 5.9 — Scalability Requirements**

| ID | Requirement Name | Requirement Statement | Rationale | Source Obj. | Verification | Priority | Status |
|----|-----------------|----------------------|-----------|-------------|--------------|----------|--------|
| **NFR-048** | Multi-Channel Architecture | The system architecture shall support the conceptual addition of additional analog input channels through modular design patterns. | Enables future expansion to multi-channel measurement through architectural extensibility. | OBJ-001, OBJ-014 | Analysis | Optional | Planned |
| **NFR-049** | Sampling Rate Scalability | The system architecture shall support future firmware enhancements to achieve higher sampling rates through configurable timing and buffering mechanisms. | Enables performance upgrades through architectural flexibility. | OBJ-002, OBJ-014 | Analysis | Optional | Planned |
| **NFR-050** | Measurement Type Extensibility | The system architecture shall support future addition of measurement types (e.g., external ADC, DAC, digital I/O) through modular analysis plugin architecture. | Enables functional expansion through architectural extensibility. | OBJ-001, OBJ-014 | Analysis | Optional | Planned |
| **NFR-051** | Hardware Abstraction Layer | The system architecture shall include hardware abstraction to support hardware revisions (e.g., different microcontroller, different ADC) with minimal firmware changes. | Enables hardware evolution through architectural abstraction. | OBJ-001, OBJ-002 | Analysis | Highly Desirable | Planned |
| **NFR-052** | Software Plugin Architecture | The host software architecture shall support future addition of analysis plugins or extensions through modular plugin interfaces. | Enables community-contributed analysis modules through architectural extensibility. | OBJ-003, OBJ-014 | Analysis | Optional | Planned |
| **NFR-053** | Configuration File Support | The system architecture shall support configuration files for saving and loading measurement setups through standardized configuration management. | Enables easy switching between measurement configurations through architectural support. | OBJ-003 | Functional Test | Optional | Planned |

These scalability requirements ensure that the system architecture can accommodate future enhancements without requiring complete redesign, supporting long-term evolution and community contribution through architectural patterns rather than specific performance predictions.

***

## 5.10 Safety Requirements

Safety requirements define the system's protection of users and equipment from harm.

**Table 5.10 — Safety Requirements**

| ID | Requirement Name | Requirement Statement | Rationale | Source Obj. | Verification | Priority | Status |
|----|-----------------|----------------------|-----------|-------------|--------------|----------|--------|
| **NFR-054** | Electrical Safety | The system shall operate at low voltage to minimize electrical shock hazard. | Ensures user safety during normal operation. | OBJ-001 | Inspection | Mandatory | Planned |
| **NFR-055** | Input Protection | The analog input shall be protected against overvoltage without damage to the system. | Prevents damage from accidental overvoltage connection. | OBJ-001 | Functional Test | Mandatory | Planned |
| **NFR-056** | Connector Safety | All external connectors shall be physically keyed or labeled to prevent incorrect connection. | Minimizes risk of misconnection and damage. | OBJ-001 | Inspection | Highly Desirable | Planned |
| **NFR-057** | Software Safety | The system shall prevent execution of commands that could damage hardware (e.g., invalid sampling rates). | Prevents accidental hardware damage via software. | OBJ-002, OBJ-003 | Functional Test | Mandatory | Planned |
| **NFR-058** | Safe Startup | The system shall initialize peripherals to safe default states on startup (e.g., ADC disconnected, outputs disabled). | Prevents unintended behavior during initialization. | OBJ-001, OBJ-002 | Functional Test | Mandatory | Planned |
| **NFR-059** | Invalid Configuration Handling | The system shall reject invalid configuration values (e.g., negative sampling rates) with appropriate error messages. | Prevents undefined behavior from invalid inputs. | OBJ-002, OBJ-003 | Functional Test | Mandatory | Planned |
| **NFR-060** | Thermal Safety | The system shall not exceed safe surface temperature under normal operating conditions. | Prevents burn hazard during extended operation. | OBJ-001 | Analysis | Highly Desirable | Planned |

These safety requirements ensure that the system protects users from electrical hazards and protects equipment from damage due to accidental misconnection or invalid configuration.

***

## 5.11 Security Requirements

Security requirements define the system's protection against accidental or malicious misuse. Given the educational nature of the project, security requirements are minimal and focused on practical considerations.

**Table 5.11 — Security Requirements**

| ID | Requirement Name | Requirement Statement | Rationale | Source Obj. | Verification | Priority | Status |
|----|-----------------|----------------------|-----------|-------------|--------------|----------|--------|
| **NFR-061** | Command Validation | The firmware shall validate all received commands before execution. | Prevents execution of invalid or potentially harmful commands. | OBJ-002 | Functional Test | Mandatory | Planned |
| **NFR-062** | Input Validation | The host software shall validate all user inputs before processing. | Prevents crashes or undefined behavior from malformed inputs. | OBJ-003 | Functional Test | Mandatory | Planned |
| **NFR-063** | Corrupted Packet Handling | The communication protocol shall detect and reject corrupted packets without processing invalid data. | Prevents data corruption or crashes from transmission errors. | OBJ-007 | Functional Test | Mandatory | Planned |
| **NFR-064** | Repository Integrity | The project repository shall use version control to maintain integrity and traceability of all changes. | Prevents unauthorized or accidental modification of source code. | OBJ-015 | Inspection | Mandatory | Planned |
| **NFR-065** | Authentication | The system shall not require user authentication (password, login) for local operation. | Simplifies use for educational purposes; system is not network-accessible. | OBJ-003 | Inspection | Mandatory | Planned |

These security requirements are minimal and appropriate for a locally-operated educational system. The system is not network-accessible and does not handle sensitive data, so extensive cybersecurity features are unnecessary.

***

## 5.12 Environmental Requirements

Environmental requirements define the system's operating conditions and environmental constraints.

**Table 5.12 — Environmental Requirements**

| ID | Requirement Name | Requirement Statement | Rationale | Source Obj. | Verification | Priority | Status |
|----|-----------------|----------------------|-----------|-------------|--------------|----------|--------|
| **NFR-066** | Operating Temperature | The system shall operate correctly in ambient temperatures typical of indoor environments (home, classroom, office). | Ensures operation in typical indoor environments. | OBJ-001 | Functional Test | Highly Desirable | Planned |
| **NFR-067** | Storage Temperature | The system shall be storable without damage in temperatures typical of indoor storage environments. | Ensures safe storage during transport or non-use periods. | OBJ-001 | Analysis | Highly Desirable | Planned |
| **NFR-068** | Humidity | The system shall operate correctly in relative humidity typical of indoor environments (non-condensing). | Ensures operation in typical indoor environments. | OBJ-001 | Functional Test | Highly Desirable | Planned |
| **NFR-069** | USB Environment | The system shall operate correctly when powered from standard USB ports. | Ensures compatibility with common USB power sources. | OBJ-001 | Functional Test | Mandatory | Planned |
| **NFR-070** | EMI Immunity | The system shall operate correctly in the presence of typical indoor electromagnetic interference (e.g., WiFi, Bluetooth, mobile phones). | Ensures operation in typical environments with wireless devices. | OBJ-001 | Functional Test | Highly Desirable | Planned |
| **NFR-071** | Mechanical Robustness | The system shall withstand normal handling (e.g., placement on desk, connection/disconnection of cables) without damage. | Ensures durability during typical use. | OBJ-001 | Demonstration | Highly Desirable | Planned |
| **NFR-072** | Laboratory vs. Home Use | The system shall be suitable for use in both educational laboratory settings and home environments. | Ensures accessibility for students regardless of location. | OBJ-001 | Inspection | Highly Desirable | Planned |

These environmental requirements ensure that the system can operate in typical student environments (home, classroom, office) without requiring specialized laboratory conditions.

***

## 5.13 Verification of Non-Functional Requirements

Each non-functional requirement category will be verified using specific strategies in Chapter 10. This section establishes the verification philosophy without duplicating detailed test procedures.

**Performance Requirements (NFR-001 through NFR-010, NFR-073 through NFR-076):**  
Verification will include timing measurements (sampling rate, latency, computation time), throughput testing (data transfer rate), responsiveness testing (command response time, startup time), and resource utilization analysis (memory usage, processor utilization). Test methods will include firmware-generated test patterns, host software timing measurements, and comparison to design targets.

**Reliability Requirements (NFR-011 through NFR-018):**  
Verification will include repeatability testing (repeated measurements), fault injection testing (communication errors, buffer overflow), recovery testing (error recovery time), and long-duration testing (continuous operation). Test methods will include controlled error injection and statistical analysis of results.

**Accuracy Requirements (NFR-019 through NFR-024):**  
Verification will include measurement repeatability testing (repeated DC measurements), calibration effectiveness testing (accuracy before/after calibration), computational correctness testing (comparison to reference implementations), and consistency testing (repeated computations). Test methods will include known reference inputs and comparison to expected values.

**Maintainability Requirements (NFR-025 through NFR-032):**  
Verification will include inspection (code structure, documentation, repository organization), build testing (reproducibility from source), and configuration management review (version control, commit history). Test methods will include checklist review and independent build attempts.

**Usability Requirements (NFR-033 through NFR-040):**  
Verification will include user testing (installation time, learning curve, configuration simplicity), documentation review (completeness, clarity), and user feedback (error message clarity, reporting usability). Test methods will include observation of new users and feedback collection.

**Portability Requirements (NFR-041 through NFR-047):**  
Verification will include cross-platform testing (Windows, macOS, Linux), Python version testing, compiler independence testing (alternative toolchains), and build automation testing (command-line builds). Test methods will include installation and execution on different platforms.

**Scalability Requirements (NFR-048 through NFR-053):**  
Verification will include architectural analysis (support for future enhancements), design review (modularity, extensibility), and documentation review (future development roadmap). Test methods will include design inspection and architectural evaluation.

**Safety Requirements (NFR-054 through NFR-060):**  
Verification will include electrical safety inspection (voltage levels, protection circuits), overvoltage testing (input protection), command validation testing (invalid command rejection), and thermal testing (surface temperature measurement). Test methods will include controlled testing and inspection.

**Security Requirements (NFR-061 through NFR-065):**  
Verification will include command validation testing (invalid command rejection), input validation testing (malformed input handling), packet corruption testing (corrupted packet rejection), and repository inspection (version control integrity). Test methods will include controlled testing and inspection.

**Environmental Requirements (NFR-066 through NFR-072):**  
Verification will include environmental testing (temperature, humidity), USB compatibility testing (different USB ports), EMI testing (operation near wireless devices), and mechanical robustness testing (handling, connection/disconnection). Test methods will include controlled environmental testing and observation.

***

## 5.14 Traceability Matrix

Table 5.13 establishes traceability from quality attributes to non-functional requirements, future architecture (Chapter 6), future verification (Chapter 10), and expected deliverables.

**Table 5.13 — Non-Functional Requirements Traceability Matrix**

| Quality Attribute | Requirement IDs | Architecture (Chapter 6) | Verification (Chapter 10) | Expected Deliverable |
|-------------------|-----------------|--------------------------|---------------------------|----------------------|
| **Performance** | NFR-001 through NFR-010, NFR-073 through NFR-076 | Performance architecture, timing constraints, resource management | TC-016 through TC-029 | Performance test results |
| **Reliability** | NFR-011 through NFR-018 | Reliability architecture, error handling | TC-030 through TC-037 | Reliability test results |
| **Accuracy** | NFR-019 through NFR-024 | Accuracy architecture, calibration subsystem | TC-038 through TC-043 | Accuracy test results |
| **Maintainability** | NFR-025 through NFR-032 | Modular architecture, documentation structure | TC-044 through TC-051 | Code, documentation, repository |
| **Usability** | NFR-033 through NFR-040 | User interface architecture, documentation | TC-052 through TC-059 | User Manual, software |
| **Portability** | NFR-041 through NFR-047 | Platform-independent architecture | TC-060 through TC-066 | Cross-platform software |
| **Scalability** | NFR-048 through NFR-053 | Extensible architecture, plugin support | TC-067 through TC-072 | Scalability analysis |
| **Safety** | NFR-054 through NFR-060 | Safety architecture, protection circuits | TC-073 through TC-079 | Safety test results |
| **Security** | NFR-061 through NFR-065 | Security architecture, validation | TC-080 through TC-084 | Security test results |
| **Environmental** | NFR-066 through NFR-072 | Environmental design, robustness | TC-085 through TC-091 | Environmental test results |

This traceability ensures that every quality attribute is addressed by non-functional requirements and that requirements are traceable to architecture, verification, and deliverables.

***

## 5.15 Requirement Quality Review

The non-functional requirements in this chapter have been developed following good requirements engineering principles. This section reviews the quality of the requirements.

**Measurability:**  
Each requirement is measurable through testing, analysis, inspection, or demonstration. Verification methods are specified for each requirement, enabling objective evaluation of compliance. For example, NFR-001 (Minimum Sampling Rate) is measurable by counting samples per second, and NFR-033 (Installation Time) is measurable by timing the installation process. Resource utilization requirements (NFR-073 through NFR-076) are measurable through memory profiling and processor utilization monitoring.

**Necessity:**  
Each requirement is necessary to achieve one or more project objectives or to ensure system quality. Unnecessary requirements are avoided to minimize scope creep. For example, NFR-065 (Authentication) explicitly states that authentication is not required, avoiding unnecessary complexity.

**Testability:**  
All requirements are testable. Testable requirements enable objective pass/fail determination, reducing subjective judgment. For example, NFR-014 (Startup Reliability) is testable by repeated power-on attempts, and NFR-054 (Electrical Safety) is testable by measuring operating voltages.

**Realism:**  
Requirements are realistic given the educational mission, resource constraints, and technical scope of the project. For example, performance targets (NFR-001, NFR-002) are achievable with the selected microcontroller, and accuracy targets (NFR-019, NFR-020) are appropriate for educational purposes.

**Implementation-Independence:**  
Requirements describe what quality attributes the system must satisfy, not how to achieve them. Implementation details are deferred to architecture and implementation chapters. For example, NFR-025 (Modular Code Structure) specifies the outcome (modular organization) without prescribing specific design patterns or file structures.

**Internal Consistency:**  
Requirements are consistent with each other and with the project objectives, constraints, and assumptions. No requirement contradicts another requirement or established design decisions. For example, performance requirements (NFR-001 through NFR-010) are consistent with reliability requirements (NFR-011 through NFR-018) and do not impose conflicting demands.

**Traceability:**  
Each requirement is traceable to one or more objectives (Chapter 3), and traceability to architecture (Chapter 6), verification (Chapter 10), and deliverables is established (Section 5.14). This traceability ensures that no requirement is orphaned and that all quality attributes are addressed.

**Completeness:**  
The requirements collectively cover all quality attributes needed to achieve the project objectives and ensure system quality. Performance, reliability, accuracy, maintainability, usability, portability, scalability, safety, security, and environmental aspects are all addressed.

This quality review ensures that the non-functional requirements are well-formed and suitable for guiding architectural design, implementation, and verification.

***

## 5.16 Chapter Summary

This chapter has defined the complete set of non-functional requirements for the μATE-STM project. The key points are:

- **Purpose:** Non-functional requirements define how well the system must perform, complementing the functional requirements (Chapter 4) that define what the system must do.
- **Quality Attribute Framework:** Ten quality attributes (performance, reliability, accuracy, maintainability, usability, portability, scalability, safety, security, environmental) were selected to reflect the educational mission, resource constraints, and technical scope of the project.
- **Complete Specification:** 76 non-functional requirements (NFR-001 through NFR-076) define measurable quality targets for all attributes, including resource utilization requirements for firmware memory, processor utilization, host memory, and storage efficiency.
- **Traceability:** Requirements are traceable to objectives, architecture, verification, and deliverables (Section 5.14).
- **Verification Strategy:** Each requirement category has a defined verification strategy (Section 5.13).
- **Quality Review:** Requirements satisfy good requirements engineering principles (measurability, necessity, testability, realism, implementation-independence, internal consistency, traceability, completeness).