# E-Bike Motor Auslegung

Python application for sizing an e-bike motor and battery from the GPS, time and
temperature data of a real bike ride. It reads the GPS track, computes speed,
acceleration, slope, driving force, motor torque, current and power, determines
the overall ride metrics, and sizes and simulates two battery chemistries
(LiPo and NMC) over the ride.

The parameters of the ride are entered in the terminal and all results are
collected in a pdf report.

## Requirements

- Python 3.11 or newer (developed on 3.14)
- The packages listed in `requirements.txt` (installed automatically in the steps below)
- A LaTeX distribution with `pdflatex` (for example MiKTeX or TeX Live) to compile
  the report. This is optional: without it the program still runs and writes the
  LaTeX source `output/report.tex`, but no pdf is produced.

## Installation

Run all commands **from the project root** (the folder that contains `pyproject.toml`).

1. Get the code:
   ```bash
   git clone https://github.com/JakobFischl/E_Bike_Motor_Auslegung.git
   cd E_Bike_Motor_Auslegung
   ```

2. Create and activate a virtual environment:

   **Windows (PowerShell):**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   **macOS / Linux:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install the project together with its dependencies:
   ```bash
   pip install -e .
   ```
   This installs the pinned packages from `requirements.txt` and makes the
   `route_dynamics`, `ebike_simulation` and `ebike_app` packages importable.

## Running

From the project root, run:
```bash
python main.py
```

**Important:** 
The program must be started from the project root, because it uses the relative paths
`simulation_data/final_project_input_data.csv` and `output/`.

The program then asks for the parameters of the ride in the terminal. Every question
shows its default value in brackets, so simply pressing enter accepts the default and
no code has to be touched:

```
Press enter to accept the default value in brackets.

Path to the GPS data file [simulation_data/final_project_input_data.csv]:
Mass of the rider in kg [70]:
Mass of the bike in kg [10]:
Drag coefficient times frontal area in m^2 [0.5625]:
Wheel diameter in inch [27]:
Motor constant in Nm/A [1.5]:
State of charge reserve [0.05]:
```

Invalid answers are asked again instead of stopping the program.

Afterwards the whole result is written to `output/report.pdf`, which contains a
summary of the input parameters, the ride metrics and the battery simulation on the
first page, followed by one page per plot (elevation profile, speed, motor power and
the current, state of charge, voltage and power profiles of both battery packs).
No plot windows are opened.

## Output

Everything the program produces is written into the `output` folder, which is created
automatically:

```
output/report.pdf           The report with all results and plots
output/report.tex           The LaTeX code of the report
output/report.aux           Auxiliary files written by pdflatex
output/report.log
output/figures/             The plots of the report as single pdf files
output/simulation.log       The log messages of the run (overwritten on each run)
```

## Project structure

```
main.py                     Entry point: runs the full analysis and simulation
pyproject.toml              Project + dependency definition (used by pip install -e .)
requirements.txt            Pinned package versions
simulation_data/            Input GPS data
diagramms/                  UML class diagram and activity diagram
output/                     Generated report, plots and log (created on each run)
src/route_dynamics/         GPS route analysis, dynamics, ride metrics, route plots
src/ebike_simulation/       Battery models, simulator, capacity sizer, plots
src/ebike_app/              Input parameters and pdf report generation
```
## Project Architecture



### UML-Class Diagram
![Class Diagram](diagramms/UML_class_diagram.svg)

### Activity Diagram
![Activity Diagram](diagramms/activity_diagram.svg)

## Team

- Jakob Fischl: battery simulation and capacity sizing, ride metrics, parameter input,
  pdf report generation, `main.py`
- Jan Horsthemke: route analysis, driving dynamics and route plots

## Implemented extensions

The project also implements:

- **Dynamic air density:** 
  Instead of a constant density of 1.225 kg/m^3 the air density is computed for every
  GPS point from its elevation and the measured temperature with the barometric formula,
  so the temperature column of the input data is actually used.
- **GPS noise filtering:** 
  GPS points that are less than a configurable time apart are merged and a rolling
  median is applied to the speed. Without this the derived acceleration explodes and
  the peak power reaches an unrealistic 9.7 kW.
- **Terminal parameter input:** 
  All ride parameters are entered in the terminal with sensible defaults, so the user
  never has to touch the code.
- **Pdf report:** 
  The results are automatically collected in a LaTeX document that is compiled to `output/report.pdf`.
- **Logging:** 
  Every step of the program writes log messages to `output/simulation.log`.
- **Conventional Commits:** 
  The commit messages follow the Conventional Commits specification.

## Sources

### Course materials

- [Abschlussprojekt](https://mrp123.github.io/MCI-MECH-B-2-PRO1-PRO1-ILV/lectures/15_abschlussprojekt/1_abschlussprojekt.html):
  the task, the bike parameters and the OCV-SoC characteristics of both battery chemistries
- [OOP](https://mrp123.github.io/MCI-MECH-B-2-PRO1-PRO1-ILV/lectures/09_oop/2_oop_uebung.html),
  [Vererbung](https://mrp123.github.io/MCI-MECH-B-2-PRO1-PRO1-ILV/lectures/09_oop/3_vererbung.html),
  [Anwendung der OOP](https://mrp123.github.io/MCI-MECH-B-2-PRO1-PRO1-ILV/lectures/09_oop/4_anwendung_oop.html) and
  [OOP-Übungen 2](https://mrp123.github.io/MCI-MECH-B-2-PRO1-PRO1-ILV/lectures/09_oop/5_oop_uebung_2.html):
  the battery pack, motor and simulator classes the project builds on
- [Numpy](https://mrp123.github.io/MCI-MECH-B-2-PRO1-PRO1-ILV/lectures/10_scientific_computing/1_numpy_intro.html),
  [Matplotlib](https://mrp123.github.io/MCI-MECH-B-2-PRO1-PRO1-ILV/lectures/10_scientific_computing/2_matplotlib_intro.html),
  [Exceptions & Tests](https://mrp123.github.io/MCI-MECH-B-2-PRO1-PRO1-ILV/lectures/11_exceptions_tests/1_exceptions_test.html) and
  [Pathlib, Logging, Datetime, OS](https://mrp123.github.io/MCI-MECH-B-2-PRO1-PRO1-ILV/lectures/12_standard_pakete/1_pathlib_datetime_os.html)
- [Algorithmik & Diagramme](https://mrp123.github.io/MCI-MECH-B-2-PRO1-PRO1-ILV/lectures/08_algorithmik_diagramme/1_algorithmik_diagramme.html):
  activity diagrams
- [Git basics](https://mrp123.github.io/MCI-MECH-B-2-PRO1-PRO1-ILV/lectures/14_versionierung_git/1_git_basic.html) and
  [collaboration with Git and GitHub](https://mrp123.github.io/MCI-MECH-B-2-PRO1-PRO1-ILV/lectures/14_versionierung_git/2_git_colab.html)

### Data

- The GPS ride data in `simulation_data/final_project_input_data.csv` was provided
  with the assignment.

### Algorithms and background

- [Clamp (function) - Wikipedia](https://en.wikipedia.org/wiki/Clamp_(function)):
  clamping the state of charge to [0, 1]
- [Binary search - W3Schools](https://www.w3schools.com/Python/python_dsa_binarysearch.asp):
  finding the smallest sufficient battery capacity
- [Lineare Interpolation - Studyflix](https://studyflix.de/mathematik/lineare-interpolation-3767):
  interpolating the OCV-SoC characteristic

### Libraries and documentation

- [scipy.interpolate.PchipInterpolator](https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.PchipInterpolator.html):
  monotonic interpolation of the OCV-SoC characteristic
- [numpy.cumsum](https://numpy.org/doc/stable/reference/generated/numpy.cumsum.html),
  [numpy.less](https://numpy.org/doc/stable/reference/generated/numpy.less.html) and
  [numpy.concatenate](https://numpy.org/doc/stable/reference/generated/numpy.concatenate.html)
- [matplotlib.pyplot.stairs](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.stairs.html) and
  [axis ticks](https://matplotlib.org/stable/users/explain/axes/axes_ticks.html)
- [dataclasses](https://docs.python.org/3/library/dataclasses.html),
  [typing.NamedTuple](https://typing.python.org/en/latest/spec/namedtuples.html) and
  [logging](https://docs.python.org/3/library/logging.html) from the Python standard library
- [Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/):
  `pyproject.toml` and `pip install -e .`

### Tools and conventions

- [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
- [draw.io](https://www.drawio.com/): UML class diagram and activity diagram
- [Real Python - Creating Great README Files](https://realpython.com/readme-python-project/)

### AI assistance

- Claude (Anthropic) and Google Gemini were used for code review, explanations and
  debugging support.