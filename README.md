# Proton-Cli

**Proton-Cli** is a tool that helps you run proton outside of steam. It downloads proton, manages prefixes, runs .exe's, manages installed applications through smartlisting and a lot more i can't list! The best part about all of this is it's incredibly easy to manage for the end-users out there. 

Before using this application i want to be open about how i made the app and its downsides. Firstly this project was vibecoded meaning the code was written by ai. But besides from the writing of the code, every other thing (debugging, testing, distrubuting, commiting) is maintained by me.  Secondly, proton needs something called "steam runtime". To put it simply it is specific libraries for proton to use. You can use proton without using steam runtime but you may encounter performance issues(not a big issue unless you are running high-end software/games). To fix that i added a little steam runtime wrapper. But to make steam runtime work you have to install steam and download steam runtime(3.0 or 2.0). The way this tool handles runtime seperates it from umu-launcher (another tool to use proton outside of steam that mimics the environment of steam runtime. However it is still complicated for the end-user) 


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
sudo pacman -S python-pipx git
```

#### 2. Clone the repository in a new directory using git

Run this command:

```bash
git clone https://github.com/hhadi34/proton-cli.git
cd ~/proton-cli
```

#### 3. Install the app

Install the app by running

```bash
pipx install .
```


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


### 4. Help

For full command reference:

```bash
proton-cli help
```

## FAQ

### Will there be Proton-GUI?

One of the reason i made proton-cli was because i wanted make a lightweight tool unlike some heavy one (like bottles). That's why instead of a GUI app i made it cli (it is still easy to use though). I would like to make GUI but i still think there are more stuff that needs to be added to the tool.

### Why should i use this when i can use umu-launcher?

There are 2 things that we do different than umu-launcher:

**1.** Proton-cli is an all in one tool meaning it does everything from managing prefixes, managing protons, running applications and a lot more. Also this tool was made with end-user in mind.

**2.** Umu-launcher is it's own wrapper meaning it copies everything that steam does while proton-cli is kind of bridge between steam and the application meaning it contacts with steam directly. That's why to use steam runtime you need to have steam and the runtime installed. 

### Will there be install method for other distros?

Right now proton-cli has native installations for debian and fedora. There will be more install methods for distros. (AUR, void linux, gentoo etc.)