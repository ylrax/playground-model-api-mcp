# playground-api-mcp

Simple proyect to test mcp, Ml model and FastApi



# instructions


- launch api:

     uvicorn api.app:app --reload


- launch mcp sever:

     run mcp dev ./mcp/server.py


This may require having node installed with:

    winget install OpenJS.NodeJS.LTS


- agent

     uv run agent/singleagent.py