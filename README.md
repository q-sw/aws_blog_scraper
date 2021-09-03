# aws_blog_scraper
Scraper Python du blog AWS (FR et EN) pour récupérer les derniers articles postés avec la possibilité de stocker les informations dans un fichier en local ou dans un bucket S3. 

## Sommaire:
1. [Construire l'image](#Construire-l-image)
2. [Utiliser l'image](#Utiliser-l-image)
	1. [Docker](#Docker)
	2. [Job Kubernetes](#Job-Kubernetes)

## Construire l'image
Pour construire l'image **DOCKER** qui porte le script **Python** il faut exécuter la commande: 
```
make build-image
```
ou directement la commande:
```
docker build -f "Dockerfile" -t aws-blog-scraper:1.0 "."
```

## Utiliser l'image:
### Docker:
Avec les paramètres par défaut

```
docker run aws-blog-scraper:1.0
````

L'output sera une liste avec l'ensemble des nouveaux articles avec leurs date de publications.  
Pour personnaliser, les categories des artibles à récupérer il faut modifier le fichier */opt/config.json* (chemin dans le container)

```
docker run -v myconfig.json:config.json aws-blog-scraper:1.0
```

Il est possible de sauvegarder l'output dans un fichier en local. Pour cela il faut modifier les paramètres suivant de la fichier config.json. 
```
"backup_result": true,
	"backup_destination": {
		"type": "local",
		"file_name": "result.json",
		"path": "/opt/result",
		"bucket_name": "" 
	},
```
ci-dessous la commande pour etre capable de récupérer les informations en dehors du container.
```
docker run -v myconfig.json:config.json -v /tmp/result:/opt/result aws-blog-scraper:1.0
```
Il est aussi possible de sauvegarder l'output dans un bucket S3. Pour cela il faut modifier les paramètres suivant de la fichier config.json.
```
"backup_result": true,
	"backup_destination": {
		"type": "s3",
		"file_name": "result.json",
		"path": "/opt/result",
		"bucket_name": "mybucket" 
	},
```
il faudra aussi ajouter des variables d'environnement dans le container.
```
docker run -v myconfig.json:config.json --env S3_URL=[URL du bucket] --env AWS_ACCESS_KEY=[ACCESS KEY] --env AWS_SECRET_ACCESS_KEY=[SECRET ACCESS KEY] aws-blog-scraper:1.0
```
ou en utilisant directement un fichier de variable sous la forme:
```
#my_var.txt

S3_URL=
AWS_ACCESS_KEY=
AWS_SECRET_ACCESS_KEY=
```
Commande docker associée:
```
docker run -v myconfig.json:config.json --env-file my_var.txt aws-blog-scraper:1.0
```

### Job Kubernetes:
Avec les paramètres par défaut

```
cd kubernetes/base
kustomize build . | kubectl apply -f -
````
Avec un persistance des données dans S3:
il faut dans un premier temps modifier le fichier *kubernetes/mysecret.txt*
```
cd kubernetes
kustomize build . | kubectl apply -f -
```