#!/usr/bin/env python3
"""
phpIPAM Importer vanuit Ansible Inventory
==========================================
Auth:      SSL with App code token
Inventory: inventory.yaml

Structuur in phpIPAM (max 2 niveaus):
  Network-Lab  (parent)
    ├── Site-A | WAN
    ├── Site-A | Providers
    ├── Site-A | Core
    ├── Site-A | Distribution
    ├── Site-A | Access
    ├── Site-A | Clients
    ├── Site-B | Routers
    ├── Site-B | Access
    └── Site-B | Clients
"""

import sys
import re
import ipaddress
import requests
import yaml

# ─── CONFIGURATIE ──────────────────────────────────────────────────────────────
PHPIPAM_URL = "https://10.11.80.202/api"
APP_ID      = "Eindwerk1"
APP_CODE    = "TNfl7qR3iWKoIMJ4OUOliwguHzzxBLzy"
INVENTORY   = "inventory.yaml"
VERIFY_SSL  = False
# ───────────────────────────────────────────────────────────────────────────────

GROUP_MAP = {
    "wan":             {"device_type": "Router",      "role": "WAN Router",             "site": "Site-A", "section": "WAN"},
    "providers":       {"device_type": "Router",      "role": "ISP Provider Router",    "site": "Site-A", "section": "Providers"},
    "core":            {"device_type": "Router",      "role": "Core Router",            "site": "Site-A", "section": "Core"},
    "distribution":    {"device_type": "Switch - L3", "role": "Distribution Switch L3", "site": "Site-A", "section": "Distribution"},
    "access_switches": {"device_type": "Switch - L2", "role": "Access Switch L2",       "site": None,     "section": "Access"},
    "site_b_routers":  {"device_type": "Router",      "role": "Site-B Router",          "site": "Site-B", "section": "Routers"},
    "clients":         {"device_type": "VPCS",        "role": "End-device",             "site": None,     "section": "Clients"},
}

PARENT_SECTION = "Network-Lab"

requests.packages.urllib3.disable_warnings()


# ─── API KLASSE ────────────────────────────────────────────────────────────────

class PhpIPAM:
    def __init__(self, base_url, app_id, app_code):
        self.base     = f"{base_url}/{app_id}"
        self.app_code = app_code
        self._check_connection()

    def _h(self):
        return {"token": self.app_code, "Content-Type": "application/json"}

    def _check_connection(self):
        try:
            r = requests.get(f"{self.base}/sections/", headers=self._h(),
                             verify=VERIFY_SSL, timeout=5)
            if r.status_code == 200:
                print(f"[OK] Verbonden met phpIPAM")
            else:
                print(f"[FOUT] Status {r.status_code}: {r.text[:200]}")
                sys.exit(1)
        except requests.exceptions.ConnectionError:
            print(f"[FOUT] Kan phpIPAM niet bereiken op {self.base}")
            sys.exit(1)

    def get(self, ep):
        r = requests.get(f"{self.base}/{ep}", headers=self._h(), verify=VERIFY_SSL)
        if r.status_code == 404:
            return None
        r.raise_for_status()
        d = r.json()
        return d.get("data") if d.get("success") else None

    def post(self, ep, payload):
        r = requests.post(f"{self.base}/{ep}", json=payload,
                          headers=self._h(), verify=VERIFY_SSL)
        d = r.json()
        if not d.get("success"):
            msg = str(d.get("message", "")).lower()
            if "already exists" in msg or "duplicate" in msg:
                return None
            print(f"  [WARN] POST /{ep}: {d.get('message')}")
            return None
        return d.get("data")

    def patch(self, ep, payload):
        r = requests.patch(f"{self.base}/{ep}", json=payload,
                           headers=self._h(), verify=VERIFY_SSL)
        d = r.json()
        if not d.get("success"):
            print(f"  [WARN] PATCH /{ep}: {d.get('message')}")
        return d.get("success")


# ─── SECTIES (max 1 niveau diep onder parent) ──────────────────────────────────

_section_cache = {}

def get_or_create_section(api, name, parent_id=None):
    """Sectienaam is uniek op basis van naam + parent_id."""
    key = (name, parent_id)
    if key in _section_cache:
        return _section_cache[key]

    sections = api.get("sections/") or []
    for s in sections:
        s_master = int(s.get("masterSection", 0) or 0)
        s_parent = parent_id or 0
        if s["name"] == name and s_master == s_parent:
            _section_cache[key] = int(s["id"])
            return int(s["id"])

    payload = {"name": name, "description": f"Network-Lab: {name}"}
    if parent_id:
        payload["masterSection"] = parent_id

    new_id = api.post("sections/", payload)
    if new_id:
        print(f"  [+] Sectie aangemaakt: {name}")
        _section_cache[key] = int(new_id)
        return int(new_id)

    # herpoging na conflict
    sections = api.get("sections/") or []
    for s in sections:
        s_master = int(s.get("masterSection", 0) or 0)
        s_parent = parent_id or 0
        if s["name"] == name and s_master == s_parent:
            _section_cache[key] = int(s["id"])
            return int(s["id"])
    return None


# ─── VLANS ─────────────────────────────────────────────────────────────────────

_vlan_cache = {}

def get_or_create_vlan(api, vlan_id, vlan_name):
    if vlan_id in _vlan_cache:
        return _vlan_cache[vlan_id]
    existing = api.get("vlans/") or []
    for v in existing:
        if str(v.get("number", "")) == str(vlan_id):
            db_id        = int(v.get("vlanId") or v.get("id"))
            current_name = v.get("name", "") or ""
            current_desc = v.get("description", "") or ""
            # Update naam en description als die niet kloppen
            patch_pl = {}
            if current_name != vlan_name:
                patch_pl["name"] = vlan_name
            correct_desc = f"VLAN {vlan_id} - {vlan_name}"
            if current_desc != correct_desc:
                patch_pl["description"] = correct_desc
            if patch_pl:
                # phpIPAM vereist altijd 'name' bij PATCH op vlans
                patch_pl["name"]   = vlan_name
                patch_pl["number"] = vlan_id
                api.patch(f"vlans/{db_id}/", patch_pl)
                print(f"    [~] VLAN {vlan_id} bijgewerkt: {current_name} → {vlan_name}")
            _vlan_cache[vlan_id] = db_id
            return db_id
    new_id = api.post("vlans/", {
        "number":      vlan_id,
        "name":        vlan_name,
        "description": f"VLAN {vlan_id} - {vlan_name}",
    })
    if new_id:
        print(f"    [+] VLAN {vlan_id} ({vlan_name})")
        _vlan_cache[vlan_id] = int(new_id)
        return int(new_id)
    # herpoging
    existing = api.get("vlans/") or []
    for v in existing:
        if str(v.get("number", "")) == str(vlan_id):
            _vlan_cache[vlan_id] = int(v.get("vlanId") or v.get("id"))
            return int(v.get("vlanId") or v.get("id"))
    return None


# ─── SUBNETS ───────────────────────────────────────────────────────────────────

def get_or_create_subnet(api, network_cidr, section_id, description="", vlan_db_id=None):
    if not section_id:
        print(f"    [SKIP] Subnet {network_cidr}: geen geldige section_id")
        return None

    net = ipaddress.ip_network(network_cidr, strict=False)
    existing = api.get(f"subnets/cidr/{network_cidr}/") or []
    for s in existing:
        if int(s.get("sectionId", 0)) == section_id:
            sid          = int(s["id"])
            current_desc = s.get("description", "") or ""
            if not current_desc or current_desc.startswith("Auto"):
                patch_pl = {"description": description}
                if vlan_db_id:
                    patch_pl["vlanId"] = vlan_db_id
                api.patch(f"subnets/{sid}/", patch_pl)
                print(f"    [~] Subnet bijgewerkt: {network_cidr}  →  {description}")
            return sid

    payload = {
        "subnet":      str(net.network_address),
        "mask":        str(net.prefixlen),
        "sectionId":   section_id,
        "description": description,
        "isFolder":    0,
    }
    if vlan_db_id:
        payload["vlanId"] = vlan_db_id

    new_id = api.post("subnets/", payload)
    if new_id:
        print(f"    [+] Subnet: {network_cidr}  ({description})")
        return int(new_id)

    existing = api.get(f"subnets/cidr/{network_cidr}/") or []
    for s in existing:
        if int(s.get("sectionId", 0)) == section_id:
            return int(s["id"])
    return None


# ─── DEVICES ───────────────────────────────────────────────────────────────────

_dtype_cache = {}

def get_device_type_id(api, label):
    if label in _dtype_cache:
        return _dtype_cache[label]
    types = api.get("tools/device_types/") or []
    for t in types:
        if t.get("tname", "").lower() == label.lower():
            _dtype_cache[label] = t["tid"]
            return t["tid"]
    return None


def get_or_create_device(api, hostname, mgmt_ip, device_type_label, description):
    devices = api.get("devices/") or []
    for d in devices:
        if d.get("hostname") == hostname:
            dev_id  = int(d["id"])
            current = d.get("description", "") or ""
            if current in ("Auto-import via Ansible inventory", ""):
                api.patch(f"devices/{dev_id}/", {"description": description})
                print(f"    [~] Device bijgewerkt: {hostname}  →  {description}")
            return dev_id

    type_id = get_device_type_id(api, device_type_label)
    payload = {"hostname": hostname, "ip": mgmt_ip, "description": description}
    if type_id:
        payload["type"] = type_id

    new_id = api.post("devices/", payload)
    if new_id:
        print(f"    [+] Device: {hostname}  ({mgmt_ip})  →  {description}")
        return int(new_id)

    devices = api.get("devices/") or []
    for d in devices:
        if d.get("hostname") == hostname:
            return int(d["id"])
    return None


# ─── IP ADRESSEN ───────────────────────────────────────────────────────────────

def add_ip(api, ip_str, subnet_id, device_id, description, hostname):
    existing = api.get(f"addresses/search/{ip_str}/") or []
    for e in existing:
        if int(e.get("subnetId", 0)) == subnet_id:
            addr_id      = e.get("id")
            current_dev  = int(e.get("deviceId", 0) or 0)
            current_desc = e.get("description", "") or ""
            # Herlink aan device als dat nog niet gedaan is
            patch_pl = {}
            if current_dev != device_id:
                patch_pl["deviceId"] = device_id
            if not current_desc or current_desc == "":
                patch_pl["description"] = description
                patch_pl["hostname"]    = hostname
            if patch_pl and addr_id:
                api.patch(f"addresses/{addr_id}/", patch_pl)
                print(f"      [~] IP bijgewerkt: {ip_str}  →  device gelinkt")
            else:
                print(f"      [~] Al aanwezig: {ip_str}")
            return
    result = api.post("addresses/", {
        "ip":          ip_str,
        "subnetId":    subnet_id,
        "description": description,
        "hostname":    hostname,
        "deviceId":    device_id,
        "note":        description,
    })
    if result:
        print(f"      [+] IP: {ip_str}  ({description})")


# ─── HOST VERWERKING ───────────────────────────────────────────────────────────

def strip_prefix(cidr):
    net = ipaddress.ip_interface(cidr)
    return str(net.ip), str(net.network.prefixlen), str(net.network.netmask)


def process_host(api, hostname, host_data, section_id, device_type_label, role):
    mgmt_ip = host_data.get("ansible_host", "")
    if not mgmt_ip:
        print(f"  [SKIP] {hostname}: geen ansible_host")
        return

    location    = host_data.get("location", "")
    device_desc = f"{role} | {hostname} | {location}" if location else f"{role} | {hostname}"

    device_id = get_or_create_device(api, hostname, mgmt_ip, device_type_label, device_desc)
    if not device_id:
        print(f"  [FOUT] Kon device niet aanmaken: {hostname}")
        return

    # ── VLANs ───────────────────────────────────────────────────────────────
    vlan_map = {}

    # Lijst van VLANs (switches)
    for vlan in (host_data.get("vlans") or []):
        vid   = int(vlan["id"])
        vname = vlan.get("name", f"VLAN{vid}")
        db_id = get_or_create_vlan(api, vid, vname)
        if db_id:
            vlan_map[vid] = db_id

    # Enkelvoudig VLAN (clients)
    single_vlan      = host_data.get("vlan")
    single_vlan_name = host_data.get("vlan_name", "")
    if single_vlan:
        vid   = int(single_vlan)
        vname = single_vlan_name or f"VLAN{vid}"
        db_id = get_or_create_vlan(api, vid, vname)
        if db_id:
            vlan_map[vid] = db_id

    # ── Management IP alleen voor switches en clients (niet voor routers) ──
    is_switch_or_client = any(x in device_type_label.lower() for x in ("switch", "vpcs"))
    has_routed_ifaces   = any(
        iface.get("ip_address") and not iface.get("ip_address_dhcp")
        for iface in (host_data.get("interfaces") or [])
    )
    if is_switch_or_client and not has_routed_ifaces:
        try:
            mgmt_if  = ipaddress.ip_interface(f"{mgmt_ip}/24")
            mgmt_net = str(mgmt_if.network)
            mgmt_vid = vlan_map.get(10)
            mgmt_sid = get_or_create_subnet(api, mgmt_net, section_id, "MGMT-Network", mgmt_vid)
            if mgmt_sid:
                add_ip(api, mgmt_ip, mgmt_sid, device_id,
                       f"{hostname} | Management IP", hostname)
        except Exception:
            pass

    # ── Interfaces + IPs ────────────────────────────────────────────────────
    interfaces = host_data.get("interfaces", [])
    if not interfaces:
        print(f"  [INFO] {hostname}: geen interfaces")
        return

    for iface in interfaces:
        iface_name = iface.get("name", "?")
        iface_desc = iface.get("description", iface_name)

        vlan_hint  = ""
        vlan_db_id = None

        # VLAN uit interface naam (Vlan10)
        m = re.search(r'[Vv]lan(\d+)', iface_name)
        if m:
            vid        = int(m.group(1))
            vlan_hint  = f" [VLAN {vid}]"
            vlan_db_id = vlan_map.get(vid)

        # VLAN uit access_vlan (access poorten)
        access_vlan = iface.get("access_vlan")
        if access_vlan and not vlan_db_id:
            vid        = int(access_vlan)
            vlan_hint  = f" [VLAN {vid}]"
            vlan_db_id = vlan_map.get(vid)

        # VLAN uit host-level (clients)
        if single_vlan and not vlan_db_id:
            vid        = int(single_vlan)
            vlan_hint  = f" [VLAN {vid}]"
            vlan_db_id = vlan_map.get(vid)

        full_desc = f"{hostname} | {iface_name} | {iface_desc}{vlan_hint}"

        # Access poorten zonder IP: VLAN is al aangemaakt, geen subnet nodig
        if iface.get("switchport_mode") == "access" and not iface.get("ip_address"):
            continue

        # IPv4
        ipv4 = iface.get("ip_address")
        if ipv4 and not iface.get("ip_address_dhcp"):
            try:
                ip_str, _, _ = strip_prefix(ipv4)
                net_cidr     = str(ipaddress.ip_interface(ipv4).network)
                subnet_id    = get_or_create_subnet(api, net_cidr, section_id,
                                                    iface_desc, vlan_db_id)
                if subnet_id:
                    add_ip(api, ip_str, subnet_id, device_id, full_desc, hostname)
            except ValueError as e:
                print(f"      [WARN] IPv4 '{ipv4}': {e}")

        # IPv6
        ipv6 = iface.get("ipv6_address")
        if ipv6:
            try:
                ip_str, _, _ = strip_prefix(ipv6)
                net_cidr     = str(ipaddress.ip_interface(ipv6).network)
                subnet_id    = get_or_create_subnet(api, net_cidr, section_id,
                                                    f"{iface_desc} [IPv6]", vlan_db_id)
                if subnet_id:
                    add_ip(api, ip_str, subnet_id, device_id,
                           full_desc + " [IPv6]", hostname)
            except ValueError as e:
                print(f"      [WARN] IPv6 '{ipv6}': {e}")


def flatten_hosts(group_data):
    hosts = {}
    if isinstance(group_data, dict):
        hosts.update(group_data.get("hosts", {}) or {})
        for child in (group_data.get("children", {}) or {}).values():
            hosts.update(flatten_hosts(child))
    return hosts


# ─── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    with open(INVENTORY, "r") as f:
        inv = yaml.safe_load(f)

    api = PhpIPAM(PHPIPAM_URL, APP_ID, APP_CODE)

    # Parent sectie (niveau 0)
    print(f"\n[*] Parent sectie: {PARENT_SECTION}")
    parent_id = get_or_create_section(api, PARENT_SECTION)

    # Alle groepen samenvoegen
    all_children = (inv.get("all", {}) or {}).get("children", {}) or {}
    top_level    = {k: v for k, v in inv.items()
                    if k != "all" and isinstance(v, dict) and "hosts" in v}
    all_groups   = {**all_children, **top_level}

    for group_name, group_data in all_groups.items():
        mapping = GROUP_MAP.get(group_name)
        if not mapping:
            print(f"\n[SKIP] Groep '{group_name}' niet in GROUP_MAP.")
            continue

        device_type  = mapping["device_type"]
        role         = mapping["role"]
        default_site = mapping["site"]
        section_tmpl = mapping["section"]

        print(f"\n{'='*60}")
        print(f"[*] {group_name}  [{device_type}]")
        print(f"{'='*60}")

        hosts = flatten_hosts(group_data)
        for hostname, host_data in (hosts or {}).items():
            if not host_data:
                continue

            # Site bepalen per host (of group default)
            site = host_data.get("location") or default_site or "Site-A"

            # Sectienaam = "Site-A | WAN"  →  altijd slechts 1 niveau onder parent
            section_name = f"{site} | {section_tmpl}"
            section_id   = get_or_create_section(api, section_name, parent_id)

            print(f"\n  → {hostname}  [{site}]")
            process_host(api, hostname, host_data, section_id, device_type, role)

    print(f"\n{'='*60}")
    print("[KLAAR] Import voltooid!")
    print(f"{'='*60}")


def list_vlans(api):
    """Toon alle VLANs die in phpIPAM staan."""
    vlans = api.get("tools/vlans/") or []
    if not vlans:
        print("  [!] Geen VLANs gevonden in phpIPAM")
        return
    print(f"  {'ID':>6}  {'Nummer':>8}  {'Naam':<20}  Beschrijving")
    print(f"  {'-'*6}  {'-'*8}  {'-'*20}  {'-'*30}")
    for v in sorted(vlans, key=lambda x: int(x.get("number", 0))):
        print(f"  {v.get('vlanId','?'):>6}  {v.get('number','?'):>8}  {v.get('name',''):.<20}  {v.get('description','')}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "vlans":
        # python3 script.py vlans  →  alleen VLANs tonen
        import requests, yaml
        requests.packages.urllib3.disable_warnings()
        api = PhpIPAM(PHPIPAM_URL, APP_ID, APP_CODE)
        print("\n[*] VLANs in phpIPAM:")
        list_vlans(api)
    else:
        main()