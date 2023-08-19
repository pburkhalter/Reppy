import grp
import io
import os
import pwd
import shutil
import subprocess
import sys


# Define setup parameters
USER = "reppy"
DEFAULT_PASSWORD = "reppy"

SERVICE_NAME = "reppy"
EXEC_COMMAND = "/path/to/your/command args"
WORKING_DIR = "/path/to/working/directory"
PERMISSIONS = 0o755

BOOT_CONFIG_PATH = "/boot/config.txt"


def is_root():
    return os.geteuid() == 0


def is_raspberry_pi():
    try:
        with open('/proc/cpuinfo', 'r') as file:
            for line in file:
                if line.startswith('Hardware') and 'BCM' in line:
                    return True
    except Exception as e:
        pass
    return False


def add_user(username, password):
    # Add user and create home directory
    subprocess.run(["sudo", "useradd", "-m", username])

    # Set password for the user
    proc = subprocess.Popen(["sudo", "passwd", username], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.communicate(input=f"{password}\n{password}\n".encode())


def grant_sudo_privileges(username):
    sudoers_file_content = f"{username} ALL=(ALL:ALL) ALL\n"
    sudoers_file_path = f"/etc/sudoers.d/{username}"

    with open(sudoers_file_path, 'w') as file:
        file.write(sudoers_file_content)

    # Set correct permissions for the file
    subprocess.run(["sudo", "chmod", "0440", sudoers_file_path])


def add_user_to_gpio_group(username):
    subprocess.run(["sudo", "usermod", "-a", "-G", "gpio", username])


def create_service_file(service_name, command, user, working_directory):
    service_content = f"""
        [Unit]
        Description={service_name} Service
        After=network.target
        
        [Service]
        ExecStart={command}
        Restart=always
        User={user}
        WorkingDirectory={working_directory}
        
        [Install]
        WantedBy=multi-user.target
    """

    service_path = f"/etc/systemd/system/{service_name}.service"

    with open(service_path, 'w') as service_file:
        service_file.write(service_content)

    print(f"Service file created at {service_path}")


def enable_and_start_service(service_name):
    subprocess.run(["sudo", "systemctl", "daemon-reload"])
    subprocess.run(["sudo", "systemctl", "enable", service_name])
    subprocess.run(["sudo", "systemctl", "start", service_name])

    print(f"{service_name} service enabled and started.")


def config_exists():
    return os.path.exists(BOOT_CONFIG_PATH)


def parse_config(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    config = {}
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#"):  # Ignore comments and empty lines
            key, value = line.split('=', 1)
            config[key] = value

    return config


def modify_or_add_config(config, key, value):
    config[key] = value


def write_config(file_path, config):
    with open(file_path, 'w') as file:
        for key, value in config.items():
            file.write(f"{key}={value}\n")


def modify_config(key, value):
    config = parse_config(BOOT_CONFIG_PATH)

    modify_or_add_config(config, key, value)
    write_config(BOOT_CONFIG_PATH, config)


def copy_dir(source_directory, destination_directory):
    shutil.copytree(source_directory, destination_directory)
    print(f"Copied {source_directory} to {destination_directory}")


def set_permissions_and_owner(path, permissions, user, group=None):
    # Set permissions
    os.chmod(path, permissions)

    # Get UID and GID
    uid = pwd.getpwnam(user).pw_uid
    gid = grp.getgrnam(group).gr_gid if group else uid

    # Set owner and group
    os.chown(path, uid, gid)


if __name__ == "__main__":
    print("-" * 80)
    print("Running Install-Script for Reppy...")
    print("-" * 80)

    if not is_root():
        print("Root-permissions needed. Rerunning as root (sudo)...")
        os.execvp("sudo", ["sudo", "python3"] + sys.argv)

    # ---------------------------------------------------------------------------------

    print(f"- 1/3 User")

    print(f"-- Creating user '{USER}'...")
    add_user(USER, DEFAULT_PASSWORD)

    print(f"-- Adding user '{USER}' to the sudo group...")
    grant_sudo_privileges(USER)

    print(f"-- Adding user '{USER}' to the gpio group...")
    add_user_to_gpio_group(USER)

    # ---------------------------------------------------------------------------------

    print(f"- Files")
    print(f"-- Copy files to '{WORKING_DIR}'...")
    copy_dir("./src", WORKING_DIR)
    print(f"-- Changing permissions on '{WORKING_DIR}'...")
    set_permissions_and_owner(WORKING_DIR, PERMISSIONS, USER)

    # ---------------------------------------------------------------------------------

    print("- 2/3 Service")
    print("-- Creating service file...")
    create_service_file(SERVICE_NAME, EXEC_COMMAND, USER, WORKING_DIR)

    # ---------------------------------------------------------------------------------

    if not is_raspberry_pi():
        print("- Not running on a Raspberry Pi. Skipping the related configurations...")
    else:
        print("- 3/3 Modifying boot-config...")
        if not config_exists():
            print("- File '/boot/config.txt' does not exist. Skipping modifications...")
            sys.exit(1)

        print("-- Setting display-preferences...")
        modify_config("hdmi_preferred", 1)

    # ---------------------------------------------------------------------------------

    print("- Enable and start service...")
    enable_and_start_service(SERVICE_NAME)

    print("- DONE. Exiting...")


