# -*- coding: utf-8 -*-
import smtplib
import email.message
import configparser
import os

# Configuramos los parámetros del servidor
# Lecturas de las variables del sistema
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini.txt')
config = configparser.ConfigParser()
config.read(config_path)

servidor = config['SERVIDOR_CORREO_SALIENTE']['SERVIDOR']
puerto = config['SERVIDOR_CORREO_SALIENTE']['PUERTO']
password = config['SERVIDOR_CORREO_SALIENTE']['PASSWORD']
usuario = config['SERVIDOR_CORREO_SALIENTE']['USUARIO']
web_nombre = config['PARTICULAR']['WEB_NOMBRE']
web_url = config['PARTICULAR']['WEB_URL']

usar_plantillas_emails = config['GENERAL']['ACTIVAR_PLANTILLAS_EMAILS']
nick_usuario_admin = config['PARTICULAR']['NICK_USUARIO_ADMIN']
web_url = config['PARTICULAR']['WEB_URL']
var_path_nextcloud = config['GENERAL']['PATH_A_NEXTCLOUD']
var_data_nextcloud = config['GENERAL']['NOMBRE_DATA_NEXTCLOUD']
directorio_plantillas_emails = "{}/{}/{}/files/Plantillas_Email".format(var_path_nextcloud, var_data_nextcloud, nick_usuario_admin)

def enviar_email_usuario(id, nombre, correo, clave, TipoMensaje, cc = []):
    msg = email.message.Message()

    ccs = cc[:]
    ## Destino en formato cadena separada por comas.
    if cc:
        msg['To'] = correo + ',' + ','.join(cc)
    else:
        msg['To'] = correo

    # Receptores en forma de lista.
    ccs.append(correo)

    msg['From'] = usuario
    msg.add_header('Content-Type', 'text/html')

    if TipoMensaje == "Aviso_Genérico":
        msg['Subject'] = email_asunto_generico
        cuerpo = email_content_generico
        if usar_plantillas_emails.upper() == "SI" and os.path.isfile(directorio_plantillas_emails + '/email_generico.html'):
            with open(directorio_plantillas_emails + '/email_generico.html') as file:
                cuerpo = file.read()
    elif TipoMensaje == "Bienvenida_Clave":
        msg['Subject'] = email_asunto_bienvenida
        cuerpo = email_content_bienvenida_clave
        if usar_plantillas_emails.upper() == "SI" and os.path.isfile(directorio_plantillas_emails + '/email_bienvenida_clave.html'):
            with open(directorio_plantillas_emails + '/email_bienvenida_clave.html') as file:
                cuerpo = file.read()
    elif TipoMensaje == "Aviso_Factura":
        msg['Subject'] = email_asunto_factura
        cuerpo = email_content_factura
        if usar_plantillas_emails.upper() == "SI" and os.path.isfile(directorio_plantillas_emails + '/email_factura.html'):
            with open(directorio_plantillas_emails + '/email_factura.html') as file:
                cuerpo = file.read()

    # cuerpo = unicode(cuerpo, encoding='utf-8')
    cuerpo = cuerpo.replace("XXXXXX", id)
    cuerpo = cuerpo.replace("YYYYYY", nombre)
    cuerpo = cuerpo.replace("ZZZZZZ", correo)
    cuerpo = cuerpo.replace("******", clave)
    cuerpo = cuerpo.replace("UUUUUU", web_url.encode('ascii','ignore'))
    cuerpo = cuerpo.replace("WWWWWW", web_nombre.encode('ascii','ignore'))
    msg.set_payload(cuerpo)

    # creacion del servidor smtp
    # server = smtplib.SMTP(servidor)
    server = smtplib.SMTP(servidor+":"+puerto)
    # server.starttls()

    # Validación del servidor con las claves de la cuenta
    server.login(msg['From'], password.encode('ascii','ignore'))

    # Envio del mensaje
    # server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.sendmail(msg['From'], ccs, msg.as_string())

    # Cerramos el servidor
    server.quit()


email_asunto_bienvenida = "Alta nuevo usuario {}-Intranet".format(web_nombre)

email_content_generico = """
<h2>
  <strong>Noticias de WWWWWW</strong>
</h2>
<h3>XXXXXX</h3>
Estimado cliente: 
<br>
<br>Nos es grato comunicarle que su zona privada de la intranet de WWWWWW ha recibido nueva informaci&oacute;n. 
<br>
<br>
<br>Le recordamos que su identificaci&oacute;n de usuario es 
<strong>XXXXXX</strong> 
<br>
<br>
<br>
<table style="border-collapse: collapse; width: 100%; height: 17px;" border="1">
  <tbody>
    <tr style="height: 17px; border-style: none;">
      <td style="width: 66.5706%; height: 17px; text-align: center; border-style: hidden;">
        <span style="font-size: 10pt; font-family: arial, helvetica, sans-serif;">
          <a href="https://UUUUUU/" target="_blank" class="cloudHQ__gmail_elements_final_btn" style="background-color: #242052; color: #ffffff; border: 1px solid #000000; border-radius: 3px; box-sizing: border-box; font-size: 13px; font-weight: bold; line-height: 42px; padding: 12px 24px; text-align: center; text-decoration: none; text-transform: uppercase; vertical-align: middle;" rel="noopener">Visite ahora WWWWWW para ver sus datos</a>
        </span>
      </td>
      <td style="width: 33.4294%; height: 17px; text-align: center; border-style: hidden;">
        <br>
        <br>
      </td>
    </tr>
    <tr>
      <td style="width: 66.5706%; text-align: center; border-style: hidden;">
        <span style="font-size: 10pt; font-family: arial, helvetica, sans-serif;">
          <span style="font-size: 10pt; font-family: arial, helvetica, sans-serif;">
            <br>
          </span>
        </span>
        <div style="text-align: center;">
          <span style="font-size: 10pt; font-family: arial, helvetica, sans-serif;">WWWWWW - Intranet de WWWWWW.</span>
        </div>
        <div style="text-align: center;">
          <span style="font-size: 10pt; font-family: arial, helvetica, sans-serif;">Este es un correo enviado autom&aacute;ticamente, por favor, no responda.</span>
        </div>
      </td>
      <td style="width: 33.4294%; text-align: center; border-style: hidden;">
        <br>
      </td>
    </tr>
  </tbody>
</table>
<div style="text-align: center;">
  <br>
</div>
<div style="text-align: center;">
  <br>
</div>
<br>
<div style="text-align: center;">&nbsp;</div>"""

email_asunto_generico = "Aviso nuevos datos {}-Intranet".format(web_nombre)

email_content_factura = """
<h2>
  <strong>Factura MRW</strong>
</h2>
<h3>XXXXXX</h3>
Estimado cliente: 
<br>
<br>Gracias por utilizar nuestros servicios de mensajer&iacute;a de 
<strong>MRW</strong>. 
<br>
<br>Ya puede consultar su nueva factura en la Zona Privada de la intranet de WWWWWW. 
<br>
<br>Le recordamos que su identificaci&oacute;n de usuario es <strong>XXXXXX</strong> 
<br>
<br>
<br>
<table style="border-collapse: collapse; width: 100%; height: 17px;" border="1">
  <tbody>
    <tr style="height: 17px; border-style: none;">
      <td style="width: 66.5706%; height: 17px; text-align: center; border-style: hidden;">
        <span style="font-size: 10pt; font-family: arial, helvetica, sans-serif;">
          <a href="https://UUUUUU/" target="_blank" class="cloudHQ__gmail_elements_final_btn" style="background-color: #242052; color: #ffffff; border: 1px solid #000000; border-radius: 3px; box-sizing: border-box; font-size: 13px; font-weight: bold; line-height: 42px; padding: 12px 24px; text-align: center; text-decoration: none; text-transform: uppercase; vertical-align: middle;" rel="noopener">Visite ahora WWWWWW para ver sus datos</a>
        </span>
      </td>
      <td style="width: 33.4294%; height: 17px; text-align: center; border-style: hidden;">
        <br>
        <br>
      </td>
    </tr>
    <tr>
      <td style="width: 66.5706%; text-align: center; border-style: hidden;">
        <span style="font-size: 10pt; font-family: arial, helvetica, sans-serif;">
          <span style="font-size: 10pt; font-family: arial, helvetica, sans-serif;">
            <br>
          </span>
        </span>
        <div style="text-align: center;">
          <span style="font-size: 10pt; font-family: arial, helvetica, sans-serif;">WWWWWW - Intranet de WWWWWW.</span>
        </div>
        <div style="text-align: center;">
          <span style="font-size: 10pt; font-family: arial, helvetica, sans-serif;">Este es un correo enviado autom&aacute;ticamente, por favor, no responda.</span>
        </div>
      </td>
      <td style="width: 33.4294%; text-align: center; border-style: hidden;">
        <br>
      </td>
    </tr>
  </tbody>
</table>
<div style="text-align: center;">
  <br>
</div>
<div style="text-align: center;">
  <br>
</div>
<br>
<div style="text-align: center;">&nbsp;</div>
"""

email_asunto_factura = "Factura MRW"

email_content_bienvenida_clave = """
<h2>¡Hola YYYYYY!</h2>
<h3>¡Le damos la bienvenida a&nbsp; 
  <img src="https://UUUUUU/logo.png" alt="Logo WWWWWW" width="49" height="20"> WWWWWW!
</h3>
<br>A partir de este momento podr&aacute; como usuario de MRW, acceder a sus facturas, notificaciones y tarifas en una 
<strong>ZONA PRIVADA</strong>. 
<br>
<br>Esperamos que disfrute de todas las ventajas del espacio para clientes. 
<br>
<br>Adem&aacute;s, recibir&aacute; un aviso en esta direcci&oacute;n de correo electr&oacute;nico cada vez que su factura, tarifa o notificaci&oacute;n est&eacute;n disponibles. 
<br>
<br>Ha sido registrado con los siguientes datos: 
<br>
<br>
<br>
<table style="border-collapse: collapse; width: 100%; height: 17px;" border="1">
  <tbody>
    <tr style="height: 17px; border-style: none;">
      <td style="width: 62.1038%; height: 17px; text-align: center; border-style: hidden;">
        <span style="font-size: 10pt; font-family: arial, helvetica, sans-serif;">Ruta de acceso:&nbsp; &nbsp; 
          <a href="https://UUUUUU" target="_blank" rel="noopener" title="Web WWWWWW">https://UUUUUU</a>
        </span> 
        <br>
        <br>
        <span style="font-size: 10pt; font-family: arial, helvetica, sans-serif;">Su identificaci&oacute;n de usuario es: XXXXXX</span> 
        <br>
        <br>
        <span style="font-size: 10pt; font-family: arial, helvetica, sans-serif;">Su clave: ****** 
          <br>
          <br>
          <a href="https://UUUUUU/index.php/login?clear=1" target="_blank" class="cloudHQ__gmail_elements_final_btn" style="background-color: #242052; color: #ffffff; border: 1px solid #000000; border-radius: 3px; box-sizing: border-box; font-size: 13px; font-weight: bold; line-height: 42px; padding: 12px 24px; text-align: center; text-decoration: none; text-transform: uppercase; vertical-align: middle;" rel="noopener">Acceda ahora</a>
        </span>
      </td>
      <td style="width: 37.8962%; height: 17px; text-align: center; border-style: hidden;">
        <br>
        <br>
      </td>
    </tr>
  </tbody>
</table>
<div style="text-align: center;">
  <br>
</div>
<div style="text-align: center;">
  <br>
  <br>
</div>
<div style="text-align: center;">
  <br>
</div>
<br>Recuerde que en WWWWWW estamos siempre a su disposici&oacute;n en todos nuestros canales. 
<br>
<br>Gracias por confiar en nosotros. 
<br>
<br>PD: Por su seguridad, recuerde que sus claves son extrictamente personales, protegen informaci&oacute;n confidencial. 
<br>
<br>
<br>
<table style="border-collapse: collapse; width: 100%;" border="1">
  <tbody>
    <tr>
      <td style="width: 66.1383%; border-style: hidden;">
        <div style="text-align: center;">
          <span style="font-size: 10pt; font-family: arial, helvetica, sans-serif;">WWWWWW - Intranet de WWWWWW.</span>
        </div>
        <div style="text-align: center;">
          <span style="font-size: 10pt; font-family: arial, helvetica, sans-serif;">Este es un correo enviado autom&aacute;ticamente, por favor, no responda.</span>
        </div>
      </td>
      <td style="width: 33.8617%; border-style: hidden;">&nbsp;</td>
    </tr>
  </tbody>
</table>
<br>
<div style="text-align: center;">&nbsp;</div>

"""
