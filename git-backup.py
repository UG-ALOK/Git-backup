#!/usr/init/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import urllib.request
import urllib.error
import time
import zipfile
import io
import threading

# ANSI Color Codes for Light Gold & Professional Terminal UI
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
LIGHT_GOLD = "\033[33m"
CYAN = "\033[96m"

# Main Download Directory in Android Internal Storage
BASE_DOWNLOAD_DIR = "/storage/emulated/0/Download"

# 1. Token file will be saved directly in main Download folder -> token.pat.txt
CONFIG_FILE = os.path.join(BASE_DOWNLOAD_DIR, "token.pat.txt")

# 2. Backups folder will be created inside Download -> Git_Ultimate_Backups (Only contains repo folders)
BACKUP_DIR = os.path.join(BASE_DOWNLOAD_DIR, "Git_Ultimate_Backups")

# Ensure directories exist
try:
    if not os.path.exists(BASE_DOWNLOAD_DIR):
        os.makedirs(BASE_DOWNLOAD_DIR, exist_ok=True)
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR, exist_ok=True)
except Exception as e:
    print(f"{RED}[!] Warning: Could not create directories automatically: {e}{RESET}")

# Global Session Variables
current_token = None
current_platform = None
current_username = None
session_lock = threading.Lock()

def print_banner():
    banner = f"""
{LIGHT_GOLD}{BOLD}
==================================================
      GIT ULTIMATE AUTO-BACKUP & MIRROR TOOL
          [ Developer : Raj Alok ]
==================================================
{RESET}
    """
    print(banner)

# Background Timer to Auto-Reset Token every 2 Minutes (120 seconds)
def token_expiry_timer():
    global current_token, current_platform, current_username
    time.sleep(120)  # Wait for 2 minutes
    with session_lock:
        current_token = None
        current_platform = None
        current_username = None
        if os.path.exists(CONFIG_FILE):
            try:
                os.remove(CONFIG_FILE)
            except:
                pass
        print(f"\n\n{RED}[!] Security Alert: token.pat.txt auto-reset & deleted after 2 minutes! Please re-configure.{RESET}")

def save_token_to_storage(token, platform, username):
    data = {"token": token, "platform": platform, "username": username}
    try:
        if not os.path.exists(BASE_DOWNLOAD_DIR):
            os.makedirs(BASE_DOWNLOAD_DIR, exist_ok=True)
            
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"{RED}[!] Failed to save token.pat.txt in Download folder: {e}{RESET}")

def load_token_from_storage():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                return data.get("token"), data.get("platform"), data.get("username")
        except:
            return None, None, None
    return None, None, None

def verify_token_input():
    global current_token, current_platform, current_username
    print(f"\n{LIGHT_GOLD}[*] Enter Personal Access Token (PAT) for Multi-Platform{RESET}")
    token = input(f"{LIGHT_GOLD}Paste Access Token: {RESET}").strip()
    if not token:
        print(f"{RED}[!] Token empty!{RESET}")
        return

    platforms = [
        {"name": "GitHub", "url": "https://api.github.com/user", "headers": {"Authorization": f"Bearer {token}", "User-Agent": "GitBackupTool", "Accept": "application/vnd.github+json"}, "parser": lambda d: d.get("login")},
        {"name": "Codeberg", "url": "https://codeberg.org/api/v1/user", "headers": {"Authorization": f"token {token}", "User-Agent": "GitBackupTool", "Accept": "application/json"}, "parser": lambda d: d.get("login")},
        {"name": "GitLab", "url": "https://gitlab.com/api/v4/user", "headers": {"PRIVATE-TOKEN": token, "User-Agent": "GitBackupTool"}, "parser": lambda d: d.get("username")},
        {"name": "Bitbucket", "url": "https://api.bitbucket.org/2.0/user", "headers": {"Authorization": f"Bearer {token}", "User-Agent": "GitBackupTool"}, "parser": lambda d: d.get("username")},
        {"name": "Gitea", "url": "https://gitea.com/api/v1/user", "headers": {"Authorization": f"token {token}", "User-Agent": "GitBackupTool", "Accept": "application/json"}, "parser": lambda d: d.get("login")}
    ]

    detected, uname = None, None
    for p in platforms:
        req = urllib.request.Request(p["url"], headers=p["headers"])
        try:
            with urllib.request.urlopen(req) as res:
                if res.status == 200:
                    data = json.loads(res.read().decode())
                    uname = p["parser"](data)
                    detected = p["name"]
                    break
        except:
            continue

    if detected and uname:
        with session_lock:
            current_token = token
            current_platform = detected
            current_username = uname
            save_token_to_storage(token, detected, uname)
        
        # Start 2-minute auto-reset timer in background
        threading.Thread(target=token_expiry_timer, daemon=True).start()
        
        print(f"\n{GREEN}[✔] Verified! Platform: {detected} | User: {uname}{RESET}")
        print(f"{CYAN}[i] token.pat.txt successfully created in Internal Storage -> Download folder!{RESET}")
    else:
        print(f"{RED}[!] Invalid token across all supported platforms.{RESET}")

def fetch_and_backup_repos():
    global current_token, current_platform, current_username
    
    t, p, u = load_token_from_storage()
    if not t:
        with session_lock:
            current_token, current_platform, current_username = None, None, None
        print(f"{RED}[!] ইন্টারনাল স্টোরেজের Download ফোল্ডারে token.pat.txt ফাইল পাওয়া যায়নি! অনুগ্রহ করে আবার একবার রেজিস্টার করে নিন (Option 1)।{RESET}")
        return

    print(f"\n{LIGHT_GOLD}[*] Fetching live repositories from {current_platform}...{RESET}")
    time.sleep(0.3)

    url, headers, repos = "", {}, []

    if current_platform == "GitHub":
        url, headers = "https://api.github.com/user/repos?per_page=100", {"Authorization": f"Bearer {current_token}", "User-Agent": "GitBackupTool", "Accept": "application/vnd.github+json"}
    elif current_platform in ["Codeberg", "Gitea"]:
        base = "https://codeberg.org" if current_platform == "Codeberg" else "https://gitea.com"
        url, headers = f"{base}/api/v1/user/repos?limit=100", {"Authorization": f"token {current_token}", "User-Agent": "GitBackupTool", "Accept": "application/json"}
    elif current_platform == "GitLab":
        url, headers = "https://gitlab.com/api/v4/projects?membership=true", {"PRIVATE-TOKEN": current_token, "User-Agent": "GitBackupTool"}
    elif current_platform == "Bitbucket":
        url, headers = "https://api.bitbucket.org/2.0/repositories?role=member", {"Authorization": f"Bearer {current_token}", "User-Agent": "GitBackupTool"}

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as res:
            raw = json.loads(res.read().decode())
            if current_platform in ["GitHub", "Codeberg", "Gitea", "GitLab"]:
                for r in raw:
                    name = r.get("name")
                    full_name = r.get("full_name") or r.get("path_with_namespace") or f"{current_username}/{name}"
                    branch = r.get("default_branch", "main")
                    if name:
                        if current_platform == "GitHub":
                            zip_url = f"https://api.github.com/repos/{full_name}/zipball/{branch}"
                        elif current_platform in ["Codeberg", "Gitea"]:
                            base = "https://codeberg.org" if current_platform == "Codeberg" else "https://gitea.com"
                            zip_url = f"{base}/api/v1/repos/{full_name}/archive/{branch}.zip"
                        elif current_platform == "GitLab":
                            proj_id = r.get("id")
                            zip_url = f"https://gitlab.com/api/v4/projects/{proj_id}/repository/archive.zip"
                        
                        repos.append({"name": name, "full_name": full_name, "zip_url": zip_url})
            elif current_platform == "Bitbucket":
                for r in raw.get("values", []):
                    name = r.get("name")
                    full_name = r.get("full_name")
                    if name:
                        zip_url = f"https://api.bitbucket.org/2.0/repositories/{full_name}/get/HEAD.zip"
                        repos.append({"name": name, "full_name": full_name, "zip_url": zip_url})

            print(f"\n{LIGHT_GOLD}=================================================={RESET}")
            print(f"{LIGHT_GOLD}[+] Total Repositories Discovered: {len(repos)}{RESET}")
            print(f"{LIGHT_GOLD}=================================================={RESET}")

            for idx, r in enumerate(repos, 1):
                print(f"{LIGHT_GOLD}{idx}. {r['name']}{RESET}")

            print(f"{LIGHT_GOLD}=================================================={RESET}")
            
            choice = input(f"\n{LIGHT_GOLD}[?] Direct download all repos into Download/Git_Ultimate_Backups? (y/n): {RESET}").strip().lower()
            if choice == 'y':
                run_bulk_backup(repos, current_token, current_platform)
    except Exception as e:
        print(f"{RED}[!] Error fetching repositories: {e}{RESET}")

def run_bulk_backup(repos, token, platform):
    print(f"\n{LIGHT_GOLD}[*] Downloading repository backups directly to Download/Git_Ultimate_Backups...{RESET}")
    success_count = 0

    for repo in repos:
        name = repo['name']
        zip_url = repo['zip_url']
        
        # Only repo code folders will be inside Git_Ultimate_Backups/
        repo_backup_dir = os.path.join(BACKUP_DIR, name)
        os.makedirs(repo_backup_dir, exist_ok=True)

        headers = {"User-Agent": "GitBackupTool"}
        if platform == "GitHub":
            headers["Authorization"] = f"Bearer {token}"
            headers["Accept"] = "application/vnd.github+json"
        elif platform in ["Codeberg", "Gitea"]:
            headers["Authorization"] = f"token {token}"
            headers["Accept"] = "application/json"
        elif platform == "GitLab":
            headers["PRIVATE-TOKEN"] = token
        elif platform == "Bitbucket":
            headers["Authorization"] = f"Bearer {token}"

        print(f"{CYAN}[+] Backing up: {name}...{RESET}", end="", flush=True)
        try:
            req = urllib.request.Request(zip_url, headers=headers)
            with urllib.request.urlopen(req) as resp:
                zip_content = resp.read()
                with zipfile.ZipFile(io.BytesIO(zip_content)) as zfile:
                    zfile.extractall(repo_backup_dir)
            print(f" {GREEN}[✔] Saved!{RESET}")
            success_count += 1
        except Exception as e:
            print(f" {RED}[✘] Failed{RESET}")

    print(f"\n{GREEN}{BOLD}==================================================")
    print(f"          BACKUP COMPLETED SUCCESSFULLY!")
    print(f" Successfully Backed Up: {success_count}/{len(repos)}")
    print(f" Saved Location: {BACKUP_DIR}")
    print(f"=================================================={RESET}\n")

def main():
    global current_token, current_platform, current_username
    print_banner()

    while True:
        t, p, u = load_token_from_storage()
        if t:
            current_token, current_platform, current_username = t, p, u
        else:
            current_token, current_platform, current_username = None, None, None

        has_token = current_token is not None

        print(f"\n{LIGHT_GOLD}┌──────────────────────────────────────────────┐{RESET}")
        print(f"{LIGHT_GOLD}│                 MAIN MENU                    │{RESET}")
        print(f"{LIGHT_GOLD}├──────────────────────────────────────────────┤{RESET}")
        
        if not has_token:
            print(f"{LIGHT_GOLD}│{RESET}  {LIGHT_GOLD}1. Input Token  {LIGHT_GOLD}│{RESET}")
            print(f"{LIGHT_GOLD}│{RESET}  {LIGHT_GOLD}2. Exit                                     {LIGHT_GOLD}│{RESET}")
        else:
            print(f"{LIGHT_GOLD}│{RESET}  {GREEN}Status: Active ({current_platform}: {current_username[:10]}){LIGHT_GOLD}│{RESET}")
            print(f"{LIGHT_GOLD}│{RESET}  {LIGHT_GOLD}1. Fetch & Direct Backup All Repositories   {LIGHT_GOLD}│{RESET}")
            print(f"{LIGHT_GOLD}│{RESET}  {LIGHT_GOLD}2. Clear Token (Deletes token.pat.txt)      {LIGHT_GOLD}│{RESET}")
            print(f"{LIGHT_GOLD}│{RESET}  {LIGHT_GOLD}3. Exit                                     {LIGHT_GOLD}│{RESET}")
            
        print(f"{LIGHT_GOLD}└──────────────────────────────────────────────┘{RESET}")

        if not has_token:
            choice = input(f"\n{LIGHT_GOLD}Select option (1-2): {RESET}").strip()
            if choice == "1":
                verify_token_input()
            elif choice == "2":
                sys.exit(0)
        else:
            choice = input(f"\n{LIGHT_GOLD}Select option (1-3): {RESET}").strip()
            if choice == "1":
                fetch_and_backup_repos()
            elif choice == "2":
                with session_lock:
                    current_token, current_platform, current_username = None, None, None
                    if os.path.exists(CONFIG_FILE):
                        os.remove(CONFIG_FILE)
                print(f"{LIGHT_GOLD}[*] token.pat.txt removed from Download folder.{RESET}")
            elif choice == "3":
                sys.exit(0)

if __name__ == "__main__":
    main()
