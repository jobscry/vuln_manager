# vuln_manager

The goal of this project is to create custom vulnerability feeds from the National Vulnerability Database (NVD).

## Data Sources

* **Common Platform Enumeration (CPE) Dictionary** - The [CPE Secification](https://nvd.nist.gov/cpe.cfm) is a "CPE is a structured naming scheme for information technology systems, software, and packages". The CPE Database is regularly updated and published by the National Institute of Standards and Technolgy (NIST).
* **Common Vulnerability Enumeration (CVE) Database** - CVE is a [registered trademark](https://cve.mitre.org/) of The MITRE Corporation.  This database is updated regularly and made available from the NVD.

## Requirements

* Django 1.8+
* lxml 3.4.2
* Requests 2.6.0
* psycopg2 2.5.4
* Postgresql
