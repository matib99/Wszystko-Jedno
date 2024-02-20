 # Your Personal God
  voice to voice pipeline, version 2

## Components:

- Visual (different repository):
    - StyleGan finetuned to generate slavic god in human image
- Audio-Linguistic:
    - [Insanely Fast Whisper](https://github.com/Vaibhavs10/insanely-fast-whisper) for voice transcryption
    - [Mistral 7B](https://mistral.ai) with [ollama](https://ollama.com) API for text generation
    - [XTTS by coqui](https://coqui.ai/blog/tts/open_xtts) for voice cloning

## Structure

- examples directory contains python codes that work independently of themselves and any other code inside this repository.
- models should contain XTTS model.
- samples should contain sample.wav file, which is a voice recording (with duration of 5 to 15 seconds) used for voice cloning and by example files.
- src contains all functionalities and initialization file

## Prerequisites and installation

Before running the script, [ollama](https://ollama.com) should be installed according to instructions provided on the ollama website. for linux only one snippet is necessary:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

easy way to deploy the code is to use conda environment. Provided conda is installed it is sufficient to use following snippet:

```bash
conda create -n Your_Personal_God python==3.10.13
conda activate Your_Personal_God
conda install -c conda-forge libstdcxx-ng
pip install -r requirements.txt
```

to use XTTS [this](https://huggingface.co/coqui/XTTS-v2/tree/main) repository should be cloned into "models" directory

## To Do

- [x] constructing and testing example files
- [x] constructing full software, publishing repository
- [ ] deploying full software on testing device (CPU only)
- [ ] writing documentation for each function and class
- [ ] deploying software on another device
- [ ] testing software on CUDA compatible machine
- [ ] finetuning models to suit our needs

## Appendix




