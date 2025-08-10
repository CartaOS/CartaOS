"""
CartaOS - A command-line tool for academic document processing.

This tool provides a command-line interface for processing academic documents
using the CartaOS library. It allows users to generate analytical summaries for
PDF files and save them to a designated directory.

The tool is designed to be extensible and can be customized to integrate with
other tools and services.

This script uses Typer to create a professional CLI that serves as the
entry point for all backend operations, including triage, lab processing,
OCR, and summarization.

The main entry point for the tool is the `cartaos` command, which provides a
helpful interface for generating summaries and configuring the tool.

The `setup` command guides the user through the initial configuration of
CartaOS, including setting up the API key for Google Gemini and the path to
the Obsidian vault.

The `summarize` command generates an analytical summary for a given PDF file
and saves it to a designated directory.

The tool uses the `typer` library to define its command-line interface and
provides helpful documentation and error messages.

The code is organized into a single module, with the main entry point at the
bottom of the file.
"""

import typer
from pathlib import Path
from typing_extensions import Annotated
import logging

# Import all the processor classes from our modules
from cartaos.processor import CartaOSProcessor
from cartaos.lab import LabProcessor
from cartaos.ocr import OcrProcessor
from cartaos.triage import TriageProcessor

# --- Configuration ---
app = typer.Typer(
    help="📚 CartaOS - A command-line tool for academic document processing.",
    add_completion=False,
    rich_markup_mode="markdown"
)

# Define base directories relative to this file's location
BASE_DIR = Path(__file__).parent.parent.parent
DIR_TRIAGE = BASE_DIR / "02_Triage"
DIR_LAB = BASE_DIR / "03_Lab"
DIR_READY_FOR_OCR = BASE_DIR / "04_ReadyForOCR"
DIR_READY_FOR_SUMMARY = BASE_DIR / "05_ReadyForSummary"

@app.command()
def setup():
    """
    Guides the user through the initial configuration of CartaOS.
    """
    typer.secho("--- CartaOS Setup ---", fg=typer.colors.CYAN)
    
    backend_root = Path(__file__).parent.parent
    env_path = backend_root / '.env'

    if env_path.exists():
        typer.secho(f"✔️ .env file already exists at: {env_path.as_posix()}", fg=typer.colors.GREEN)
    else:
        typer.echo("Let's configure your API key for Google Gemini.")
        api_key = typer.prompt("Please paste your Google API Key here")
        
        obsidian_path = typer.prompt(
            "(Optional) Enter the absolute path to your Obsidian vault. Leave blank to skip", 
            default=""
        )

        with open(env_path, "w") as f:
            f.write(f'GOOGLE_API_KEY="{api_key}"\n')
            if obsidian_path:
                f.write(f'OBSIDIAN_VAULT_PATH="{obsidian_path}"\n')
        
        typer.secho(f"🎉 Success! Configuration saved to {env_path.as_posix()}", fg=typer.colors.GREEN)


@app.command()
def triage():
    """
    Scans the Triage (02) directory and classifies files.
    """
    typer.secho("--- Starting Triage Process ---", fg=typer.colors.BLUE)
    try:
        processor = TriageProcessor(
            input_dir=DIR_TRIAGE,
            summary_dir=DIR_READY_FOR_SUMMARY,
            lab_dir=DIR_LAB
        )
        processor.process()
        typer.secho("✅ Triage process completed successfully.", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"❌ An error occurred during triage: {str(e)}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

@app.command()
def lab(
    pdf_path: Annotated[Path, typer.Argument(exists=True, help="Path to the PDF file in the Lab to be corrected.")]
):
    """
    Sends a PDF to the manual correction lab with ScanTailor.
    """
    typer.secho(f"🔬 Sending '{pdf_path.name}' to the correction lab...", fg=typer.colors.MAGENTA)
    try:
        processor = LabProcessor(input_path=pdf_path, output_dir=DIR_READY_FOR_OCR)
        processor.process()
    except Exception as e:
        typer.secho(f"❌ An error occurred during lab processing: {str(e)}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    
@app.command()
def ocr():
    """
    Runs batch OCR on all PDFs in the ReadyForOCR (04) directory.
    """
    typer.secho(f"👁️‍🗨️ Starting batch OCR on directory: {DIR_READY_FOR_OCR}", fg=typer.colors.BLUE)
    pdf_files = list(DIR_READY_FOR_OCR.rglob("*.pdf"))
    if not pdf_files:
        typer.secho("No PDF files found to process in the OCR queue.", fg=typer.colors.YELLOW)
        return

    with typer.progressbar(pdf_files, label="Processing files") as progress:
        for pdf in progress:
            out_pdf = DIR_READY_FOR_SUMMARY / pdf.relative_to(DIR_READY_FOR_OCR)
            processor = OcrProcessor(input_path=pdf, output_path=out_pdf)
            if processor.process():
                pdf.unlink() # Remove original after success
            else:
                typer.secho(f"\nFailed to process {pdf.name}", fg=typer.colors.RED)
    
    typer.secho("✅ Batch OCR complete.", fg=typer.colors.GREEN)

@app.command()
def summarize(
    pdf_path: Annotated[Path, typer.Argument(help="Path to the PDF file to be processed.")],
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Run without saving or moving files.")] = False,
    debug: Annotated[bool, typer.Option("--debug", help="Save extracted text and stop before AI call.")] = False,
    force_ocr: Annotated[bool, typer.Option("--force-ocr", help="Force OCR processing before summarization.")] = False, # <-- NOVA OPÇÃO
):
    """
    Generates an analytical summary for a given PDF file.
    """
    expanded_pdf_path = pdf_path.expanduser()

    if not expanded_pdf_path.exists():
        typer.secho(f"❌ Error: File not found at '{expanded_pdf_path}'", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.secho(f"▶️  Starting summary for: {expanded_pdf_path.name}", fg=typer.colors.CYAN)
    try:
        processor = CartaOSProcessor(
            pdf_path=str(expanded_pdf_path),
            dry_run=dry_run,
            debug=debug,
            force_ocr=force_ocr # <-- Passa a nova opção
        )
        
        if processor.process():
            typer.secho(f"✅ Summary for '{expanded_pdf_path.name}' completed successfully.", fg=typer.colors.GREEN)
            
            # ADD THIS BLOCK: Check for and display captured warnings
            if processor.captured_warnings:
                typer.secho(
                    "\n" + "="*50, fg=typer.colors.YELLOW)
                typer.secho(
                    "       ⚠️  DOCUMENT QUALITY WARNING", fg=typer.colors.YELLOW, bold=True)
                typer.secho(
                    "   Internal issues were detected in the original PDF file.\n"
                    "   This may have affected the quality of the text extraction and,\n"
                    "   consequently, the final summary.",
                    fg=typer.colors.YELLOW
                )
                typer.secho(
                    "="*50 + "\n", fg=typer.colors.YELLOW)

        else:
            typer.secho(f"⚠️ Summary for '{expanded_pdf_path.name}' failed. Check logs for details.", fg=typer.colors.YELLOW, err=True)
            raise typer.Exit(code=1)

    except Exception as e:
        typer.secho(f"❌ Fatal error during processing: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
if __name__ == "__main__":
    app()




