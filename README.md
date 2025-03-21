# 🔎 Multi Agentic Research (RAG)

- Multi-agentic researcher researches the query/topic from documents fetched from Tavily Search Engine.
- The output is the report about the query/topic based on the retrieved documents.
- The graph ends when the hallucination point is 1, or else the graph restarts from collecting documents from Tavily 
for generated queries to retrieve related info.

## Demo
[![Website](https://img.shields.io/badge/Demo%20Website-google%20clould%20platform-teal?style=for-the-badge&logo=world&logoColor=white&color=0891b2)](https://app-930736962858.europe-west3.run.app/docs)
![img.png](./media/Screenshot%202025-03-05%20at%2016.38.14.png)
![img.png](./media/Screenshot%202025-03-05%20at%2016.38.26.png)
![img.png](./media/Screenshot%202025-03-05%20at%2016.38.57.png)

## Work in progress

1. INTERNAL DOCUMENTATION
2. Access to documents to reliable sources for academic sources (sciencedirect, elsevier, springer, ...)
3. Construct more detail report (e.g Write report for each query)
4. Human input (e.g research plan, sources to fetch documents for queries)

### Installation

1. Install Python 3.12 or later. [Guide](https://www.tutorialsteacher.com/python/install-python).
2. Clone the project and navigate to the directory:

    ```bash
    git clone https://github.com/maihoangbichtram/multi_agentic_rag
    cd multi_agentic_rag
    ```

3. Set up API keys by exporting them or storing them in a `.env` file.

    ```bash
    Copy .env.example to .env
    ```

4. Create and Activate virtual environment

   4.1 In terminal:
   Create a virtual environment

   ```bash
   python3 -m venv .venv
   ```
   Activate the virtual environment

   ```bash
   . .venv/bin/activate
   ```
   4.2 Poetry

   ```bash
   poetry shell
   ```
5. Install dependencies and start the server:

    5.1 In terminal:
    ```bash
    pip install -r requirements.txt
    ```
    5.2 Poetry
   ```bash
   poetry install
   ```
6. Start the application

   6.1 In terminal:

   ```bash
   python app/main.py
   ```
   6.2 Poetry
   ```bash
   poetry run uvicorn app.main:app --reload --timeout-keep-alive 720
   ```

## Deployment
### Google Cloud
#### Prerequisites
- Google Cloud Account
- Google CLI
- Service account under IAM (to access to Google Cloud services.)
- (Access) Key downloaded as json (for the service account)
#### Terraforming GC Components
##### Tf files
- main.tf
- variables.tf
- terraform.tfvars (not public): Declare values for variables
   ```bash
   #  GCP settings
   project_id = "project_id"

   # GCP region
   region = "europe-west3"

   #  Artifact registry repository
   registry_id = "registry_id"
   ```
##### Commands
Run commands in order
- `terraform init`
- `terraform plan`
- `terraform apply`: create the GCP resources

##### Note
Enable GCP APIs manually if Terraform reports errors with permission:
```bash
gcloud services enable artifactregistry.googleapis.com
gcloud services enable run.googleapis.com
```
#### Deploying to cloud
- Create `requirements.txt` for docker file
```bash
poetry export -f requirements.txt --output requirements.txt
```
##### Build and test docker image locally
```bash
docker build --pull --rm -f "Dockerfile" -t <image_name>:latest "."
```
```bash
docker run --rm -it -p 8080:8080/tcp <image_name>:latest
```
##### Build docker image for Cloud Run
- Create builder
```bash
docker buildx create --name <builder_name> --bootstrap --use
```
- Build the image
```bash
docker buildx build --file Dockerfile \
  --platform linux/amd64 \
  --builder <builder_name> \
  --progress plain \
  --build-arg DOCKER_REPO=<gcd_region>-docker.pkg.dev/<gcd_project_id>/<gcd_repository_name>/ \
  --pull --push \
  --tag <gcd_region>-docker.pkg.dev/<gcd_project_id>/<gcd_repository_name>/<image_name>:latest .
```
##### Deploy
```bash
gcloud run deploy app \                             
--image <gcd_region>-docker.pkg.dev/<gcd_project_id>/<gcd_repository_name>/<image_name>:latest \
--region <gcd_region> \
--platform managed \
--allow-unauthenticated \
--set-env-vars GOOGLE_API_KEY=<GOOGLE_API_KEY>,TAVILY_API_KEY=<TAVILY_API_KEY>,CO_API_KEY=<CO_API_KEY>
```





