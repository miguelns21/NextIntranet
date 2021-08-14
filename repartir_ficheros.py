# -*- coding: utf-8 -*-q
import subprocess
import os
import shutil
import logging
import funciones as rut
import correos

if __name__ == '__main__':
    """
    Este script tomará los ficheros pdf que se encuentren en una ubicación especificada y en función de
    unas reglas establecidas (atendiendo al formato del nombre del fichero XXXXXX-AAA..AA.pdf), moverá dichos
    ficheros a las carpetas del usuario.
    """

    logger = logging.getLogger(rut.nick_usuario_admin)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('{}/{}/{}/{}/files/logs_info.txt'.format(rut.var_path_nextcloud, rut.var_data_nextcloud, rut.nick_usuario_admin))
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    tam_fichero_log = rut.comprobar_fichero_log()
    if tam_fichero_log > 1048576:   #Si el fichero de log es mayor de 1 MB lo borro para no acumular
        logger.error('El fichero log ({} Bytes) es mayor de 1MB. Se ha borrado ahora.'.format(tam_fichero_log))

    usuarios_facturas = []
    Contador_Facturas = 0
    Contador_Errores_Facturas = 0
    for ruta, directorios, archivos in os.walk(rut.directorio_usuario_reparto_factura, topdown=True):
        archivos.sort()
        for fichero in archivos:
            fac = rut.obtener_datos_factura(os.path.split(fichero)[1])
            if type(fac) is str:
                logger.error('{}:{}'.format(fichero, fac))
                Contador_Errores_Facturas = Contador_Errores_Facturas + 1
                continue

            id = fac['abonado']
            if os.path.isdir(rut.directorio_destino_base + id):
                #El directorio factura está protegido, tengo que pasarlo a 755 para poder copiar en él
                rut.run_cmd('chmod -R 755 {}'.format(rut.directorio_destino_base + id + rut.sufijo_directorio_destino_factura))
                ruta_relativa = ruta.replace(rut.directorio_usuario_reparto_factura, "")

                if not os.path.isdir(rut.directorio_destino_base + id + rut.sufijo_directorio_destino_factura + ruta_relativa):
                    os.makedirs(rut.directorio_destino_base + id + rut.sufijo_directorio_destino_factura + ruta_relativa)
                shutil.move(ruta+"/"+fichero, rut.directorio_destino_base + id + rut.sufijo_directorio_destino_factura + ruta_relativa +"/"+ os.path.basename(fichero))
                #Una vez hecho el reparto hay que volver a proteger la carpeta.
                rut.run_cmd('chmod -R 555 {}'.format(rut.directorio_destino_base + id + rut.sufijo_directorio_destino_factura))
                if Contador_Facturas == 0 and Contador_Errores_Facturas == 0:
                    logger.info('COMIENZA ---->Reparto de FACTURAS')
                logger.info("Factura: {} del usuario con Id: {}. Ok.".format(rut.formato(ruta_relativa +"/"+ os.path.basename(fichero), 35), rut.formato(id, 6, 'r')))
                Contador_Facturas = Contador_Facturas + 1
                if not (id in usuarios_facturas):
                    usuarios_facturas.append(id)
            else:
                if Contador_Facturas == 0 and Contador_Errores_Facturas == 0:
                    logger.info('COMIENZA ---->Reparto de FACTURAS')
                logger.error("No existe la carpeta del usuario con Id: {} no existe. ".format(rut.formato(id, 6, 'r')))
                logger.error("El fichero {} no será procesado.".format(rut.formato(os.path.split(fichero)[1], 35)))
                Contador_Errores_Facturas = Contador_Errores_Facturas + 1

    if Contador_Facturas > 0 or Contador_Errores_Facturas > 0:
        logger.info('Se han procesado {} facturas de {} usuarios.     {} errores'.format(Contador_Facturas, len(usuarios_facturas), Contador_Errores_Facturas))
        logger.info('FIN ----> Reparto de FACTURAS')
        logger.info('\n')

    #Actualizamos las BBDD de Nextcloud con los cambios producidos
    #en el caso de haber repartido algún fichero
    if Contador_Facturas > 0 :
        comando = "{} {} {}occ files:scan --all".format(rut.var_apache_user, rut.var_path_to_php, rut.var_path_nextcloud)
        rut.run_cmd(comando)

    if len(usuarios_facturas) > 0:
        logger.info('COMIENZO ----> Envio email a los usuarios')

    #Mandamos los correos de facturación
    Contador_Usuarios = 0;
    Contador_emails = 0
    #Enviarmos los emails a los usuarios avisando de que tienen facturas
    for usuario in usuarios_facturas:
        Contador_Usuarios = Contador_Usuarios + 1
        datos_occ = rut.run_occ_info(rut.var_apache_user, usuario)
        if datos_occ:
            if not rut.es_correo_valido(datos_occ['email']):
                logger.error("El email especificado \"{}\" para el usuario {} no es valido".format(datos_occ['email'], usuario))
                logger.error("El proceso seguirá con el siguiente usuario.")
                continue

            if not 'admin' in datos_occ['groups']:
                if rut.enviar_email and datos_occ['enabled'] == 'true':
                    ccs = rut.emails_adicionales(usuario)
                    correos.enviar_email_usuario(usuario, datos_occ['display_name'], datos_occ['email'], "", "Aviso_Factura", ccs)
                    Contador_emails = Contador_emails + 1
                    logger.info("Email de aviso enviado a: \"{}\" del usuario {}".format(datos_occ['email'], usuario))
                    for c in ccs:
                        Contador_emails = Contador_emails + 1
                        logger.info("Email adicional de aviso enviado a: \"{}\" del usuario {}".format(c, usuario))
            else:
                logger.error("El usuario \"{}\" es administrador. No se le envía correo.".format(usuario))

    if len(usuarios_facturas) > 0:
        logger.info('Se han enviado {} emails de {} usuarios de facturas.'.format(Contador_emails, Contador_Usuarios))
        logger.info('FINAL ----> Envio email de facturas a los usuarios')
        logger.info('\n')

    logging.shutdown()
