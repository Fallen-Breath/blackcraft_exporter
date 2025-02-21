# BlackCraft Exporter

[![License](https://img.shields.io/github/license/Fallen-Breath/blackcraft_exporter.svg)](http://www.gnu.org/licenses/gpl-3.0.html)
[![Issues](https://img.shields.io/github/issues/Fallen-Breath/blackcraft_exporter.svg)](https://github.com/Fallen-Breath/blackcraft_exporter/issues)
[![Docker](https://img.shields.io/docker/v/fallenbreath/blackcraft_exporter/latest)](https://hub.docker.com/r/fallenbreath/blackcraft_exporter)

A [blackbox_exporter](https://github.com/prometheus/blackbox_exporter)-like prober for Minecraft

## To run

The BlackCraft Exporter requires no configuration file and can be started with no extra argument.

By default, it will listen on tcp `0.0.0.0:9165`. Run with `--help` argument to see all available CLI arguments

### with pip

TODO

### with docker

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
curl http://localhost:9115/probe?type=java&target=mc.example.com
```

Query parameters:

- `type`: The type of the Minecraft server. Options: `java`, `bedrock`
- `target`: The address to the Minecraft server
- `timeout`: (optional) The maximum request timeout in seconds, including all steps inside probing. Default: `10`

### Prometheus

Example config for Minecraft Java Edition:

```yml
scrape_configs:
  - job_name: blackcraft          # Can be any name you want
    metrics_path: /probe
    params:
      type: [java]                # Set type to java
    static_configs:
      - targets:
        - 192.168.1.1             # IP only
        - 192.168.1.1:25566       # IP with port
        - mc.example.com          # Hostname only. SRV is supported
        - mc.example.com:25566    # Hostname with port
    relabel_configs:
      - source_labels: [__address__]
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
      - source_labels: [type]  # maps the "type" label into the query parameter
        target_label: __param_type
      - source_labels: [__address__]
        target_label: __param_target
      - target_label: __address__
        replacement: localhost:9165  # Your BlackCraft Exporter's hostname:port
```

### Grafana

Example dashboard for the BlackCraft Exporter: https://grafana.com/grafana/dashboards/22915
