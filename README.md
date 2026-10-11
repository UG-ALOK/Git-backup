# 🚀 Git Repository Backup

**Git Repository Backup** is a high-security, multi-platform terminal utility designed for developers to effortlessly back up all their remote code repositories directly to their device's Android internal storage without dealing with cumbersome local git clone limitations.

---

## 🌐 Supported Platforms
The tool seamlessly connects and fetches live repositories from the following platforms:
* **GitHub** (`github.com`)
* **Codeberg** (`codeberg.org`)
* **GitLab** (`gitlab.com`)
* **Bitbucket** (`bitbucket.org`)
* **Gitea** (`gitea.com` or self-hosted instances)

---

## 🚀 Key Features
* **Direct Android Storage Integration:** Fetches repository zip archives and saves them straight into your phone's **Internal Storage -> Download -> Git_Repository_Backups** folder.
* **Isolated Token Management:** Saves your Personal Access Token cleanly as `token.pat.txt` directly inside the root **Download** folder for easy visibility and management.
* **Advanced Security & Auto-Reset:** Features an automatic **2-minute security timer** that wipes and deletes the token file from storage to prevent accidental leaks.
* **Professional UI:** Clean interactive terminal menus with dynamic token verification across 5 major Git hosting services.

---

## 📦 Installation (Termux / Linux)

To download the repository and run the automated installation script, execute the following commands in your terminal:

```bash
git clone https://github.com/UG-ALOK/Git-backup.git
```
```bash
cd Git-backup
```
```bash
chmod +x install.sh
```
```bash
bash install.sh
```

---

## 🚀 Quick Start Guide

* **Input Token:** Select **Option 1** to paste your Personal Access Token (PAT). The tool will automatically verify your account across supported platforms and securely generate a `token.pat.txt` file in your main `Download` folder.
* **Fetch & Backup:** Select **Option 1** from the active menu to discover all your repositories and trigger bulk direct downloading. Each project will be neatly saved into its own designated folder inside `Download/Git_Repository_Backups`.
* **Auto-Reset Security:** For your protection, the token session automatically expires and deletes `token.pat.txt` after **2 minutes**. You can also manually clear it anytime using **Option 2**.

---

## 👨‍💻 Developer

* **Developer:** ug-alok

---

## 📄 License & Disclaimer

This tool is designed strictly for **self-auditing and personal data backup**. Please use it responsibly and in accordance with platform terms of service.
