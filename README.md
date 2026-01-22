# Proton-Cli

**Proton-Cli** is a tool that helps you run proton outside of steam. It can manage everything you need to run windows software on linux: Proton, Steam Runtime, Wine prefixes. Then it wraps everything up and runs your software with a lot of features i can't list here!

Note: This project has been vibecoded (meaning the code was written by AI) but every other thing (debugging, testing, distrubuting, commiting) is maintained by me. This is a passion/hobby project and i do not gain anything from your usage of this tool.


## Installation

### Download for Debian (and derrivatives)

Install .deb file through the [Releases](#) page and open it. (If you don't have a graphical installer run this command)


```bash
sudo dpkg -i proton-cli.deb # Change the .deb file's name to the version you downloaded
```

### Download for Fedora (and derrivatives)

Install .rpm file through the [Releases](#) page and open it. (If you don't have a graphical installer run this command)

```bash
sudo dnf install ./proton-cli.rpm # Change the .rpm file's name to the version you downloaded
```

### Download through pipx (for other distros) 

#### 1. Install pipx

For example for Arch Linux:

```bash
sudo pacman -S python-pipx
```

#### 2. Download the source code and install the app

Download source code through [Releases](#) page and run this command inside source folder:

```bash
pipx install .
```


## Basic Usage

### 1. Checking Proton and Steam Runtime Installation

If you already have Proton installed via steam, heroic or lutris, run:

```bash
proton-cli check
```

This command will scan specific directories for proton installations and steam runtime installations to save it for later use. If you installed proton in another specific directory there will be an option to manually enter it. If multiple Proton versions are found, you’ll be prompted to choose one. If you don't have steam runtime installed, applications will run with system libraries(This means some performance problems/bugs can happen. Steam runtime is recommended but optional)

### 2. Downloading Proton

If you don’t have Proton installed, simply run:

```bash
proton-cli pull-proton
```

This command automatically downloads the latest GE-Proton release

### 3. Downloading Steam Runtime

If you don’t have Proton installed, simply run:

```bash
proton-cli pull-runtime
```

This command automatically downloads the latest Steam runtime sniper release.

### 4. Running Executable Files

To run a .exe file:

```bash
proton-cli run /path/to/file.exe
```

This will create a new prefix automatically if one doesn’t exist and ask for environment variables if you would like one. If you want a shortcut (.desktop file) you may add one or update an already existing one.


### 5. Help

For full command reference:

```bash
proton-cli help
```

## FAQ

### Will there be Proton-GUI?

One of the reason i made proton-cli was because i wanted make a lightweight tool unlike some heavy one (like bottles). That's why instead of a GUI app i made it cli (it is still easy to use though). I would like to make GUI but i still think there are more stuff that needs to be added to the tool.

### Why should i use this when i can use umu-launcher?

Proton-cli is an all in one tool meaning it does everything from managing prefixes, managing protons, running applications and a lot more. Also this tool was made with end-user in mind.  

### Will there be install method for other distros?

Right now proton-cli has native installations for debian and fedora. There will be more install methods for distros. (AUR, void linux, gentoo etc.)

