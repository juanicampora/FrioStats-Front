> 👉 **Para actualizar en docker** - Abrir `Docker` y ejecutar los siguientes comandos en cmd estando en el directorio del proyecto:

```bash
$ docker build -t juaniiic/friostats-front . 
$ docker push juaniiic/friostats-front 
```
> Recordar eliminar el anterior docker con `docker rmi juaniiic/friostats-front` (probar)
> Luego entrar a portainer.io y actualizar la imagen de docker ( http://186.13.28.124:9000/ )

Visit `http://localhost:5085` in your browser. The app should be up & running.

<br />

### ✨ Crear un nuevo `.env` usando el sample `env.sample`

The meaning of each variable can be found below:

- `DEBUG`: if `True` the app runs in develoment mode
  - For production value `False` should be used
- `ASSETS_ROOT`: used in assets management
  - default value: `/static/assets`
- `OAuth` via Github
  - `GITHUB_ID`=<GITHUB_ID_HERE>
  - `GITHUB_SECRET`=<GITHUB_SECRET_HERE>

<br />

### 👉 Set Up for `Windows`

> Instalar modulos via `VENV`

```
$ virtualenv env
$ .\env\Scripts\activate
$ pip install -r requirements.txt

```

### 👉 Iniciar el proyecto

> Click derecho al archivo run.py + "Ejecutar el archivo python en terminal"

### ✨ Estructura del proyecto

```bash
< PROJECT ROOT >
   |
   |-- apps/
   |    |
   |    |-- home/                           # A simple app that serve HTML files
   |    |    |-- routes.py                  # Define app routes
   |    |
   |    |-- authentication/                 # Handles auth routes (login and register)
   |    |    |-- routes.py                  # Define authentication routes
   |    |    |-- models.py                  # Defines models
   |    |    |-- forms.py                   # Define auth forms (login and register)
   |    |
   |    |-- static/
   |    |    |-- <css, JS, images>          # CSS files, Javascripts files
   |    |
   |    |-- templates/                      # Templates used to render pages
   |    |    |-- includes/                  # HTML chunks and components
   |    |    |    |-- navigation.html       # Top menu component
   |    |    |    |-- sidebar.html          # Sidebar component
   |    |    |    |-- footer.html           # App Footer
   |    |    |    |-- scripts.html          # Scripts common to all pages
   |    |    |
   |    |    |-- layouts/                   # Master pages
   |    |    |    |-- base-fullscreen.html  # Used by Authentication pages
   |    |    |    |-- base.html             # Used by common pages
   |    |    |
   |    |    |-- accounts/                  # Authentication pages
   |    |    |    |-- login.html            # Login page
   |    |    |    |-- register.html         # Register page
   |    |    |
   |    |    |-- home/                      # UI Kit Pages
   |    |         |-- index.html            # Index page
   |    |         |-- 404-page.html         # 404 page
   |    |         |-- *.html                # All other pages
   |    |
   |  config.py                             # Set up the app
   |    __init__.py                         # Initialize the app
   |
   |-- requirements.txt                     # App Dependencies
   |
   |-- .env                                 # Inject Configuration via Environment
   |-- run.py                               # Start the app - WSGI gateway
   |
   |-- ************************************************************************
```
