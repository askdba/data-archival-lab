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

MySQL should be configured with the following variables.
<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
log_bin ( enabled )
server-id ( configured ) 
binlog_format=row
binlog_row_image=full
Table should have the PRIMARY KEY to better work with ReplacingMergetree engine.
</code></pre>

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
clone git repo
</code></pre>

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
2) Switch to MySQL folder
</code></pre>

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
3) Run the “docker-compose.yml”

docker-compose -f docker-compose.yml up

Before running the docker-compose file, we need to update the EXTERNAL connection string using our own IP. ( Kafka component ) The reason is, a chistadata-connector needs to communicate with kafka using external IP as per the current implementation.

Also change user directory in Kafka volume

version: "3.9"
services:
  mysql:
    container_name: mysql
    image: docker.io/bitnami/mysql:latest
    restart: "no"
    ports:
      - "3306:3306"
    environment:
      - MYSQL_ROOT_PASSWORD=root
      - MYSQL_DATABASE=test
      - ALLOW_EMPTY_PASSWORD=yes
    healthcheck:
      test: [ 'CMD', '/opt/bitnami/scripts/mysql/healthcheck.sh' ]
      interval: 15s
      timeout: 5s
      retries: 6
 
  zookeeper:
    image: confluentinc/cp-zookeeper:5.5.3
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
  kafka:
    image: 'bitnami/kafka:latest'
    user: root
    environment:
      - KAFKA_BROKER_ID=1
      - KAFKA_CFG_ZOOKEEPER_CONNECT=zookeeper:2181
      - ALLOW_PLAINTEXT_LISTENER=yes
      - KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CLIENT:PLAINTEXT,EXTERNAL:PLAINTEXT
      - KAFKA_CFG_LISTENERS=CLIENT://:9092,EXTERNAL://:9093
      - KAFKA_CFG_ADVERTISED_LISTENERS=CLIENT://192.168.1.188:9092,EXTERNAL://192.168.1.188:9093
      - KAFKA_CFG_INTER_BROKER_LISTENER_NAME=CLIENT
    ports:
      - "9092:9092"
      - "29092:29092"
      - "9093:9093"
    depends_on:
      - zookeeper
    volumes:
      - /Users/emrahidman/ClickHouseArchival/Data-Archival-Project-main/MySQL/chistadata-connector.py:/docker-entrypoint-initdb.d/chistadata-connector.py
  clickhouse:
    image: clickhouse/clickhouse-server
    ports:
      - "8002:9000"
      - "9123:8123"
    ulimits:
      nproc: 65535
      nofile:
        soft: 262144
        hard: 262144
    depends_on: [zookeeper, kafka]
  debezium:
    image: debezium/connect:2.0.0.Final
    ports:
      - "8083:8083"
    environment:
      - BOOTSTRAP_SERVERS=192.168.1.188:9092
      - GROUP_ID=1
      - CONFIG_STORAGE_TOPIC=my_connect_configs
      - OFFSET_STORAGE_TOPIC=my_connect_offsets
      - STATUS_STORAGE_TOPIC=my_connect_statuses
    depends_on: [zookeeper, kafka]



</code></pre>

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
4) Debezium connector configuration

Execute the following command inside the “debezium” container to configure the connector.
Note: Make sure to change the credentials and connection strings based on the environment.


echo '{
"name": "mysql-connector-1",
"config": {
"connector.class": "io.debezium.connector.mysql.MySqlConnector",
"snapshot.locking.mode": "none",
"tasks.max": "1",
"database.history.kafka.topic": "schema-changes.mysql",
"database.whitelist": "test",
"database.user": "root",
"database.server.id": "1",
"database.server.name": "mysql1",
"database.port": "3306",
"topic.prefix": "mysql1",
"database.hostname": "mysql",
"database.password": "root",
"snapshot.mode": "initial",
"key.converter": "org.apache.kafka.connect.json.JsonConverter",
"value.converter": "org.apache.kafka.connect.json.JsonConverter",
"key.converter.schemas.enable": "false",
"value.converter.schemas.enable": "false",
"internal.key.converter": "org.apache.kafka.connect.json.JsonConverter",
"internal.value.converter": "org.apache.kafka.connect.json.JsonConverter",
"database.history.kafka.bootstrap.servers": "mysql-kafka-1:9092",
"schema.history.internal.kafka.topic": "mysql1",
"schema.history.internal.kafka.bootstrap.servers": "mysql-kafka-1:9092",
"internal.key.converter.schemas.enable": "false",
"internal.value.converter.schemas.enable": "false"
}
}' > debezium.json


curl -H 'Content-Type: application/json' debezium:8083/connectors --data "@debezium.json"


</code></pre>


<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
5) Verify the streaming inside the Kafka container

The following commands can be used to check the topic and the messages inside the kafka container.

/opt/bitnami/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092  --list

/opt/bitnami/kafka/bin/kafka-console-consumer.sh  --bootstrap-server localhost:9092  --topic mysql1.test.chista --from-beginning

Update the topic name.

</code></pre>



<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
6) Table creation:

Table has to be manually created on ClickHouse using the ReplacingMergeTree engine. For example,

MySQL:

Connect MySQL

mysql -u root -p
password: root

CREATE TABLE `chista` (
  `id` int NOT NULL,
  `name` varchar(16) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

ClickHouse:

CREATE TABLE IF NOT EXISTS default.chista
(
id Int32,
name String
)
ENGINE = ReplacingMergeTree
ORDER BY id;

</code></pre>



<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
7) Build the docker image for chistadata-connector

We already have the dockerfile in the repo. 

sakthivel@Sris-MacBook-Pro MySQL % cat dockerfile 
FROM python:3.9
ADD requirements.txt /
RUN pip install -r requirements.txt
RUN pip install kafka-python
ADD chistadata-connector.py /
CMD [ "python", "./chistadata-connector.py" ]

The docker-connector.py needs the following modifications.

consumer = KafkaConsumer('mysql1.test.chista',   
                         bootstrap_servers=['192.168.1.2:9093'],
                         auto_offset_reset='earliest',
                         group_id='my-group',
                         enable_auto_commit=False)

client = Client(host='192.168.1.2', port=8002)

....
....


            client.execute('INSERT INTO default.chista (id,name) VALUES',
                           data)       
            print(data)
        elif dat['op'] == 'd':

            client.execute(f"alter table default.chista delete where id = {data[0]['id']}")
            print(data)


After modifying the topic name and connection details, Just execute the following command to build the image.

docker build -t dockerfile:latest .
docker run dockerfile:latest

When we run the “docker run” command, it will start the container and start to apply the messages on ClickHouse from kafka topic.


</code></pre>




# POSTGRESQL TO CLICKHOUSE 

PostgreSQL Implementation:
Requirements
The wal_level setting must have a logical value and max_replication_slots parameter must have a value at least 2 in the PostgreSQL config file. 

Each replicated table must have one of the following replica identity:
primary key (by default)
index

So we decided to use Debezium PostgreSQL image for these requirements on the docker-compose. These settings are configured by default on this version.

1) Clone the GIT repo 

https://github.com/ChistaDATA/Data-Archival-Project.git


2) Choose PostgreSQL

So we should have these components

Docker-compose.yml - Docker components configuration. 
Debezium.json - Debezium components configuration for source db.
Config.xml - To allow ClickHouse external connections.

3) Run the “docker-compose.yml”

After apply these steps, we can start our docker-compose file with “docker-compose up -d”

➜  PostgreSQL docker-compose up -d                  
[+] Running 6/6
debezium/connect:latest
clickhouse/clickhouse-server:latest
confluentinc/cp-kafka:latest
confluentinc/cp-zookeeper:latest 
debezium/postgres:14
ihsnlky/python:latest


4) To start CDC process, create Kafka Topic and apply this one on Debezium side this debezium.json

curl -H 'Content-Type: application/json' debezium:8083/connectors --data "@debezium.json"


All configurations set for shipment_db in PostgreSQL side. If you want to learn more detail about postgreSQL information, or if you want to migrate another table to Kafka, you can edit the debezium.json file in the Debezium container. If necessary, we can use the “*” option to migrate all tables instead of one table name.

5) Create a table and insert some data to the PostgreSQL

After all of the components are created, we need to connect PostgreSQL side and create the table which name is shipments and insert some data: 

root@874d7d8b47fc:/# su - postgres
postgres@874d7d8b47fc:~$ psql -U postgresuser -d shipment_db


Then;
CREATE TABLE IF NOT EXISTS shipments
(
    shipment_id bigint NOT NULL,
    order_id bigint NOT NULL,
    date_created character varying(255) COLLATE pg_catalog."default",
    status character varying(25) COLLATE pg_catalog."default",
    CONSTRAINT shipments_pkey PRIMARY KEY (shipment_id)
);

INSERT INTO shipments values (30500,10500,'2021-01-21','COMPLETED');

6) Checking the Kafka Topic to have messages

So we can connect the Kafka container now:

With this command, we created the kafka topic which name is “shipments.public.shipment”
To check and validate this, need to connect kafka container and list the all topics:

/usr/bin/kafka-topics --list  --bootstrap-server kafka:9092


To see the messages on Kafka Topic, we need to read the messages. So when we manipulate the source db, it should be shown on the Kafka Topic as messages after the installed configuration.
Messages can read with:
/usr/bin/kafka-console-consumer  --bootstrap-server kafka:9092  --topic shipment.public.shipments --from-beginning

For example I’ll insert some data on the PostgreSQL side and should see these new messages on the Kafka Topic side. After the Topic is created, we can see the new messages only. That means you couldn't see the old data in messages which were on the PostgreSQL side. Only new insert/update/delete operations (op: c, op:u and op:d) migrated to the Kafka Topic side.

Table is created on the ClickHouse side manually.So we should see new messages like “op: c” on the Kafka Topic side after this operation.

Now we clearly migrate the data PostgreSQL to Kafka until now. And now we need to create ClickHouse table to migrate:

7) Creating the table on ClickHouse side


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







8) Connect the Python side and run the python script


python3 chistadata-connector.py


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
