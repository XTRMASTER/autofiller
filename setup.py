from setuptools import setup, find_packages

setup(
    name="cha-document-autofill",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "PyQt6==6.5.0",
        "python-docx==0.8.11",
        "openpyxl==3.1.2",
    ],
    entry_points={
        "console_scripts": [
            "cha-autofill=app.main:main",
        ],
    },
)
