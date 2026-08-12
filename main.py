#!/usr/bin/env python3
"""
GenesisBeast v5.0 - Mobile Forensic Suite
Complete Android Mobile Forensics Tool for Termux
Developer: tawfique02 | GitHub: github.com/tawfique02
"""

import os
import sys
import subprocess
import json
import requests
import sqlite3
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich import box
    from rich.text import Text
    from rich.tree import Tree
except ImportError:
    print("❌ Rich library not found. Install with:")
    print("   pip install rich requests")
    sys.exit(1)


class MobileForensics:
    """Complete Mobile Forensic Tool for Termux"""

    def __init__(self):
        self.console = Console()
        self.version = "5.0"
        self.developer = "tawfique02"
        self.github = "github.com/tawfique02"
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.case_name = f"MOBILE_FORENSIC_{self.timestamp}"
        self.case_dir = Path(self.case_name)
        self.case_dir.mkdir(exist_ok=True)
        self.scan_results = {}
        self.is_android = self.check_android()
        self.has_root = self.check_root()

        self.modules = self.get_mobile_modules()

    def check_android(self):
        try:
            result = subprocess.getoutput("getprop ro.build.version.release 2>/dev/null")
            return bool(result.strip())
        except:
            return False

    def check_root(self):
        try:
            result = subprocess.getoutput("su -c 'echo test' 2>/dev/null")
            return bool(result) and "test" in result
        except:
            return False

    def get_mobile_modules(self):
        return {
            "📱 DEVICE INFO": {
                "1. Device Information": self.get_device_info,
                "2. Android Version": self.get_android_version,
                "3. Device IDs": self.get_device_ids,
                "4. Battery Status": self.get_battery_status,
                "5. SELinux Status": self.get_selinux_status,
                "6. Root Detection": self.check_root_access,
            },
            "📦 APP ANALYSIS": {
                "7. Installed Apps": self.get_installed_apps,
                "8. App Permissions": self.get_app_permissions,
                "9. Running Services": self.get_running_services,
                "10. Intent History": self.get_intent_history,
            },
            "👤 USER DATA": {
                "11. Contacts": self.get_contacts,
                "12. SMS Messages": self.get_sms,
                "13. Call Logs": self.get_call_logs,
                "14. Account Info": self.get_accounts,
            },
            "💬 SOCIAL MEDIA": {
                "15. WhatsApp Data": self.get_whatsapp_data,
                "16. Telegram Data": self.get_telegram_data,
                "17. Browser History": self.get_browser_history,
            },
            "🔐 SECURITY": {
                "18. WiFi Passwords": self.get_wifi_passwords,
                "19. Suspicious Files": self.scan_suspicious_files,
                "20. Ransomware Scan": self.ransomware_scanner,
            },
            "📁 FILE SYSTEM": {
                "21. Recent Files": self.get_recent_files,
                "22. Modified Files": self.get_modified_files,
                "23. Deleted Files": self.get_deleted_files,
                "24. System Logs": self.get_system_logs,
            },
            "🌐 NETWORK": {
                "25. Active Connections": self.get_active_connections,
                "26. Geolocation": self.get_geo_intelligence,
                "27. DNS Cache": self.get_dns_cache,
            }
        }

    def show_banner(self):
        banner = f"""
╔══════════════════════════════════════════════════════════════════╗
║   📱 GENESIS BEAST v{self.version} - MOBILE FORENSIC SUITE                  ║
║   👨‍ Developer: {self.developer} | 🔗 {self.github}            ║
╚══════════════════════════════════════════════════════════════════╝
        """
        self.console.print(banner, style="cyan bold")

        # Show status
        status = Text()
        status.append("📱 Android: ", style="yellow")
        status.append("✅" if self.is_android else "❌", style="green" if self.is_android else "red")
        status.append("  |  ")
        status.append("🔑 Root: ", style="yellow")
        status.append("✅" if self.has_root else "❌", style="green" if self.has_root else "red")
        self.console.print(status)
        self.console.print()

    def show_main_menu(self):
        menu = """
        [cyan bold]▸ MAIN MENU[/]

        [green]1[/] 🔍 Start Full Mobile Scan
        [green]2[/] 📊 View Scan Results
        [green]3[/] 📁 Export Reports
        [green]4[/] 📈 Case Statistics
        [green]5[/] 👾 About & Info
        [green]6[/] 🚪 Exit
        """
        self.console.print(menu)
        return Prompt.ask("Select option", choices=["1", "2", "3", "4", "5", "6"])

    def show_module_selection(self):
        self.console.print("\n[cyan bold]▸ SELECT MODULES TO SCAN[/]\n")

        modules_list = []
        table = Table(title="Available Mobile Forensic Modules", box=box.HEAVY_EDGE)
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Category", style="yellow")
        table.add_column("Module", style="green")
        table.add_column("Status", style="blue")

        idx = 1
        for category in self.modules.keys():
            for name in self.modules[category].keys():
                table.add_row(str(idx), category, name, "🟢 Ready")
                modules_list.append((name, self.modules[category][name]))
                idx += 1

        self.console.print(table)
        self.console.print(f"\n[dim]📊 Total Modules: {len(modules_list)}[/]")

        selected_str = Prompt.ask(
            "\nEnter module numbers (comma-separated, or 'all' for all)",
            default="all"
        )

        if selected_str.lower() == "all":
            return modules_list

        try:
            selected_indices = [int(x.strip()) - 1 for x in selected_str.split(",")]
            selected = []
            for i in selected_indices:
                if 0 <= i < len(modules_list):
                    selected.append(modules_list[i])
            return selected
        except:
            self.console.print("[red]Invalid input[/]")
            return []

    # ============ DEVICE INFO METHODS ============

    def get_device_info(self):
        try:
            info = "📱 DEVICE INFORMATION\n"
            info += "━" * 60 + "\n"

            # Get all properties
            props = {}
            result = subprocess.getoutput("getprop 2>/dev/null")
            for line in result.split('\n'):
                if '[' in line and ']' in line:
                    parts = line.strip().split(']: [')
                    if len(parts) == 2:
                        key = parts[0].strip('[')
                        value = parts[1].strip(']')
                        props[key] = value

            # Important properties
            important = [
                ("Device", "ro.product.device"),
                ("Model", "ro.product.model"),
                ("Brand", "ro.product.brand"),
                ("Manufacturer", "ro.product.manufacturer"),
                ("Board", "ro.product.board"),
                ("Hardware", "ro.hardware"),
                ("Platform", "ro.board.platform"),
                ("CPU ABI", "ro.product.cpu.abi"),
                ("Density", "ro.sf.lcd_density"),
            ]

            for name, key in important:
                value = props.get(key, "N/A")
                info += f"{name}: {value}\n"

            # Additional info
            info += f"\n📊 Additional Info:\n"
            info += f"  • Screen Size: {props.get('ro.product.display.resolution', 'N/A')}\n"
            info += f"  • RAM: {props.get('ro.product.ram', 'N/A')}\n"
            info += f"  • Storage: {props.get('ro.product.storage', 'N/A')}\n"

            return info
        except Exception as e:
            return f"⚠️ Error: {str(e)}\n\n💡 Try: This module requires proper permissions."

    def get_android_version(self):
        try:
            info = "📱 ANDROID VERSION\n"
            info += "━" * 60 + "\n"

            props = {}
            result = subprocess.getoutput("getprop 2>/dev/null")
            for line in result.split('\n'):
                if '[' in line and ']' in line:
                    parts = line.strip().split(']: [')
                    if len(parts) == 2:
                        key = parts[0].strip('[')
                        value = parts[1].strip(']')
                        props[key] = value

            versions = [
                ("Release Version", "ro.build.version.release"),
                ("SDK Level", "ro.build.version.sdk"),
                ("Security Patch", "ro.build.version.security_patch"),
                ("Build ID", "ro.build.id"),
                ("Build Date", "ro.build.date"),
                ("Build Type", "ro.build.type"),
                ("Build Tags", "ro.build.tags"),
                ("Build Fingerprint", "ro.build.fingerprint"),
                ("Incremental", "ro.build.version.incremental"),
                ("Codename", "ro.build.version.codename"),
            ]

            for name, key in versions:
                value = props.get(key, "N/A")
                info += f"{name}: {value}\n"

            return info
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    def get_device_ids(self):
        try:
            info = "🔑 DEVICE IDS\n"
            info += "━" * 60 + "\n"

            # Serial number
            serial = subprocess.getoutput("getprop ro.serialno 2>/dev/null")
            info += f"Serial Number: {serial if serial else 'N/A'}\n"

            # Android ID
            android_id = subprocess.getoutput("settings get secure android_id 2>/dev/null")
            info += f"Android ID: {android_id if android_id else 'N/A'}\n"

            # Google Service Framework ID (GSF)
            gsf = subprocess.getoutput("settings get secure gsf_android_id 2>/dev/null")
            info += f"GSF ID: {gsf if gsf else 'N/A'}\n"

            # IMEI (requires root)
            if self.has_root:
                imei1 = subprocess.getoutput('su -c "service call iphonesubinfo 4" 2>/dev/null | grep -o "[0-9]\\{15\\}"')
                imei2 = subprocess.getoutput('su -c "service call iphonesubinfo 5" 2>/dev/null | grep -o "[0-9]\\{15\\}"')
                info += f"IMEI 1: {imei1 if imei1 else 'N/A'}\n"
                info += f"IMEI 2: {imei2 if imei2 else 'N/A'}\n"

                # MEID (CDMA phones)
                meid = subprocess.getoutput('su -c "service call iphonesubinfo 6" 2>/dev/null | grep -o "[0-9]\\{14\\}"')
                info += f"MEID: {meid if meid else 'N/A'}\n"
            else:
                info += "\n⚠️ Root required to read IMEI/MEID\n"
                info += "💡 Use: su -c 'service call iphonesubinfo 4'\n"

            # Fingerprint
            fingerprint = subprocess.getoutput("getprop ro.build.fingerprint 2>/dev/null")
            info += f"\nFingerprint: {fingerprint if fingerprint else 'N/A'}\n"

            return info
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    def get_battery_status(self):
        try:
            info = "🔋 BATTERY STATUS\n"
            info += "━" * 60 + "\n"

            result = subprocess.getoutput("dumpsys battery 2>/dev/null")

            if not result or "No such file" in result:
                return " Battery info not available\n\n💡 Try: dumpsys battery (requires proper permissions)"

            lines = result.split('\n')
            battery_data = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    battery_data[key.strip()] = value.strip()

            # Display important info
            important = ["level", "scale", "temperature", "voltage", "status", "health", "present"]
            for key in important:
                if key in battery_data:
                    value = battery_data[key]
                    if key == "temperature":
                        value = f"{int(value) / 10:.1f}°C"
                    elif key == "voltage":
                        value = f"{int(value) / 1000:.2f}V"
                    elif key == "status":
                        status_map = {
                            "1": "Unknown", "2": "Charging", "3": "Discharging",
                            "4": "Not Charging", "5": "Full"
                        }
                        value = status_map.get(value, value)
                    elif key == "health":
                        health_map = {
                            "1": "Unknown", "2": "Good", "3": "Overheat",
                            "4": "Dead", "5": "Over Voltage", "6": "Unspecified Failure"
                        }
                        value = health_map.get(value, value)

                    info += f"{key.capitalize()}: {value}\n"

            # Battery percentage
            if "level" in battery_data and "scale" in battery_data:
                level = int(battery_data["level"])
                scale = int(battery_data["scale"])
                percentage = (level / scale) * 100
                info += f"\nBattery Percentage: {percentage:.1f}%\n"

                if percentage < 20:
                    info += "⚠️ WARNING: Low battery!\n"
                elif percentage > 80:
                    info += "✅ Battery is well charged\n"

            return info
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    def get_selinux_status(self):
        try:
            info = "🔒 SELINUX STATUS\n"
            info += "━" * 60 + "\n"

            status = subprocess.getoutput("getenforce 2>/dev/null")
            if not status:
                return "ℹSELinux status not available\n\n💡 This device may not support SELinux"

            info += f"Status: {status}\n"

            if status.lower() == "enforcing":
                info += "✅ SELinux is ENFORCING - System is secure\n"
                info += "   - All processes are restricted\n"
                info += "   - Denied actions are blocked\n"
            elif status.lower() == "permissive":
                info += "⚠️ SELinux is PERMISSIVE - Less secure\n"
                info += "   - Actions are only logged, not blocked\n"
                info += "   - Potential security risk\n"
            else:
                info += "⚠️ SELinux is DISABLED\n"
                info += "   - No security enforcement\n"
                info += "   - High security risk\n"

            # Get more info
            mode = subprocess.getoutput("getprop ro.boot.selinux 2>/dev/null")
            if mode:
                info += f"\nBoot Mode: {mode}\n"

            return info
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    def check_root_access(self):
        try:
            info = "🔑 ROOT ACCESS ANALYSIS\n"
            info += "━" * 60 + "\n"

            # Check SU binary
            su_paths = ["/system/bin/su", "/system/xbin/su", "/data/local/tmp/su", "/sbin/su"]
            found_su = False
            info += "🔍 Checking for SU binaries:\n"
            for path in su_paths:
                if os.path.exists(path):
                    info += f"  ✅ Found: {path}\n"
                    found_su = True
                else:
                    info += f"  ❌ Not found: {path}\n"

            # Check Magisk
            magisk = subprocess.getoutput("magisk -v 2>/dev/null")
            if magisk:
                info += f"\n✅ Magisk detected: {magisk}\n"

            # Check SuperSU
            supersu = subprocess.getoutput("which supersu 2>/dev/null")
            if supersu:
                info += f"\n✅ SuperSU detected: {supersu}\n"

            # Check KingRoot
            kingroot = subprocess.getoutput("which kingroot 2>/dev/null")
            if kingroot:
                info += f"\n✅ KingRoot detected: {kingroot}\n"

            # Check current UID
            uid = os.getuid()
            info += f"\n📊 Current UID: {uid}\n"

            if uid == 0:
                info += "✅ RUNNING AS ROOT (UID 0)\n"
                info += "   - Full system access available\n"
                info += "   - Can read all files\n"
            else:
                info += "❌ NOT RUNNING AS ROOT\n"
                info += f"   - Current UID: {uid}\n"
                info += "   - Limited access to system files\n"
                info += "   - Some modules may not work\n"
                info += "\n💡 To get root access:\n"
                info += "   - Use: su (if rooted)\n"
                info += "   - Or install Magisk/SuperSU\n"

            return info
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    # ============ APP ANALYSIS ============

    def get_installed_apps(self):
        try:
            info = "📦 INSTALLED APPS\n"
            info += "━" * 60 + "\n"

            # Get all packages
            result = subprocess.getoutput("pm list packages 2>/dev/null")

            if not result:
                return "❌ Could not enumerate packages\n\n💡 Permission denied. Try:\n   - Run with root: su\n   - Check: pm list packages"

            packages = []
            for line in result.split('\n'):
                if line.startswith("package:"):
                    packages.append(line.replace("package:", ""))

            info += f"📊 Total Apps: {len(packages)}\n\n"

            # Get first 30 apps with details
            info += "📋 First 30 Apps:\n"
            for app in packages[:30]:
                # Try to get app name
                app_name = subprocess.getoutput(f"dumpsys package {app} 2>/dev/null | grep 'applicationInfo' | head -1")
                if app_name:
                    app_name = app_name.split('name=')[-1].strip() if 'name=' in app_name else app
                else:
                    app_name = app.split('.')[-1]

                info += f"  • {app_name[:30]} ({app[:30]})\n"

            if len(packages) > 30:
                info += f"\n... and {len(packages) - 30} more apps\n"

            # Count system vs user apps
            system_apps = [p for p in packages if p.startswith(("android", "com.android"))]
            info += f"\n📊 System Apps: {len(system_apps)}\n"
            info += f"📊 User Apps: {len(packages) - len(system_apps)}\n"

            return info
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    def get_app_permissions(self):
        try:
            info = "🔐 APP PERMISSIONS\n"
            info += "━" * 60 + "\n"

            # Get running apps
            result = subprocess.getoutput("dumpsys package 2>/dev/null | grep -A 10 'permissions:' | head -50")

            if not result:
                return "ℹ Permission info not available\n\n💡 Try:\n   - Run with root: su\n   - dumpsys package permissions"

            # Parse permissions
            permissions = []
            current_app = ""
            for line in result.split('\n'):
                if "Package" in line and "[" in line:
                    current_app = line.split('[')[-1].split(']')[0] if '[' in line else "Unknown"
                elif "permission" in line and ":" in line:
                    perm = line.split(':')[-1].strip() if ':' in line else line.strip()
                    if perm and perm not in permissions:
                        permissions.append(perm)

            if permissions:
                info += f"📊 Found {len(permissions)} unique permissions\n\n"
                info += "📋 Permission List:\n"
                for perm in permissions[:20]:
                    info += f"  • {perm}\n"
                if len(permissions) > 20:
                    info += f"\n... and {len(permissions) - 20} more permissions\n"
            else:
                info += "✅ No permissions found or access denied\n"

            return info
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    def get_running_services(self):
        try:
            info = "🔄 RUNNING SERVICES\n"
            info += "━" * 60 + "\n"

            # Get processes with different methods
            methods = [
                ("ps aux", "ps aux 2>/dev/null | head -40"),
                ("ps -ef", "ps -ef 2>/dev/null | head -40"),
                ("top -n 1", "top -n 1 -b 2>/dev/null | head -20")
            ]

            output = ""
            for name, cmd in methods:
                result = subprocess.getoutput(cmd)
                if result and "No such" not in result:
                    output = result
                    break

            if not output:
                return "ℹ No process data available\n\n💡 Try: ps aux (requires proper permissions)"

            info += output

            # Process count
            count = len([l for l in output.split('\n') if l.strip()])
            info += f"\n\n📊 Total processes shown: {count}"

            return info
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    def get_intent_history(self):
        try:
            info = "🎯 INTENT HISTORY\n"
            info += "━" * 60 + "\n"

            result = subprocess.getoutput("dumpsys package m 2>/dev/null | grep -E '(intent|action)' | head -30")

            if not result:
                return "ℹ Intent history not accessible\n\n💡 Try:\n   - Run with root: su\n   - dumpsys package m"

            intents = []
            for line in result.split('\n'):
                if "intent" in line.lower():
                    intents.append(line.strip())

            if intents:
                info += f"📊 Found {len(intents)} intents\n\n"
                for intent in intents[:20]:
                    info += f"  • {intent[:80]}\n"
            else:
                info += "✅ No intents found\n"

            return info
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    # ============ USER DATA ============

    def get_contacts(self):
        try:
            info = "👤 CONTACTS\n"
            info += "━" * 60 + "\n"

            # Try different content providers
            providers = [
                "content://contacts/phones",
                "content://contacts/people",
                "content://com.android.contacts/contacts"
            ]

            contacts = []
            for provider in providers:
                result = subprocess.getoutput(f"content query --uri {provider} 2>/dev/null")
                if result and "No result" not in result:
                    for line in result.split('\n'):
                        if "name=" in line or "display_name=" in line:
                            name = "Unknown"
                            number = "Unknown"

                            if "display_name=" in line:
                                name = self.extract_value(line, "display_name")
                            elif "name=" in line:
                                name = self.extract_value(line, "name")

                            if "number=" in line:
                                number = self.extract_value(line, "number")
                            elif "data1=" in line:
                                number = self.extract_value(line, "data1")

                            if name and number:
                                contacts.append(f"  • {name}: {number}")
                    break

            if contacts:
                info += f"📊 Found {len(contacts)} contacts\n\n"
                for contact in contacts[:50]:
                    info += f"{contact}\n"
                if len(contacts) > 50:
                    info += f"\n... and {len(contacts) - 50} more contacts\n"
            else:
                info += "❌ No contacts found or permission denied\n\n💡 To grant permission:\n"
                info += "   - Settings → Apps → Termux → Permissions\n"
                info += "   - Enable Contacts permission\n"
                info += "   - Or run with root: su\n"

            return info
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    def get_sms(self):
        try:
            info = "💬 SMS MESSAGES\n"
            info += "━" * 60 + "\n"

            result = subprocess.getoutput("content query --uri content://sms 2>/dev/null")

            if not result or "No result" in result:
                return "❌ No SMS found or permission denied\n\n💡 To grant permission:\n   - Settings → Apps → Termux → Permissions\n   - Enable SMS permission\n   - Or run with root: su"

            messages = []
            for line in result.split('\n'):
                if "address=" in line:
                    from_num = self.extract_value(line, "address")
                    body = self.extract_value(line, "body")
                    date = self.extract_value(line, "date")

                    if from_num and body:
                        messages.append({
                            "from": from_num,
                            "body": body[:50],
                            "date": date
                        })

            if messages:
                info += f"📊 Found {len(messages)} messages\n\n"
                for msg in messages[:20]:
                    info += f"  • From: {msg['from']}\n"
                    info += f"    Body: {msg['body']}...\n"
                    info += f"    Date: {msg['date']}\n\n"
                if len(messages) > 20:
                    info += f"\n... and {len(messages) - 20} more messages\n"
            else:
                info += "✅ No SMS messages found\n"

            return info
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    def get_call_logs(self):
        try:
            info = "📞 CALL LOGS\n"
            info += "━" * 60 + "\n"

            result = subprocess.getoutput("content query --uri content://call_log/calls 2>/dev/null")

            if not result or "No result" in result:
                return "❌ No call logs found or permission denied\n\n💡 To grant permission:\n   - Settings → Apps → Termux → Permissions\n   - Enable Phone permission\n   - Or run with root: su"

            calls = []
            for line in result.split('\n'):
                if "number=" in line:
                    number = self.extract_value(line, "number")
                    call_type = self.extract_value(line, "type")
                    duration = self.extract_value(line, "duration")
                    date = self.extract_value(line, "date")

                    type_map = {"1": "Incoming", "2": "Outgoing", "3": "Missed"}
                    call_type = type_map.get(call_type, call_type)

                    if number:
                        calls.append({
                            "number": number,
                            "type": call_type,
                            "duration": duration,
                            "date": date
                        })

            if calls:
                info += f"📊 Found {len(calls)} call logs\n\n"
                for call in calls[:30]:
                    info += f"  • {call['number']} - {call['type']} - {call['duration']}s\n"
                    info += f"    Date: {call['date']}\n\n"
                if len(calls) > 30:
                    info += f"\n... and {len(calls) - 30} more calls\n"
            else:
                info += "✅ No call logs found\n"

            return info
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    def get_accounts(self):
        try:
            info = "🔐 ACCOUNT INFO\n"
            info += "━" * 60 + "\n"

            result = subprocess.getoutput("dumpsys account 2>/dev/null")

            if not result:
                return "ℹ No accounts found or permission denied\n\n💡 Try:\n   - Run with root: su\n   - dumpsys account"

            accounts = []
            for line in result.split('\n'):
                if "name=" in line:
                    name = self.extract_value(line, "name")
                    acc_type = self.extract_value(line, "type")
                    if name and acc_type:
                        accounts.append(f"{name} ({acc_type})")

            if accounts:
                info += f"📊 Found {len(accounts)} accounts\n\n"
                for account in accounts[:20]:
                    info += f"  • {account}\n"
            else:
                info += "✅ No accounts found\n"

            return info
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    # ============ SOCIAL MEDIA ============

    def get_whatsapp_data(self):
        try:
            info = "💬 WHATSAPP DATA\n"
            info += "━" * 60 + "\n"

            paths = [
                ("/sdcard/Android/media/com.whatsapp", "WhatsApp Media"),
                ("/data/data/com.whatsapp", "WhatsApp Data"),
                ("/sdcard/WhatsApp", "WhatsApp Storage"),
                ("/storage/emulated/0/Android/media/com.whatsapp", "WhatsApp Media (Alt)")
            ]

            found = False
            for path, label in paths:
                if os.path.exists(path):
                    info += f"✅ Found: {label}\n"
                    info += f"   📁 Path: {path}\n"
                    found = True

                    # Check subdirectories
                    try:
                        # Database
                        db_path = Path(path) / "databases"
                        if db_path.exists():
                            db_files = list(db_path.glob("*.db"))
                            info += f"   📊 Databases: {len(db_files)} files\n"

                        # Media
                        media_path = Path(path) / "media"
                        if media_path.exists():
                            media_count = sum(1 for _ in media_path.rglob("*") if _.is_file())
                            info += f"   📸 Media files: {media_count}\n"

                        # Backups
                        backup_path = Path(path) / "backups"
                        if backup_path.exists():
                            backup_count = len(list(backup_path.glob("*")))
                            info += f"   💾 Backups: {backup_count} files\n"
                    except:
                        pass

                    info += "\n"

            if not found:
                info += "❌ WhatsApp not found or not installed\n\n"
                info += "💡 WhatsApp data locations:\n"
                info += "   • /sdcard/Android/media/com.whatsapp\n"
                info += "   • /data/data/com.whatsapp (requires root)\n"
                info += "   • /sdcard/WhatsApp\n"

            return info
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    def get_telegram_data(self):
        try:
            info = "✈️ TELEGRAM DATA\n"
            info += "━" * 60 + "\n"

            paths = [
                ("/sdcard/Android/media/org.telegram.messenger", "Telegram Media"),
                ("/data/data/org.telegram.messenger", "Telegram Data"),
                ("/storage/emulated/0/Android/media/org.telegram.messenger", "Telegram Media (Alt)")
            ]

            found = False
            for path, label in paths:
                if os.path.exists(path):
                    info += f"✅ Found: {label}\n"
                    info += f"   📁 Path: {path}\n"
                    found = True

                    try:
                        # Cache
                        cache_path = Path(path) / "cache"
                        if cache_path.exists():
                            cache_count = sum(1 for _ in cache_path.rglob("*") if _.is_file())
                            info += f"   💾 Cache files: {cache_count}\n"

                        # Files
                        files_path = Path(path) / "files"
                        if files_path.exists():
                            file_count = sum(1 for _ in files_path.rglob("*") if _.is_file())
                            info += f"   📁 Files: {file_count}\n"
                    except:
                        pass

                    info += "\n"

            if not found:
                info += "❌ Telegram not found or not installed\n\n"
                info += "💡 Telegram data locations:\n"
                info += "   • /sdcard/Android/media/org.telegram.messenger\n"
                info += "   • /data/data/org.telegram.messenger (requires root)\n"

            return info
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    def get_browser_history(self):
        try:
            info = "🌐 BROWSER HISTORY\n"
            info += "━" * 60 + "\n"

            found = False

            # Chrome
            chrome_paths = [
                "/data/data/com.android.chrome/app_chrome/Default/History",
                "/data/data/com.chrome.beta/app_chrome/Default/History"
            ]

            for path in chrome_paths:
                if os.path.exists(path):
                    info += f"✅ Chrome history found: {path}\n"
                    found = True

                    try:
                        conn = sqlite3.connect(path)
                        cursor = conn.cursor()
                        cursor.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 10")
                        history = cursor.fetchall()
                        conn.close()

                        if history:
                            info += "\n📋 Recent URLs:\n"
                            for url, title, time in history:
                                info += f"  • {title[:30] if title else 'No Title'}\n"
                                info += f"    URL: {url[:60]}...\n"
                                info += f"    Time: {time}\n\n"
                    except:
                        info += "   ⚠️ Could not read database (permission denied)\n"
                        info += "   💡 Run with root: su\n"

            # Firefox
            firefox_path = "/data/data/org.mozilla.firefox/files/mozilla"
            if os.path.exists(firefox_path):
                for profile in Path(firefox_path).glob("*/places.sqlite"):
                    if profile.exists():
                        info += f"\n✅ Firefox history found: {profile}\n"
                        found = True
                        try:
                            conn = sqlite3.connect(str(profile))
                            cursor = conn.cursor()
                            cursor.execute("SELECT url, title, last_visit_date FROM moz_places ORDER BY last_visit_date DESC LIMIT 10")
                            history = cursor.fetchall()
                            conn.close()

                            if history:
                                info += "\n📋 Recent URLs:\n"
                                for url, title, time in history:
                                    info += f"  • {title[:30] if title else 'No Title'}\n"
                                    info += f"    URL: {url[:60]}...\n\n"
                        except:
                            info += "   ⚠️ Could not read database (permission denied)\n"

            if not found:
                info += "❌ No browser history found\n\n"
                info += "💡 Browser data locations:\n"
                info += "   • Chrome: /data/data/com.android.chrome/\n"
                info += "   • Firefox: /data/data/org.mozilla.firefox/\n"
                info += "   • Brave: /data/data/com.brave.browser/\n"
                info += "   💡 Requires root access to read\n"

            return info
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    # ============ SECURITY ============

    def get_wifi_passwords(self):
        try:
            info = "🔑 WIFI PASSWORDS\n"
            info += "━" * 60 + "\n"

            if not self.has_root:
                return "❌ Root required to extract WiFi passwords\n\n💡 To get WiFi passwords:\n   1. Root your device\n   2. Run: su\n   3. cat /data/misc/wifi/wpa_supplicant.conf\n\n 💡 Alternative:\n   • Use termux-wifi-connectioninfo (if installed)"

            result = subprocess.getoutput("su -c 'cat /data/misc/wifi/wpa_supplicant.conf' 2>/dev/null")

            if not result:
                return "❌ Could not read WiFi config\n\n💡 Try:\n   • Check if WiFi is enabled\n   • Verify root access\n   • File location: /data/misc/wifi/wpa_supplicant.conf"

            networks = []
            current = {}

            for line in result.split('\n'):
                line = line.strip()
                if line.startswith('network='):
                    current = {}
                elif 'ssid=' in line:
                    current['ssid'] = line.split('=')[1].strip('"')
                elif 'psk=' in line:
                    current['password'] = line.split('=')[1].strip('"')
                elif '}' in line and current:
                    if 'ssid' in current and 'password' in current:
                        networks.append(current)
                    current = {}

            if networks:
                info += f"📊 Found {len(networks)} saved WiFi networks\n\n"
                for net in networks[:10]:
                    info += f"  • SSID: {net.get('ssid', 'Unknown')}\n"
                    info += f"    Password: {net.get('password', 'Unknown')}\n\n"
            else:
                info += "✅ No saved WiFi networks found\n"
                info += "💡 Make sure WiFi was connected before\n"

            return info
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    def scan_suspicious_files(self):
        try:
            info = "🔍 SUSPICIOUS FILES\n"
            info += "━" * 60 + "\n"

            suspicious_exts = [".apk", ".dex", ".jar", ".so", ".tmp", ".cache", ".log"]
            suspicious_paths = [
                "/data/local/tmp",
                "/sdcard/Download",
                "/sdcard/Android/data",
                os.path.expanduser("~/.ssh"),
                "/sdcard/DCIM/.thumbnails"
            ]

            found_files = []
            for path in suspicious_paths:
                if os.path.exists(path):
                    try:
                        for root, dirs, files in os.walk(path):
                            for file in files[:10]:
                                file_path = os.path.join(root, file)
                                ext = os.path.splitext(file)[1].lower()
                                if ext in suspicious_exts:
                                    found_files.append({
                                        "path": file_path,
                                        "ext": ext,
                                        "size": os.path.getsize(file_path) if os.path.exists(file_path) else 0
                                    })
                    except:
                        pass

            if found_files:
                info += f"📊 Found {len(found_files)} suspicious files\n\n"
                for f in found_files[:20]:
                    info += f"  • {f['ext']} {f['path']}\n"
                    info += f"    Size: {f['size']} bytes\n"
                if len(found_files) > 20:
                    info += f"\n... and {len(found_files) - 20} more files\n"
            else:
                info += "✅ No suspicious files detected\n"
                info += "💡 Checked paths:\n"
                for path in suspicious_paths:
                    info += f"   • {path}\n"

            return info
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    def ransomware_scanner(self):
        try:
            info = "🛡️ RANSOMWARE SCAN\n"
            info += "━" * 60 + "\n"

            ransomware_exts = [
                ".crypt", ".locked", ".wanacry", ".locky", ".enc",
                ".crypted", ".zips", ".cryeye", ".encrypted",
                ".bitcoin", ".pay", ".ransom", ".restore"
            ]

            scan_paths = [
                os.path.expanduser("~"),
                "/sdcard",
                "/data/media",
                "/sdcard/Download",
                "/sdcard/DCIM",
                "/sdcard/Pictures"
            ]

            found = []
            for ext in ransomware_exts:
                for path in scan_paths:
                    if os.path.exists(path):
                        try:
                            cmd = f"find {path} -name '*{ext}' 2>/dev/null | head -5"
                            res = subprocess.getoutput(cmd)
                            if res.strip():
                                for line in res.split('\n'):
                                    if line.strip():
                                        found.append(f"[{ext}] {line}")
                        except:
                            pass

            if found:
                info += f"⚠️ RANSOMWARE INDICATORS FOUND! ({len(found)} files)\n\n"
                for item in found[:20]:
                    info += f"  • {item}\n"
                if len(found) > 20:
                    info += f"\n... and {len(found) - 20} more files\n"
                info += "\n⚠️ WARNING: These files may be encrypted by ransomware!\n"
                info += "   • Do NOT delete or modify\n"
                info += "   • Contact security team immediately\n"
            else:
                info += "✅ CLEAN - No ransomware signatures detected\n"
                info += "💡 Scanned directories:\n"
                for path in scan_paths:
                    info += f"   • {path}\n"

            return info
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    # ============ FILE SYSTEM ============

    def get_recent_files(self):
        try:
            info = "📁 RECENT FILES (Last 7 days)\n"
            info += "━" * 60 + "\n"

            home = os.path.expanduser("~")
            cmd = f"find {home} -type f -mtime -7 2>/dev/null | head -25"
            output = subprocess.getoutput(cmd)

            if output:
                files = [f for f in output.split('\n') if f.strip()]
                info += f"📊 Found {len(files)} recent files\n\n"
                for file in files[:20]:
                    if os.path.exists(file):
                        size = os.path.getsize(file)
                        info += f"  • {os.path.basename(file)}\n"
                        info += f"    Path: {file[:80]}...\n"
                        info += f"    Size: {size} bytes\n\n"
            else:
                info += "✅ No recent files found\n"
                info += "💡 Checked: ~/ (home directory)\n"
                info += "   Only files modified in last 7 days\n"

            return info
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    def get_modified_files(self):
        try:
            info = "📝 MODIFIED FILES\n"
            info += "━" * 60 + "\n"

            home = os.path.expanduser("~")
            cmd = f"find {home} -type f -printf '%T@ %p\\n' 2>/dev/null | sort -rn | head -20"
            output = subprocess.getoutput(cmd)

            if output:
                files = [f for f in output.split('\n') if f.strip()]
                info += f"📊 Found {len(files)} modified files\n\n"
                for file in files[:20]:
                    parts = file.split(' ', 1)
                    if len(parts) == 2:
                        timestamp, path = parts
                        try:
                            date = datetime.fromtimestamp(float(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
                            size = os.path.getsize(path) if os.path.exists(path) else 0
                            info += f"  • {os.path.basename(path)}\n"
                            info += f"    Date: {date}\n"
                            info += f"    Size: {size} bytes\n"
                            info += f"    Path: {path[:80]}...\n\n"
                        except:
                            pass
            else:
                info += "✅ No modified files found\n"

            return info
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    def get_deleted_files(self):
        try:
            info = "🗑️ DELETED FILES\n"
            info += "━" * 60 + "\n"

            deleted_paths = [
                "/sdcard/.trash",
                "/sdcard/LOST.DIR",
                "/data/local/tmp",
                "/sdcard/Android/.trash",
                "/storage/emulated/0/.trash"
            ]

            found_files = []
            for path in deleted_paths:
                if os.path.exists(path):
                    try:
                        for file in Path(path).glob("*"):
                            if file.is_file():
                                size = file.stat().st_size if file.exists() else 0
                                found_files.append({
                                    "name": file.name,
                                    "path": str(file),
                                    "size": size
                                })
                    except:
                        pass

            if found_files:
                info += f"📊 Found {len(found_files)} deleted/recovered files\n\n"
                for f in found_files[:20]:
                    info += f"  • {f['name']}\n"
                    info += f"    Path: {f['path'][:80]}...\n"
                    info += f"    Size: {f['size']} bytes\n\n"
                if len(found_files) > 20:
                    info += f"\n... and {len(found_files) - 20} more files\n"
            else:
                info += "✅ No deleted files found\n"
                info += "💡 Checked paths:\n"
                for path in deleted_paths:
                    info += f"   • {path}\n"

            return info
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    def get_system_logs(self):
        try:
            info = "📋 SYSTEM LOGS\n"
            info += "━" * 60 + "\n"

            # Try multiple methods
            methods = [
                ("logcat -d", "logcat -d 2>/dev/null | head -40"),
                ("dmesg", "dmesg 2>/dev/null | head -30"),
                ("lastlog", "lastlog 2>/dev/null | head -20")
            ]

            found = False
            for name, cmd in methods:
                result = subprocess.getoutput(cmd)
                if result and "No such" not in result:
                    info += f"📊 Log Source: {name}\n"
                    info += "━" * 60 + "\n"
                    info += result
                    found = True
                    break

            if not found:
                info += "❌ No system logs available\n\n"
                info += "💡 Try:\n"
                info += "   • Run with root: su\n"
                info += "   • Install logcat: pkg install termux-api\n"
                info += "   • Or check: /var/log/\n"

            return info
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    # ============ NETWORK ============

    def get_active_connections(self):
        try:
            info = "🔌 ACTIVE CONNECTIONS\n"
            info += "━" * 60 + "\n"

            methods = [
                "netstat -an 2>/dev/null | grep -E '(ESTABLISHED|LISTEN|TIME_WAIT)' | head -20",
                "ss -an 2>/dev/null | grep -E '(ESTAB|LISTEN|TIME-WAIT)' | head -20"
            ]

            output = ""
            for cmd in methods:
                result = subprocess.getoutput(cmd)
                if result and "No such" not in result:
                    output = result
                    break

            if output:
                connections = [l for l in output.split('\n') if l.strip()]
                info += f"📊 Found {len(connections)} active connections\n\n"
                info += output
            else:
                info += "✅ No active connections found\n"
                info += "💡 Try:\n"
                info += "   • netstat -an\n"
                info += "   • ss -an\n"
                info += "   • Or run with root: su\n"

            return info
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    def get_geo_intelligence(self):
        try:
            info = "🌐 GEOLOCATION\n"
            info += "━" * 60 + "\n"

            # Get IPs from connections
            cmd = "netstat -an 2>/dev/null | grep ESTAB | awk '{print $5}' | cut -d: -f1 | sort -u"
            ips_raw = subprocess.getoutput(cmd).split('\n')

            # Filter external IPs
            ips = []
            for ip in ips_raw:
                if ip and not ip.startswith(('127.', '192.', '10.', '172.', '::', 'fe80', 'fc00')):
                    ips.append(ip)

            if not ips:
                return "✅ No external connections found\n\n💡 Check:\n   • Active internet connection\n   • External IPs only (not private/local)"

            info += f"📊 Found {len(ips)} external IP(s)\n\n"
            info += f"{'IP Address':<20} {'Country':<15} {'City':<20} {'ISP':<25}\n"
            info += "━" * 80 + "\n"

            for ip in ips[:15]:
                try:
                    r = requests.get(
                        f"http://ip-api.com/json/{ip}?fields=status,country,city,isp",
                        timeout=5
                    ).json()

                    if r.get('status') == 'success':
                        country = r.get('country', 'Unknown')
                        city = r.get('city', 'Unknown')
                        isp = r.get('isp', 'Unknown')[:22]
                        info += f"{ip:<20} {country:<15} {city:<20} {isp:<25}\n"
                    else:
                        info += f"{ip:<20} {'Private':<15} {'Reserved':<20} {'N/A':<25}\n"
                except Exception as e:
                    info += f"{ip:<20} {'API Error':<15} {'Retry Later':<20} {'N/A':<25}\n"

            return info
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    def get_dns_cache(self):
        try:
            info = "📋 DNS CACHE\n"
            info += "━" * 60 + "\n"

            # Get DNS servers
            methods = [
                ("getprop net.dns1", "getprop net.dns1 2>/dev/null"),
                ("getprop net.dns2", "getprop net.dns2 2>/dev/null"),
                ("cat /etc/resolv.conf", "cat /etc/resolv.conf 2>/dev/null")
            ]

            found = False
            for name, cmd in methods:
                result = subprocess.getoutput(cmd)
                if result and "No such" not in result:
                    info += f"📊 {name}:\n"
                    info += f"   {result}\n"
                    found = True

            if not found:
                info += "✅ No DNS configuration found\n"
                info += "💡 Check:\n"
                info += "   • /etc/resolv.conf\n"
                info += "   • getprop net.dns1\n"

            # Try to get DNS cache from different sources
            try:
                result = subprocess.getoutput("dumpsys connectivity 2>/dev/null | grep -A 10 'DNS' | head -20")
                if result:
                    info += f"\n📊 DNS Cache (dumpsys):\n"
                    info += f"   {result[:200]}...\n"
            except:
                pass

            return info
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    # ============ HELPER METHODS ============

    def extract_value(self, line, key):
        try:
            pattern = f"{key}=([^,)]+)"
            match = re.search(pattern, line)
            if match:
                return match.group(1).strip()
        except:
            pass
        return "Unknown"

    def run_command(self, title, cmd):
        if callable(cmd):
            return cmd()
        try:
            output = subprocess.check_output(
                cmd, shell=True, stderr=subprocess.STDOUT, timeout=15
            ).decode()
            return output.strip() if output.strip() else "✓ No data found"
        except subprocess.TimeoutExpired:
            return "⏱️ Command timeout"
        except Exception as e:
            return f"⚠️ Error: {str(e)[:100]}"

    def start_scan(self, modules_to_run):
        if not modules_to_run:
            self.console.print("[red]No modules selected[/]")
            return

        self.scan_results = {}
        total = len(modules_to_run)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        ) as progress:
            task = progress.add_task("[cyan]🔍 Scanning...", total=total)

            for idx, (title, cmd) in enumerate(modules_to_run):
                progress.update(task, description=f"[cyan]🔍 {title}")
                self.scan_results[title] = self.run_command(title, cmd)
                progress.advance(task)

        self.console.print("\n[green bold]✅ Scan completed successfully![/]\n")
        self.show_scan_summary()

    def show_scan_summary(self):
        table = Table(title="📊 Scan Summary", box=box.HEAVY_EDGE)
        table.add_column("Module", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Size", style="yellow")

        for module, result in self.scan_results.items():
            size = f"{len(result)} chars"
            table.add_row(module[:40], "✓ Scanned", size)

        self.console.print(table)

    def view_results(self):
        if not self.scan_results:
            self.console.print("[red]No scan results available[/]")
            return

        while True:
            modules_list = list(self.scan_results.keys())

            self.console.print("\n[cyan bold]▸ SELECT RESULT TO VIEW[/]\n")

            table = Table(title="Available Results", box=box.HEAVY_EDGE)
            table.add_column("ID", style="cyan", width=5)
            table.add_column("Module", style="green")
            table.add_column("Size", style="yellow")

            for idx, name in enumerate(modules_list, 1):
                size = len(self.scan_results[name])
                table.add_row(str(idx), name[:40], f"{size} bytes")

            self.console.print(table)

            choice = Prompt.ask("Enter module number (0 to go back)", default="0")

            if choice == "0":
                break

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(modules_list):
                    module_name = modules_list[idx]
                    result = self.scan_results[module_name]

                    self.console.print(f"\n[cyan bold]▸ {module_name}[/]\n")
                    self.console.print(Panel(result, border_style="green", expand=False))
            except:
                self.console.print("[red]Invalid input[/]")

    def show_case_statistics(self):
        if not self.scan_results:
            self.console.print("[red]No data available[/]")
            return

        stats = Table(title="📈 Case Statistics", box=box.HEAVY_EDGE)
        stats.add_column("Metric", style="cyan")
        stats.add_column("Value", style="green")

        total_size = sum(len(v) for v in self.scan_results.values())
        stats.add_row("Total Modules", str(len(self.scan_results)))
        stats.add_row("Total Data", f"{total_size:,} bytes")
        stats.add_row("Case ID", self.case_name)
        stats.add_row("Timestamp", self.timestamp)

        self.console.print(stats)

    def export_html(self):
        if not self.scan_results:
            self.console.print("[red]No results to export[/]")
            return

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>GenesisBeast Mobile Forensics Report</title>
    <style>
        body {{ background: #0d1117; color: #c9d1d9; font-family: 'Courier New', monospace; padding: 20px; }}
        h1 {{ color: #58a6ff; text-align: center; border-bottom: 3px solid #238636; padding-bottom: 20px; }}
        .module {{ background: #010409; border: 2px solid #238636; padding: 15px; margin: 15px 0; border-radius: 8px; color: #39ff14; white-space: pre-wrap; }}
        .footer {{ text-align: center; margin-top: 50px; color: #8b949e; }}
        .meta {{ text-align: center; color: #8b949e; margin-bottom: 30px; }}
        .warning {{ background: #161b22; border-left: 4px solid #ff7b72; padding: 15px; margin: 20px 0; color: #f85149; }}
    </style>
</head>
<body>
    <h1>📱 MOBILE FORENSIC REPORT</h1>
    <div class="meta">
        Case: {self.case_name}<br>
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
        Developer: {self.developer} | GitHub: {self.github}
    </div>
    <div class="warning">
        ⚠️ CONFIDENTIAL: This report contains sensitive forensic data.
        Store securely and restrict access to authorized personnel only.
    </div>
"""

        for title, content in self.scan_results.items():
            safe_content = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            html += f"<h2>▸ {title}</h2>\n"
            html += f"<div class='module'>{safe_content}</div>\n"

        html += f"""
    <div class="footer">
        GenesisBeast v{self.version} - Mobile Forensic Suite<br>
        Developer: {self.developer} | GitHub: {self.github}<br>
        For authorized forensic analysis only.
    </div>
</body>
</html>
"""

        file_path = self.case_dir / f"Report_{self.timestamp}.html"
        with open(file_path, 'w') as f:
            f.write(html)

        self.console.print(f"[green]✅ HTML report exported: {file_path}[/]")

    def export_json(self):
        if not self.scan_results:
            return

        data = {
            "case": self.case_name,
            "timestamp": self.timestamp,
            "developer": self.developer,
            "github": self.github,
            "version": self.version,
            "platform": "Android (Termux)",
            "results": self.scan_results
        }

        file_path = self.case_dir / f"Report_{self.timestamp}.json"
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

        self.console.print(f"[green]✅ JSON report exported: {file_path}[/]")

    def export_txt(self):
        if not self.scan_results:
            return

        content = f"""
╔══════════════════════════════════════════════════════════════════╗
║   GENESIS BEAST v{self.version} - MOBILE FORENSIC REPORT         ║
║              Complete Android Forensics Analysis                 ║
╚══════════════════════════════════════════════════════════════════╝

Case ID: {self.case_name}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Developer: {self.developer}
GitHub: {self.github}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  CONFIDENTIAL: This report contains sensitive forensic data.
    Handle with care and store securely.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

        for title, result in self.scan_results.items():
            content += f"\n▸ {title}\n"
            content += "─" * 70 + "\n"
            content += result + "\n"
            content += "─" * 70 + "\n"

        file_path = self.case_dir / f"Report_{self.timestamp}.txt"
        with open(file_path, 'w') as f:
            f.write(content)

        self.console.print(f"[green]✅ Text report exported: {file_path}[/]")

    def show_export_menu(self):
        menu = """
        [cyan bold]▸ EXPORT OPTIONS[/]

        [green]1[/] Export as HTML
        [green]2[/] Export as JSON
        [green]3[/] Export as Text
        [green]4[/] Back to Main Menu
        """
        self.console.print(menu)
        choice = Prompt.ask("Select option", choices=["1", "2", "3", "4"])

        if choice == "1":
            self.export_html()
        elif choice == "2":
            self.export_json()
        elif choice == "3":
            self.export_txt()

    def show_about(self):
        about_text = f"""
╔═══════════════════════════════════════════════════════════════════╗
║           GENESISBEAST v{self.version} - MOBILE FORENSIC SUITE               ║
║           Complete Android Forensics Intelligence Tool            ║
╚═══════════════════════════════════════════════════════════════════╝

Developer: {self.developer}
GitHub: {self.github}
Platform: Android (Termux)
Type: Complete Mobile Forensic Toolkit

📋 FEATURES (27 Modules):
  • Device Information & IDs
  • App Analysis (Installed, Permissions)
  • User Data (Contacts, SMS, Call Logs)
  • Social Media (WhatsApp, Telegram)
  • Security Analysis (Root, WiFi, Ransomware)
  • File System Analysis
  • Network Intelligence

📱 REQUIREMENTS:
  • Termux (latest version)
  • Python 3.8+
  • rich, requests libraries

🔧 INSTALLATION:
  1. pkg update && pkg upgrade
  2. pkg install python
  3. pip install rich requests
  4. python mobile_forensics.py

⚠️  LEGAL NOTICE:
  This tool is for authorized forensic analysis only.
  Unauthorized system access is illegal.

═══════════════════════════════════════════════════════════════════
        """
        self.console.print(Panel(about_text, border_style="cyan", expand=False))

    def run(self):
        self.show_banner()

        while True:
            choice = self.show_main_menu()

            if choice == "1":
                modules = self.show_module_selection()
                if modules:
                    self.start_scan(modules)
                    input("\n[Press Enter to continue]")

            elif choice == "2":
                self.view_results()

            elif choice == "3":
                self.show_export_menu()
                input("\n[Press Enter to continue]")

            elif choice == "4":
                self.show_case_statistics()
                input("\n[Press Enter to continue]")

            elif choice == "5":
                self.show_about()
                input("\n[Press Enter to continue]")

            elif choice == "6":
                self.console.print("\n[yellow]👋 Exiting GenesisBeast...[/]\n")
                break

            self.console.clear()
            self.show_banner()


def main():
    try:
        tool = MobileForensics()
        tool.run()
    except KeyboardInterrupt:
        print("\n[yellow]⚠️ Process interrupted[/]")
        sys.exit(0)
    except Exception as e:
        print(f"[red]❌ Error: {str(e)}[/]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
