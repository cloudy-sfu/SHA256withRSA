# SHA256withRSA

 The SHA256withRSA Algorithm with GUI

![](https://img.shields.io/badge/dependencies-python%203.9-blue)

## Introduction

It is a web-based GUI for SHA256withRSA operations as follows. It automatically starts service at localhost. Neither does it rely on the public webserver, nor does it rely on the GUI interface of the operational system.

**Verify signature**: 
Given the content and signature, use the public key to verify if the signature is valid.

**Generate**:
Generate a SHA256withRSA keypair, including a public key and a private key.

**Sign**:
Given the content, use the private key to sign it.

## Usage

**End user**: Download from the latest release, unzip and run `main.exe`.

**Developer**:

```bash
pip install -r requirements.txt
pyinstaller main.spec
```
