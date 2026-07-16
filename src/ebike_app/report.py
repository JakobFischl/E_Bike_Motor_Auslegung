from ebike_app.parameters import RideParameters
from route_dynamics.ride_metrics import RideMetrics
import shutil
import subprocess
import logging

from string import Template
from pathlib import Path
from datetime import datetime

# Set up local logger
logger = logging.getLogger(__name__)

# Characters that have to be replaced.
LATEX_SPECIAL_CHARACTERS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


class LatexTemplate(Template):
    """Template that marks placeholders with @ because LaTeX already uses $ for math mode."""
    delimiter = "@"


REPORT_TEMPLATE = LatexTemplate(r"""\documentclass[a4paper,11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{graphicx}
\usepackage[margin=2.5cm,landscape]{geometry}

\title{E-Bike Motor Auslegung \\ Ride Report}
\date{@DATE}
\author{Jakob Fischl, Jan Horsthemke}

\begin{document}
\maketitle

\section*{Input parameters}
\begin{tabular}{ll}
\hline
Parameter & Value \\
\hline
@PARAMETER_ROWS
\hline
\end{tabular}

\vspace{1em}

\noindent
\begin{minipage}[t]{0.48\textwidth}
\section*{Ride metrics}
\begin{tabular}{ll}
\hline
Quantity & Value \\
\hline
@METRIC_ROWS
\hline
\end{tabular}
\end{minipage}
\hfill
\begin{minipage}[t]{0.48\textwidth}
\section*{Battery simulation}
@BATTERY_TABLE
\end{minipage}

\clearpage
\centering
@FIGURE_PAGES
\end{document}
""")


def escape_latex(text) -> str:
    """Return the text with every character that has a special meaning in LaTeX escaped."""
    return "".join(LATEX_SPECIAL_CHARACTERS.get(character, character) for character in str(text))


def format_table_rows(rows: list[tuple]) -> str:
    """
    Turn (label, value) pairs into the rows of a two column LaTeX table.
    """
    return "\n".join(f"{label} & {value} \\\\" for label, value in rows)


def format_parameter_rows(parameters: RideParameters) -> str:
    """Return the input parameters the user chose in a table."""
    return format_table_rows([
        ("Data file", escape_latex(parameters.data_file_path)),
        ("Mass of the rider", f"{parameters.rider_mass_kg:.1f} kg"),
        ("Mass of the bike", f"{parameters.bike_mass_kg:.1f} kg"),
        ("Drag coefficient times frontal area", f"{parameters.cwA_m2:.4f} m\\textsuperscript{{2}}"),
        ("Wheel diameter", f"{parameters.wheel_diameter_inch:.1f} inch"),
        ("Motor constant", f"{parameters.motor_constant_Nm_A:.2f} Nm/A"),
        ("State of charge reserve", f"{parameters.soc_reserve * 100:.1f} \\%"),
        ("Initial state of charge", f"{parameters.initial_soc * 100:.1f} \\%"),
    ])


def format_metric_rows(metrics: RideMetrics) -> str:
    """Return the aggregate ride metrics in a table."""
    return format_table_rows([
        ("Distance travelled", f"{metrics.total_distance_m / 1000:.2f} km"),
        ("Time needed", f"{metrics.total_time_s / 60:.1f} min"),
        ("Average speed", f"{metrics.average_speed_m_s * 3.6:.2f} km/h"),
        ("Elevation gain", f"{metrics.elevation_gain_m:.1f} m"),
        ("Elevation loss", f"{metrics.elevation_loss_m:.1f} m"),
        ("Peak mechanical power", f"{metrics.max_power_W:.1f} W"),
    ])


def format_battery_table(battery_results: list[tuple]) -> str:
    """
    Return the results of every simulated battery pack as a LaTeX table.
    battery_results: (name, capacity in Ah, SummaryResult) for each pack.
    """
    column_spec = "l" + "r" * len(battery_results)
    header = "Quantity & " + " & ".join(escape_latex(name) for name, _, _ in battery_results)

    rows = [
        ("Required capacity (Ah)", [f"{capacity:.1f}" for _, capacity, _ in battery_results]),
        ("Final state of charge (\\%)", [f"{result.final_soc * 100:.2f}" for _, _, result in battery_results]),
        ("Lowest state of charge (\\%)", [f"{result.min_soc * 100:.2f}" for _, _, result in battery_results]),
        ("Peak power draw (W)", [f"{result.max_power:.1f}" for _, _, result in battery_results]),
        ("Energy usage (Wh)", [f"{result.total_energy / 3600:.1f}" for _, _, result in battery_results]),
        ("Total discharge (Ah)", [f"{result.total_discharge / 3600:.2f}" for _, _, result in battery_results]),
    ]
    body = "\n".join(f"{label} & " + " & ".join(values) + " \\\\" for label, values in rows)

    return (
        f"\\begin{{tabular}}{{{column_spec}}}\n"
        "\\hline\n"
        f"{header} \\\\\n"
        "\\hline\n"
        f"{body}\n"
        "\\hline\n"
        "\\end{tabular}"
    )


def save_figures(figures: list[tuple], figures_folder: Path) -> list[tuple]:
    """
    Save every figure as a vector pdf and return (file name, caption) for each of them.
    figures: (figure, caption) pairs in the order they should appear in the report.
    """
    figures_folder.mkdir(parents=True, exist_ok=True)
    saved = []

    for number, (figure, caption) in enumerate(figures, start=1):
        file_name = f"figure{number:02d}.pdf"
        figure.savefig(figures_folder / file_name, bbox_inches="tight")
        saved.append((file_name, caption))

    logger.debug(f"Saved {len(saved)} figures to '{figures_folder}'.")
    return saved


def format_figure_pages(saved_figures: list[tuple]) -> str:
    """Return one LaTeX page per saved figure, each with its caption as a heading."""
    pages = []
    for file_name, caption in saved_figures:
        pages.append(
            f"\\section*{{{escape_latex(caption)}}}\n"
            f"\\centering"
            f"\\includegraphics[width=\\textwidth,height=0.8\\textheight,keepaspectratio]{{figures/{file_name}}}\n"
            "\\clearpage"
        )
    return "\n".join(pages)


def compile_report(tex_path: Path) -> Path | None:
    """
    Compile a LaTeX file into a pdf and return the path to the pdf.
    Returns None if no LaTeX engine is installed or the compilation failed,
    so that a missing engine never stops the rest of the application.
    """
    if shutil.which("pdflatex") is None:
        logger.warning("pdflatex was not found, only the LaTeX source was written.")
        return None

    try:
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex_path.name],
            cwd=tex_path.parent,
            capture_output=True,
            text=True,
            timeout=180
        )
    except subprocess.TimeoutExpired:
        logger.error("pdflatex did not finish within 180 seconds.")
        return None

    if result.returncode != 0:
        logger.error(f"pdflatex failed:\n{result.stdout[-2000:]}")
        return None

    pdf_path = tex_path.with_suffix(".pdf")
    logger.info(f"Compiled the report to '{pdf_path}'.")
    return pdf_path


def build_report(
        parameters: RideParameters,
        metrics: RideMetrics,
        battery_results: list[tuple],
        figures: list[tuple],
        output_folder: Path) -> Path | None:
    """
    Write a LaTeX report with the input parameters, the ride metrics and every figure
    and compile it into a pdf. Returns the path to the pdf, or to the LaTeX source
    when no pdf could be produced.
    parameters: the parameters the user chose.
    metrics: the aggregate metrics of the ride.
    battery_results: (name, capacity in Ah, SummaryResult) for each simulated pack.
    figures: (figure, caption) pairs in the order they should appear.
    output_folder: folder the report and the figures are written to.
    """

    output_folder.mkdir(exist_ok=True)
    saved_figures = save_figures(figures, output_folder / "figures")

    source = REPORT_TEMPLATE.substitute(
        DATE=datetime.now().strftime("%Y-%m-%d %H:%M"),
        PARAMETER_ROWS=format_parameter_rows(parameters),
        METRIC_ROWS=format_metric_rows(metrics),
        BATTERY_TABLE=format_battery_table(battery_results),
        FIGURE_PAGES=format_figure_pages(saved_figures)
    )

    tex_path = output_folder / "report.tex"
    tex_path.write_text(source, encoding="utf-8")
    logger.info(f"Wrote the LaTeX source to '{tex_path}'.")

    pdf_path = compile_report(tex_path)
    if pdf_path is None:
        return tex_path
    return pdf_path
