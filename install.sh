#!/usr/bin/env bash

# ANSI Color Codes for Professional Terminal Output
RESET="\033[0m"
BOLD="\033[1m"
RED="\033[91m"
GREEN="\033[92m"
LIGHT_GOLD="\033[33m"
CYAN="\033[96m"

echo -e "${LIGHT_GOLD}${BOLD}"
echo "=================================================="
echo "   INSTALLING GIT BACKUP "
echo "            [ Developer : Raj Alok ]"
echo "=================================================="
echo -e "${RESET}"

# Step 1: Check for Python3
echo -e "${LIGHT_GOLD}[*] Checking Python3 installation...${RESET}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[!] Python3 is not installed! Installing Python3...${RESET}"
    if command -v pkg &> /dev/null; then
        pkg update -y && pkg install python3 -y
    elif command -v apt &> /dev/null; then
        sudo apt update && sudo apt install python3 -y
    else
        echo -e "${RED}[!] Please install Python3 manually to proceed.${RESET}"
        exit 1
    fi
else
    echo -e "${GREEN}[✔] Python3 is already installed.${RESET}"
fi

# Step 2: Check main python script (git-backup.py)
TARGET_PY="git-backup.py"
if [ ! -f "$TARGET_PY" ]; then
    if [ -f "main.py" ]; then
        mv main.py git-backup.py
        TARGET_PY="git-backup.py"
    else
        echo -e "${RED}[!] Error: Python script not found! Please ensure git-backup.py is present.{RESET}"
        exit 1
    fi
fi

# Step 3: Setup executable permissions
echo -e "${LIGHT_GOLD}[*] Configuring script permissions...${RESET}"
chmod +x "$TARGET_PY"
if [ -f "git-backup.sh" ]; then
    chmod +x "git-backup.sh"
fi
echo -e "${GREEN}[✔] Permissions configured successfully!{RESET}"

# Step 4: Check and request storage permissions (Termux)
if [ -d "/data/data/com.termux" ]; then
    echo -e "${LIGHT_GOLD}[*] Checking Termux storage permissions...${RESET}"
    if ! [ -d "/storage/emulated/0/Download" ]; then
        echo -e "${CYAN}[i] Requesting storage permission (termux-setup-storage)...${RESET}"
        termux-setup-storage
    else
        echo -e "${GREEN}[✔] Internal storage access verified.${RESET}"
    fi
fi

echo -e "\n${GREEN}${BOLD}=================================================="
echo "          INSTALLATION COMPLETED SUCCESSFULLY!"
echo "=================================================="
echo -e "${RESET}"
echo -e "${LIGHT_GOLD}To run the tool, simply execute the following command:${RESET}"
echo -e "${CYAN}${BOLD}python git-backup.py${RESET}\n"
