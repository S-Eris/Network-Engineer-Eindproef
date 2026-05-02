🌐 Network Engineer Eindproef – Enterprise Network Design
📌 Overzicht

Dit repository bevat het eindwerk voor de opleiding Network Engineer.

Het project focust op het ontwerpen en documenteren van een realistische enterprise netwerkarchitectuur met aandacht voor:

High Availability
Security
Redundantie
Schaalbaarheid
Correct gebruik van routing- en netwerkprotocollen
Automation & uitbreidbaarheid
Multi-ISP connectiviteit
Enterprise routing design

De netwerkdiagrammen zijn opgesteld met draw.io.

🏗️ Architectuur Overzicht

Het netwerk maakt gebruik van een:

👉 3-tier hiërarchisch model
👉 Hybride topologie (mesh + star + point-to-point)

🔥 Site-A (Hoofdsite)
pfSense High Availability (HA) cluster
CARP (Virtual IP’s)
pfsync (state synchronisatie)
Core Layer:
R-CORE-1
R-CORE-2
Distribution Layer:
Distri-Switch1
Distri-Switch2
Access Layer:
Access-Switch1 / 2 / 3
Dual ISP:
TELENET
PROXIMUS
eBGP tussen firewall/WAN en ISP’s
VLAN-segmentatie
Local Internet Breakout
🔐 Site-B (Remote site)
Router: R-SITE-B
LAN subnet: 10.20.40.0/24
Gateway: 10.20.40.254
Verbinding:
👉 Site-to-Site IPsec VPN (of WAN simulatie)
Routing:
👉 Statische routes / BGP (optioneel uitbreiding)
🌐 Netwerksegmentatie – VLAN’s
VLAN	Naam	Subnet	Gateway (VIP)
10	MGMT	10.10.10.0/24	10.10.10.254
20	OFFICE	10.10.20.0/24	10.10.20.254
30	IT	10.10.30.0/24	10.10.30.254
40	SALES	10.10.40.0/24	10.10.40.254
🔁 High Availability
🔹 pfSense HA
CARP (VIP failover)
pfsync (state sync)
XML-RPC (config sync)
🔹 Switching redundancy
HSRP (gateway redundancy)
VLAN	Active	Standby
10	SW1	SW2
20	SW1	SW2
30	SW2	SW1
40	SW2	SW1
🌍 WAN & BGP-ontwerp
Autonomous Systems
Component	AS
WAN / Firewall	65000
CORE	65001
TELENET	65002
PROXIMUS	65003
SITE-B	65004
BGP-strategie
Enkel eBGP
Geen iBGP
Geen BGP intern
Geen BGP over VPN

BGP wordt gebruikt voor:

Multihoming
Failover
Internet routing
🔗 Point-to-Point Netwerken
Link	Netwerk
WAN ↔ TELENET	10.255.1.0/30
WAN ↔ PROXIMUS	10.255.1.4/30
WAN ↔ SITE-B	10.255.2.0/30
CORE ↔ TELENET	10.255.0.0/30
CORE ↔ PROXIMUS	10.255.0.4/30
CORE ↔ CORE	10.0.0.0/30
CORE ↔ DISTRI	10.0.0.4/30
🔁 Routing Architectuur
🔹 Intern (OSPFv3)
Core ↔ Distribution
Area 0 backbone
Dual-stack ondersteuning
🔹 Extern (BGP)
ISP connecties
Route selectie
Failover
🔐 VPN-architectuur
Type: Site-to-Site IPsec VPN
Terminatie:
Site-A: WAN / CARP VIP
Site-B: WAN IP
Routing:
Statisch of BGP (uitbreiding)
Geen standaard dynamische routing
🌐 NAT
Type: PAT (NAT overload)
Locatie: WAN-router / firewall

➡️ Interne IP’s → publiek IP

🔄 Packet Flow Analyse
Scenario: Client → Internet
Client → VIP (HSRP/CARP gateway)
Distribution / Firewall
Core routing
WAN-router → NAT
ISP → Internet

➡️ Return via dezelfde weg

💥 Failover Analyse
🔹 Firewall failure
CARP neemt over
🔹 Switch failure
HSRP failover
🔹 ISP failure
BGP kiest andere ISP
🔹 Core failure
OSPF herberekent routes

➡️ Netwerk blijft operationeel

🌳 Layer 2 Stabiliteit
Rapid-PVST
BPDU Guard
PortFast

➡️ Voorkomt loops

🔒 Security-principes
Default deny firewall policy
Inter-VLAN filtering
Management via VLAN
WAN management disabled
VPN encryptie (AES-256, IKEv2, PFS)
🔧 Troubleshooting
ping 8.8.8.8
traceroute 8.8.8.8
show ip route
show ip bgp summary
show standby
show ospfv3 neighbor
🧠 Design Keuzes
Waarom BGP?
Multi-ISP
Realistisch WAN
Waarom OSPF?
Snelle interne routing
Waarom HSRP/CARP?
Gateway redundancy
Waarom VLANs?
Segmentatie
Security
Performance
Waarom /30 links?
Efficiënt IP gebruik
🌍 Topologie Type

Dit netwerk is:

➡️ Hybride topologie

Mesh (core + ISP)
Star (access layer)
Point-to-point (WAN links)

➡️ Gebaseerd op:
👉 3-tier enterprise model

🤖 Automation & configuratie

Voorbereid voor automation:

YAML-configuraties
VLAN’s
Firewallregels
BGP configs
VPN parameters

Tools:

Ansible
Netplan
FRR
pfSense API
📂 Inhoud van het repository
Eindwerk.drawio → netwerkdiagram
README.md → documentatie
configs/ → automation (toekomstig)
🚀 Mogelijke uitbreidingen
IPv6
Monitoring (Zabbix / Prometheus)
SIEM
Automation
802.1X
Zero Trust
🏁 Conclusie

Dit netwerkontwerp demonstreert:

Enterprise-level netwerkdesign
High availability
Routing optimalisatie
Security principes

👉
Het netwerk is schaalbaar, redundant en geschikt voor real-life bedrijfsomgevingen.

👤 Auteur

Sitki Eris
Opleiding: Network Engineer
Context: Eindwerk / Enterprise Network Design