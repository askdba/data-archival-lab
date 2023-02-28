# Data-Archival-Project
The repository contains all the details and codes  about the Data archival projects

# Data-Archival-Project
The repository contains all the details and codes  about the Data archival projects

This document provides the complete details about the Data archival project from Source databases to ClickHouse. It contains the following details.

Overview
Architecture and Components
Implementation


<img width="631" alt="Screenshot 2023-01-02 at 23 10 36" src="https://user-images.githubusercontent.com/46593013/210274619-f7e39608-d36b-4508-bbe9-74d05136c8b9.png">

Overview:

The data archival project is getting developed to perform the archival process from source database to ClickHouse. Currently, we are working on the following databases.


<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
MySQL to ClickHouse migration
PostgreSQL to ClickHouse migration
</code></pre>


Aspects:

The tool can migrate the existing data from source to destination
The tool can perform the live streaming from source to destination. This can be used to perform the HA, Live analytics, Minimise the time for environment migration.
Every component is dockerized and can be built using the docker-compose file.
Easy to configure.


Note:  1) The tool was just created and passed the initial testing. We have to develop this further and need to test with different scenarios before implementing on production. Based on the testing results, we can improve the tool further. 2) Few of the variables are hardcoded. We have to check the possibilities to make them as variables. 

The architecture contains the following components
<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 

Source databases
Debezium connector
Kafka
ChistaData connector
ClickHouse

Source databases: It can be any database which supports Debezium. In our project, we are exploring the databases MySQL, MariaDB and PostgreSQL.

Debezium connector: Debezium is a set of source connectors for Apache Kafka Connect. Each connector ingests changes from a different database by using that database's features for change data capture (CDC).

Kafka: Kafka is primarily used to build real-time streaming data pipelines and applications that adapt to the data streams. It combines messaging, storage, and stream processing to allow storage and analysis of both historical and real-time data.

ChistaData Connector: It is being developed by ChistaData’s engineers. The tool can be used to apply the changes from Kafka topic to ClickHouse database.

ClickHouse: ClickHouse is an open-source column-oriented DBMS (columnar database management system) for online analytical processing (OLAP) that allows users to generate analytical reports using SQL queries in real-time.
</code></pre>


# MYSQL TO CLICKHOUSE 

Each replicated table must have one of the following replica identity: primary key (by default) index

So we decided to use Debezium MySQL image for these requirements on the docker-compose. These settings are configured by default on this version.

1- Clone the GIT repo

Create GitHub folder in Documents and clone repo in it.
<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 

git clone https://github.com/ChistaDATA/Data-Archival-Project.git

</code></pre>

Choose MySQL
So we should have these components

Docker-compose.yml - Docker components configuration. Debezium.json - Debezium components configuration for source db. Config.xml - To allow ClickHouse external connections.

2- Run the “docker-compose.yml”
After apply these steps, we can start our docker-compose file with “docker-compose up -d”

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
➜  MySQl docker-compose up -d                  
[+] 
debezium/connect:latest
clickhouse/clickhouse-server:latest
confluentinc/cp-kafka:latest
confluentinc/cp-zookeeper:latest 
debezium/mysql:14
cansayin/python:latest

</code></pre>

3 - Create a table and insert some data to the MySQL

To create initial data, you have to insert data in MySQL before the enable debezium and kafka.
After all of the components are created, we need to connect MySQL side and create the table which name is chista and insert some data:

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
Table creation:

## MySQL:

## Connect MySQL


mysql -u root -p
password: root

use test;

CREATE TABLE chista (
     id MEDIUMINT NOT NULL AUTO_INCREMENT,
     name CHAR(30) NOT NULL,
     PRIMARY KEY (id)
);

## Insert data into MySQL
## following query inserts 10k rows to MySQL

INSERT INTO chista (id, name)
SELECT n, CONCAT('name', n)
  FROM
(
select a.N + b.N * 10 + c.N * 100 + d.N * 1000 + 1 N
from (select 0 as N union all select 1 union all select 2 union all select 3 union all select 4 union all select 5 union all select 6 union all select 7 union all select 8 union all select 9) a
      , (select 0 as N union all select 1 union all select 2 union all select 3 union all select 4 union all select 5 union all select 6 union all select 7 union all select 8 union all select 9) b
      , (select 0 as N union all select 1 union all select 2 union all select 3 union all select 4 union all select 5 union all select 6 union all select 7 union all select 8 union all select 9) c
      , (select 0 as N union all select 1 union all select 2 union all select 3 union all select 4 union all select 5 union all select 6 union all select 7 union all select 8 union all select 9) d
) t;

</code></pre>



4- To start CDC process, create Kafka Topic and apply this one on Debezium container this debezium.json 

You have to wait mysql to get up after running docker compose file. Otherwise you will get an error with the command below. Please wait a couple of minutes to run the command below.

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
curl -H 'Content-Type: application/json' debezium:8083/connectors --data "@debezium.json"


</code></pre>

Then you will have an output like this. 

{"name":"mysql-connector-1","config":{"connector.class":"io.debezium.connector.mysql.MySqlConnector","snapshot.locking.mode":"none","tasks.max":"1","database.whitelist":"test","database.user":"root","database.server.id":"1","database.server.name":"mysql","database.port":"3306","topic.prefix":"mysql","database.hostname":"mysql","database.password":"root","snapshot.mode":"initial","key.converter":"org.apache.kafka.connect.json.JsonConverter","value.converter":"org.apache.kafka.connect.json.JsonConverter","key.converter.schemas.enable":"false","value.converter.schemas.enable":"false","internal.key.converter":"org.apache.kafka.connect.json.JsonConverter","internal.value.converter":"org.apache.kafka.connect.json.JsonConverter","database.history.kafka.bootstrap.servers":"mysql-kafka-1:9092","schema.history.internal.kafka.topic":"mysql1","schema.history.internal.kafka.bootstrap.servers":"mysql-kafka-1:9092","internal.key.converter.schemas.enable":"false","internal.value.converter.schemas.enable":"false","name":"mysql-connector-1"},"tasks":[],"type":"source"}


All configurations set for test in MySQL side. If you want to learn more detail about MySQL information, or if you want to migrate another table to Kafka, you can edit the debezium.json file in the Debezium container. If necessary, we can use the “*” option to migrate all tables instead of one table name.


5- Create table in ClickHouse
<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
## Table creation:

## Table has to be manually created on ClickHouse using the ReplacingMergeTree engine. For example,

## ClickHouse:

clickhouse-client

CREATE TABLE IF NOT EXISTS default.chista
(
id Int32,
name String
)
ENGINE = ReplacingMergeTree
ORDER BY id;
</code></pre>

6- With this command, we created the kafka topic which name is “mysql.test.chista” To check and validate this, need to connect kafka container and list the all topics:


<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 

/usr/bin/kafka-topics --list  --bootstrap-server kafka:9092

you will see an output like this
__consumer_offsets #/default Kafka topic
my_connect_configs #/default Kafka topic
my_connect_offsets #/default Kafka topic
my_connect_statuses #/default Kafka topic
mysql          
mysql.test.chista /our kafka topic
mysql1
</code></pre>


To see the messages on Kafka Topic, we need to read the messages. So when we manipulate the source db, it should be shown on the Kafka Topic as messages after the installed configuration. Messages can read with:

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 

/usr/bin/kafka-console-consumer  --bootstrap-server kafka:9092  --topic mysql.test.chista --from-beginning

</code></pre>

For example I’ll insert some data on the MySQL side and should see these new messages on the Kafka Topic side. After the Topic is created, we can see the new messages only. That means you couldn't see the old data in messages which were on the MySQL side. Only new insert/update/delete operations (op: c, op:u and op:d) migrated to the Kafka Topic side.


 
7 - Connect to python container and run the following command to start chistada connector

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
python3 chistadata-connector.py
</code></pre>

According to operation names (op: c, op: u and op: d), python side will apply the changes to ClickHouse side. When we check the ClickHouse side, data should be see:


8- Now you can connect to ClickHouse container and check the data
<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
clickhouse-client

use default

select * from chista;

# then optimize clickhouse table 

optimize table chista;
</code></pre

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
------------------
</code></pre>

# POSTGRESQL TO CLICKHOUSE 

Firstly you have to clone this repo in $HOME/Documents/GitHub

PostgreSQL Implementation:
Requirements
The wal_level setting must have a logical value and max_replication_slots parameter must have a value at least 2 in the PostgreSQL config file. 

Each replicated table must have one of the following replica identity:
primary key (by default)
index

So we decided to use Debezium PostgreSQL image for these requirements on the docker-compose. These settings are configured by default on this version.

1- Clone the GIT repo

Create GitHub folder in Documents and clone repo in it.
<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 

git clone https://github.com/ChistaDATA/Data-Archival-Project.git

</code></pre>


2) Choose PostgreSQL

So we should have these components

Docker-compose.yml - Docker components configuration. 
Debezium.json - Debezium components configuration for source db.
Config.xml - To allow ClickHouse external connections.

3) Run the “docker-compose.yml”

After apply these steps, we can start our docker-compose file with “docker-compose up -d”

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;">
➜  PostgreSQL docker-compose up -d                  
[+] Running 6/6
debezium/connect:latest
clickhouse/clickhouse-server:latest
confluentinc/cp-kafka:latest
confluentinc/cp-zookeeper:latest 
debezium/postgres:14
ihsnlky/python:latest
</code></pre>

4) Create a table and insert some data to the PostgreSQL

After all of the components are created, we need to connect PostgreSQL side and create the table which name is shipments and insert some data: 
<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;">
root@874d7d8b47fc:/# su - postgres
postgres@874d7d8b47fc:~$ psql -U postgresuser -d shipment_db
</code></pre>

Then;
<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;">
\c shipment_db

CREATE TABLE IF NOT EXISTS shipments
(
    shipment_id bigint NOT NULL,
    order_id bigint NOT NULL,
    date_created character varying(255) COLLATE pg_catalog."default",
    status character varying(25) COLLATE pg_catalog."default",
    CONSTRAINT shipments_pkey PRIMARY KEY (shipment_id)
);

INSERT INTO shipments values (30500,10500,'2021-01-21','COMPLETED');
</code></pre>
5)  To start CDC process, create Kafka Topic and apply this one on Debezium container this debezium.json
<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;">
curl -H 'Content-Type: application/json' debezium:8083/connectors --data "@debezium.json"
</code></pre>

All configurations set for shipment_db in PostgreSQL side. If you want to learn more detail about postgreSQL information, or if you want to migrate another table to Kafka, you can edit the debezium.json file in the Debezium container. If necessary, we can use the “*” option to migrate all tables instead of one table name.


6) Checking the Kafka Topic to have messages

So we can connect the Kafka container now:

With this command, we created the kafka topic which name is “shipments.public.shipment”
To check and validate this, need to connect kafka container and list the all topics:
<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;">
/usr/bin/kafka-topics --list  --bootstrap-server kafka:9092
</code></pre>

To see the messages on Kafka Topic, we need to read the messages. So when we manipulate the source db, it should be shown on the Kafka Topic as messages after the installed configuration.
Messages can read with:
<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
/usr/bin/kafka-console-consumer  --bootstrap-server kafka:9092  --topic shipment.public.shipments --from-beginning
</code></pre>
For example I’ll insert some data on the PostgreSQL side and should see these new messages on the Kafka Topic side. After the Topic is created, we can see the new messages only. That means you couldn't see the old data in messages which were on the PostgreSQL side. Only new insert/update/delete operations (op: c, op:u and op:d) migrated to the Kafka Topic side.

Table is created on the ClickHouse side manually.So we should see new messages like “op: c” on the Kafka Topic side after this operation.

Now we clearly migrate the data PostgreSQL to Kafka until now. And now we need to create ClickHouse table to migrate:

7) Creating the table on ClickHouse side

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
clickhouse-client

CREATE TABLE IF NOT EXISTS default.kafka_table
(
    `shipment_id` UInt64,
    `order_id` UInt64,
    `date_created` String,
    `status` String
)
ENGINE = ReplacingMergeTree
ORDER BY shipment_id;
</code></pre>


 -- optional --
 

But maybe you want to use MergeTree table according to your scenario, if so, you should apply a command on source table side.

In postgresql:
\c shipment_db
ALTER TABLE shipmets REPLICA IDENTITY FULL;

-- optional --

8) Python Script applies the changes to ClickHouse side automatically. If operation is r, it will apply bulk insert. If operation is c,u or d, this script go with as CDC. Also if this container stops, you can start it after creating the table in ClickHouse. Creating table will be automatic for ClickHouse in near time. So, we will get rid of this step.

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
python3 chistadata-connector.py
</code></pre>

According to operation names (op: c, op: u and op: d), python side will apply the changes to ClickHouse side.
When we check the ClickHouse side, data should be see:



9) Deleting data from PostgreSQL (optional - experimental)

Deleting the data which is migrated to the ClickHouse already:

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
#primary key: shipment_id
#psql_table name: shipments
#ch_table name: kafka_table

#!/bin/bash
clear

#PostgreSQL side

psql -U postgresuser -t -A -F","  -d shipment_db -c "SELECT md5(CAST((${primary_key})AS text)) FROM ${psql_table}" -o /a.txt

#ClickHouse side

clickhouse-client --send_logs_level none --query "select lower(hex(MD5(toString(${primary_key})))) from ${ch_table};" >b.txt

#Specified the data hashes which existed only on the PostgreSQL side according to primary key hashes. All text files should be in one location only. It gives us data only on the PostgreSQL side.

diff a.txt b.txt --new-line-format="" --old-line-format="%L" --unchanged-line-format="" > c.txt

#We need some editing and after that, we can delete the data from the PostgreSQL side according to the hashes. Before this process, I need to stop the debezium side of course. So that means, we need to create a Kafka Topic for each table. We’ll delete all the data except the data in PostgreSQL only from the PostgreSQL side.

sed -i "s/^/'/;s/$/'/" /tmp/c.txt
sed -i '$!s/$/,/' /tmp/c.txt
to_rem=`cat /tmp/c.txt`
delete from $psql_table where $primary_key not in ( select $primary_key from $psql_table where md5(CAST(($primary_key)AS text)) IN ($to_rem));


</code></pre>


# EC2 Version - MySQL

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 

### Supported Data Types
int
bigInt
smallInt
mediumInt
vharchar
decimal
text
float
double
date
enum

auto incremant is supported
unsigned is supported

</code></pre>

1- Connect to MySQL Instance and upload your data

2- Connect to ClickHouse Instance and Create the same table that you will archive from MySQL on ClickHouse

3- Connect to Debezium Instance and edit debezium-mysql.properties file with the following parameters
<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
sudo su - kafka

## edit the following parameter name
cd config/

vi debezium-mysql.properties

topic.prefix = topicName
database.whitelist = test


# Check current running Debezium processes with the following command (you can run only one Debezium Process with port 8083)
lsof -i tcp:8083
# if there is a running process you can kill it with;
kill -9 id

## Then start Debezium
/home/kafka/bin/connect-standalone.sh /home/kafka/config/connect-standalone.properties /home/kafka/config/debezium-mysql.properties
</code></pre>

4- Connect to Kafka Instance and list our topics
<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
sudo su - kafka

## ( Optinal )List Topics
/home/kafka/bin/kafka-topics.sh --list  --bootstrap-server localhost:9092

## ( Optinal ) Edit following command with your current topic name and run the query if you like to list data coming from MySQL 
/home/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic topicName.databaseName.tableName --from-beginning


</code></pre>



5- Connect to Kafka Instance and list our topics
<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
sudo su - kafka

## Go to following directory
cd config/python/

## Open ChistaDATA connector and edit following parameters
vi mysql_clickhouse_v3.py

dest_table='deneme4'                    / should be your ClickHouse Destination Table
topic_name='mysql31.test.deneme4'       / should be your Kafka Topic

## Run the ChistaDATA connector
python3 mysql_clickhouse_v3.py

</code></pre>

6- Go to ClickHouse and check your data 

