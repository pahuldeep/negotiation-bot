from setuptools import setup, find_packages

setup(
    name="nego-bot",
    version="0.1",
    packages=find_packages(),
    install_requires=[],  # keep empty or parse from requirements.txt
    entry_points={
        'console_scripts': [
            'nego-bot = hf_negotiate.QABot:main',
        ],
    },
)
