#!/usr/bin/env python3

import subprocess
import os
import threading
import time

# Define color codes
RESET = "\033[0m"
HEADER = "\033[96m"   # Light Cyan
TEXT = "\033[93m"     # Yellow
INFO = "\033[94m"     # Blue
SUCCESS = "\033[92m"  # Green
WARNING = "\033[93m"  # Yellow
ERROR = "\033[91m"    # Red
BOLD = "\033[1m"
UNDERLINE = "\033[4m"

BACKUP_FILE = "mac_backup.txt"
auto_change_thread = None
stop_auto_change = False

def clear_terminal():
    # Clear the terminal screen
    os.system('clear')  # Use 'cls' for Windows

def print_header():
    print(f"\n{HEADER}" + "=" * 50)
    print("           ╭━╮╭━╮╱╱╱╱╱╭━━━╮╱╱╱╱╭╮╱╭╮")
    print("           ┃┃╰╯┃┃╱╱╱╱╱╰╮╭╮┃╱╱╱╱┃┃╱┃┃")
    print("           ┃╭╮╭╮┣━━┳━━╮┃┃┃┣━━┳━╯┣━╯┣╮╱╭╮")
    print("           ┃┃┃┃┃┃╭╮┃╭━╯┃┃┃┃╭╮┃╭╮┃╭╮┃┃╱┃┃")
    print("           ┃┃┃┃┃┃╭╮┃╰━┳╯╰╯┃╭╮┃╰╯┃╰╯┃╰━╯┃")
    print("           ╰╯╰╯╰┻╯╰┻━━┻━━━┻╯╰┻━━┻━━┻━╮╭╯")
    print("           ╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╭━╯┃")
    print("           ╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╰━━╯")
    print("=" * 50 + RESET + "\n")

def change_mac_address():
    while True:
        interface = input("Enter the interface name: ")

        # Check if the interface exists
        if interface not in get_interfaces():
            print(f"{ERROR}Invalid interface name. Please try again.{RESET}")
            continue
        
        try:
            # Bring the interface down
            subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'down'], check=True)
            
            # Change the MAC address
            result = subprocess.run(['sudo', 'macchanger', '-r', interface], stdout=subprocess.PIPE, text=True)
            print(f"{SUCCESS}{result.stdout}{RESET}")
            
            # Bring the interface up
            subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'up'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"{ERROR}[ERROR] {e}{RESET}")

        # Ask if the user wants to try another interface or return to the menu
        choice = input("Do you want to try another interface? (y/n): ").strip().lower()
        if choice == 'n':
            break

def reset_mac_address():
    while True:
        interface = input("Enter the interface name: ")

        # Check if the interface exists
        if interface not in get_interfaces():
            print(f"{ERROR}Invalid interface name. Please try again.{RESET}")
            continue
        
        try:
            # Bring the interface down
            subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'down'], check=True)
            
            # Reset the MAC address
            result = subprocess.run(['sudo', 'macchanger', '-p', interface], stdout=subprocess.PIPE, text=True)
            print(f"{SUCCESS}{result.stdout}{RESET}")
            
            # Bring the interface up
            subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'up'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"{ERROR}[ERROR] {e}{RESET}")

        # Ask if the user wants to try another interface or return to the menu
        choice = input("Do you want to try another interface? (y/n): ").strip().lower()
        if choice == 'n':
            break

def show_interfaces():
    result = subprocess.run(['ip', 'link', 'show'], stdout=subprocess.PIPE, text=True)
    lines = result.stdout.splitlines()
    interfaces = []

    for i in range(0, len(lines), 2):
        interface_info = lines[i].split(': ')
        if len(interface_info) > 1:
            interface_name = interface_info[1].split('@')[0].strip()
            mac_address = lines[i + 1].split()[1].strip()
            interfaces.append((interface_name, mac_address))

    if not interfaces:
        print(f"{WARNING}No interfaces found.{RESET}")
        return

    # Print header
    print(f"{INFO}\nAvailable Interfaces:{RESET}")
    print("                       ")
    print("{:<20} {:<20}".format("Interface", "MAC Address"))
    print(f"{HEADER}-" * 40)

    for interface, mac_address in interfaces:
        print("{:<20} {:<20}".format(interface, mac_address))
        print(f"{HEADER}-" * 40)

def show_mac_addresses():
    while True:
        interface = input("Enter the interface name: ")

        # Check if the interface exists
        if interface not in get_interfaces():
            print(f"{ERROR}Invalid interface name. Please try again.{RESET}")
            continue

        # Show MAC address information
        print(f"{INFO}Showing MAC address information for {interface}...{RESET}\n")
        
        try:
            result = subprocess.run(['macchanger', '-s', interface], stdout=subprocess.PIPE, text=True)
            if result.returncode != 0:
                print(f"{ERROR}[ERROR] Could not retrieve MAC addresses for {interface}: {result.stderr.strip()}{RESET}")
            else:
                print(f"{SUCCESS}{result.stdout}{RESET}")
            
            # Show additional information
            result = subprocess.run(['ip', 'addr', 'show', interface], stdout=subprocess.PIPE, text=True)
            if result.returncode == 0:
                print(f"{INFO}\nAdditional Interface Information:{RESET}")
                print("                                   ")
                print(f"{SUCCESS}{result.stdout}{RESET}")
            else:
                print(f"{ERROR}[ERROR] Could not retrieve additional information for {interface}: {result.stderr.strip()}{RESET}")
        
        except subprocess.CalledProcessError as e:
            print(f"{ERROR}[ERROR] {e}{RESET}")

        # Ask if the user wants to try another interface or return to the menu
        choice = input("Do you want to try another interface? (y/n): ").strip().lower()
        if choice == 'n':
            break

def change_all_mac_addresses():
    interfaces = get_interfaces()
    if not interfaces:
        print(f"{WARNING}No interfaces found.{RESET}")
        return
    for interface in interfaces:
        try:
            # Bring the interface down
            subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'down'], check=True)
            
            # Change the MAC address
            result = subprocess.run(['sudo', 'macchanger', '-r', interface], stdout=subprocess.PIPE, text=True)
            print(f"{SUCCESS}{result.stdout}{RESET}")
            
            # Bring the interface up
            subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'up'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"{ERROR}[ERROR] {e}{RESET}")

def reset_all_mac_addresses():
    interfaces = get_interfaces()
    if not interfaces:
        print(f"{WARNING}No interfaces found.{RESET}")
        return
    for interface in interfaces:
        try:
            # Bring the interface down
            subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'down'], check=True)
            
            # Reset the MAC address
            result = subprocess.run(['sudo', 'macchanger', '-p', interface], stdout=subprocess.PIPE, text=True)
            print(f"{SUCCESS}{result.stdout}{RESET}")
            
            # Bring the interface up
            subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'up'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"{ERROR}[ERROR] {e}{RESET}")

def get_interfaces():
    result = subprocess.run(['ip', 'link', 'show'], stdout=subprocess.PIPE, text=True)
    lines = result.stdout.splitlines()
    interfaces = [line.split(': ')[1].split('@')[0].strip() for line in lines if ': ' in line and not 'LOOPBACK' in line]
    return interfaces

def backup_mac_addresses():
    interfaces = get_interfaces()
    if not interfaces:
        print(f"{WARNING}No interfaces found to back up.{RESET}")
        return

    with open(BACKUP_FILE, 'w') as file:
        for interface in interfaces:
            result = subprocess.run(['ip', 'link', 'show', interface], stdout=subprocess.PIPE, text=True)
            lines = result.stdout.splitlines()
            mac_address = lines[1].split()[1].strip()
            file.write(f"{interface} {mac_address}\n")
    print(f"{SUCCESS}MAC addresses backed up to {BACKUP_FILE}.{RESET}")

def restore_mac_addresses():
    if not os.path.exists(BACKUP_FILE):
        print(f"{ERROR}Backup file not found.{RESET}")
        return

    with open(BACKUP_FILE, 'r') as file:
        for line in file:
            interface, mac_address = line.strip().split()
            try:
                subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'down'], check=True)
                subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'address', mac_address], check=True)
                subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'up'], check=True)
                print(f"{SUCCESS}MAC address for {interface} restored to {mac_address}.{RESET}")
            except subprocess.CalledProcessError as e:
                print(f"{ERROR}[ERROR] Could not restore MAC address for {interface}: {e}{RESET}")

def custom_mac_address():
    while True:
        interface = input("Enter the interface name: ")

        # Check if the interface exists
        if interface not in get_interfaces():
            print(f"{ERROR}Invalid interface name. Please try again.{RESET}")
            continue

        new_mac = input("Enter the new MAC address (format: XX:XX:XX:XX:XX:XX): ")
        try:
            # Bring the interface down
            subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'down'], check=True)
            
            # Change to the custom MAC address
            subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'address', new_mac], check=True)
            
            # Bring the interface up
            subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'up'], check=True)
            print(f"{SUCCESS}MAC address for {interface} changed to {new_mac}.{RESET}")
        except subprocess.CalledProcessError as e:
            print(f"{ERROR}[ERROR] {e}{RESET}")

        # Ask if the user wants to try another interface or return to the menu
        choice = input("Do you want to try another interface? (y/n): ").strip().lower()
        if choice == 'n':
            break

def check_interface_status():
    while True:
        interface = input("Enter the interface name: ")

        # Check if the interface exists
        if interface not in get_interfaces():
            print(f"{ERROR}Invalid interface name. Please try again.{RESET}")
            continue

        try:
            result = subprocess.run(['ip', 'link', 'show', interface], stdout=subprocess.PIPE, text=True)
            lines = result.stdout.splitlines()
            status = "up" if "state UP" in lines[0] else "down"
            print(f"{INFO}Interface {interface} is currently {status}.{RESET}")
        except subprocess.CalledProcessError as e:
            print(f"{ERROR}[ERROR] {e}{RESET}")

        # Ask if the user wants to check another interface or return to the menu
        choice = input("Do you want to check another interface? (y/n): ").strip().lower()
        if choice == 'n':
            break

def auto_change_mac_addresses(interval):
    global stop_auto_change
    while not stop_auto_change:
        interfaces = get_interfaces()
        if not interfaces:
            print(f"{WARNING}No interfaces found.{RESET}")
            return
        for interface in interfaces:
            try:
                # Bring the interface down
                subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'down'], check=True)
                
                # Change the MAC address
                result = subprocess.run(['sudo', 'macchanger', '-r', interface], stdout=subprocess.PIPE, text=True)
                print(f"{SUCCESS}{result.stdout}{RESET}")
                
                # Bring the interface up
                subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'up'], check=True)
            except subprocess.CalledProcessError as e:
                print(f"{ERROR}[ERROR] {e}{RESET}")
        time.sleep(interval)

def start_auto_change():
    global auto_change_thread, stop_auto_change
    if auto_change_thread is not None and auto_change_thread.is_alive():
        print(f"{WARNING}Automatic MAC address changing is already running.{RESET}")
        return
    
    try:
        interval = int(input("Enter the interval between MAC address changes in seconds: "))
        if interval <= 0:
            print(f"{ERROR}Interval must be a positive integer.{RESET}")
            return
        
        stop_auto_change = False
        auto_change_thread = threading.Thread(target=auto_change_mac_addresses, args=(interval,))
        auto_change_thread.start()
        print(f"{SUCCESS}Automatic MAC address changing started with an interval of {interval} seconds.{RESET}")
        time.sleep(2)
    except ValueError:
        print(f"{ERROR}Invalid interval value. Please enter a positive integer.{RESET}")

def stop_auto_change_mac():
    global stop_auto_change, auto_change_thread
    if auto_change_thread is None or not auto_change_thread.is_alive():
        print(f"{WARNING}Automatic MAC address changing is not running.{RESET}")
        return
    
    print("Stopping automatic MAC changing")
    time.sleep(2)
    print("may take a moment ...")
    print("                     ")
    stop_auto_change = True
    auto_change_thread.join()
    print(f"{SUCCESS}Automatic MAC address changing has stopped.{RESET}")
    
def change_interface_state():
    while True:
        interface = input("Enter the interface name: ")

        # Check if the interface exists
        if interface not in get_interfaces():
            print(f"{ERROR}Invalid interface name. Please try again.{RESET}")
            continue

        state = input("Enter the desired state (up/down): ").strip().lower()
        if state not in ['up', 'down']:
            print(f"{ERROR}Invalid state. Please enter 'up' or 'down'.{RESET}")
            continue
        
        try:
            # Change the interface state
            subprocess.run(['sudo', 'ip', 'link', 'set', interface, state], check=True)
            print(f"{SUCCESS}Interface {interface} has been set to {state}.{RESET}")
        except subprocess.CalledProcessError as e:
            print(f"{ERROR}[ERROR] {e}{RESET}")

        # Ask if the user wants to try another interface or return to the menu
        choice = input("Do you want to try another interface? (y/n): ").strip().lower()
        if choice == 'n':
            break
    
def main_menu():
    while True:
        clear_terminal()
        print_header()
        print(f"{INFO}          MacDaddy - MAC Address Changer{RESET}")
        print(f"{HEADER}=" * 50)
        print(f"{TEXT}1.   Show available interfaces{RESET}")
        print(f"{TEXT}2.    Show MAC address information{RESET}")
        print(f"{TEXT}3.     Change MAC address of an interface{RESET}")
        print(f"{TEXT}4.      Change MAC addresses of all interfaces{RESET}")
        print(f"{TEXT}5.       Reset MAC address of an interface{RESET}")
        print(f"{TEXT}6.        Reset MAC addresses of all interfaces{RESET}")
        print(f"{TEXT}7.         Backup MAC addresses to txt file{RESET}")
        print(f"{TEXT}8.          Restore MAC addresses from backup{RESET}")
        print(f"{TEXT}9.           Change MAC address to a custom value{RESET}")
        print(f"{TEXT}10.           Check interface status{RESET}")
        print(f"{TEXT}11.            Start auto MAC address changing{RESET}")
        print(f"{TEXT}12.             Stop auto MAC address changing{RESET}")
        print(f"{TEXT}13.              Change interface state (up/down){RESET}")
        print(f"{TEXT}14.               Exit{RESET}")
        print(f"{HEADER}=" * 50)

        choice = input("Enter your choice: ")

        clear_terminal()
        
        if choice == '1':
            print_header()
            show_interfaces()
        elif choice == '2':
            print_header()
            show_mac_addresses()
        elif choice == '3':
            print_header()
            change_mac_address()
        elif choice == '4':
            print_header()
            change_all_mac_addresses()
        elif choice == '5':
            print_header()
            reset_mac_address()
        elif choice == '6':
            print_header()
            reset_all_mac_addresses()
        elif choice == '7':
            print_header()
            backup_mac_addresses()
        elif choice == '8':
            print_header()
            restore_mac_addresses()
        elif choice == '9':
            print_header()
            custom_mac_address()
        elif choice == '10':
            print_header()
            check_interface_status()
        elif choice == '11':
            print_header()
            start_auto_change()
        elif choice == '12':
            print_header()
            stop_auto_change_mac()
        elif choice == '13':
            print_header()
            change_interface_state()
        elif choice == '14':
            clear_terminal()
            break
        else:
            print_header()
            print(f"{ERROR}Invalid choice. Please try again.{RESET}")

        input("Press Enter to go back...")


if __name__ == "__main__":
    main_menu()
