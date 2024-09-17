# list all files in data/evaluation folder

import os

def list_files():
    files = os.listdir('data/evaluations')
    if '.DS_Store' in files:
        files.remove('.DS_Store')
    return files

if __name__ == '__main__':
    files = list_files()
    print('Select a file to upload:')
    for i in range(len(files)):
        print(str(i+1)+':', files[i])
    file_num = int(input())
    file = files[file_num-1]
    print('You selected:', file)
    print('Sending file to email...')
    username = file.split('_')[0]

    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    # Configurazione dell'email
    sender_email = 'erpini.1936274@studenti.uniroma1.it'
    receiver_email = 'erpini.1936274@studenti.uniroma1.it'
    password = 'wmji xsmp iuch euzd'

    # Crea il messaggio
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = 'Valutazione ' + username

    # Corpo dell'email
    body = ' ' 
    msg.attach(MIMEText(body, 'plain'))

    # Allega il file
    from email.mime.base import MIMEBase
    from email import encoders
    filename = file
    attachment = open(f'data/evaluations/{filename}', 'rb')
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename= ' + filename)
    msg.attach(part)


    # Connessione al server SMTP e invio dell'email
    try:
        # Usa il server SMTP di Gmail come esempio; modifica come necessario
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Abilita la crittografia
            server.login(sender_email, password)  # Effettua il login
            server.sendmail(sender_email, receiver_email, msg.as_string())  # Invia l'email

            print('Email inviata con successo!')
    except Exception as e:
        print(f'Errore durante l\'invio dell\'email: {e}')
