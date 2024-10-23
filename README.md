> epub2tts-edge is a free and open source python app to easily create a full-featured audiobook from an epub or text file using realistic text-to-speech from [Microsoft Edge TTS](https://github.com/rany2/edge-tts/).

## 🚀 Features

- [x] Creates standard format M4B audiobook file
- [x] Automatic chapter break detection
- [x] Embeds cover art if specified
- [x] Uses MS Edge for free cloud-based TTS
- [x] Reads sentences in parallel for very fast audiobook creation
- [x] Resumes where it left off if interrupted
- [x] NOTE: epub file must be DRM-free


## 📖 Usage
<details>
<summary> Usage instructions</summary>

*NOTE:* If you want to specify where NLTK tokenizer will be stored (about 50mb), use an environment variable: `export NLTK_DATA="your/path/to/nltk_data"`

## OPTIONAL - activate the virutal environment if using
1. `source .venv/bin/activate`

## FIRST - extract epub contents to text and cover image to png:
1. `epub2tts-edge mybook.epub`
2. **edit mybook.txt**, replacing `# Part 1` etc with desired chapter names, and removing front matter like table of contents and anything else you do not want read. **Note:** First two lines can be Title: and Author: to use that in audiobook metadata.

## Read text to audiobook:

* `epub2tts-edge mybook.txt --cover mybook.png`
* Optional: specify a speaker with `--speaker <speaker>`. List available voices with `edge-tts --list-voices`, default speaker is `en-US-AndrewNeural` if `--speaker` is not specified.


## All options
* `-h, --help` - show this help message and exit
* `--speaker SPEAKER` - Speaker to use (example: en-US-EricNeural)
* `--cover image.[jpg|png]` - image to use for cover
* `--paragraphpause <N>` - number of milliseconds to pause between paragraphs
* `--sentencepause <N>` - number of milliseconds to pause between sentences

## Deactivate virtual environment
`deactivate`
</details>

## 🐞 Reporting bugs
<details>
<summary>How to report bugs/issues</summary>

Thank you in advance for reporting any bugs/issues you encounter! If you are having issues, first please [search existing issues](https://github.com/aedocw/epub2tts-edge/issues) to see if anyone else has run into something similar previously.

If you've found something new, please open an issue and be sure to include:
1. The full command you executed
2. The platform (Linux, Windows, OSX, Docker)
3. Your Python version if not using Docker

</details>

## 🗒️ Release notes
<details>
<summary>Release notes </summary>

* 20240628: Improved how chapter items are ordered (https://github.com/prydom)
* 20240627: Added check for NLTK tokenizer, download if not already there
* 20240626: Catch multiple !!! and ??? which chokes Edge TTS (https://github.com/erfansamandarian)
* 20240609: Added progress bar (https://github.com/The-Ducktor)
* 20240502: Added export of cover image
* 20240429: Fixed issues with running on linux
* 20240428: Improved final audio by using flac for intermediate audio files, sounds much better
* 20240412: Initial release

</details>

## 📦 Install

Required Python version is 3.11.

*NOTE:* If you want to specify where NLTK tokenizer will be stored (about 50mb), use an environment variable: `export NLTK_DATA="your/path/to/nltk_data"`

<details>
<summary>MAC INSTALLATION</summary>

This installation requires Python < 3.12 and [Homebrew](https://brew.sh/) (I use homebrew to install espeak, [pyenv](https://stackoverflow.com/questions/36968425/how-can-i-install-multiple-versions-of-python-on-latest-os-x-and-use-them-in-par) and ffmpeg).

```
#install dependencies
brew install espeak pyenv ffmpeg
#install epub2tts-edge
git clone https://github.com/aedocw/epub2tts-edge
cd epub2tts-edge
pyenv install 3.11
pyenv local 3.11
#OPTIONAL - install this in a virtual environment
python -m venv .venv && source .venv/bin/activate
pip install .
```
</details>

<details>
<summary>LINUX INSTALLATION</summary>

These instructions are for Ubuntu 22.04 (20.04 showed some depedency issues), but should work (with appropriate package installer mods) for just about any repo. Ensure you have `ffmpeg` installed before use.

```
#install dependencies
sudo apt install espeak-ng ffmpeg
#clone the repo
git clone https://github.com/aedocw/epub2tts-edge
cd epub2tts-edge
#OPTIONAL - install this in a virtual environment
python -m venv .venv && source .venv/bin/activate
pip install .
```

</details>

<details>
<summary>WINDOWS INSTALLATION</summary>

Runnig epub2tts in WSL2 with Ubuntu 22 is the easiest approach, but these steps should work for running directly in windows.

(TBD)

</details>


## Updating

<details>
<summary>UPDATING YOUR INSTALLATION</summary>

1. cd to repo directory
2. `git pull`
3. Activate virtual environment you installed epub2tts in if you installed in a virtual environment using "source venv/bin/activate"
4. `pip install . --upgrade`
</details>


## Author

👤 **Christopher Aedo**

- Website: [aedo.dev](https://aedo.dev)
- GitHub: [@aedocw](https://github.com/aedocw)
- LinkedIn: [@aedo](https://linkedin.com/in/aedo)

👥 **Contributors**

[![Contributors](https://contrib.rocks/image?repo=aedocw/epub2tts-edge)](https://github.com/aedocw/epub2tts-edge/graphs/contributors)

## 🤝 Contributing

Contributions, issues and feature requests are welcome!\
Feel free to check the [issues page](https://github.com/aedocw/epub2tts-edge/issues) or [discussions page](https://github.com/aedocw/epub2tts-edge/discussions).

## Show your support

Give a ⭐️ if this project helped you!
