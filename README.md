# proton-cli

**proton-cli** is a lightweight command-line interface that makes it easier to run Windows software on Linux using **Proton** or **GE-Proton**.

It automates common setup tasks such as locating your Proton installation, managing prefixes, and running executables with minimal hassle — all from the terminal.



## Introduction

Running Windows software with Proton is great — but setting up prefixes, managing versions, and launching apps can be tedious.  
**proton-cli** simplifies this process.

With a few simple commands, you can:
- Detect and configure your existing Proton installations  
- Download and manage GE-Proton builds  
- Automatically create and manage prefixes  
- Run `.exe` files seamlessly  
- Generate desktop shortcuts for quick access  



## Installation

You can install **proton-cli** in two ways:

### Option 1: Using `.deb` Package
Download the latest `.deb` release from the [Releases](#) page and install it:

```bash
sudo dpkg -i proton-cli_<version>.deb
```

If any dependencies are missing, fix them with:
```bash
sudo apt --fix-broken install
```
### Option 2: Using the script manually
Download proton_cli.py then make it an executable file by running:
```bash
chmod +x proton_cli.py
```
then put the file into /usr/local/bin/ by using
```bash
sudo cp /path/to/proton_cli.py /usr/local/bin/proton-cli
```
*Note:* In the current state of the development, **there isn't a method to update the software unless if you redownload it**. Next update will add the self updating system.

## Usage

### 1. Checking Proton Installation

If you already have Proton installed (via **Steam**, **Heroic**, or **Lutris**):

```bash
proton-cli check
```

This command scans your system for Proton installations and selects a default version automatically.  
If multiple Proton versions are found, you’ll be prompted to choose one.

If **no installation is found**, you can manually specify the directory after running the `check` command.



### 2. Downloading Proton

If you don’t have Proton installed, simply run:

```bash
proton-cli pull
```

This command automatically downloads the **latest GE-Proton release** and sets it as the default Proton version.



### 3. Running Executable Files

To run a Windows `.exe` file:

```bash
proton-cli run /path/to/file.exe
```

This will:
- Create a new **prefix** automatically if one doesn’t exist  
- Ask for **environment variables** if needed  
- Launch the `.exe` file under Proton  

*Note:* The first `.exe` you run is often the installer. After installation, use `run-app` to find and launch the main executable.



### 4. Running Installed Applications

To find and launch installed apps:

```bash
proton-cli run-app
```

This lets you:
- Choose a prefix  
- View a **smartlisted** set of `.exe` files (the first is usually the correct one)  
- Customize variables before launching  

You can also create a **desktop shortcut** during this process — simply choose a name when prompted, and a `.desktop` file will be generated automatically.



### 5. Help

For full command reference:

```bash
proton-cli -h
```



## The Software’s Origin

My friends and I entered a competition to create an XR game. I was in charge of the music and sound effects, but I ended up wasting half of my time just trying to get FL Studio to run on Linux. I first tried running it with Wine, but it was incredibly sluggish. Then I tried using it with Proton through Bottles, but Bottles itself was slow (for context, my laptop was only a year old and had good specs). The only way I could make it work was by adding the .exe to my Steam library and setting up a bunch of environment variables in the Python script that runs Proton. After that, I created a .desktop file so I could launch it easily without having to remember all the necessary variables. This might sound simple, but it actually took a lot of effort. I had to dig through multiple directories using Nemo and consult different AI models to make it all work. In the end, we lost the competition because half of the code broke at the last minute and the presentation fell apart. Months later, when talking with my friends about what did we do while making the game, the idea for my new software came to me. I realized two things: 1. Proton is better than Wine. That’s why many people who have issues with Wine might prefer Proton. Proton can actually run independently with the right environment variables, directories, and dependencies. So, on New Year’s Eve, I started working on it. Just as we entered the new year, the software was ready.


## The Future of proton-cli

Here’s what’s planned for upcoming releases:

- ARM support for Steam Frame and similar devices  
- Distribution packages for Fedora, Arch, and more  
- A GTK-based graphical interface  
- Advanced options for power users  
- Deeper integration with other software (beyond environment variables)  
