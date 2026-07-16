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

**Important:** the program must be started from the project root, because it uses
the relative paths `simulation_data/final_project_input_data.csv` and `output/`.

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
![Class Diagram](diagramms/UML-Classdiagramm.png)

### Activity Diagram
![Activity Diagram](diagramms/Aktivitätsdiagramm.png)