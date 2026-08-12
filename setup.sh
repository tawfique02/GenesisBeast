#!/bin/bash

# ============================================================
#  🚀 GenesisBeast v5.0 - Mobile Forensic Suite
#  📱 Complete Android Mobile Forensics Tool for Termux
#  👨‍💻 Developer: tawfique02 | GitHub: github.com/tawfique02
# ============================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# ============================================================
#  BANNER
# ============================================================

clear
echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║   📱 GENESIS BEAST v5.0 - MOBILE FORENSIC SUITE                  ║"
echo "║   🔍 The World's First Complete Mobile Forensic Tool for Termux  ║"
echo "║   👨‍💻 Developer: tawfique02 | 🔗 github.com/tawfique02           ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ============================================================
#  CHECK TERMUX ENVIRONMENT
# ============================================================

echo -e "${YELLOW}🔍 Checking Termux Environment...${NC}"

# Check if running in Termux
if [ ! -d "/data/data/com.termux" ]; then
    echo -e "${RED}❌ This script is designed for Termux on Android!${NC}"
    echo -e "${YELLOW}💡 Please run this in Termux environment.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Termux environment detected!${NC}"

# ============================================================
#  CHECK AND INSTALL REQUIRED PACKAGES
# ============================================================

echo -e "\n${YELLOW}📦 Checking and installing required packages...${NC}"

# Function to check and install package
check_and_install() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✅ $1 already installed${NC}"
    else
        echo -e "${YELLOW}📥 Installing $1...${NC}"
        pkg install $1 -y
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ $1 installed successfully${NC}"
        else
            echo -e "${RED}❌ Failed to install $1${NC}"
        fi
    fi
}

# Update packages first
echo -e "\n${YELLOW}🔄 Updating package lists...${NC}"
pkg update -y

# Install core packages
check_and_install python
check_and_install git
check_and_install openssl
check_and_install libffi
check_and_install binutils
check_and_install termux-api
check_and_install tsu

# ============================================================
#  CHECK AND INSTALL PYTHON PACKAGES
# ============================================================

echo -e "\n${YELLOW}📦 Checking and installing Python packages...${NC}"

# Function to check and install Python package
check_pip_package() {
    if pip show $1 &> /dev/null; then
        echo -e "${GREEN}✅ $1 already installed${NC}"
    else
        echo -e "${YELLOW}📥 Installing $1...${NC}"
        pip install $1
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ $1 installed successfully${NC}"
        else
            echo -e "${RED}❌ Failed to install $1${NC}"
        fi
    fi
}

# Upgrade pip first
echo -e "\n${YELLOW}🔄 Upgrading pip...${NC}"
pip install --upgrade pip

# Install required Python packages
check_pip_package rich
check_pip_package requests
check_pip_package psutil

# ============================================================
#  CHECK AND INSTALL TERMUX-API (OPTIONAL)
# ============================================================

echo -e "\n${YELLOW}📡 Checking Termux-API...${NC}"
if command -v termux-wifi-connectioninfo &> /dev/null; then
    echo -e "${GREEN}✅ Termux-API already installed${NC}"
else
    echo -e "${YELLOW}📥 Installing Termux-API...${NC}"
    pkg install termux-api -y
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Termux-API installed successfully${NC}"
    else
        echo -e "${YELLOW}⚠️ Termux-API installation failed (optional)${NC}"
    fi
fi

# ============================================================
#  GRANT STORAGE PERMISSION
# ============================================================

echo -e "\n${YELLOW}🔑 Checking storage permission...${NC}"

if [ -d "/sdcard" ]; then
    echo -e "${GREEN}✅ Storage already accessible${NC}"
else
    echo -e "${YELLOW}📱 Granting storage permission...${NC}"
    termux-setup-storage
    sleep 2
    if [ -d "/sdcard" ]; then
        echo -e "${GREEN}✅ Storage permission granted successfully!${NC}"
    else
        echo -e "${YELLOW}⚠️ Storage permission not granted. Please manually allow in Settings.${NC}"
    fi
fi

# ============================================================
#  DOWNLOAD OR UPDATE THE TOOL
# ============================================================

echo -e "\n${YELLOW}📥 Setting up GenesisBeast tool...${NC}"

# Check if tool already exists
if [ -d "genesisbeast" ]; then
    echo -e "${YELLOW}⚠️ GenesisBeast directory already exists!${NC}"
    read -p "Do you want to update it? (y/n): " update_choice
    if [[ $update_choice == "y" || $update_choice == "Y" ]]; then
        echo -e "${YELLOW}🔄 Updating GenesisBeast...${NC}"
        cd genesisbeast
        git pull
        cd ..
        echo -e "${GREEN}✅ Updated successfully!${NC}"
    else
        echo -e "${YELLOW}⚠️ Using existing version.${NC}"
    fi
else
    echo -e "${YELLOW}📥 Cloning GenesisBeast...${NC}"
    git clone https://github.com/tawfique02/genesisbeast.git
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Downloaded successfully!${NC}"
    else
        echo -e "${RED}❌ Failed to clone repository${NC}"
        exit 1
    fi
fi

# ============================================================
#  CREATE REQUIRED DIRECTORIES
# ============================================================

echo -e "\n${YELLOW}📁 Creating directories...${NC}"

cd genesisbeast || exit

mkdir -p cases
mkdir -p reports
mkdir -p logs
mkdir -p evidence

echo -e "${GREEN}✅ Directories created!${NC}"

# ============================================================
#  CHECK IF main.py EXISTS, IF NOT RENAME
# ============================================================

echo -e "\n${YELLOW}🔍 Checking main file...${NC}"

if [ -f "main.py" ]; then
    echo -e "${GREEN}✅ main.py found!${NC}"
    MAIN_FILE="main.py"
elif [ -f "genesisbeast.py" ]; then
    echo -e "${YELLOW}⚠️ genesisbeast.py found, but main.py is preferred${NC}"
    echo -e "${YELLOW}🔄 Creating symlink main.py -> genesisbeast.py${NC}"
    ln -sf genesisbeast.py main.py
    MAIN_FILE="main.py"
else
    echo -e "${RED}❌ No main Python file found!${NC}"
    echo -e "${YELLOW}📥 Downloading main.py...${NC}"
    wget -O main.py https://raw.githubusercontent.com/tawfique02/genesisbeast/main/main.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ main.py downloaded successfully!${NC}"
        MAIN_FILE="main.py"
    else
        echo -e "${RED}❌ Failed to download main.py${NC}"
        exit 1
    fi
fi

# ============================================================
#  CREATE REQUIREMENTS.TXT
# ============================================================

echo -e "\n${YELLOW}📝 Creating requirements.txt...${NC}"

cat > requirements.txt << 'EOF'
# GenesisBeast v5.0 Requirements
rich>=10.0.0
requests>=2.25.0
psutil>=5.8.0
EOF

echo -e "${GREEN}✅ requirements.txt created!${NC}"

# ============================================================
#  CREATE RUN SCRIPT (main.py support)
# ============================================================

echo -e "\n${YELLOW}📝 Creating run script...${NC}"

cat > run.sh << 'EOF'
#!/bin/bash
# GenesisBeast v5.0 - Run Script
# Developer: tawfique02

clear
echo "🔍 Starting GenesisBeast v5.0..."
echo "📱 Mobile Forensic Suite for Termux"
echo "===================================="

# Check if main.py exists
if [ -f "main.py" ]; then
    python main.py
elif [ -f "genesisbeast.py" ]; then
    python genesisbeast.py
else
    echo "❌ Error: No main Python file found!"
    exit 1
fi
EOF

chmod +x run.sh
echo -e "${GREEN}✅ run.sh created!${NC}"

# ============================================================
#  CREATE UNINSTALL SCRIPT
# ============================================================

echo -e "\n${YELLOW}📝 Creating uninstall script...${NC}"

cat > uninstall.sh << 'EOF'
#!/bin/bash
# GenesisBeast v5.0 - Uninstall Script

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}⚠️ WARNING: This will remove GenesisBeast!${NC}"
read -p "Do you want to continue? (y/n): " confirm

if [[ $confirm == "y" || $confirm == "Y" ]]; then
    cd ..
    rm -rf genesisbeast
    echo -e "${GREEN}✅ GenesisBeast removed successfully!${NC}"
else
    echo -e "${YELLOW}❌ Uninstall cancelled.${NC}"
fi
EOF

chmod +x uninstall.sh
echo -e "${GREEN}✅ uninstall.sh created!${NC}"

# ============================================================
#  CREATE LAUNCHER SCRIPT (Global)
# ============================================================

echo -e "\n${YELLOW}📝 Creating global launcher...${NC}"

cat > $PREFIX/bin/genesisbeast << 'EOF'
#!/bin/bash
cd ~/genesisbeast
python main.py
EOF

chmod +x $PREFIX/bin/genesisbeast
echo -e "${GREEN}✅ Global launcher created!${NC}"
echo -e "${YELLOW}💡 Now you can run 'genesisbeast' from anywhere${NC}"

# ============================================================
#  CHECK ROOT ACCESS
# ============================================================

echo -e "\n${YELLOW}🔑 Checking root access...${NC}"

if command -v su &> /dev/null; then
    echo -e "${GREEN}✅ Root access available${NC}"
    echo -e "${YELLOW}💡 Some advanced features will work with root${NC}"
else
    echo -e "${YELLOW}⚠️ Root access not available${NC}"
    echo -e "${YELLOW}💡 Most features will work without root${NC}"
fi

# ============================================================
#  DISPLAY INSTALLATION SUMMARY
# ============================================================

echo -e "\n${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  ✅ INSTALLATION COMPLETE!                                       ║"
echo "║  📱 GenesisBeast v5.0 is ready to use!                          ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}📊 Installation Summary:${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📁 Directory:${NC} $(pwd)"
echo -e "${BLUE}📄 Main File:${NC} $MAIN_FILE"
echo -e "${BLUE}🐍 Python:${NC} $(python --version 2>&1)"
echo -e "${BLUE}📦 Rich:${NC} $(pip show rich 2>/dev/null | grep Version || echo 'Not installed')"
echo -e "${BLUE}📦 Requests:${NC} $(pip show requests 2>/dev/null | grep Version || echo 'Not installed')"
echo -e "${BLUE}🔑 Root Access:${NC} $(if command -v su &> /dev/null; then echo '✅ Available'; else echo '❌ Not Available'; fi)"
echo -e "${BLUE}📱 Termux:${NC} ✅"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# ============================================================
#  SHOW NEXT STEPS
# ============================================================

echo -e "\n${YELLOW}📌 NEXT STEPS:${NC}"
echo -e "${GREEN}1.${NC} cd genesisbeast"
echo -e "${GREEN}2.${NC} python main.py              ${YELLOW}# Run the tool${NC}"
echo -e "${GREEN}3.${NC} ./run.sh                    ${YELLOW}# Or use the run script${NC}"
echo -e "${GREEN}4.${NC} genesisbeast                ${YELLOW}# Or use global command${NC}"
echo -e ""
echo -e "${YELLOW}💡 Quick Commands:${NC}"
echo -e "   ${CYAN}python main.py${NC}               - Start the tool"
echo -e "   ${CYAN}python main.py --help${NC}        - Show help"
echo -e "   ${CYAN}./run.sh${NC}                     - Run with script"
echo -e "   ${CYAN}./uninstall.sh${NC}               - Uninstall tool"
echo -e "   ${CYAN}genesisbeast${NC}                 - Run from anywhere"

echo -e "\n${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  🚀 Enjoy using GenesisBeast v5.0!                              ║"
echo "║  🔍 The World's First Complete Mobile Forensic Suite for Termux ║"
echo "║  👨‍💻 Developer: tawfique02                                       ║"
echo "║  🔗 GitHub: github.com/tawfique02                               ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ============================================================
#  END OF SCRIPT
# ============================================================
