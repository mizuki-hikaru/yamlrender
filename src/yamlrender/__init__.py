import sys
import yaml
import re
import subprocess
import tempfile
from pathlib import Path
from renderlet import render_file


def yamlrender(input_path, template_path, output_path):
    input_path = Path(input_path)
    template_path = Path(template_path)
    output_path = Path(output_path)

    # Load YAML data
    with input_path.open('r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    templates_dir = template_path.parent

    # Set up Jinja2 environment
    rendered_html = render_file(template_path, **data)

    # Output
    if output_path.suffix == ".pdf":
        with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8') as tmp:
            header_inject = '<style>@page { margin-top: 0; padding-top: 2em; margin-bottom: 0; padding-bottom: 2em; }</style>'
            if '</head>' in rendered_html:
                html_for_pdf = rendered_html.replace('</head>', header_inject + '</head>', 1)
            else:
                html_for_pdf = header_inject + rendered_html
            tmp.write(html_for_pdf)
            tmp_path = Path(tmp.name)
        try:
            subprocess.run([
                "google-chrome",
                "--disable-gpu",
                "--headless",
                f"--print-to-pdf={output_path}",
                str(tmp_path),
            ], check=True)
        finally:
            tmp_path.unlink()
    else:
        output_path.write_text(rendered_html, encoding='utf-8')

def cli():
    import argparse

    parser = argparse.ArgumentParser(description="Render HTML or PDF from a YAML file and Jinja2 template.")
    parser.add_argument("input", help="Path to input YAML file")
    parser.add_argument("template", help="Path to Jinja2 template file")
    parser.add_argument("output", help="Path to output HTML or PDF file")
    args = parser.parse_args()

    try:
        yamlrender(args.input, args.template, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
