from setuptools import setup, find_packages

setup(
    name='perfscan',
    version='4.0',
    packages=find_packages(), # Encontra a pasta src automaticamente
    py_modules=['main'],      # Inclui o main.py
    install_requires=[
        'rich',
        'playwright',
        'requests',
        'pyfiglet',
    ],
    entry_points={
        'console_scripts': [
            'perfscan=main:main',  # ISSO É O SEGREDO! Cria o comando 'perfscan'
        ],
    },
)