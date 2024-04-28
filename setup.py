from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="epub2tts-edge",
    description="Tool to read an epub to audiobook using MS Edge TTS",
    author="Christopher Aedo aedo.dev",
    author_email="c@aedo.dev",
    url="https://github.com/aedocw/epub2tts-edge",
    license="GPL 3.0",
    version="1.1.2",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'epub2tts-edge = epub2tts_edge:main'
        ]
    },
)
