from pathlib import Path

import yaml


ROOT = Path(__file__).parents[2]


def test_production_compose_has_required_services_and_internal_network():
    document = yaml.safe_load((ROOT / "deployment/docker-compose.prod.yml").read_text())
    assert {"postgres", "redis", "backend", "worker", "nginx"} <= set(document["services"])
    assert document["networks"]["internal"]["internal"] is True
    assert "POSTGRES_PASSWORD" in (ROOT / "deployment/docker-compose.prod.yml").read_text()


def test_nginx_serves_spa_and_proxies_api():
    config = (ROOT / "deployment/nginx/nginx.conf").read_text()
    assert "try_files $uri $uri/ /index.html" in config
    assert "proxy_pass http://agnidrishti_backend/" in config
