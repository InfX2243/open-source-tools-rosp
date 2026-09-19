from envguard.core.generator import generate_env_example, suggest_dummy_value
from envguard.core.models import CodeReference, ScanCodebaseResult


def test_suggest_dummy_value():
    assert suggest_dummy_value("PORT") == "8000"
    assert suggest_dummy_value("DATABASE_URL") == "postgresql://postgres:postgres@localhost:5432/app_dev"
    assert suggest_dummy_value("STRIPE_KEY") == "your_secret_key_here"
    assert suggest_dummy_value("DEBUG") == "false"


def test_generate_env_example_from_scan(tmp_path):
    scan_res = ScanCodebaseResult(
        variables={
            "PORT": [CodeReference(file_path="app.py", line_number=1, line_content="", language="python")],
            "SECRET_TOKEN": [CodeReference(file_path="auth.py", line_number=5, line_content="", language="python")],
        },
        files_scanned=2,
        total_references=2,
    )

    out_file = tmp_path / ".env.example"
    content = generate_env_example(scan_result=scan_res, output_path=str(out_file))

    assert "PORT=8000" in content
    assert "SECRET_TOKEN=your_secret_key_here" in content
    assert out_file.exists()
