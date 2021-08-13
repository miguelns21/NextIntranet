# -*- coding: utf-8 -*-
import re
import subprocess
import string
import random
import os
import configparser


#Variables para  el programa
# Para probar desde el usuario root en terminal o ssh
# var_apache_user = "sudo -u miguelns -E"
var_apache_user = ""

# Lecturas de las variables del sistema
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini.txt')
config = configparser.ConfigParser()
config.read(config_path)

nick_usuario_admin = config['PARTICULAR']['NICK_USUARIO_ADMIN'];
web_url = config['PARTICULAR']['WEB_URL'];
enviar_email = (config['GENERAL']['ACTIVAR_ENVIO_EMAIL'] == "Si");

var_user_group = config['GENERAL']['USUARIO_GRUPO']
var_path_to_php = config['GENERAL']['PATH_A_PHP']
var_path_nextcloud = config['GENERAL']['PATH_A_NEXTCLOUD']
var_data_nextcloud = config['GENERAL']['NOMBRE_DATA_NEXTCLOUD']

# Variables proceso IMPORTAR_USUARIO
directorio_clientes_csv = "{}/{}/{}/files/Clientes_CSV".format(var_path_nextcloud, var_data_nextcloud, nick_usuario_admin)
var_skeleton = "{}/core/skeleton/".format(var_path_nextcloud)
directorio_destino_base = "{}/{}".format(var_path_nextcloud, var_data_nextcloud)

# Variables proceso REPARTIR
# Recupero una lista de los ficheros pdf que hay que repartir.
directorio_usuario_reparto_factura = "{}/{}/{}/files/Reparto_Facturas/".format(
    var_path_nextcloud, var_data_nextcloud, nick_usuario_admin)
directorio_usuario_base = "{}/{}/{}/files/".format(
    var_path_nextcloud, var_data_nextcloud, nick_usuario_admin)

# Variables proceso EMAIL
fichero_usuario_emails_alternativos = "{}/{}/{}/files/Emails_Alternativos.txt".format(
    var_path_nextcloud, var_data_nextcloud, nick_usuario_admin)

fichero_usuario_logs = "{}/{}/{}/files/logs_info.txt".format(
    var_path_nextcloud, var_data_nextcloud, nick_usuario_admin)


directorio_destino_base = "{}/{}/".format(var_path_nextcloud, var_data_nextcloud)
sufijo_directorio_destino_factura = "/files/Facturas/"

#Si el fichero de log es mayor de 1Mb, lo borramos
def comprobar_fichero_log():
    if os.path.isfile(fichero_usuario_logs):
        tam = os.path.getsize(fichero_usuario_logs)
        if tam > 1048576:  #(1Mb)
            os.remove(fichero_usuario_logs)
    return tam

def emails_adicionales(abonado):
    lista = []
    if os.path.isfile(fichero_usuario_emails_alternativos):
        f = open(fichero_usuario_emails_alternativos)
        for linea in f:
            cc = linea.lstrip().rstrip('\n').rstrip('\r').split(";")
            if cc[0] == abonado:
               cc.pop(0)
               for c in cc:
                   if es_correo_valido(c.lower()):
                       lista.append(c)
        f.close()

    return lista

def clave_aleatoria():
    alphabet = string.ascii_letters + string.digits
    while True:
        password = ''.join(random.choice(alphabet) for i in range(10))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and sum(c.isdigit() for c in password) >= 3):
            break
    return password

var_password = clave_aleatoria()

def es_correo_valido(correo):
    expresion_regular = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
    return re.match(expresion_regular, correo) is not None

def run_occ_info(var_apache_user, id):

    comando = "{} {} {}occ user:info {} ".format(var_apache_user, var_path_to_php, var_path_nextcloud, id)
    process = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    datos_occ = {}
    for line in process.stdout:
        if line.rstrip('\n') == "":
            continue
        if line.find("user not found") > -1:
            break
        campos = line.rstrip('\n').split(':')
        campos_s = campos[0].lstrip(" ").split(' ')
        if campos_s[1] == 'groups':
            lista_grupo = []
            datos_occ['groups'] = lista_grupo
        elif len(campos) == 1:
            if len(campos_s) > 1: #Si tiene algún grupo asignado
                lista_grupo.append(campos_s[1].lstrip(" "))
                datos_occ['groups'] = lista_grupo
        elif len(campos) >= 1:
            datos_occ[campos_s[1].lstrip(" ")] = campos[1].lstrip(" ")

    return datos_occ

def run_cmd(cmd):
    """
    Ejecuta una orden en el sistema operativo. Imprimir por pantalla la salida del comando.
    :param cmd: por ejemplo 'ls'
    :return: Una excepción si no se pudo ejecutar el comando
    """
    result = []
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in process.stdout:
        result.append(line)
    errcode = process.returncode
    if errcode is not None:
        raise Exception('cmd %s failed, see above for details', cmd)

def run_occ_info_groups(var_apache_user):

    #Genera un diccionario de grupos con sus usuarios
    comando = "{} {} {}occ group:list".format(var_apache_user, var_path_to_php, var_path_nextcloud)
    process = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    datos_occ = {}
    for line in  process.stdout:
        if line == '\n':
            break

        campos = line.rstrip('\n').split(':')
        campos_s = campos[0].lstrip(" ").split(' ')
        if len(campos) == 2:
            grupo = campos_s[1].lstrip(" ")
            lista_grupo = []
        elif len(campos) == 1:
            lista_grupo.append(campos_s[1].lstrip(" "))
            datos_occ[grupo] = lista_grupo

    return datos_occ

def formato(cadena, with_formato=20, alineacion='l'):
    if (len(cadena) > with_formato):
        return cadena[:with_formato/2-2]+'...'+cadena[-(with_formato/2-1):]
    elif alineacion == 'l':
        return '{0: <{width}}'.format(cadena, width=with_formato)
    elif alineacion == 'r':
        return '{0: >{width}}'.format(cadena, width=with_formato)

def obtener_datos_factura(fichero):
    resultado = {}
    if fichero.count('.') < 1:  #Falta la extensión
        return 'Falta la extensión del fichero'
    extension = fichero.split('.')[-1]  #Extensión
    fichero = fichero.replace('.'+extension, '')

    if fichero.count('_') + fichero.count('-') < 1:  #Hay al menos 1 separador
        return 'Debe haber 1 separador de fichero (-_)'
    aux_bajo = fichero.split("_")
    aux_medio = fichero.split("-")

    if (len(aux_bajo[0]) < len(aux_medio[0])):
        resultado['abonado'] = aux_bajo[0].lstrip("0")
    else:
        resultado['abonado'] = aux_medio[0].lstrip("0")

    if resultado['abonado'] == '':
        return 'El abonado no puede estar vacío'

    return resultado

