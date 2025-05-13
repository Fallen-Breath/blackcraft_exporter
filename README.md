# BlackCraft Exporter

[![License](https://img.shields.io/github/license/Fallen-Breath/blackcraft_exporter.svg)](http://www.gnu.org/licenses/gpl-3.0.html)
[![Issues](https://img.shields.io/github/issues/Fallen-Breath/blackcraft_exporter.svg)](https://github.com/Fallen-Breath/blackcraft_exporter/issues)
[![PyPI Version](https://img.shields.io/pypi/v/blackcraft_exporter.svg?label=PyPI)](https://pypi.org/project/blackcraft_exporter)
[![Docker](https://img.shields.io/docker/v/fallenbreath/blackcraft_exporter/latest?label=DockerHub)](https://hub.docker.com/r/fallenbreath/blackcraft_exporter)

A [blackbox_exporter](https://github.com/prometheus/blackbox_exporter)-like prober for Minecraft

## To run

BlackCraft Exporter requires no configuration file and can be started with no extra argument

By default, it will listen on tcp `0.0.0.0:9165`. Run with `--help` argument to see all available CLI arguments

### with PyPI

> [!IMPORTANT]
> BlackCraft Exporter is a standalone application and has strict version requirements for its dependent Python packages.
> It's highly suggested to install it with [pipx](https://github.com/pypa/pipx), 
> or install it in a dedicated [venv](https://docs.python.org/3/library/venv.html) environment

BlackCraft Exporter is available on PyPI: [blackcraft_exporter](https://pypi.org/project/blackcraft_exporter/)
as a regular python package. It requires Python >= 3.11 to run

You can install it with [pipx](https://github.com/pypa/pipx):

```bash
pipx install blackcraft_exporter
```

Then you should be able to run it using the `blackcraft_exporter` command (make sure your pipx binary $PATH has been [set](https://pipx.pypa.io/stable/installation/#installing-pipx) correctly)

```bash
$ blackcraft_exporter --version
BlackCraft Exporter v0.1.7
$ blackcraft_exporter
41832 2025-03-16 09:10:18.367 - INFO:     Starting BlackCraft Exporter v0.1.7
41832 2025-03-16 09:10:18.367 - INFO:     Started server process [41832]
41832 2025-03-16 09:10:18.368 - INFO:     Waiting for application startup.
41832 2025-03-16 09:10:18.368 - INFO:     Application startup complete.
41832 2025-03-16 09:10:18.368 - INFO:     Uvicorn running on http://0.0.0.0:9165 (Press CTRL+C to quit)
```

### with docker

BlackCraft Exporter is available on DockerHub: [fallenbreath/blackcraft_exporter](https://hub.docker.com/r/fallenbreath/blackcraft_exporter)

```bash
docker run --rm -p 9165/tcp fallenbreath/blackcraft_exporter
```

### manual installation

1. Install [poetry](https://python-poetry.org/)
2. Get the repository, run `poetry install` inside
3. Run `python -m blackcraft_exporter`

## To use

### Basic usage

Just like the blackbox exporter, you need to send an HTTP GET request to the `/probe` endpoint
to get the metrics of the target Minecraft server

```bash
curl http://localhost:9165/probe?type=java&target=mc.example.com
```

Query parameters:

- `type`: The type of the Minecraft server. Options: `java`, `bedrock`
- `target`: The address to the Minecraft server
- `timeout`: (optional) The maximum request timeout in seconds, including all steps inside probing. Default: `10`
- `mimic`: (optional, java only) Override the hostname and port in the handshake packet. By default, the `target` parameter will be used
- `proxy`: (optional, java only) If provided, connect to the server using the given proxy address
  - Supported http, socks4, socks5 proxy. See the [python-socks](https://github.com/romis2012/python-socks) library for more information
  - The address syntax is something like `http://127.0.0.1:1081` or `socks5://user:password@127.0.0.1:1080`
- `max_attempts`: (optional) The maximum probe attempts, including retries. Note that each attempt has the timeout of `timeout / max_attempts`. Default: `1`

### Prometheus

Example config for Minecraft Java Edition:

```yml
scrape_configs:
  - job_name: blackcraft          # Can be any name you want
    metrics_path: /probe
    params:
      type: [ java ]                # Set type to java
    static_configs:
      - targets:
        - 192.168.1.1             # IP only
        - 192.168.1.1:25566       # IP with port
        - mc.example.com          # Hostname only. SRV is supported
        - mc.example.com:25566    # Hostname with port
    relabel_configs:
      - source_labels: [ __address__ ]
        target_label: __param_target
      - target_label: __address__
        replacement: localhost:9165  # Your BlackCraft Exporter's hostname:port
```

Example config with more flexible control on the targets

```yml
scrape_configs:
  - job_name: blackcraft          # Can be any name you want
    metrics_path: /probe
    static_configs:
      - targets:
        - labels: 
            instance: 'My Java Server'  # Its disabled name in grafana
            type: 'java'
          targets: [ 'mc.example.com' ]
        - labels: 
            instance: 'My Bedrock Server'
            type: 'bedrock'
          targets: [ 'bedrock.example.com:25566' ]
    relabel_configs:
      - source_labels: [ type ]  # maps the "type" label into the query parameter
        target_label: __param_type
      - source_labels: [ __address__ ]
        target_label: __param_target
      - target_label: __address__
        replacement: localhost:9165  # Your BlackCraft Exporter's hostname:port
```

### Grafana

Example dashboard for BlackCraft Exporter: https://grafana.com/grafana/dashboards/22915
