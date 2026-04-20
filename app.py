"""
Gradio web app for the Euclid Consortium Editorial Board (ECEB) style linter.
Deploy on Hugging Face Spaces (SDK: Gradio).
"""

import tempfile
from pathlib import Path

import gradio as gr

from lint_euclid_style import __version__, lint_file, _CATEGORY_MAP

ALL_CATS = list(_CATEGORY_MAP.keys())
SEVERITY_ICON = {"error": "🔴", "warning": "🟡", "suggestion": "🔵"}


def run_linter(latex_source: str, min_severity: str, categories: list[str]) -> str:
    if not latex_source.strip():
        return "Paste some LaTeX source and click **Check style**."

    cats = categories if categories else ALL_CATS

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".tex", encoding="utf-8", delete=False
    ) as tmp:
        tmp.write(latex_source)
        tmp_path = Path(tmp.name)

    violations = lint_file(tmp_path, categories=cats, min_severity=min_severity)
    tmp_path.unlink(missing_ok=True)

    if not violations:
        return "✅ No violations found."

    n_err  = sum(1 for v in violations if v.severity == "error")
    n_warn = sum(1 for v in violations if v.severity == "warning")
    n_sugg = sum(1 for v in violations if v.severity == "suggestion")

    lines = latex_source.splitlines()
    parts = [
        f"**{len(violations)} violation(s)** — "
        f"🔴 {n_err} error(s) · 🟡 {n_warn} warning(s) · 🔵 {n_sugg} suggestion(s)\n\n---\n"
    ]

    for v in violations:
        icon = SEVERITY_ICON.get(v.severity, "•")
        src = lines[v.line - 1].strip() if 1 <= v.line <= len(lines) else ""
        sg  = f" · §{v.sg_section}" if v.sg_section else ""
        parts.append(
            f"{icon} **Line {v.line}** · `{v.rule_id}`{sg}\n"
            f"{v.message}\n"
            + (f"```latex\n{src}\n```\n" if src else "")
        )

    return "\n".join(parts)


with gr.Blocks(title="ECEB Style Linter") as demo:
    gr.Markdown(
        f"# 🔭 Euclid Style Linter  \n"
        f"*Linter version `v{__version__}`*\n\n"
        f"Check your LaTeX source against the **ECEB Style Guide V4.0** — "
        f"44 rules covering naming, British English, units, typesetting, references, and style."
    )

    with gr.Row():
        with gr.Column(scale=3):
            latex_input = gr.Textbox(
                label="LaTeX source",
                placeholder="\\documentclass{aa}\n\\begin{document}\n...\n\\end{document}",
                lines=20,
            )
            check_btn = gr.Button("Check style", variant="primary")

        with gr.Column(scale=1):
            severity = gr.Radio(
                label="Minimum severity",
                choices=["suggestion", "warning", "error"],
                value="suggestion",
            )
            cats = gr.CheckboxGroup(
                label="Categories",
                choices=ALL_CATS,
                value=ALL_CATS,
            )

    output = gr.Markdown(label="Results")

    check_btn.click(fn=run_linter, inputs=[latex_input, severity, cats], outputs=output)

if __name__ == "__main__":
    demo.launch()
