"""
Test suite for simplified installer that focuses on dependency checking
rather than system-level installation.
"""

import platform
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from cartaos.install_dev_env.simplified_installer import (DependencyChecker,
                                                          DependencyStatus,
                                                          InstallationGuide,
                                                          SimplifiedInstaller)


class TestDependencyChecker:
    """Test dependency checking functionality."""

    def test_check_system_dependency_found(self):
        """Test that system dependencies are correctly detected when available."""
        checker = DependencyChecker()

        with patch("shutil.which", return_value="/usr/bin/tesseract"):
            status = checker.check_system_dependency("tesseract")

        assert status.name == "tesseract"
        assert status.available is True
        assert status.path == "/usr/bin/tesseract"
        assert status.installation_guide is None

    def test_check_system_dependency_missing(self):
        """Test that missing system dependencies are correctly detected."""
        checker = DependencyChecker()

        with patch("shutil.which", return_value=None):
            status = checker.check_system_dependency("tesseract")

        assert status.name == "tesseract"
        assert status.available is False
        assert status.path is None
        assert status.installation_guide is not None

    def test_check_all_required_dependencies(self):
        """Test checking all required system dependencies."""
        checker = DependencyChecker()
        required_deps = ["tesseract", "unpaper", "scantailor-advanced"]

        with patch(
            "shutil.which",
            side_effect=lambda x: "/usr/bin/" + x if x != "unpaper" else None,
        ):
            results = checker.check_all_dependencies(required_deps)

        assert len(results) == 3
        assert results["tesseract"].available is True
        assert results["unpaper"].available is False
        assert results["scantailor-advanced"].available is True

    def test_check_python_version_valid(self):
        """Test Python version checking with valid version."""
        checker = DependencyChecker()

        with patch("sys.version_info", (3, 12, 0)):
            status = checker.check_python_version()

        assert status.available is True
        assert "3.12.0" in status.details

    def test_check_python_version_invalid(self):
        """Test Python version checking with invalid version."""
        checker = DependencyChecker()

        with patch("sys.version_info", (3, 8, 0)):
            status = checker.check_python_version()

        assert status.available is False
        assert "3.8.0" in status.details
        assert "requires Python 3.9+" in status.installation_guide


class TestInstallationGuide:
    """Test installation guide generation."""

    def test_get_platform_specific_guide_linux(self):
        """Test platform-specific installation guides for Linux."""
        guide = InstallationGuide()

        with patch("platform.system", return_value="Linux"):
            instructions = guide.get_installation_instructions("tesseract")

        assert "sudo apt-get install tesseract-ocr" in instructions
        assert "sudo dnf install tesseract" in instructions
        assert "sudo pacman -S tesseract" in instructions

    def test_get_platform_specific_guide_macos(self):
        """Test platform-specific installation guides for macOS."""
        guide = InstallationGuide()

        with patch("platform.system", return_value="Darwin"):
            instructions = guide.get_installation_instructions("tesseract")

        assert "brew install tesseract" in instructions

    def test_get_platform_specific_guide_windows(self):
        """Test platform-specific installation guides for Windows."""
        guide = InstallationGuide()

        with patch("platform.system", return_value="Windows"):
            instructions = guide.get_installation_instructions("tesseract")

        assert "winget install" in instructions or "choco install" in instructions

    def test_get_unknown_dependency_guide(self):
        """Test installation guide for unknown dependencies."""
        guide = InstallationGuide()

        instructions = guide.get_installation_instructions("unknown-tool")

        assert "Please install unknown-tool manually" in instructions
        assert "system package manager" in instructions


class TestSimplifiedInstaller:
    """Test the main simplified installer functionality."""

    def test_installer_initialization(self):
        """Test installer initializes correctly."""
        installer = SimplifiedInstaller(dry_run=True)

        assert installer.dry_run is True
        assert isinstance(installer.dependency_checker, DependencyChecker)
        assert isinstance(installer.installation_guide, InstallationGuide)

    def test_check_system_dependencies_all_present(self):
        """Test system dependency checking when all dependencies are present."""
        installer = SimplifiedInstaller()

        mock_checker = Mock()
        mock_checker.check_all_dependencies.return_value = {
            "tesseract": DependencyStatus("tesseract", True, "/usr/bin/tesseract"),
            "unpaper": DependencyStatus("unpaper", True, "/usr/bin/unpaper"),
        }
        installer.dependency_checker = mock_checker

        result = installer.check_system_dependencies()

        assert result is True
        mock_checker.check_all_dependencies.assert_called_once()

    def test_check_system_dependencies_some_missing(self):
        """Test system dependency checking when some dependencies are missing."""
        installer = SimplifiedInstaller()

        mock_checker = Mock()
        mock_checker.check_all_dependencies.return_value = {
            "tesseract": DependencyStatus("tesseract", True, "/usr/bin/tesseract"),
            "unpaper": DependencyStatus(
                "unpaper", False, None, "Install with: sudo apt-get install unpaper"
            ),
        }
        installer.dependency_checker = mock_checker

        result = installer.check_system_dependencies()

        assert result is False
        mock_checker.check_all_dependencies.assert_called_once()

    def test_setup_project_environment_success(self):
        """Test project environment setup when all tools are available."""
        installer = SimplifiedInstaller()

        with patch("shutil.which", return_value="/usr/bin/node"), patch(
            "subprocess.run"
        ) as mock_run:
            mock_run.return_value.returncode = 0

            result = installer.setup_project_environment()

        assert result is True

    def test_setup_project_environment_missing_node(self):
        """Test project environment setup when Node.js is missing."""
        installer = SimplifiedInstaller()

        with patch("shutil.which", return_value=None):
            result = installer.setup_project_environment()

        assert result is False

    def test_run_checks_only_mode(self):
        """Test running installer in check-only mode."""
        installer = SimplifiedInstaller(check_only=True)

        mock_checker = Mock()
        mock_checker.check_all_dependencies.return_value = {
            "tesseract": DependencyStatus("tesseract", True, "/usr/bin/tesseract")
        }
        mock_checker.check_python_version.return_value = DependencyStatus(
            "python", True, "3.12.0"
        )
        installer.dependency_checker = mock_checker

        result = installer.run()

        assert result is True
        mock_checker.check_all_dependencies.assert_called_once()
        mock_checker.check_python_version.assert_called_once()

    def test_run_full_setup_mode(self):
        """Test running installer in full setup mode."""
        installer = SimplifiedInstaller(check_only=False)

        with patch.object(
            installer, "check_system_dependencies", return_value=True
        ), patch.object(installer, "setup_project_environment", return_value=True):

            result = installer.run()

        assert result is True

    def test_run_fails_on_missing_dependencies(self):
        """Test installer fails when system dependencies are missing."""
        installer = SimplifiedInstaller(check_only=False)

        with patch.object(installer, "check_system_dependencies", return_value=False):
            result = installer.run()

        assert result is False

    def test_generate_summary_report(self):
        """Test generation of dependency status summary report."""
        installer = SimplifiedInstaller()

        status_results = {
            "tesseract": DependencyStatus("tesseract", True, "/usr/bin/tesseract"),
            "unpaper": DependencyStatus(
                "unpaper", False, None, "Install with: sudo apt-get install unpaper"
            ),
        }

        summary = installer.generate_summary_report(status_results)

        assert "tesseract" in summary
        assert "unpaper" in summary
        assert "✓" in summary  # Success indicator
        assert "✗" in summary  # Failure indicator
        assert "sudo apt-get install unpaper" in summary


class TestDependencyStatus:
    """Test DependencyStatus data class."""

    def test_dependency_status_available(self):
        """Test DependencyStatus for available dependency."""
        status = DependencyStatus("tesseract", True, "/usr/bin/tesseract")

        assert status.name == "tesseract"
        assert status.available is True
        assert status.path == "/usr/bin/tesseract"
        assert status.installation_guide is None
        assert status.details is None

    def test_dependency_status_missing(self):
        """Test DependencyStatus for missing dependency."""
        guide = "Install with: sudo apt-get install tesseract-ocr"
        status = DependencyStatus("tesseract", False, None, guide, "Not found in PATH")

        assert status.name == "tesseract"
        assert status.available is False
        assert status.path is None
        assert status.installation_guide == guide
        assert status.details == "Not found in PATH"
