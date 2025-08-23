"""
Test suite to ensure codebase consistency in English language.
This test detects Portuguese content in code comments, strings, and documentation.
"""
import re
from pathlib import Path
import pytest


class TestI18nConsistency:
    """Test internationalization consistency across the codebase."""
    
    # Portuguese words commonly found in code
    PORTUGUESE_PATTERNS = [
        r'\bLógica\b',
        r'\bações\b', 
        r'\barquivo\b',
        r'\bsubmissão\b',
        r'\bmodificação\b',
        r'\bramo\b',
        r'\butilizar\b',
        r'\bsubmetido\b',
        r'\bvocê\b',
        r'\baqui\b',
        r'\bverá\b',
        r'\bprecisam\b',
        r'\bcorreção\b',
        r'\bmanual\b(?!\s+(correction|page|steps|routing))',  # Exclude English contexts
        r'\bcria\b',
        r'\bdepois\b',
        r'\bverifica\b',
        r'\bpoluir\b',
        r'\brepositório\b',
        r'\bLaboratório\b',
        r'\bAqui\b'
    ]
    
    def _scan_file_for_portuguese(self, file_path: Path) -> list[tuple[int, str]]:
        """Scan a file for Portuguese content and return line numbers with matches."""
        violations = []
        try:
            # Skip if it's a directory or not a regular file
            if not file_path.is_file():
                return violations
                
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                for pattern in self.PORTUGUESE_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        violations.append((line_num, line.strip()))
                        break  # Only report one violation per line
        except (UnicodeDecodeError, PermissionError, IsADirectoryError):
            # Skip binary files, directories, or files we can't read
            pass
            
        return violations
    
    def test_no_portuguese_in_python_files(self):
        """Test that Python files contain no Portuguese content."""
        backend_dir = Path(__file__).parent.parent
        python_files = []
        
        for py_file in backend_dir.rglob("*.py"):
            # Skip virtual environment, node_modules, and .git directories
            if any(part in str(py_file) for part in ['.venv', 'node_modules', '.git', '__pycache__']):
                continue
            python_files.append(py_file)
        
        all_violations = {}
        for py_file in python_files:
            violations = self._scan_file_for_portuguese(py_file)
            if violations:
                all_violations[str(py_file)] = violations
        
        if all_violations:
            error_msg = "Portuguese content found in Python files:\n"
            for file_path, violations in all_violations.items():
                error_msg += f"\n{file_path}:\n"
                for line_num, line in violations:
                    error_msg += f"  Line {line_num}: {line}\n"
            pytest.fail(error_msg)
    
    def test_no_portuguese_in_frontend_files(self):
        """Test that frontend files contain no Portuguese content."""
        project_root = Path(__file__).parent.parent.parent
        frontend_dir = project_root / "frontend"
        
        if not frontend_dir.exists():
            pytest.skip("Frontend directory not found")
        
        # Check TypeScript, JavaScript, and Svelte files, excluding node_modules and build artifacts
        frontend_files = []
        for pattern in ["*.ts", "*.js", "*.svelte"]:
            for file_path in frontend_dir.rglob(pattern):
                # Skip node_modules, build artifacts, and other dependency directories
                path_str = str(file_path)
                if any(part in path_str for part in ["node_modules", ".git", ".svelte-kit", "build", "dist"]):
                    continue
                frontend_files.append(file_path)
        
        all_violations = {}
        for file_path in frontend_files:
            violations = self._scan_file_for_portuguese(file_path)
            if violations:
                all_violations[str(file_path)] = violations
        
        if all_violations:
            error_msg = "Portuguese content found in frontend files:\n"
            for file_path, violations in all_violations.items():
                error_msg += f"\n{file_path}:\n"
                for line_num, line in violations:
                    error_msg += f"  Line {line_num}: {line}\n"
            pytest.fail(error_msg)
    
    def test_no_portuguese_in_rust_files(self):
        """Test that Rust files contain no Portuguese content."""
        project_root = Path(__file__).parent.parent.parent
        rust_dir = project_root / "src-tauri"
        
        if not rust_dir.exists():
            pytest.skip("Rust directory not found")
        
        rust_files = list(rust_dir.rglob("*.rs"))
        
        all_violations = {}
        for rs_file in rust_files:
            violations = self._scan_file_for_portuguese(rs_file)
            if violations:
                all_violations[str(rs_file)] = violations
        
        if all_violations:
            error_msg = "Portuguese content found in Rust files:\n"
            for file_path, violations in all_violations.items():
                error_msg += f"\n{file_path}:\n"
                for line_num, line in violations:
                    error_msg += f"  Line {line_num}: {line}\n"
            pytest.fail(error_msg)
