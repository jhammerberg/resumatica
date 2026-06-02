#!/usr/bin/env -S uv run

from yaspin import yaspin
from termcolor import colored

# Fun spinner while we load packages
spinner = yaspin()
spinner.text = colored("Initializing...", "yellow")
spinner.start()

import jinja2
import argparse
from pathlib import Path
from dataclasses import dataclass, asdict
import subprocess
import yaml
import re

PROJECT_DIR = Path(__file__).parent
DEFAULT_TEMPLATE = (PROJECT_DIR / "templates" / "classic.jinja")
DEFAULT_RESUME = (PROJECT_DIR / "resumes" / "resume.yaml")
DOCKER_IMAGE = "texlive/texlive:latest"

@dataclass
class Education:
    school: str
    location: str
    degree: str
    field_of_study: str
    start_date: str
    end_date: str

@dataclass
class Position:
    title: str
    start_date: str
    end_date: str
    bullets: list[str]    

@dataclass
class Experience:
    company: str
    location: str
    positions: list[Position]    

@dataclass
class Resume:
    first_name: str
    last_name: str
    contact_info: list[str]

    education: list[Education]
    work_experience: list[Experience]
    project_experience: list[Experience]
    skills: dict[str, list[str]]

_MARKDOWN_URL_RE = re.compile(r'^\[([^\]]*)\]\(([^)]+)\)$')

def markdown_url_to_latex(text: str) -> str | None:
    match = _MARKDOWN_URL_RE.match(text.strip())
    if not match:
        return None
    label, url = match.group(1), match.group(2)
    if url.startswith('mailto:'):
        return rf'\href{{{url}}}{{{escape_latex(label)}}}'
    return rf'\url{{{url}}}'

def escape_latex(text: str) -> str:
    """Escapes reserved LaTeX characters in a string."""
    if not isinstance(text, str):
        return text
        
    latex_replacements = {
        '\\': r'\textbackslash{}',
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}'
    }
    
    # Use regex to replace characters efficiently without double-escaping
    regex = re.compile('|'.join(re.escape(key) for key in latex_replacements.keys()))
    return regex.sub(lambda match: latex_replacements[match.group(0)], text)

def escape_latex_recursive(data):
    """Recursively traverses dictionaries and lists to escape LaTeX characters in strings."""
    if isinstance(data, str):
        if latex_url := markdown_url_to_latex(data):
            return latex_url
        return escape_latex(data)
    elif isinstance(data, list):
        return [escape_latex_recursive(item) for item in data]
    elif isinstance(data, dict):
        return {key: escape_latex_recursive(value) for key, value in data.items()}
    return data

def load_resume_from_yaml(file_path: Path) -> Resume:
    with open(file_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
        
    # Recursively escape all strings in the parsed YAML dictionary
    data = escape_latex_recursive(data)
        
    # Process Education
    education_objects = [
        Education(**edu) for edu in data.get('education', [])
    ]
    
    # Process Work Experience
    work_objects = []
    for exp in data.get('work_experience', []):
        positions = [Position(**pos) for pos in exp.get('positions', [])]
        work_objects.append(Experience(
            company=exp['company'],
            location=exp['location'],
            positions=positions
        ))
        
    # Process Project Experience
    project_objects = []
    for exp in data.get('project_experience', []):
        positions = [Position(**pos) for pos in exp.get('positions', [])]
        project_objects.append(Experience(
            company=exp['company'],
            location=exp['location'],
            positions=positions
        ))
        
    # Construct final Resume object
    return Resume(
        first_name=data.get('first_name', ''),
        last_name=data.get('last_name', ''),
        contact_info=data.get('contact_info', []),
        education=education_objects,
        work_experience=work_objects,
        project_experience=project_objects,
        skills=data.get('skills', {})
    )

def make_tex(template_path: Path, output_dir: Path, resume: Resume) -> Path:
    tex_file_name = template_path.stem + ".tex"
    output_path = output_dir / tex_file_name

    latex_jinja_env = jinja2.Environment(
        block_start_string=r"\BLOCK{",
        block_end_string="}",
        variable_start_string=r"\VAR{",
        variable_end_string="}",
        comment_start_string=r"\#{",
        comment_end_string="}",
        line_statement_prefix="%%",
        line_comment_prefix="%#",
        trim_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader(Path.cwd()),
    )

    template = latex_jinja_env.get_template(str(template_path.relative_to(Path.cwd())))
    rendered_tex = template.render(asdict(resume))

    with open(output_path, "w") as f:
        f.write(rendered_tex)

    return output_path


def prepare_docker() -> None:
    # Check if docker is installed
    with yaspin(
        text=colored("Checking Docker installation...", "yellow"), color="yellow"
    ) as docker_spinner:
        result = subprocess.run(
            ["docker", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode != 0:
            docker_spinner.write(
                colored(
                    "Docker is not installed or not in PATH. Please install Docker or run with the --native flag.",
                    "red",
                )
            )
            exit(1)
            
        # Check if texlive image is available, if not pull it
        result = subprocess.run(
            ["docker", "images", "-q", DOCKER_IMAGE],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if not result.stdout.strip():
            docker_spinner.text = colored(
                f"Pulling Docker image {DOCKER_IMAGE}...", "yellow"
            )
            pull_result = subprocess.run(
                ["docker", "pull", DOCKER_IMAGE],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if pull_result.returncode != 0:
                docker_spinner.write(
                    colored(f"Error pulling Docker image {DOCKER_IMAGE}:", "red")
                )
                print(pull_result.stderr)
                print(pull_result.stdout)
                exit(1)


def compile_tex(tex_path: Path, output_dir: Path, docker: bool = True) -> None:
    result = None
    if docker:
        prepare_docker()

        with yaspin(
            text=colored("Compiling LaTeX with Docker...", "yellow"), color="yellow"
        ) as compile_spinner:
            cmd = [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{PROJECT_DIR}:/workdir:z",
                DOCKER_IMAGE,
                "xelatex",
                "-output-directory",
                Path("/workdir") / output_dir,
                (output_dir / tex_path.name),
            ]
            for _ in range(2):
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                if result.returncode != 0:
                    break
    else:
        cmd = [
            "pdflatex",
            "-output-directory",
            str(output_dir),
            str(tex_path),
        ]
        for _ in range(2):
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.returncode != 0:
                break
    if result.returncode != 0:
        print(colored("Error compiling LaTeX:", "red"))
        print(result.stderr)
        print(result.stdout)
    else:
        print(colored(f"LaTeX compiled successfully to: {(output_dir / tex_path.stem).absolute()}.pdf", "green"))


def prase_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a resume from a template and data file."
    )

    parser.add_argument(
        "-t",
        "--template", 
        type=Path, 
        default=DEFAULT_TEMPLATE,
        help=f"Path to the LaTeX-Jinja template file (Default is {DEFAULT_TEMPLATE})"
    )

    parser.add_argument(
        "-r",
        "--resume",
        type=Path,
        default=DEFAULT_RESUME,
        help=f"Path to the YAML file containing resume data (Default is {DEFAULT_RESUME})",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("build/"),
        help="Path to build directory where the output will be saved (Default is 'build/')",
    )

    parser.add_argument(
        "--native",
        action="store_true",
        help="Compile LaTeX natively without Docker (Requires local LaTeX installation)",
    )

    return parser.parse_args()


def main() -> None:
    args = prase_cli_args()
    args.output.mkdir(parents=True, exist_ok=True)
    print(colored(f"Using template: {args.template}", "green"))
    print(colored(f"Using resume data: {args.resume}", "green"))
    print(colored(f"Output directory: {args.output}", "green"))
    resume = load_resume_from_yaml(args.resume)
    tex_path = make_tex(args.template, args.output, resume)
    compile_tex(tex_path, args.output)


if __name__ == "__main__":
    spinner.stop()
    main()
