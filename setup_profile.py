from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
REQUIRED_DIRECTORIES = (
    Path("templates/pages"),
    Path("static/css/pages"),
    Path("static/js/pages"),
)


def main():
    for relative_path in REQUIRED_DIRECTORIES:
        directory = PROJECT_ROOT / relative_path
        if directory.exists() and not directory.is_dir():
            if directory.stat().st_size:
                raise FileExistsError(f"Expected a directory at {directory}")
            directory.unlink()
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Ready: {relative_path}")


if __name__ == "__main__":
    main()