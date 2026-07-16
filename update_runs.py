from pathlib import Path
import subprocess
import sys

LOG_PATH = Path(r"C:\Users\trvplutos\Desktop\UnrankedServer\logs\games_zm.log")
REPO_PATH = Path(r"C:\Users\trvplutos\Desktop\UnrankedServer\MurciaServers_zm-leaderboard")
RUNS_PATH = REPO_PATH / "runs.txt"
BRANCH = "main"

def extract_exports(log_text):
    lines = []
    seen = set()
    for raw in log_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        idx = line.find("ZM_EXPORT;")
        if idx == -1:
            continue
        export_line = line[idx:]
        if export_line not in seen:
            seen.add(export_line)
            lines.append(export_line)
    return lines

def run_git(args, cwd):
    result = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        shell=False
    )
    return result

def main():
    if not LOG_PATH.exists():
        print(f"No existe el log: {LOG_PATH}")
        sys.exit(1)

    if not REPO_PATH.exists():
        print(f"No existe el repo: {REPO_PATH}")
        sys.exit(1)

    log_text = LOG_PATH.read_text(encoding="utf-8", errors="ignore")
    exports = extract_exports(log_text)

    if not exports:
        print("No se encontraron líneas ZM_EXPORT.")
        sys.exit(0)

    new_content = "\n".join(exports) + "\n"
    old_content = RUNS_PATH.read_text(encoding="utf-8", errors="ignore") if RUNS_PATH.exists() else ""

    if new_content == old_content:
        print("runs.txt ya está actualizado. No hay cambios.")
        sys.exit(0)

    RUNS_PATH.write_text(new_content, encoding="utf-8")
    print(f"runs.txt actualizado con {len(exports)} líneas.")

    add_res = run_git(["add", "runs.txt"], REPO_PATH)
    if add_res.returncode != 0:
        print("Error en git add")
        print(add_res.stderr)
        sys.exit(1)

    commit_res = run_git(["commit", "-m", f"Actualizar runs.txt ({len(exports)} runs)"], REPO_PATH)
    if commit_res.returncode != 0:
        if "nothing to commit" in commit_res.stdout.lower() or "nothing to commit" in commit_res.stderr.lower():
            print("Nada que commitear.")
            sys.exit(0)
        print("Error en git commit")
        print(commit_res.stderr or commit_res.stdout)
        sys.exit(1)

    push_res = run_git(["push", "origin", BRANCH], REPO_PATH)
    if push_res.returncode != 0:
        print("Error en git push")
        print(push_res.stderr or push_res.stdout)
        sys.exit(1)

    print("Cambios subidos correctamente a GitHub.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Se produjo un error:")
        print(e)
    input("Pulsa Enter para cerrar...")