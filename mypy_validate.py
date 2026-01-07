import subprocess
import sys
import time



complete_count = time_count = 0


def run_mypy_checks():
    files = [
        ('telegram_handler.py', 'src/notif_hub/api/telegram_handler.py'),
        ("managers.py", "src/notif_hub/database/managers.py"),
        ("bot_router.py", "src/notif_hub/bot/router.py"),
        ("templates_router.py", "src/notif_hub/templates/router.py"),
    ]

    for display_name, file_path in files:
        print(f"\n\033[1;34m{display_name}:\033[0m")
        print(f"poetry run mypy {file_path}")
        
        try:
            start = time.perf_counter()

            result = subprocess.run(
                ["poetry", "run", "mypy", file_path],
                check=True,
                text=True,
                capture_output=True
            )

            end = time.perf_counter()

            global time_count
            time_count += round(end - start, 3)

            print(result.stdout, f'Время выполнения: {round(end - start, 3)}', sep='\n')

            if 'Success:' in result.stdout:
                global complete_count
                complete_count += 1

        except subprocess.CalledProcessError as e:
            print(e.stdout)
            print(e.stderr, file=sys.stderr)

    print(f'Прошли проверку: [{complete_count}/{len(files)}] за {round(time_count, 3)}')


if __name__ == "__main__":
    run_mypy_checks()