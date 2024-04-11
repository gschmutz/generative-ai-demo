# Generative AI with RAG (retrieval augmented generation) Demo

Important Links

  * <http://github.com/trivadispf/platys-modern-data-platform>
  * <http://github.com/gschmutz/generative-ai-demo>

Show the application running on 

* Ollama Web UI: <http://10.0.4.68:28338/>

Now ask the following questions: 

1. `in football what is a VAR`
1. `can a player asked for an incident to be reviewed by the VAR`

Now show the RAG application

* Flowise: <http://10.0.4.68:28340/>

Now ask the question: `can a player asked for an incident to be reviewed by the VAR`

## Create the Platys stack

Quickly navigate to <https://github.com/TrivadisPF/platys-modern-data-platform/tree/develop>

show how platys works: <https://github.com/TrivadisPF/platys/blob/master/documentation/images/platys-tool.png>

```bash
export DOCKER_HOST=unix:///Users/guido.schmutz/.orbstack/run/docker.sock
export PUBLIC_IP=10.0.4.68
export DOCKER_HOST_IP=localhost

mkdir platys-llm-demo
cd platys-llm-demo

platys init -n demo-platform --stack trivadis/platys-modern-data-platform --stack-version develop --structure flat
```

edit the config.yml

```bash
code .
```

Enable the following services

  * `FLOWISE_enable`
  * `CHROMA_enable`
  * `OLLAMA_enable`
  * `OLLAMA_WEBUI_enable`
  * `REDIS_STACK_enable`
  * `REDIS_INSIGHT_enable`
  * `VECTOR_ADMIN_enable`
  * `POSTGRESQL_enable`


If you run Ollama locally (recommended if you run on a Mac)

```bash
OLLAMA_enable: true
OLLAMA_url: http://${PUBLIC_IP}:11434
```

if you are running Ollama on docker, specify the model(s) to download (as a comma-separated list)

```bash
OLLAMA_llms: llama2,mistral
```

```bash
platys gen
```

Navigate to <http://markdown-viewer.platys-llm-demo.orb.local/>

## Ollama

### Running locally

make sure that you have the `llama2` model available

```bash
ollama pull llama2
```

Check for the models

```bash
ollama list
```

### Running on docker

```bash
docker exec -ti ollama ollama list
```


## Flowise

### load the documents

Load the flow `webpage-load.json`

Open the `webpage-load` flow and on the last node add the **Connect Credential**:

  * **CREDENTIAL NAME:** `chroma`
  * **Chroma Api Key:** `abc123!`


### Ask questions

Load the flow `webpage-ask-questions.json`

Open the `webpage-ask-questions ` flow and on the **Redis-Backed Chat Memory** node and add the **Connect Credential**:

  * click on `Redis URL`
  * **CREDENTIAL NAME:** `redis`
  * **Redis URL:** `redis://redis-stack-1:6379`

Now ask the question: `can a player asked for an incident to be reviewed by the VAR
`  