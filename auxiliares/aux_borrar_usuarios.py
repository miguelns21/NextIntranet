# -*- coding: utf-8 -*-
import os
import logging
import funciones as rut
import sys
import configparser

logging.basicConfig(
    format = '%(asctime)-5s %(name)-15s %(levelname)-8s %(message)s',
    level  = logging.INFO, # Nivel de los eventos que se registran en el logger
)

if __name__ == '__main__':
    """
    Borramos todos los usuarios y directorio que sean numericos.
    """
    #Para probar desde el usuario root en terminal o ssh
    if len(sys.argv) == 2:
        id = sys.argv[1]
    else:
        print("Error - Introduce los argumentos correctamente")
        print('Ejemplo: python aux_borrar_usuarios.py all/id')
        print('Salgo del programa ahora.')
        exit()

    #var_apache_user = "sudo -u stabulacion.com -E"
    var_apache_user = ""

    # Lecturas de las variables del sistema
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini.txt')
    config = configparser.ConfigParser()
    config.read(config_path)

    var_path_to_php = config['GENERAL']['PATH_A_PHP']
    var_path_nextcloud = config['GENERAL']['PATH_A_NEXTCLOUD']
    var_data_nextcloud = config['GENERAL']['NOMBRE_DATA_NEXTCLOUD']
    directorio_destino_base = "{}/{}".format(var_path_nextcloud, var_data_nextcloud)

    logging.info('COMIENZA BORRADO')

    listado_Usuarios = []
    if os.path.isdir(directorio_destino_base):
         listado_Usuarios = os.listdir(directorio_destino_base)

    for var_username in listado_Usuarios:
        if id != "all" and id != var_username:
            continue
        datos_occ = rut.run_occ_info(var_apache_user, str(var_username))
        if datos_occ:
            logging.info("Nombre del usuario \"{}\": {} : {}".format(str(var_username), datos_occ['display_name'], datos_occ['email']))

            if not 'admin' in datos_occ['groups']:
                #Borro el usuario junto con sus ficheros residuales que no se borran al tener permisos 555.
                comando = "{} {} {}occ user:delete {}".format(var_apache_user, var_path_to_php, var_path_nextcloud, var_username)
                logging.info("Borrando usuario \"{}\": ".format(var_username))
                rut.run_cmd(comando)
                logging.info("Borrando carpetas residuales del usuario \"{}\": ".format(str(var_username)))
                rut.run_cmd('chmod 755 -R {}'.format(directorio_destino_base +"/"+ str(var_username)))
                rut.run_cmd('rm -rf {}'.format(directorio_destino_base +"/"+ str(var_username)))
            else:
                logging.info("El usuario \"{}\" es administrador. No se borra.".format(var_username))
        else:
            logging.info("El directorio \"{}\", no es un cliente.".format(var_username))


    comando = "{} {} {}occ files:scan  --all".format(var_apache_user, var_path_to_php, var_path_nextcloud)
    rut.run_cmd(comando)
    logging.info('FIN BORRADO')
    logging.info('\n')

    logging.shutdown()


