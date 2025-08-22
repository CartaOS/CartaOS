"""Test documentation completeness for Issue #3"""

import os
from pathlib import Path


def test_changelog_exists():
    """Test that CHANGELOG.md exists and has required content."""
    changelog_path = Path("../CHANGELOG.md")
    assert changelog_path.exists(), "CHANGELOG.md should exist"
    
    content = changelog_path.read_text()
    assert "## [0.1.0]" in content, "Changelog should have version 0.1.0 entry"
    assert "### Added" in content, "Changelog should have Added section"
    assert "CartaOS" in content, "Changelog should mention CartaOS"


def test_troubleshooting_exists():
    """Test that TROUBLESHOOTING.md exists and has required sections."""
    troubleshooting_path = Path("../TROUBLESHOOTING.md")
    assert troubleshooting_path.exists(), "TROUBLESHOOTING.md should exist"
    
    content = troubleshooting_path.read_text()
    assert "Installation Issues" in content, "Should have Installation Issues section"
    assert "Configuration Issues" in content, "Should have Configuration Issues section"
    assert "Runtime Issues" in content, "Should have Runtime Issues section"
    assert "API Key Problems" in content, "Should have API troubleshooting"


def test_release_guide_exists():
    """Test that RELEASE.md exists and has build instructions."""
    release_path = Path("../RELEASE.md")
    assert release_path.exists(), "RELEASE.md should exist"
    
    content = release_path.read_text()
    assert "Build Process" in content, "Should have build process section"
    assert "cargo tauri build" in content, "Should mention Tauri build command"
    assert "Prerequisites" in content, "Should list prerequisites"


def test_readme_updated():
    """Test that README.md has been updated with installation and screenshots."""
    readme_path = Path("../README.md")
    assert readme_path.exists(), "README.md should exist"
    
    content = readme_path.read_text()
    assert "Quick Start (Recommended)" in content, "Should have quick start section"
    assert ".deb" in content, "Should mention .deb packages"
    assert ".AppImage" in content, "Should mention AppImage"
    assert "Screenshots" in content, "Should have screenshots section"
    assert "System Requirements" in content, "Should have system requirements"


def test_docs_directory_structure():
    """Test that docs directory exists with proper structure."""
    docs_dir = Path("../docs")
    assert docs_dir.exists(), "docs directory should exist"
    
    assets_dir = docs_dir / "assets"
    assert assets_dir.exists(), "docs/assets directory should exist"
    
    assets_readme = assets_dir / "README.md"
    assert assets_readme.exists(), "docs/assets/README.md should exist"


def test_documentation_consistency():
    """Test that documentation is consistent across files."""
    # Check version consistency
    changelog_path = Path("../CHANGELOG.md")
    release_path = Path("../RELEASE.md")
    readme_path = Path("../README.md")
    
    if all(p.exists() for p in [changelog_path, release_path, readme_path]):
        changelog_content = changelog_path.read_text()
        release_content = release_path.read_text()
        readme_content = readme_path.read_text()
        
        # All should mention CartaOS
        assert "CartaOS" in changelog_content, "Changelog should mention CartaOS"
        assert "CartaOS" in release_content, "Release guide should mention CartaOS"
        assert "CartaOS" in readme_content, "README should mention CartaOS"


def test_installation_instructions_complete():
    """Test that installation instructions are comprehensive."""
    readme_path = Path("../README.md")
    if readme_path.exists():
        content = readme_path.read_text()
        
        # Should have multiple installation methods
        assert "dpkg -i" in content, "Should have .deb installation command"
        assert "dnf install" in content, "Should have .rpm installation command"
        assert "chmod +x" in content, "Should have AppImage setup command"
        
        # Should mention system requirements
        assert "RAM" in content, "Should mention RAM requirements"
        assert "Storage" in content, "Should mention storage requirements"


def test_troubleshooting_coverage():
    """Test that troubleshooting covers key areas."""
    troubleshooting_path = Path("../TROUBLESHOOTING.md")
    if troubleshooting_path.exists():
        content = troubleshooting_path.read_text()
        
        # Should cover main problem areas
        assert "API Key" in content, "Should cover API key issues"
        assert "Obsidian" in content, "Should cover Obsidian integration"
        assert "OCR" in content, "Should cover OCR problems"
        assert "Permissions" in content, "Should cover permission issues"
        assert "Dependencies" in content, "Should cover dependency issues"


def test_release_documentation_complete():
    """Test that release documentation covers all necessary aspects."""
    release_path = Path("../RELEASE.md")
    if release_path.exists():
        content = release_path.read_text()
        
        # Should cover build process
        assert "Frontend Build" in content, "Should document frontend build"
        assert "Backend Build" in content, "Should document backend build"
        assert "npm run build" in content, "Should mention npm build command"
        
        # Should cover distribution
        assert ".deb" in content, "Should mention .deb packages"
        assert ".rpm" in content, "Should mention .rpm packages"
        assert ".AppImage" in content, "Should mention AppImage"
