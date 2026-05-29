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
import subprocess

DOCKER_IMAGE = "texlive/texlive:latest"


def make_tex(template_path: Path, output_dir: Path, data: dict) -> Path:
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

    template = latex_jinja_env.get_template(str(template_path))
    rendered_tex = template.render(data)

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
            result = subprocess.run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "-v",
                    f"{output_dir.absolute()}:/workdir:z",
                    DOCKER_IMAGE,
                    "pdflatex",
                    "-output-directory",
                    "/workdir",
                    tex_path.name,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
    else:
        result = subprocess.run(
            ["pdflatex", "-output-directory", str(output_dir), str(tex_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    if result.returncode != 0:
        print(colored("Error compiling LaTeX:", "red"))
        print(result.stderr)
        print(result.stdout)


def prase_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a resume from a template and data file."
    )

    parser.add_argument("template", type=Path, help="Path to the LaTeX template file.")

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("build/"),
        help="Path to build directory where the output will be saved (Default is 'build/')",
    )

    return parser.parse_args()


def main() -> None:
    args = prase_cli_args()
    # Make the output directory if it doesnt already exist
    args.output.mkdir(parents=True, exist_ok=True)

    data = {}
    tex_path = make_tex(args.template, args.output, data)
    compile_tex(tex_path, args.output)


if __name__ == "__main__":
    spinner.stop()
    main()
