# -*- coding: utf-8 -*-
import subprocess
import os
import shutil
import logging
import correos
import funciones as rut

def run_occ(cmd, usuario="", nombre=""):
    """
    Ejecuta una orden en el sistema operativo. Imprimir por pantalla la salida del comando.
    Versión modificada porque escribe en un fichero para ver el log y crea el home del usuario a partir
    del skeleton
    :param cmd: por ejemplo 'php occ add:user'
    :return: Una excepción si no se pudo ejecutar el comando
    """
    nuevo_usuario = False
    result = []
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in process.stdout:
        result.append(line)
    errcode = process.returncode

    #Solo para debug
    for line in result:
        # logger.info(line)
        if line.find("was created successfully") > -1:
            logger.info("Usuario con id: {} y nombre \"{}\" creado.".format(rut.formato(usuario, 6, 'r'), rut.formato(nombre, 30, 'l')))
            nuevo_usuario = True

            #Creo el skeleton porque solo se crea si se entra por primera vez
            if os.path.exists(rut.var_skeleton):
                arbol = shutil.copytree(rut.var_skeleton, rut.directorio_destino_base + "/" + usuario + "/files")
                #run_cmd('chown -R {} {}'.format(usuario_grupo, var_path_usuario+"/"+usuario+"/files"))
                #logging.info('Cambiando el propietario :'+'chown -R \"{}\" {}'.format(usuario_grupo, var_path_usuario+"/"+usuario+"/files"))
        elif line.find("already exists") > -1 and line.find("The user") > -1:
            logger.info("Usuario con id: {} y nombre \"{}\" ya existe.".format(rut.formato(usuario, 6, 'r'), nombre))
        elif line.find("user not found") > -1:
            logger.info("El abonado con id: {} no existe.".format(rut.formato(usuario, 6, 'r')))
        elif line.find("group not found") > -1:
            logging.error("El grupo {} no existe.".format(usuario))
        elif line.find("already exists") > -1 and line.find("Group") > -1:
            logging.error("El grupo {} ya existe.".format(usuario))

    if errcode is not None:
        raise logger.info('cmd %s failed, see above for details', cmd)
    return nuevo_usuario

if __name__ == '__main__':
    """
    Cuerpo principal del programa.
    El programa leerá un fichero csv en un path especificado con una estructura dada:
        id;nombre;email
    
    Se establecen las variables que dependerán finalmente del sistema en el que se instale.
    
    Se procederá a crear a través del comando occ de nextcloud un usuario con una clave especificada.
    Se copiará el directorio skeleton de la instalación de nextcloud a cada usuario ya que esto se produce
    de forma automática cuando el usuario se validad por primera vez pero el comando occ carece de dicha
    funcionalidad.
    
    Según una variable indicada se enviará o no un email de bienvenida.
    """

    #Definicion del logger
    logger = logging.getLogger(rut.nick_usuario_admin)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('{}/{}/{}/files/logs_info.txt'.format(rut.var_path_nextcloud, rut.var_data_nextcloud, rut.nick_usuario_admin))
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)


    fileExt = r".csv"
    ficheros_csv = []
    if os.path.isdir(rut.directorio_clientes_csv):
        ficheros_csv = [os.path.join(rut.directorio_clientes_csv, _) for _ in os.listdir(rut.directorio_clientes_csv) if
                    _.endswith(fileExt)]

    #Llegan dos tipos de ficheros:
    # - Clientes : Abonado;Razón social Cliente;Email empresa
    # - Tarifas: CODIGO;CODTARIFA
    # Detecto cual es cada uno para tener un array separado y procesar primero los clientes y luego sus tarifas
    ficheros_csv_clientes = []
    ficheros_csv_tarifas = []
    errores = 0
    for fichero_csv in ficheros_csv:
        nombre_fichero = os.path.split(fichero_csv)[1]
        f = open(fichero_csv)
        linea = f.next().split(";")
        f.close()
        if linea[0].count("Abonado") > 0 and len(linea) >= 3:
            logger.info('El fichero csv: {} es de clientes'.format(rut.formato(nombre_fichero, 35)))
            ficheros_csv_clientes.append(fichero_csv)
        elif linea[0].count("CODIGO") > 0 and len(linea) >= 2:
            logger.info('El fichero csv: {} es de tarifas'.format(rut.formato(nombre_fichero, 35)))
            ficheros_csv_tarifas.append(fichero_csv)
        else:
            logger.error("El fichero {} no se procesará. Suba ahora un fichero correcto.".format(rut.formato(nombre_fichero, 35)))
            errores = errores + 1
            continue

    ficheros_csv = ficheros_csv_clientes
    if len(ficheros_csv) > 0:
        logger.info('COMIENZA ---->Importación Abonados')
        ficheros_csv = sorted(ficheros_csv)

    for fichero_csv in ficheros_csv:
        nombre_fichero = os.path.split(fichero_csv)[1]
        # logger.info('Procesando el fichero csv: {}'.format(rut.formato(nombre_fichero, 40)))
        f = open(fichero_csv)
        f.next() #La primera linea es el encabezado
        for linea in f:
            # Esperamos un formato de fichero: id;nombre;email
            campos = linea.split(";")
            if not rut.es_correo_valido(campos[2].lstrip().rstrip('\n').rstrip('\r').lower()):
                logger.error("El email especificado \"{}\" para el usuario {} no es valido".format(campos[2].ltrip().rstrip('\n').rstrip('\r').lower(), rut.formato(campos[1], 6, 'r')))
                logger.error("El proceso se cancelará ahora. Suba ahora un fichero correcto.")
                break
            else:
                logger.error("El fichero CSV debe tener la estructura minima id;nombre;email")
                break

            var_username = campos[0].lstrip('0')
            var_name = campos[1]
            var_email = campos[2].lstrip().rstrip('\n').rstrip('\r').lower()
            var_accion = "";
            if len(campos) >= 4:
                var_accion = campos[3].rstrip('\n').rstrip('\r')

            usuario_nuevo = False
            if var_accion != "BORRAR":
                #Creo el usuario
                comando_prefix = "export OC_PASS={};".format(rut.var_password)
                comando = "{} {} {}occ user:add --display-name=\"{}\" --password-from-env -- {}".format(
                    rut.var_apache_user, rut.var_path_to_php, rut.var_path_nextcloud, var_name, var_username)
                usuario_nuevo = run_occ(comando_prefix + comando, var_username, var_name)
                # logger.info('Usuario creado: {} '.format(var_username))
            else:
                #Borro el usuario junto con sus ficheros residuales que no se borran al tener permisos 555.
                comando = "{} {} {}occ user:delete {}".format(rut.var_apache_user, rut.var_path_to_php, rut.var_path_nextcloud, var_username)
                logger.info("Borrando usuario \"{}\": ".format(var_username))
                run_occ(comando)
                rut.run_cmd('chmod 755 -R {}'.format(rut.directorio_destino_base +"/"+ var_username))
                rut.run_cmd('rm -rf {}'.format(rut.directorio_destino_base +"/"+ var_username))

            #Solo se cambia la clave y envia el mensaje de bienvenida cuando el usuario es nuevo
            if usuario_nuevo:
                comando = "{} {} {}occ user:setting {} settings email \"{}\"".format(rut.var_apache_user, rut.var_path_to_php, rut.var_path_nextcloud, var_username, var_email.lower())
                run_occ(comando)
                if rut.enviar_email:
                    correos.enviar_email_usuario(var_username, var_name, var_email, rut.var_password, "Bienvenida_Clave")
                    logger.info("Email de bienvenida enviado a: {}".format(var_email))

        f.close()
        os.remove(fichero_csv)
        logger.info("Borro el fichero de importación csv: {}.".format(rut.formato(os.path.split(fichero_csv)[1], 35)))

    ficheros_csv = ficheros_csv_tarifas
    if len(ficheros_csv) > 0:
        logger.info('COMIENZA ---->Importación Tarifas de Abonados')

    for fichero_csv in ficheros_csv:
        nombre_fichero = os.path.split(fichero_csv)[1]
        logger.info('Procesando el fichero csv: {}'.format(rut.formato(nombre_fichero, 35)))
        f = open(fichero_csv)
        f.next() #La primera linea es el encabezado
        for linea in f:
            campos = linea.split(";")

            var_username = campos[0].lstrip('0')
            var_group = campos[1].rstrip('\n').rstrip('\r')
            datos_occ = rut.run_occ_info(rut.var_apache_user, var_username)
            if datos_occ: #Si el usuario existe
                # Consulto los grupos
                datos_occ_grupos = rut.run_occ_info_groups(rut.var_apache_user)
                if not var_group in datos_occ_grupos: #Si no existe el grupo lo creo
                    logger.info('Añadiendo la tarifa {}.'.format(var_group))
                    comando = "{} {} {}occ group:add {}".format(
                        rut.var_apache_user, rut.var_path_to_php, rut.var_path_nextcloud, var_group, var_username)
                    run_occ(comando)
                #Asigno el grupo al usuario
                logger.info('Asignando tarifa {} al abonado {}'.format(var_group, var_username))
                comando = "{} {} {}occ group:adduser {} {}".format(
                    rut.var_apache_user, rut.var_path_to_php, rut.var_path_nextcloud, var_group, var_username)
                run_occ(comando, var_username)
                # logger.info('Comando procesado : '.format(var_password) + comando)
            else:
                logger.error('El usuario {} no existe. No asigno tarifa'.format(var_username))

        f.close()
        os.remove(fichero_csv)
        logger.info("Borro el fichero de importación csv: {}.".format(rut.formato(os.path.split(fichero_csv)[1], 35)))


    if len(ficheros_csv_clientes) > 0 or len(ficheros_csv_tarifas) or errores > 0:
        comando = "{} {} {}occ files:scan {}".format(rut.var_apache_user, rut.var_path_to_php, rut.var_path_nextcloud, rut.nick_usuario_admin)
        rut.run_cmd(comando)
        logger.info('FIN ---->Importación Usuarios')
        logger.info('\n')

    logging.shutdown()


