
backend-setup:
	cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt

backend-run:
	cd backend && source venv/bin/activate && uvicorn app.main:app --reload

frontend-setup:
	cd frontend && npm install

frontend-run:
	cd frontend && npm run dev

docker-up:
	docker-compose up --build

test:
	cd backend && pytest