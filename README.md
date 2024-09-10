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
conda create -n Your_Personal_God --file requirements.txt
```

or more explicitly (may be buggy):

```bash
conda create -n Your_Personal_God python==3.10.13
conda activate Your_Personal_God
conda install -c conda-forge libstdcxx-ng
pip install -r requirements1.txt
```

to use XTTS [this](https://huggingface.co/coqui/XTTS-v2/tree/main) repository should be cloned into "models" directory

## Running and testing

After propper installation every example from "examples" directory should work flawlessly. testing them all before main file is advised.

## Using software as splitted local-server system

Large Language Model runns via ollama wrapper. Installing it is impossible on server we ought use, thus this part has to run locally and send informations (generated string of phrases) for further processing to the server. Server firstly listens to audio, then redirects to local LLM and then vocalises the response. 

So you have to first direct your audio to ssh server, for example using:
```bash
arecord -f cd -t raw | oggenc - -r | ssh <user>@<remotehost> mplayer -
```
or
```bash
ffmpeg -f alsa -ac 1 -i hw:3 -f ogg - \
    | ssh <user>@<remotehost> mplayer - -idle -demuxer ogg
```
and then be able to receive audio from the server, for example using:
```bash
ssh <user>@<remotehost> 'arecord -f cd -t raw | oggenc - -r' | mplayer -
```
or
```bash
ssh <user>@<remotehost> 'arecord -f cd -D plughw:2 | ffmpeg -ac 1 -i - -f ogg -' \
    | mplayer - -idle -demuxer ogg
```
where for these commands to work you have to change "<user>@<remotehost>" to your system value and "hw:3" to your alsadevice that you can find with command:
```bash
arecord -l
```
If you encounter problems with that task, you may consult [this thread](https://unix.stackexchange.com/questions/116919/redirect-sound-microphone-via-ssh-how-to-telephone-via-ssh).

If you can't resolve the problems you might need to run everything locally OR change files so that you automatically copy recorded voice and translate it on the server (I can do that for you if that will be too challenging).

<span style="color:red"> *WARNING!* </span> You may have to change the default device name in ./src/ear.py to name of microphone that is shown by "arecord -l" command. 

After you moved the audio streams you should do the following: clone the repository locally and on the server, then run "local_mind_ssh.py" locally and "server_vocal_ssh.py" on your server. The communication is as follows:

1. server_vocal.py (Remote Server):
    - Captures audio from local machine.
    - Creates an SSH connection to the local machine using paramiko.
    - Sends an HTTP request (via curl or equivalent) through the SSH tunnel to http://localhost:5000/generate_response on the local machine.

2. local_mind.py (Local Machine):
    - Receives the HTTP request.
    - Generates responce string and sends back the result as an HTTP response.

3. server_vocal.py (Remote Server):
    - Receives the response over the SSH tunnel and generates audio that is played via local machine.


## To Do

- [x] constructing and testing example files
- [x] constructing full software, publishing repository
- [X] deploying full software on testing device (CPU only)
- [X] splitting software to two local servers
- [X] splitting software to two local and external server (ssh connection)
- [ ] ~~writing documentation for each function and class~~
- [ ] deploying software on another device
- [ ] testing software on CUDA compatible machine
- [ ] ~~finetuning models to suit our needs~~
- [ ] ~~writing all paths in terms of absolute repository paths~~

## Appendix




