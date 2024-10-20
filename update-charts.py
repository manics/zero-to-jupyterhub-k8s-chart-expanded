#!/usr/bin/env python
# coding: utf-8
import os
import re
import requests
import shutil
import tarfile
from tarfile import TarFile
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse
import yaml


def get_chart(name, version, url):
    if os.path.exists(version):
        raise ValueError(f"{version} already exists")
    outname = urlparse(url).path.rsplit("/")[-1]
    with open(outname, "wb+") as tmp:
        print(f"Downloading {url} ➡ {outname}")
        r = requests.get(chart, stream=True)
        r.raise_for_status()
        tmp.write(r.content)
    t = tarfile.open(outname)
    for item in t.getmembers():
        if not item.name.startswith(f"{name}/"):
            raise Exception(f"Archive member does not start with {name}/: {item.name}")
    t.extractall()
    t.close()
    shutil.move(name, version)
    os.remove(outname)


def get_z2jh_releases():
    index_url = "https://hub.jupyter.org/helm-chart/index.yaml"
    r = requests.get(index_url)
    r.raise_for_status()
    index = yaml.safe_load(r.text)

    version_re = r"v?[\d\.]+(-(alpha|beta|rc)[\d\.]+)?$"
    charts = {}
    for e in index["entries"]["jupyterhub"]:
        if re.match(version_re, e["version"]):
            if len(e["urls"]) != 1:
                raise Exception(f"Expected one URL, received {e['urls']}")
            charts[e["version"]] = e["urls"][0]
    return charts


charts = get_z2jh_releases()
for (version, chart) in charts.items():
    if not os.path.exists(version):
        get_chart("jupyterhub", version, chart)
