from SystemCode.connector.database.mysql_client import MySQLClient


client = MySQLClient('remote')
print(client.check_kb_exist('Uc05f0c49225d43858247b416db1b2f64', ['KBa7f4868cec8d41baa1e99c7111cd3997']))