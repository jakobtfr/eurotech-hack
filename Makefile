.PHONY: doctor sanity lint format test validate-registry build-stub run-stub calibrate-stub evaluate-stub render-stub freeze-stub demo mcp mcp-smoke smoke

doctor:
	uv run python scripts/doctor.py --config configs/demo.yaml

sanity: doctor validate-registry lint test

lint:
	uv run ruff check .

format:
	uv run ruff format .

test:
	uv run pytest

validate-registry:
	uv run python scripts/validate_registry.py data/registry/sources.jsonl

build-stub:
	uv run python -m src.data.build --config configs/data/stub.yaml

run-stub:
	uv run python -m src.models.run --config configs/models/subspacead.yaml --split data/splits/stub_v0.csv --shots 1 --seed 17

calibrate-stub:
	uv run python -m src.evaluation.calibrate --run "$${RUN:?set RUN=runs/<run_id>}"

evaluate-stub:
	uv run python -m src.evaluation.evaluate --run "$${RUN:?set RUN=runs/<run_id>}"

render-stub:
	uv run python -m src.rendering.render --run "$${RUN:?set RUN=runs/<run_id>}"

freeze-stub:
	uv run python -m src.packaging.freeze --run "$${RUN:?set RUN=runs/<run_id>}"

demo:
	uv run python -m src.packaging.build_demo --config configs/demo.yaml

mcp:
	uv run python -m src.mcp_server

mcp-smoke:
	uv run pytest tests/test_mcp_server.py

smoke: build-stub
	@RUN=$$(uv run python -m src.models.run --config configs/models/subspacead.yaml --split data/splits/stub_v0.csv --shots 1 --seed 17 --plain | tail -n 1); \
	uv run python -m src.evaluation.calibrate --run "$$RUN"; \
	uv run python -m src.evaluation.evaluate --run "$$RUN"; \
	uv run python -m src.rendering.render --run "$$RUN"; \
	uv run python -m src.packaging.freeze --run "$$RUN"; \
	uv run python scripts/validate_run.py "$$RUN"
