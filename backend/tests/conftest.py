import pytest
from pathlib import Path
import cartaos.processor as module

@pytest.fixture(autouse=True)
def use_temp_prompt_dir(tmp_path, monkeypatch):
    # Copies the real summary_prompt.md to tmp_path
    real_prompt = Path(module.__file__).parent / "prompts" / "summary_prompt.md"
    target = tmp_path / "prompts"
    target.mkdir()
    (target / "summary_prompt.md").write_text(real_prompt.read_text())

    # Monkeypatches the __file__ attribute of processor to point to tmp_path
    fake_file = tmp_path / "processor.py"
    fake_file.write_text(module.__file__)
    monkeypatch.setattr(module, "__file__", str(fake_file))
    yield

