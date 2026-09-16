"""
accounts_config.py — Configuracion centralizada de cuentas Gmail y campanas.
12 cuentas Gmail con app password + OAuth client ID.
1 campana: Servicio Tecnico de Computadoras y Productos de Tecnologia.
"""

import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "inputs", "contacts.db")
CREDENTIALS_DIR = os.path.join(PROJECT_ROOT, "data", "credentials", "google")
LOG_DIR = os.path.join(PROJECT_ROOT, "logs", "campaigns")

# === 12 CUENTAS GMAIL ===
ACCOUNTS = [
    {
        "email": "wwwlanuscomputacion@gmail.com",
        "app_password": "szbm rxyk kodl ilgn",
        "client_secret": "client_secret_997721949653-lb4ofpob473p7bsh0kluohgukls4rbd3.apps.googleusercontent.com.json",
    },
    {
        "email": "adrianaavila131969@gmail.com",
        "app_password": "wwra bzce lntl cjxs",
        "client_secret": "client_secret_956111709211-dpj85mip1napq31voos9oo0sekv4b90p.apps.googleusercontent.com.json",
    },
    {
        "email": "fernando1141967@gmail.com",
        "app_password": "jdni pnvh boaq nhgm",
        "client_secret": "client_secret_188518434756-cvvbmi8t1673t22hqfgrnhhg2vkhidmi.apps.googleusercontent.com.json",
    },
    {
        "email": "selvaggiesteban9@gmail.com",
        "app_password": "krlt orio ennc fimx",
        "client_secret": "client_secret_437651612224-e601a0ei1nd9hfi6gc4jh9hdbs1is19o.apps.googleusercontent.com.json",
    },
    {
        "email": "selvaggiesteban4@gmail.com",
        "app_password": "dfxw jvft icwm jbdq",
        "client_secret": "client_secret_484229814609-r6o0v0b87mn7a5b825q2h35l82ag2sc4.apps.googleusercontent.com.json",
    },
    {
        "email": "selvaggiesteban11@gmail.com",
        "app_password": "aldv hyyb nvuq ntfj",
        "client_secret": "client_secret_900132637788-34u5rnedb16k20d5es0mrpol1j06gqtn.apps.googleusercontent.com.json",
    },
    {
        "email": "marketing1a1oficial@gmail.com",
        "app_password": "atcd yuvl ylzf ezcj",
        "client_secret": "client_secret_608213982273-7ug4nvhu9houumph44h5975c0ioj1k8v.apps.googleusercontent.com.json",
    },
    {
        "email": "selvaggiconsultores@gmail.com",
        "app_password": "pyoy fuia yhmh abpb",
        "client_secret": "client_secret_798738471459-32s1b2oqp22mgigh29p9gff21icetdk3.apps.googleusercontent.com.json",
    },
    {
        "email": "estebanmfwd@gmail.com",
        "app_password": "deqf wsjg lysi gtta",
        "client_secret": "client_secret_1019520889342-bn7r87ihd09aafbvi428bqvcihv8k99d.apps.googleusercontent.com.json",
    },
    {
        "email": "selvaggiesteban1@gmail.com",
        "app_password": "onmh pbwv xsrg wikw",
        "client_secret": "client_secret_32606590971-2pksi1799pa5387iam3kel19j5paqr1p.apps.googleusercontent.com.json",
    },
    {
        "email": "selvaggiesteban2@gmail.com",
        "app_password": "bkbz ddag fmkj xrov",
        "client_secret": "client_secret_109046658774-lka605qhl79fu00a3j1cvib163cusupc.apps.googleusercontent.com.json",
    },
    {
        "email": "marcelagomez7799@gmail.com",
        "app_password": "sxkt usfb cnrk krfd",
        "client_secret": "client_secret_804810259658-j4th7g76nm9gf1nfbkl8l4r1pjg9j5k9.apps.googleusercontent.com.json",
    },
]

# === SMTP CONFIG ===
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

# === CAMPANA: SERVICIO TECNICO ===
CAMPAIGN = {
    "id": "servicio_tecnico_20260803",
    "title": "Servicio Tecnico de Computadoras y Productos de Tecnologia",
    "subject": "Servicio Tecnico de Computadoras y Productos de Tecnologia",
    "message": (
        "Hola, buenos dias. "
        "Como estas? Espero que muy bien. "
        "Me comunico facilitando servicio tecnico de computadoras y productos de tecnologia. "
        "Brindamos soluciones tanto para particulares como para comercios y empresas de la zona. "
        "Si necesitás reparacion, mantenimiento o equipamiento, podes contactarnos. "
        "Quedo a disposicion para lo que necesites.\n\n"
        "Saludos cordiales"
    ),
    "target": "buenos_aires_valid",
}

# === CONFIGURACION DE ENVIO ===
SEND_CONFIG = {
    "bcc_per_email": 50,
    "delay_min": 1,
    "delay_max": 10,
    "delay_pattern": "sinusoidal",
    "start_hour": 7,
    "end_hour": 13,
    "target_day": 0,
    "to_email": "selvaggiesteban@gmail.com",
}
