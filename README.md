<h1> zbxcmd </h1>
<p>A command line tool to help automating some Zabbix repetitive tasks not handled well by the GUI</p>

<h2> Installation </h2>
<p>zbxcmd depends on <a href="https://github.com/lukecyca/pyzabbix">pyzabbix</a>, so you need to have it installed before using it. The easiest way to do this is using pip:</p>
<strong>pip install pyzabbix</strong>

<h2>Commands</h2>
<h3>host</h3>
<h4>availble methods:</h4>
<h5>get:</h5>
<p>The get method retrieves the requested attributes for the host collection that matches the filters given</p>
<command>zbxcmd.py --server http://[zabbix_server_hostname]/zabbix --username [zabbix_username] --cmd host --method get</command>
<p>You can use the --host filter to restrict the query to a single host</p>
<command>zbxcmd.py --server http://[zabbix_server_hostname]/zabbix --username [zabbix_username] --cmd host --method get --host [hostname]</command>
<p>This would return information only about the host with the matching hostname</p>
<h3>trigger</h3>
<h4>availble methods:</h4>
<p>The get method retrieves the requested attributes for the trigger collection that matches the filters given</p>
<command>zbxcmd.py --server http://[zabbix_server_hostname]/zabbix --username [zabbix_username] --cmd trigger --method get --host [hostname]</command>
<p>You can use the --host filter to restrict the query to a single host</p>
<command>zbxcmd.py --server http://[zabbix_server_hostname]/zabbix --username [zabbix_username] --cmd trigger --method get --host [hostname]</command>
