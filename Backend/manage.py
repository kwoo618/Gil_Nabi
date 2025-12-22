#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings") 
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
            "장고를 가져올 수 없습니다. PYTHONPATH 환경 변수에 설치되어 있고, "
            "사용할 수 있는지 확실합니까?"
            "혹은 가상환경 활성화를 잊으셨나요?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
