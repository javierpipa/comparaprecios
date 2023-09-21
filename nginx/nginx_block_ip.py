import re
import subprocess
import time
from datetime import datetime, timedelta

import os
from dotenv import load_dotenv

import ipaddress  # Importa el módulo ipaddress para trabajar con direcciones IP

# Cargar las variables de entorno desde el archivo .env
load_dotenv()
# Obtener el valor de las variables de entorno

# Ruta al archivo de registro de IPs bloqueadas
blocked_ips_log     = os.getenv("BLOCKED_IPS_LOG")
# Ruta al archivo de registro de IPs desbloqueadas
unblocked_ips_log   = os.getenv("UNBLOCKED_IPS_LOG")
# Ruta al archivo de registro de Nginx
nginx_log_file      = os.getenv("NGINX_LOG_FILE")
# Leer los términos a bloquear desde el archivo
blocked_terms_file  = os.getenv("BLOCKED_TERMS_FILE")
# Posibles ataques
possible_attacks_log = os.getenv("POSSIBLE_ATTACKS_LOG")
# Modo ejecucion
debug               = os.getenv("DEBUG")

blocked_user_agents_file = os.getenv("BLOCKED_USER_AGENTS_FILE")

# Expresión regular para buscar direcciones IP en el registro de Nginx
ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'

# Expresión regular para buscar URLs en el registro de Nginx
url_pattern = r'"\w+\s+([^"]+)'

# Expresión regular para buscar el agente de usuario en el registro de Nginx
user_agent_pattern = r'"([^"]+)"$'

# Función para verificar si un archivo existe y, si no, crearlo
def create_if_not_exists(file_path):
    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            file.write("")
    else:
        print(f'Archivo {file_path} si existe')

# Verificar y crear los archivos de log si no existen
create_if_not_exists(blocked_ips_log)
create_if_not_exists(unblocked_ips_log)
create_if_not_exists(nginx_log_file)
create_if_not_exists(blocked_terms_file)
create_if_not_exists(possible_attacks_log)
create_if_not_exists(blocked_user_agents_file)

# Tiempo de bloqueo en segundos (por ejemplo, 1 hora)
block_time = 3600

# Términos para bloquear
with open(blocked_terms_file, 'r') as f:
    blocked_terms = [line.strip() for line in f.readlines()]

# Agentes a bloquear
with open(blocked_user_agents_file, 'r') as f:
    blocked_user_agents = [line.strip() for line in f.readlines()]

# Términos para no bloquear
whitelisted_terms = ['favicon.ico']
# # Función para bloquear una subred utilizando UFW
# def block_subnet(subnet, reason, line):
#     if not is_subnet_blocked(subnet):
#         with open(blocked_ips_log, "r") as log_file:
#             existing_entries = log_file.readlines()

#         for entry in existing_entries:
#             if subnet in entry:
#                 return

#         subprocess.run(["sudo", "ufw", "insert", "1", "deny", "from", subnet])
        
#         print(f"Subnet {subnet} bloqueada por {block_time} segundos. Motivo: {reason}")
#         print(f"Envio: {line}")

#         # Registrar la subred bloqueada en el archivo de registro
#         now = datetime.now()
#         until_time = now + timedelta(seconds=block_time)
#         log_entry = f"{subnet} {reason} {now} {until_time}\n"

#         with open(blocked_ips_log, "a") as log_file:
#             log_file.write(log_entry)

# Función para verificar si una subred ya está bloqueada en UFW
def is_subnet_blocked(subnet):
    output = subprocess.check_output(["sudo", "ufw", "status", "verbose"]).decode("utf-8")
    return subnet in output

# Función para verificar si un agente de usuario está bloqueado
def is_blocked_user_agent(user_agent, line):
    retorno = any(agent in user_agent for agent in blocked_user_agents)
    # if retorno:
    #     ip = extract_ip_from_line(line)
    #     print(ip, user_agent)
    # else:
    #     print(f'este agente {user_agent} no esta en archivo de agentes detenidos')
    return retorno

# Función para verificar si una IP ya está bloqueada en el firewall
def is_ip_blocked(ip):
    # output = subprocess.check_output(["sudo", "iptables", "-L", "INPUT", "-v", "-n"]).decode("utf-8")
    output = subprocess.check_output(["sudo", "ufw", "status", "verbose"]).decode("utf-8")

    return ip in output

def is_blocked_line(line):
    return any(term in line for term in blocked_terms) and (" 404 " in line or " 500 " in line or " 301 " in line )

def extract_ip_from_line(line):
    ip_match = re.search(ip_pattern, line)
    if ip_match:
        return ip_match.group()
    return None

# Función para verificar si una URL es válida y no está bloqueada
def is_valid_and_not_blocked_url(url):
    for term in blocked_terms:
        if term in url:
            return True
    return False

# Función para generar la subred correspondiente a partir de una dirección IP
# for i in {fin..inicio};do yes| sudo ufw delete $i;done
# for i in {fin..inicio};do yes| sudo iptables -D INPUT $i;done

# iptables -D INPUT 669


# iptables -L INPUT -n --line-numbers
# ufw status numbered

def generate_subnet(ip_address):
    try:
        ip = ipaddress.ip_interface(ip_address)
        subnet = ip.network.network_address
        return str(subnet)
    except ValueError:
        return None


# Función para analizar el archivo de registro de Nginx
def analyze_logs():
    with open(nginx_log_file, 'r') as f:
        lines = f.readlines()

    for line in lines:
        
        url_match = re.search(url_pattern, line)
        user_agent_match = re.search(user_agent_pattern, line)
        
        if user_agent_match:
            user_agent = user_agent_match.group(1)
            if is_blocked_user_agent(user_agent, line):
                ip = extract_ip_from_line(line)
                if ip:
                    block_ip(ip, "Block Agent ", line)
        
        if url_match:
            
            url = url_match.group(1)
            if is_blocked_line(line):
                if is_valid_and_not_blocked_url(url):
                    with open(possible_attacks_log, "a") as possible_attacks_file:
                        possible_attacks_file.write(url + "\n")
                        ip = extract_ip_from_line(line)
                        if ip:
                            block_ip(ip, "Possible attack", line)



def block_ip(ip, reason, line):
    # Genera la subred correspondiente usando la función generate_subnet
    subnet = generate_subnet(ip)
    if subnet:
        if not is_subnet_blocked(subnet):
            with open(blocked_ips_log, "r") as log_file:
                existing_entries = log_file.readlines()

            for entry in existing_entries:
                if subnet in entry:
                    print(f"Subred {subnet} ya está bloqueada en el registro.")
                    return

            # Ejecuta la regla de bloqueo utilizando ufw para la subred en lugar de una IP específica
            subprocess.run(["sudo", "ufw", "insert", "1", "deny", "from", subnet])
            print(f"Subred {subnet} bloqueada por {block_time} segundos. Motivo: {reason}")


            # Registrar la subred bloqueada en el archivo de registro
            now = datetime.now()
            until_time = now + timedelta(seconds=block_time)
            log_entry = f"{subnet} {reason} {now} {until_time}\n"

            with open(blocked_ips_log, "a") as log_file:
                log_file.write(log_entry)
        else:
            print(f"Subred {subnet} ya está bloqueada en el firewall.")
    else:
        print(f"Error al generar la subred para la IP {ip}.")



   

if __name__ == "__main__":
    # while True:
    #     analyze_logs()
    #     time.sleep(60)  # Analizar los registros cada minuto


    analyze_logs()