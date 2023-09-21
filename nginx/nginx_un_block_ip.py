from datetime import datetime
import subprocess

import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()
# Obtener el valor de las variables de entorno

blocked_ips_log = os.getenv("BLOCKED_IPS_LOG")
unblocked_ips_log = os.getenv("UNBLOCKED_IPS_LOG")
# Modo ejecucion
debug               = os.getenv("DEBUG")

def unblock_ip(ip_to_unblock):
    if not debug:
        subprocess.run(["sudo", "iptables", "-D", "INPUT", "-s", ip_to_unblock, "-j", "DROP"])
    print(f"Ip {ip_to_unblock} desbloqueada.")

def move_to_unblocked_log(line):
    if not debug:
        with open(unblocked_ips_log, "a") as log_file:
            log_file.write(line)

def unblock_ips_from_log():
    current_time = datetime.now()

    with open(blocked_ips_log, "r") as log_file:
        lines = log_file.readlines()

    updated_lines = []

    for line in lines:
        parts = line.strip().split()
        if len(parts) == 5:
            ip, reason, start_time_str, end_time_str, _ = parts
            start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S.%f")
            end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S.%f")

            if current_time > end_time:
                unblock_ip(ip)
                move_to_unblocked_log(line)
                print(f"Ip {ip} desbloqueada y movida al log de desbloqueos.")
            else:
                updated_lines.append(line)
        else:
            updated_lines.append(line)

    with open(blocked_ips_log, "w") as log_file:
        log_file.writelines(updated_lines)

if __name__ == "__main__":
    unblock_ips_from_log()
