"""скрипт запуска пайплайна на датасете."""
from pathlib import Path

from src.extract import extract
from src.classify import classify
from src.check_subject import check_subject


def main() -> None:
    """Прогоняет пайплайн на dataset/ и выводит отчёт."""
    ds = Path("dataset")

    print()
    print("EXTRACT + CLASSIFY")
    print()
    for f in sorted(ds.glob("doc*.txt")):
        text = f.read_text(encoding="utf-8")
        fields = extract(text)
        doc_type, conf = classify(text)
        print(f"\n {f.name}")
        print(f"   extract: {fields}")
        print(f"   classify: {doc_type} (уверенность: {conf:.2f})")

    print("\n")
    print("CHECK_SUBJECT")
    print()
    subjects_file = ds / "subjects_test.txt"
    if not subjects_file.exists():
        print("Файл subjects_test.txt не найден")
        return

    for line in subjects_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 2:
            continue
        subj, expected = parts
        ok, conf, reason = check_subject(subj)
        status = "PASS" if ok else "FAIL"
        print(f"{status} [{conf:.2f}] (ожид:{expected}) {subj}")
        print(f"   → {reason}")


if __name__ == "__main__":
    main()