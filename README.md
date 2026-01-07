# Proton-Cli

**Proton-Cli** is a tool that helps you run proton outside of steam. It downloads proton, manages prefixes, runs .exe's, manages installed applications through smartlisting and a lot more i can't list! The best part about all of this is it's incredibly easy to manage for the end-users out there. 

Before using this application i want to be open about how i made the app and its downsides. Firstly this project was vibecoded meaning the code was written by ai. But besides from the writing of the code, every other thing (debugging, testing, distrubuting, commiting) is maintained by me. Secondly there isn't an installation method that is distro-specific. Although many of you would prefer this, the end user might still find it difficult to install (i will try to help as much as i can in the installation segment). Lastly, steam runtime (at the time of developing) is not available. This means some performance issues or errors could happen(although unlikely for modern distros there is still a chance). Luckily i have implemented the steam runtime before (1.4.1) that's why it shouldn't be a problem.

*Warning:* This version of the tool is not production ready yet. Although i added a tutorial on how to install it, i did not want a full release because i wanted to take a diffirent approach on the tool instead of what i did in the 1.4.x release cycle. 


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
mkdir -p ~/proton-cli
cd ~/proton-cli
git clone https://github.com/hhadi34/proton-cli.git
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

This will create a new prefix automatically if one doesn’t exist and ask for environment variables if you would like one

*Note:* The first .exe you run is often the installer. After installation, use run-app to find and launch the actual executable.

### 4. Running Installed Applications

To find and launch installed apps:

```bash
proton-cli run-app
```

This lists out the .exe extension files in a prefix. With the smartlisting feature usually the first few .exe is the correct one. You can also save this configurations you made by creating a .desktop(basically a shortcut). The tool will create a .desktop for you if you say yes in the terminal



### 5. Help

For full command reference:

```bash
proton-cli -h
```

## The Future of Proton-Cli

I did not get a chance to try this tool in other systems or distros (i use linux mint btw) and like i said this tool doesn't have distro specific installation methods. I want to publish this through distro repos in the future. Although it is near-future steam runtime wrapper will also be added.
