### Run Locally

```bash
# 1. install python deps
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. front‑end deps
cd dashboard && npm install && cd ..

# 3. start everything
docker compose up --build

# open    →  http://localhost:3000
# backend →  http://localhost:8000/docs  (FastAPI swagger)

