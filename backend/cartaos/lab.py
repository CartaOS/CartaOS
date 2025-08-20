# -*- coding: utf-8 -*-
# backend/cartaos/lab.py


from loguru import logger

import os
import subprocess
import tempfile
from pathlib import Path
from typing import List
from xml.etree.ElementTree import Element, SubElement, tostring, Comment
from xml.dom import minidom

# It is highly recommended to use the Pillow library to read image metadata.
# If it is not in your environment, install with: pip install Pillow
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("Pillow (PIL) not found. Using default DPI and image size values.")

from .utils.pdf_utils import extract_pages, recompose_pdf


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
        tmp_dir = Path.home() / ".cache" / "cartaos" / "tmp"
        os.makedirs(tmp_dir, exist_ok=True)
        workspace = tempfile.mkdtemp(dir=str(tmp_dir))
        try:
            logger.info("Extracting pages from input PDF")
            images: List[Path] = extract_pages(self.input_path, Path(workspace))
            
            logger.info("Running unpaper cleanup")
            self._run_unpaper_cleanup(workspace, images)

            logger.info("Generating ScanTailor project file")
            project_file_path = self._create_scantailor_project(Path(workspace))
            if not project_file_path:
                return False

            logger.info("Running manual correction using ScanTailor Advanced")
            self._run_manual_correction(workspace, project_file_path)

            logger.info("Recomposing PDF from corrected images")
            output_pdf_path = self.output_dir / f"corrected_{self.input_path.name}"
            
            # Images processed by ScanTailor are placed in the 'out' subdirectory
            corrected_images_dir = Path(workspace) / "out"
            corrected_images = sorted(corrected_images_dir.glob('*.tif'))

            if not corrected_images:
                logger.warning("No corrected images found in the ScanTailor output directory. The PDF will not be recreated.")
                return False

            recomposed_pdf = recompose_pdf(corrected_images, output_pdf_path)

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
            # Use capture_output=True to suppress unpaper output in the console
            subprocess.run(["unpaper", str(image), str(output_image)], cwd=workspace, check=True, capture_output=True)
            processed_images.append(output_image)
        # Atualiza a lista original com as imagens processadas
        images[:] = processed_images

    def _create_scantailor_project(self, project_dir: Path):
        """
        Create a compatible .scantailor project file, replicating the exact
        structure of version 3, following the provided example file.
        """
        project_dir = Path(project_dir).resolve()
        project_name = project_dir.name
        project_file_path = project_dir / f"{project_name}.scantailor"
        output_dir = project_dir / "out"
        output_dir.mkdir(exist_ok=True)

        logger.info(f"Generating ScanTailor (v3) project at: {project_file_path}")

        image_extensions = ['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp']
        all_image_paths = sorted([p for p in project_dir.iterdir() if p.is_file() and p.suffix.lower() in image_extensions])

        if not all_image_paths:
            logger.warning(f"No image files found in {project_dir}.")
            return None

        dir_map, file_map, image_map, page_map = {}, {}, {}, {}
        next_id = 1

        root = Element('project', version="3", outputDirectory=str(output_dir), layoutDirection="LTR")
        root.append(Comment(" Generated by CartaOS "))

        directories_el = SubElement(root, 'directories')
        files_el = SubElement(root, 'files')
        images_el = SubElement(root, 'images')
        pages_el = SubElement(root, 'pages')
        
        for img_path in all_image_paths:
            dir_path_str = str(img_path.parent)
            
            if dir_path_str not in dir_map:
                dir_map[dir_path_str] = next_id
                SubElement(directories_el, 'directory', id=str(next_id), path=dir_path_str)
                next_id += 1
            dir_id = dir_map[dir_path_str]

            file_id = next_id
            file_map[str(img_path)] = file_id
            SubElement(files_el, 'file', dirId=str(dir_id), name=img_path.name, id=str(file_id))
            next_id += 1

            image_id = next_id
            image_map[str(img_path)] = image_id
            image_el = SubElement(images_el, 'image', fileImage="0", fileId=str(file_id), id=str(image_id), subPages="1")
            next_id += 1

            width, height, dpi_h, dpi_v = "2480", "3508", "300", "300"
            if PIL_AVAILABLE:
                try:
                    with Image.open(img_path) as im:
                        width, height = str(im.width), str(im.height)
                        if im.info.get('dpi'):
                            dpi_h, dpi_v = str(int(im.info['dpi'][0])), str(int(im.info['dpi'][1]))
                except Exception as e:
                    logger.warning(f"Could not read metadata from {img_path.name}: {e}")

            SubElement(image_el, 'size', width=width, height=height)
            SubElement(image_el, 'dpi', horizontal=dpi_h, vertical=dpi_v)

            page_id = next_id
            page_map[str(img_path)] = page_id
            page_attrs = {'imageId': str(image_id), 'subPage': 'single', 'id': str(page_id)}
            if len(page_map) == 1:
                 page_attrs['selected'] = 'selected'
            SubElement(pages_el, 'page', page_attrs)
            next_id += 1

        disambiguation_el = SubElement(root, 'file-name-disambiguation')
        for img_path, file_id in file_map.items():
            SubElement(disambiguation_el, 'mapping', file=str(file_id), label="0")

        filters_el = SubElement(root, 'filters')
        
        fix_orientation_el = SubElement(filters_el, 'fix-orientation')
        SubElement(fix_orientation_el, 'image-settings')

        SubElement(filters_el, 'page-split', defaultLayoutType="auto-detect")
        
        deskew_el = SubElement(filters_el, 'deskew')
        SubElement(deskew_el, 'image-settings')

        SubElement(filters_el, 'select-content', pageDetectionTolerance="0.1")
        SubElement(filters_el, 'page-layout', showMiddleRect="1")
        output_el = SubElement(filters_el, 'output')

        for page_id in page_map.values():
            page_id_str = str(page_id)
            page_out_el = SubElement(output_el, 'page', id=page_id_str)
            SubElement(page_out_el, 'zones')
            SubElement(page_out_el, 'fill-zones')
            params_out_el = SubElement(page_out_el, 'params', despeckleLevel="1", blackOnWhite="1", depthPerception="2")
            SubElement(params_out_el, 'dpi', horizontal="600", vertical="600")
            color_params_el = SubElement(params_out_el, 'color-params', colorMode="bw")
            SubElement(color_params_el, 'bw', binarizationMethod="otsu")

        logger.info(f"XML structure (v3) created for {len(all_image_paths)} images.")

        xml_string = tostring(root, 'utf-8')
        pretty_xml = minidom.parseString(xml_string).toprettyxml(indent="  ", encoding="UTF-8").decode('utf-8')

        try:
            with open(project_file_path, 'w', encoding='utf-8') as f:
                f.write(pretty_xml)
            logger.info(f"ScanTailor project saved successfully at {project_file_path}")
            return project_file_path
        except IOError as e:
            logger.error(f"Failed to save project file: {e}")
            return None

    def _run_manual_correction(self, workspace: str, project_file_path: Path) -> None:
        """
        Run manual correction using ScanTailor Advanced.

        Args:
            workspace (str): The temporary workspace directory.
            project_file_path (Path): The path to the ScanTailor project file.
        """
        logger.info("Please correct the images using ScanTailor Advanced.")
        # input() was removed for a more streamlined flow, but can be re-added if needed
        # input("Press [Enter] to continue...")
        command = ["flatpak", "run", "com.github._4lex4.ScanTailor-Advanced", str(project_file_path)]
        
        try:
            # Redirect output to DEVNULL to keep the console clean
            process = subprocess.Popen(command, cwd=workspace, start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            process.wait() # Wait for the ScanTailor process to finish (user closes the program)
            logger.info("ScanTailor Advanced closed. Continuing the process.")
        except FileNotFoundError:
             logger.error("'flatpak' command not found. Please ensure Flatpak is installed.")
             raise
        except Exception as e:
            logger.error(f"An error occurred while running ScanTailor via Flatpak: {e}")
            raise