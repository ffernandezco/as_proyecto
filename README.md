# Agenda cultural de Euskadi

**Francisco Fernández**

Administración de Sistemas / Grado en Ingeniería Informática de Gestión y Sistemas de Información

*[UPV-EHU](https://www.ehu.eus/) / Curso 2024-25*

## Introducción

Este proyecto propone la creación de una aplicación web funcional basándose en los contenedores de Docker y, de forma opcional, realizar el despliegue equivalente de Kubernetes.

En este caso, la idea es crear un portal web interactivo que permita consultar la Agenda Cultural de Euskadi con actualizaciones en tiempo real. Para ello, se ha hecho uso de la información proporcionada en el [portal Open Data del Servicio web del Gobierno Vasco](https://opendata.euskadi.eus/catalogo/-/kulturklik-agenda-cultural/), que provee diferentes formas de acceso a la información completa.

Se ha elegido hacer uso de un servidor web basado en nginx, que se encargará de redirigir las peticiones a un servidor Flask. La información de los eventos queda registrada en una base de datos PostgreSQL y, mediante un entorno adicional basado en Python, se actualizan los datos de los eventos a partir de la [API de Open Data](https://opendata.euskadi.eus/apis/-/apis-open-data/) para contar con actualizaciones en tiempo real. Además, se cuenta con un entorno adicional que permite exportar los detalles de los eventos a un formato PDF, siendo más cómodo para imprimir o compartir en caso de ser necesario.

## Despliegue mediante Docker

Los ficheros necesarios para realizar el despliegue mediante Docker se encuentran en [la carpeta Docker](/Docker/). Para evitar la exposición de contraseñas, deberá crearse un secreto que se encargará de guardar la contraseña que utilizará la base de datos PostgreSQL. Basta con crear un archivo en el directorio *secrets* que contenga en texto plano la contraseña.

Como se ha creado un entorno Docker Compose, es posible instanciarlo de forma sencilla ejecutando el comando ```docker compose up --build``` desde dicha ruta. De este modo, asumiendo que primero se ha [clonado el repositorio](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) y que se ha realizado la [instalación de Docker y Docker Compose](https://docs.docker.com/get-started/get-docker/) en el equipo, ejecutando los siguientes comandos se puede replicar el escenario:

```bash
$ cd Docker
$ mkdir secrets
$ echo "micontraseña" > ./secrets/postgres_password
$ docker compose up --build
```

## Despliegue mediante Kubernetes

Para realizar el despliegue mediante Kubernetes en un entorno basado en la [funcionalidad de Docker Desktop](https://docs.docker.com/desktop/features/kubernetes/), lo primero que será necesario es definir un objeto de tipo secreto que albergará el nombre de usuario y la contraseña de la base de datos PostgreSQL. Para ello, se debe ejecutar el siguiente comando, modificando *"micontraseña"* por la contraseña deseada:

```bash
$ kubectl create secret generic postgres-secret \
$ --from-literal=POSTGRES_USER="as" \
$ --from-literal=POSTGRES_PASSWORD="micontraseña"
```

A continuación, será necesario ir instanciando cada uno de los objetos de tipo PVC, ConfigMap, Deployment, Service, CronJob e Ingress para un correcto funcionamiento. Tras haber [clonado el repositorio](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository), ejecutando los siguientes comandos pueden inicializarse todos los contenedores, aplicando la configuración del controlador nginx indicada para el Ingress:

```bash
$ cd Kubernetes
$ kubectl apply -f postgres-configmap.yaml
$ kubectl apply -f postgres-pvc.yaml
$ kubectl apply -f postgres-deployment.yaml
$ kubectl apply -f postgres-service.yaml
$ kubectl apply -f adminer-deployment.yaml
$ kubectl apply -f adminer-service.yaml
$ kubectl apply -f updater-cronjob.yaml
$ kubectl apply -f gotenberg-deployment.yaml
$ kubectl apply -f gotenberg-service.yaml
$ kubectl apply -f flask-deployment.yaml
$ kubectl apply -f flask-service.yaml
$ kubectl apply -f nginx-configmap.yaml
$ kubectl apply -f nginx-deployment.yaml
$ kubectl apply -f nginx-service.yaml
$ kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.11.3/deploy/static/provider/cloud/deploy.yaml
$ kubectl apply -f ingress.yaml
```

## Servicios disponibles
### Servicios

* **nginx:**
  * Servidor nginx configurado para redirigir el tráfico al servicio Flask.
  * Imagen: https://hub.docker.com/_/nginx

* **postgres:**
  * Servidor de base de datos PostgreSQL para almacenar información de eventos.
  * Imagen: https://hub.docker.com/_/postgres

* **adminer:**
  * Herramienta de administración de bases de datos para PostgreSQL.
  * Imagen: https://hub.docker.com/_/adminer/

* **updater:**
  * Actualiza la base de datos PostgreSQL con datos de la API de Open Data Euskadi.
  * Imagen (propia): https://hub.docker.com/r/franciscofdez/as-updater
    * Soporta arquitecturas ARM64 y AMD64.
    * Versión para Kubernetes: https://hub.docker.com/r/franciscofdez/as-updater-k8s

* **flask:**
  * Proporciona una interfaz web para interactuar con la base de datos y el servicio Gotenberg.
  * Imagen (propia): https://hub.docker.com/r/franciscofdez/as-flask
    * Soporta arquitecturas ARM64 y AMD64.
    * Versión para Kubernetes: https://hub.docker.com/r/franciscofdez/as-flask-k8s

* **gotenberg:**
  * Genera archivos PDF a partir de las solicitudes del servicio Flask.
  * Imagen: https://hub.docker.com/r/gotenberg/gotenberg:8