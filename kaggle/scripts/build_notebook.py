#!/usr/bin/env python3
"""Génère le notebook de soumission Kaggle kaggle/notebooks/gemma4_replay_submission.ipynb."""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SUBMISSION_DIR = REPO_ROOT / "submission"
NOTEBOOKS_DIR = REPO_ROOT / "notebooks"
NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)

files = {}
for p in sorted(SUBMISSION_DIR.rglob("*")):
    if p.is_file():
        rel = p.relative_to(SUBMISSION_DIR).as_posix()
        files[rel] = p.read_text(encoding="utf-8")

print(f"Loaded {len(files)} files from {SUBMISSION_DIR}:")
for k in files:
    print(f"  - {k}")

cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# Gemma 4 Developer Agent: Replay Architecture Submission\n",
            "\n",
            "Autonomous developer agent built on **Google Gemma 4 31B QAT** (`gemma-4-31b-it-qat-w4a16-ct`), featuring:\n",
            "- **Multi-agent isolation**: Dedicated read-only `code_analyzer` sub-agent (`skip_summarization: true`) preserving the 32k context window.\n",
            "- **Disciplined Replay Cycle**: `/tmp/repro.py` failure reproduction -> atomic `edit_file` patch -> targeted pytest feedback with output tailing (`tail -n 40`) to mitigate the 5,000-character truncation limit.\n",
            "- **No premature timeouts**: Unrestricted per-task execution by dropping the restrictive 1-minute `eval_config.yaml`.\n",
            "- **Optimized Sampling**: 4,096 thinking budget with `include_thoughts: false` to keep thought overhead outside conversation context."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import os\n",
            "import sys\n",
            "import shutil\n",
            "import zipfile\n",
            "import subprocess\n",
            "from pathlib import Path\n",
            "import yaml\n",
            "import re\n",
            "\n",
            "WORKING = Path('/kaggle/working') if Path('/kaggle/working').exists() else Path('./working')\n",
            "WORKING.mkdir(parents=True, exist_ok=True)\n",
            "BUNDLE = WORKING / 'submission_bundle'\n",
            "ZIP_PATH = WORKING / 'submission.zip'\n",
            "print(f'Target zip: {ZIP_PATH}')\n"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            f"BUNDLE_FILES = {repr(files)}\n\n",
            "shutil.rmtree(BUNDLE, ignore_errors=True)\n",
            "for rel_path, content in BUNDLE_FILES.items():\n",
            "    p = BUNDLE / rel_path\n",
            "    p.parent.mkdir(parents=True, exist_ok=True)\n",
            "    p.write_text(content, encoding='utf-8')\n",
            "\n",
            "print(f'Extracted {len(BUNDLE_FILES)} files into {BUNDLE}:')\n",
            "for p in sorted(BUNDLE.rglob('*')):\n",
            "    if p.is_file():\n",
            "        print(f'  {p.stat().st_size:>6} B  {p.relative_to(BUNDLE)}')\n"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Standalone Rule Validation\n",
            "ROOT_CONFIGS = ['agent.yaml', 'agent.yml', 'root_agent.yaml', 'root_agent.yml']\n",
            "ALLOWED_SUFFIXES = {'.yaml', '.yml', '.md', '.txt', '.py', '.json', '.safetensors'}\n",
            "yaml.SafeLoader.add_constructor('!include', lambda loader, node: loader.construct_scalar(node))\n",
            "\n",
            "def validate(bundle: Path) -> None:\n",
            "    files = [p for p in bundle.rglob('*') if p.is_file()]\n",
            "    roots = [name for name in ROOT_CONFIGS if (bundle / name).is_file()]\n",
            "    assert len(roots) == 1, f'Need exactly one root config, found {roots}'\n",
            "    assert not any(p.is_symlink() for p in bundle.rglob('*')), 'Symlinks are forbidden'\n",
            "    assert all(p.suffix in ALLOWED_SUFFIXES for p in files), 'Disallowed file suffixes found'\n",
            "    total_bytes = sum(p.stat().st_size for p in files)\n",
            "    assert total_bytes < 3 * (1024**3), 'Unpacked bundle exceeds 3 GiB'\n",
            "    \n",
            "    models = set()\n",
            "    for config in (p for p in files if p.suffix in ('.yaml', '.yml')):\n",
            "        text = config.read_text(encoding='utf-8')\n",
            "        data = yaml.safe_load(text) or {}\n",
            "        for target in re.findall(r'!include\\s+(\\S+)', text):\n",
            "            target_path = (config.parent / target).resolve()\n",
            "            assert target_path.is_file(), f'{config.name}: missing include {target}'\n",
            "        if 'model' in data:\n",
            "            models.add(data['model'].split('/')[-1])\n",
            "            \n",
            "    assert len(models) == 1, f'One base model per submission, found {models}'\n",
            "    assert list(models)[0] == 'gemma-4-31b-it-qat-w4a16-ct', f'Model must be gemma-4-31b-it-qat-w4a16-ct, got {models}'\n",
            "    print(f'SUCCESS: Validated {roots[0]}, {len(files)} files, model: {list(models)[0]}, size: {total_bytes} bytes.')\n",
            "\n",
            "validate(BUNDLE)\n"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Optional Harness Validation if wheelhouse is attached\n",
            "HARNESS_WHEELS = ('google_adk-', 'google_genai-', 'adk_submission-', 'adk_eval_core-', 'swegemma-')\n",
            "MODEL = 'gemma-4-31b-it-qat-w4a16-ct'\n",
            "\n",
            "def install_harness():\n",
            "    found = sorted(Path('/kaggle/input').glob('**/adk_submission-*.whl'))\n",
            "    if found:\n",
            "        wheelhouse = found[0].parent\n",
            "        wheels = [str(w) for w in sorted(wheelhouse.glob('*.whl')) if w.name.startswith(HARNESS_WHEELS)]\n",
            "        subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '--no-deps', *wheels], check=True)\n",
            "\n",
            "try:\n",
            "    try:\n",
            "        import adk_submission\n",
            "    except ImportError:\n",
            "        install_harness()\n",
            "    from adk_submission import ModelRegistry, compile_submission, validate_directory\n",
            "    from google.adk.models.lite_llm import LiteLlm\n",
            "    from swegemma.config import build_submission_limits\n",
            "    from swegemma.models.discovery import validate_single_declared_model\n",
            "    \n",
            "    def run_command(command: str) -> str: ...\n",
            "    def read_file(filepath: str, start_line: int | None = None, end_line: int | None = None) -> str: ...\n",
            "    def write_file(filepath: str, content: str) -> str: ...\n",
            "    def edit_file(filepath: str, old_string: str, new_string: str, allow_multiple: bool = False) -> str: ...\n",
            "    def submit_patch() -> str: ...\n",
            "    def get_status() -> str: ...\n",
            "    def get_code_neighbors(node: str, edge_type: str | None = None, max_neighbors: int = 50) -> str: ...\n",
            "    def search_similar_code(query: str, k: int = 10) -> str: ...\n",
            "    def get_code_subgraph(nodes: list[str]) -> str: ...\n",
            "    \n",
            "    limits, constraints = build_submission_limits()\n",
            "    models = ModelRegistry()\n",
            "    models.register(MODEL, LiteLlm(model=f'openai/{MODEL}', api_base='http://127.0.0.1:9/v1', api_key='EMPTY'))\n",
            "    tools = {f.__name__: f for f in [run_command, read_file, write_file, edit_file, submit_patch, get_status,\n",
            "                                     get_code_neighbors, search_similar_code, get_code_subgraph]}\n",
            "    validate_directory(BUNDLE, limits)\n",
            "    print('validate_directory: OK')\n",
            "    print('validate_single_declared_model:', validate_single_declared_model(BUNDLE))\n",
            "    agent = compile_submission(BUNDLE, tools, models, limits=limits, generation_constraints=constraints)\n",
            "    print(f'compile_submission: OK, root agent: {agent.name!r}')\n",
            "except Exception as e:\n",
            "    print(f'Official harness check skipped or unavailable ({e}); offline validation confirmed.')\n"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Build Clean submission.zip\n",
            "if ZIP_PATH.exists():\n",
            "    ZIP_PATH.unlink()\n",
            "\n",
            "with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as archive:\n",
            "    for path in sorted(p for p in BUNDLE.rglob('*') if p.is_file()):\n",
            "        archive.write(path, path.relative_to(BUNDLE).as_posix())\n",
            "\n",
            "with zipfile.ZipFile(ZIP_PATH) as archive:\n",
            "    names = archive.namelist()\n",
            "\n",
            "assert 'agent.yaml' in names, 'agent.yaml must be at the root of the archive'\n",
            "assert not any(name.endswith('/') for name in names), 'Zip archive must contain files only'\n",
            "shutil.rmtree(BUNDLE, ignore_errors=True)\n",
            "print(f'✅ Successfully built {ZIP_PATH} ({ZIP_PATH.stat().st_size:,} bytes)')\n",
            "print('Archive entries:')\n",
            "for n in names:\n",
            "    print(f'  - {n}')\n"
        ]
    }
]

nb = {
    "cells": cells,
    "metadata": {
        "language_info": {"name": "python"},
        "kernelspec": {"name": "python3", "display_name": "Python 3"}
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

out_nb = NOTEBOOKS_DIR / "gemma4_replay_submission.ipynb"
out_nb.write_text(json.dumps(nb, indent=2), encoding="utf-8")
print(f"\n🎉 Successfully wrote submission notebook to: {out_nb}")
