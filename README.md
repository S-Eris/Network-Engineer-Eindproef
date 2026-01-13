# Network Engineer Eindproef

## 📌 Overzicht
Dit repository bevat het eindwerk voor de opleiding **Network Engineer**.

Het project focust op het **ontwerpen en documenteren van een realistische enterprise netwerkarchitectuur** met aandacht voor:
- High Availability
- Security
- Redundantie
- Schaalbaarheid
- Correct gebruik van routing- en netwerkprotocollen
- Automation & uitbreidbaarheid

De netwerkdiagrammen zijn opgesteld met **draw.io**.

---

## 🏗️ Architectuur samenvatting

### 🔥 Site-A (Hoofdsite)
- pfSense **High Availability (HA)** cluster
  - CARP (Virtual IP’s)
  - pfsync (state synchronisatie)
- Dual ISP (Telenet & Proximus)
- **eBGP** tussen firewall en ISP’s
- Core / Distribution / Access switching (Layer 2)
- VLAN-segmentatie
- Local Internet Breakout

### 🔐 Site-B (Remote site)
- Single firewall
- Eigen WAN-subnet (publiek IP)
- Eigen LAN-subnet
- Site-to-Site **IPsec VPN** met Site-A
- Statische routing over VPN

---

## 🌐 Netwerksegmentatie – Site-A (VLAN’s)

| VLAN | Naam | Subnet | Gateway (CARP) |
|----|----|----|----|
| 10 | Management | 192.168.10.0/24 | 192.168.10.1 |
| 20 | Office | 192.168.20.0/24 | 192.168.20.1 |
| 30 | IT | 192.168.30.0/24 | 192.168.30.1 |
| 40 | Sales | 192.168.40.0/24 | 192.168.40.1 |

---

## 🌐 Netwerksegmentatie – Site-B

| Site | Subnet | Gateway |
|----|----|----|
| Site-B LAN | 192.168.50.0/24 | 192.168.50.1 |

---

## 🔁 High Availability (pfSense HA)

pfSense HA bestaat uit:
- **CARP** – Virtual IP failover
- **pfsync** – Synchronisatie van actieve firewall-, NAT- en VPN-sessies
- **XML-RPC** – Configuratiesynchronisatie

Bij uitval van de actieve firewall neemt de standby firewall automatisch over zonder merkbare downtime.

---

## 🌍 WAN & BGP-ontwerp

### Autonomous Systems
- Eigen organisatie: **AS65000**
- ISP 1 (Telenet): **AS45000**
- ISP 2 (Proximus): **AS4200**

### BGP-strategie
- Enkel **eBGP** tussen firewall en ISP
- Geen iBGP
- Geen BGP intern
- Geen BGP over VPN

BGP wordt gebruikt voor:
- Multihoming
- Betere failover
- Realistisch enterprise WAN-design

---

## 🔐 VPN-architectuur

- Type: Site-to-Site IPsec VPN
- Terminatie:
  - Site-A: WAN CARP VIP
  - Site-B: WAN firewall IP
- Routing: statische routes / Phase-2 selectors
- Geen dynamische routing over VPN

---

## 🔒 Security-principes
- Default deny firewall policy
- Inter-VLAN filtering op firewall
- Management enkel via management VLAN
- WAN-management uitgeschakeld
- Sterke VPN-encryptie (AES-256, IKEv2, PFS)

---

## 🤖 Automation & configuratie

Dit project is voorbereid voor **automation en orchestration**.

### YAML-configuraties (toekomstige uitbreiding)
- Netwerkconfiguraties (VLAN’s, IP-plannen)
- Firewallregels
- BGP-configuraties
- VPN-parameters

Deze configuraties kunnen gebruikt worden met tools zoals:
- **Ansible**
- **Netplan**
- **FRR**
- **pfSense API**

---

## 📂 Inhoud van het repository

- **Eindwerk.drawio**  
  Hoofdnetwerkdiagram van het project

- **README.md**  
  Projectdocumentatie en uitleg

- **configs/** *(optioneel / toekomstig)*  
  YAML-configuraties voor automation

---

## 🚀 Mogelijke uitbreidingen
- IPv6
- Monitoring & logging
- SIEM
- Vulnerability scanning
- Automation (Ansible)
- 802.1X
- Check Point ClusterXL equivalent

---

## 👤 Auteur
Naam: *Sitki Eris*  
Opleiding: Network Engineer  
Context: Eindwerk / Enterprise Network Design
