from fastapi import FastAPI

app = FastAPI()


@app.get('/')
async def probe():
	return 'BlackCraft Exporter is running'


@app.get('/probe')
async def probe():
	pass


@app.get('/metrics')
async def probe():
	pass
