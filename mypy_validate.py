import subprocess
import sys
import time



complete_count = time_count = 0


def run_mypy_checks():
    files = [
        ("auth.py", "src/notif_hub/auth/cookie_auth/auth.py"),
        ("helpers.py", "src/notif_hub/auth/cookie_auth/helpers.py"),
        ("schemas.py", "src/notif_hub/auth/cookie_auth/schemas.py"),
        ("utils.py", "src/notif_hub/auth/cookie_auth/utils.py"),
        ("validation.py", "src/notif_hub/auth/cookie_auth/validation.py"),
        ('channels_handler.py', 'src/notif_hub/api/channels_handler.py'),
        ('channels_helpers.py', 'src/notif_hub/api/channels_helpers.py'),
        ('telegram_handler.py', 'src/notif_hub/api/telegram_handler.py'),
        ('email_handler.py', 'src/notif_hub/api/email_handler.py'),
        ('email_helpers.py', 'src/notif_hub/api/email_helpers.py'),
        ('webhook_handler.py', 'src/notif_hub/api/webhook_handler.py'),
        ('github_router.py', 'src/notif_hub/auth/github_router.py'),
        ('google_router.py', 'src/notif_hub/auth/google_router.py'),
        ('oauth_github.py', 'src/notif_hub/auth/oauth_github.py'),
        ('oauth_google.py', 'src/notif_hub/auth/oauth_google.py'),
        ('jwt_parse.py', 'src/notif_hub/auth/jwt_parse.py'),
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