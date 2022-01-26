# SHA256withRSA

 The SHA256withRSA Algorithm with GUI

![](https://img.shields.io/badge/dependencies-python%203.9-blue)
![](https://img.shields.io/badge/OS-windows%2010-lightgrey)


## Introduction

<img src="https://user-images.githubusercontent.com/41314224/121566185-d46be500-ca4f-11eb-9e68-6cc519dd206c.png" width="360" height="600" alt="screenshot">

## Functions

1. Generate RSA keypair. Public key's extension is `*.pub`; private key doesn't have an extension name.
2. Sign for a message.
3. Verify if a message from the private key holder is valid.

## Usage

### 1. For compiling

Run `pip install -r requirements` to install the dependent packages.

Run `pyinstaller -F -w main.py` to generate executable program in `dist` folder.

### 2. For directly using

This software is designed at 1080p screen size. It will adapt to the system zoom. If you cannot see the text on buttons clearly, the software may not be suitable for your screen.

To start with, please get the latest release in this repository and run `main.exe`.
