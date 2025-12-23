from __future__ import annotations

from pathlib import Path
from typing import Dict
import yaml

from .config import CountyConfig


def load_county_configs(config_dir: Path) -> Dict[str, CountyConfig]:
    configs: Dict[str, CountyConfig] = {}
    for p in sorted(config_dir.glob("*.yaml")):
        data = yaml.safe_load(p.read_text())
        cfg = CountyConfig.model_validate(data)
        configs[cfg.county.lower()] = cfg
    return configs
