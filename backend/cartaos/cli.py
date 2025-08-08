"""
CartaOS - A command-line tool for academic document processing.

This tool provides a command-line interface for processing academic documents
using the CartaOS library. It allows users to generate analytical summaries for
PDF files and save them to a designated directory.

The tool is designed to be extensible and can be customized to integrate with
other tools and services.

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
from cartaos.processor import CartaOSProcessor

app = typer.Typer(
    help="CartaOS - A command-line tool for academic document processing.",
    add_completion=False
)

@app.command()
def setup():
    # ... (código permanece o mesmo) ...
    """
    Guides the user through the initial configuration of CartaOS.
    """
    typer.secho("--- CartaOS Setup ---", fg=typer.colors.CYAN)
    
    backend_root = Path(__file__).parent.parent
    env_path = backend_root / '.env'

    if env_path.exists():
        typer.secho(f"✔️ .env file already exists at: {env_path}", fg=typer.colors.GREEN)
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
        
        typer.secho(f"🎉 Success! Configuration saved to {env_path}", fg=typer.colors.GREEN)


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
        typer.secho(f"❌ Error: File not found at '{expanded_pdf_path}'", fg=typer.colors.RED, err=True)
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
        else:
            typer.secho(f"⚠️ Summary for '{expanded_pdf_path.name}' failed. Check logs for details.", fg=typer.colors.YELLOW, err=True)
            raise typer.Exit(code=1)

    except Exception as e:
        typer.secho(f"❌ Fatal error during processing: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()


