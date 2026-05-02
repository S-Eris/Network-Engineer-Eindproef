# 🌐 Network Engineer Eindproef – Enterprise Network Design

<p align="center">
  <img src="https://img.shields.io/badge/Network-Enterprise-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Routing-BGP%20%7C%20OSPFv3-informational?style=for-the-badge" />
  <img src="https://img.shields.io/badge/HA-HSRP%20%7C%20CARP-success?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Security-IPsec%20VPN-important?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Status-Completed-brightgreen?style=for-the-badge" />
</p>

---

## 📌 Overzicht
Dit repository bevat het eindwerk voor de opleiding **Network Engineer**.

Het project focust op het **ontwerpen en documenteren van een realistische enterprise netwerkarchitectuur** met aandacht voor:

- High Availability  
- Security  
- Redundantie  
- Schaalbaarheid  
- Correct gebruik van routing- en netwerkprotocollen  
- Automation & uitbreidbaarheid  
- Multi-ISP connectiviteit  
- Enterprise routing design  

De netwerkdiagrammen zijn opgesteld met **draw.io**.

---

## 📚 Inhoudsopgave
- [🏗️ Architectuur Overzicht](#️-architectuur-overzicht)
- [🔥 Site-A](#-site-a-hoofdsite)
- [🔐 Site-B](#-site-b-remote-site)
- [🌐 VLAN Segmentatie](#-netwerksegmentatie--vlans)
- [🔁 High Availability](#-high-availability)
- [🌍 WAN & BGP](#-wan--bgp-ontwerp)
- [🔁 Routing Architectuur](#-routing-architectuur)
- [🔐 VPN Architectuur](#-vpn-architectuur)
- [🌐 NAT](#-nat)
- [🔄 Packet Flow](#-packet-flow-analyse)
- [💥 Failover Analyse](#-failover-analyse)
- [🌳 Layer 2](#-layer-2-stabiliteit)
- [🔒 Security](#-security-principes)
- [🔧 Troubleshooting](#-troubleshooting)
- [🧠 Design Keuzes](#-design-keuzes)
- [🌍 Topologie](#-topologie-type)
- [🤖 Automation](#-automation--configuratie)
- [📂 Repository Inhoud](#-inhoud-van-het-repository)
- [🚀 Uitbreidingen](#-mogelijke-uitbreidingen)
- [🏁 Conclusie](#-conclusie)

---

## 🏗️ Architectuur Overzicht
Het netwerk maakt gebruik van een:

👉 **3-tier hiërarchisch model**  
👉 **Hybride topologie (mesh + star + point-to-point)**  

---

## 🔥 Site-A (Hoofdsite)
- pfSense **High Availability (HA)** cluster  
  - CARP (Virtual IP’s)  
  - pfsync (state synchronisatie)  

- Core:
  - R-CORE-1  
  - R-CORE-2  

- Distribution:
  - Distri-Switch1  
  - Distri-Switch2  

- Access:
  - Access-Switch1 / 2 / 3  

- Dual ISP:
  - TELENET  
  - PROXIMUS  

---

## 🔐 Site-B (Remote site)
- Router: R-SITE-B  
- LAN: 10.20.40.0/24  
- Gateway: 10.20.40.254  
- Site-to-Site IPsec VPN  

---

## 🌐 Netwerksegmentatie – VLAN’s

| VLAN | Naam | Subnet | Gateway |
|------|------|--------|--------|
| 10 | MGMT | 10.10.10.0/24 | 10.10.10.254 |
| 20 | OFFICE | 10.10.20.0/24 | 10.10.20.254 |
| 30 | IT | 10.10.30.0/24 | 10.10.30.254 |
| 40 | SALES | 10.10.40.0/24 | 10.10.40.254 |

---

## 🔁 High Availability

### HSRP
| VLAN | Active | Standby |
|------|--------|--------|
| 10 | SW1 | SW2 |
| 20 | SW1 | SW2 |
| 30 | SW2 | SW1 |
| 40 | SW2 | SW1 |

### pfSense HA
- CARP  
- pfsync  
- XML-RPC  

---

## 🌍 WAN & BGP-ontwerp

| Device | AS |
|--------|----|
| WAN | 65000 |
| CORE | 65001 |
| TELENET | 65002 |
| PROXIMUS | 65003 |
| SITE-B | 65004 |

---

## 🔁 Routing Architectuur

### OSPFv3
- Intern routing protocol  
- Area 0 backbone  

### BGP
- ISP routing  
- Failover  

---

## 🔐 VPN Architectuur
- Site-to-Site IPsec  
- AES encryptie  
- Secure tunnel tussen sites  

---

## 🌐 NAT
- PAT (NAT overload)  
- Internet toegang  

---

## 🔄 Packet Flow Analyse

1. Client → Gateway (HSRP VIP)  
2. Distribution → Core  
3. Core → WAN  
4. NAT → Internet  

---

## 💥 Failover Analyse

- HSRP failover  
- BGP ISP switch  
- OSPF reconvergence  

---

## 🌳 Layer 2 Stabiliteit
- Rapid-PVST  
- BPDU Guard  
- PortFast  

---

## 🔒 Security-principes
- Default deny  
- VLAN isolatie  
- VPN encryptie  

---

## 🔧 Troubleshooting

```bash
ping 8.8.8.8
show ip route
show ip bgp summary
show standby
show ospfv3 neighbor
```

---

## 🧠 Design Keuzes
- BGP = extern  
- OSPF = intern  
- HSRP = redundancy  

---

## 🌍 Topologie Type
Hybride + 3-tier model

---

## 🤖 Automation & configuratie
- Ansible  
- Netplan  
- FRR  
- pfSense API  

---

## 📂 Inhoud van het repository
- draw.io diagram  
- README  
- configs  

---

## 🚀 Mogelijke uitbreidingen
- IPv6  
- Monitoring  
- SIEM  

---

## 🏁 Conclusie
Enterprise-grade netwerk met redundantie en schaalbaarheid.

---

## 👤 Auteur
Sitki Eris – Network Engineer
