"""Entry point for running the Kedro project from the command line."""
from pathlib import Path

from kedro.framework.project import configure_project


def main():
    configure_project("nhanes_diabetes")
    from kedro.framework.session import KedroSession
    with KedroSession.create() as session:
        session.run()


if __name__ == "__main__":
    main()
