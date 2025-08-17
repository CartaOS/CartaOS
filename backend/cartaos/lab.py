# -*- coding: utf-8 -*- 
# backend/cartaos/lab.py


from loguru import logger

import os
import subprocess
import tempfile
from pathlib import Path
from typing import List
from .utils.pdf_utils import extract_pages, recompose_pdf

# Configure logging to output to console
#logging.basicConfig(level=logging.INFO, format='[%(asctime)s][%(levelname)s][%(name)s] %(message)s')
#logger = logging.getLogger(__name__)


class LabProcessor:
    def __init__(self, input_path: Path, output_dir: Path) -> None:
        """
        Initialize the LabProcessor with the input PDF and output directory.

        Args:
            input_path (Path): The path to the source PDF file.
            output_dir (Path): The destination directory for the corrected PDF.
        """
        self.input_path: Path = input_path
        self.output_dir: Path = output_dir

    def process(self) -> bool:
        """
        Send the PDF to the manual correction lab with ScanTailor.

        Returns:
            bool: True on success, False on failure.
        """
        workspace = tempfile.mkdtemp()
        try:
            logger.info("Extracting pages from input PDF")
            images: List[Path] = extract_pages(self.input_path, Path(workspace))
            
            logger.info("Running unpaper cleanup")
            self._run_unpaper_cleanup(workspace, images)

            logger.info("Generating ScanTailor project file")
            self._generate_scantailor_project(workspace, images)

            logger.info("Running manual correction using ScanTailor Advanced")
            self._run_manual_correction(workspace, images)

            logger.info("Recomposing PDF from corrected images")
            output_pdf_path = self.output_dir / f"corrected_{self.input_path.name}"
            recomposed_pdf = recompose_pdf(images, output_pdf_path)

            if recomposed_pdf:
                logger.info(f"Corrected PDF saved to {recomposed_pdf}")
                return True
            else:
                logger.error("Failed to create the corrected PDF.")
                return False
        except Exception as e:
            logger.error(f"An error occurred during lab processing: {e}")
            return False
        finally:
            # Cleanup the temporary directory
            import shutil
            shutil.rmtree(workspace)

    def _run_unpaper_cleanup(self, workspace: str, images: List[Path]) -> None:
        """
        Run unpaper cleanup on the extracted TIFF images.

        Args:
            workspace (str): The temporary workspace directory.
            images (List[Path]): The list of paths to the extracted TIFF images.
        """
        processed_images = []
        for image in images:
            output_image = Path(workspace) / f"unpaper_{image.name}"
            subprocess.run(["unpaper", str(image), str(output_image)], cwd=workspace, check=True)
            processed_images.append(output_image)
        images[:] = processed_images # Update the original list with processed images

    def _generate_scantailor_project(self, workspace: str, images: List[Path]) -> None:
        """
        Generate a ScanTailor project file.

        Args:
            workspace (str): The temporary workspace directory.
            images (List[Path]): The list of paths to the extracted TIFF images.
        """
        with open(os.path.join(workspace, "project.scantailor"), "w") as f:
            f.write("<project>\n")
            for image in images:
                f.write(f"<image>{image.name}</image>\n")
            f.write("</project>\n")

    def _run_manual_correction(self, workspace: str, images: List[Path]) -> None:
        """
        Run manual correction using ScanTailor Advanced.

        Args:
            workspace (str): The temporary workspace directory.
            images (List[Path]): The list of paths to the extracted TIFF images.
        """
        logger.info("Please correct the images using ScanTailor Advanced.")
        input("Press [Enter] to continue...")
        command = ["flatpak", "run", "com.github._4lex4.ScanTailor-Advanced", "project.scantailor"]
        
        with tempfile.TemporaryFile(mode='w+', encoding='utf-8') as stdout_file, \
             tempfile.TemporaryFile(mode='w+', encoding='utf-8') as stderr_file:
            process = subprocess.Popen(command, cwd=workspace, start_new_session=True, stdout=stdout_file, stderr=stderr_file)
            process.wait() # Wait for the process to finish

