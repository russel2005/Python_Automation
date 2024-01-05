from api.zabbix_api5 import ZabbixApiClient

def main():
    zabbix_client = ZabbixApiClient()
    zabbix_client.run_checks()

if __name__ == "__main__":
    main()
