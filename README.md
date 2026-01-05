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

### Option 2: Manual method
Download the proton_cli.py and copy it to /usr/local/bin by running:

```bash
sudo cp /path/to/proton_cli.py /usr/local/bin 
```
Then make it an executable file by

```bash
sudo chmod +x/usr/local/bin/proton_cli.py 
```


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

## The Future of proton-cli

Here’s what’s planned for upcoming releases:

- ARM support for Steam Frame and similar devices  
- Distribution packages for Fedora, Arch, and more  
- Advanced options for power users  
- Deeper integration with other software (beyond environment variables)  
