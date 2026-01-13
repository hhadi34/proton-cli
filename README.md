# Proton-Cli

**Proton-Cli** is a tool that helps you run proton outside of steam. It downloads proton, manages prefixes, runs .exe's, manages installed applications through smartlisting and a lot more i can't list! The best part about all of this is it's incredibly easy to manage for the end-users out there. 

Before using this application i want to be open about how i made the app and its downsides. Firstly this project was vibecoded meaning the code was written by ai. But besides from the writing of the code, every other thing (debugging, testing, distrubuting, commiting) is maintained by me.  Secondly, proton needs something called "steam runtime". To put it simply it is specific libraries for proton to use. You can use proton without using steam runtime but you may encounter performance issues(not a big issue unless you are running high-end software/games). To fix that i added a little steam runtime wrapper. But to make steam runtime work you have to install steam and download steam runtime(3.0 or 2.0). The way this tool handles runtime seperates it from umu-launcher (another tool to use proton outside of steam that mimics the environment of steam runtime. However it is still complicated for the end-user) 


## Installation

### 1. Download pipx and git for your distro

For example for debian/ubuntu:

```bash
sudo apt install pipx git
```

pipx is needed because it will create a contained environment for python without breaking the system packages.

### 2. Clone the repository in a new directory using git

Run this command:

```bash
git clone https://github.com/hhadi34/proton-cli.git
cd ~/proton-cli
```

This will be the building directory.

### 3. Install the app

Install the app by running

```bash
pipx install .
```

This command will build the app in the ~/.local/share/pipx/venvs/proton-cli/ directory.


## Usage

### 1. Checking Proton Installation

If you already have Proton installed via steam, heroic or lutris, run:

```bash
proton-cli check
```

This command will scan specific directories for proton installations and save it for later use. If you installed proton in another specific directory there will be an option to manually enter it. If multiple Proton versions are found, you’ll be prompted to choose one.

### 2. Downloading Proton

If you don’t have Proton installed, simply run:

```bash
proton-cli pull
```

This command automatically downloads the latest GE-Proton release and sets it as the default Proton version.

### 3. Running Executable Files

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

## The Future of Proton-Cli

There are a lot of testing and bug fixing documentation i need to do to make the tool better. 
