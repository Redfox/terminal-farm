from setuptools import setup, find_packages

setup(
    name="terminal-farm",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask>=2.0.0",
    ],
    entry_points={
        'console_scripts': [
            'terminal-farm=terminal_farm.terminal.terminal_ui:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A farming game that can be played in both terminal and web interfaces",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/terminal-farm",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
) 