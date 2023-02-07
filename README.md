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
https://github.com/ChistaDATA/Data-Archival-Project.git

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




3- To start CDC process, create Kafka Topic and apply this one on Debezium side this debezium.json

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
curl -H 'Content-Type: application/json' debezium:8083/connectors --data "@debezium.json"
</code></pre>



All configurations set for shipment_db in PostgreSQL side. If you want to learn more detail about postgreSQL information, or if you want to migrate another table to Kafka, you can edit the debezium.json file in the Debezium container. If necessary, we can use the “*” option to migrate all tables instead of one table name.

4 - Create a table and insert some data to the MySQL

After all of the components are created, we need to connect MySQL side and create the table which name is shipments and insert some data:

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
Table creation:

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

Insert data into MySQL

insert into chista values (47,"can");


Just create table in clickhouse

ClickHouse:

CREATE TABLE IF NOT EXISTS default.chista
(
id Int32,
name String
)
ENGINE = ReplacingMergeTree
ORDER BY id;

</code></pre>

5- With this command, we created the kafka topic which name is “mysql.test.chista” To check and validate this, need to connect kafka container and list the all topics:


<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 

/usr/bin/kafka-topics --list  --bootstrap-server kafka:9092
</code></pre>


To see the messages on Kafka Topic, we need to read the messages. So when we manipulate the source db, it should be shown on the Kafka Topic as messages after the installed configuration. Messages can read with:

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 

/usr/bin/kafka-console-consumer  --bootstrap-server kafka:9092  --topic mysql.test.chista --from-beginning

</code></pre>

For example I’ll insert some data on the MySQL side and should see these new messages on the Kafka Topic side. After the Topic is created, we can see the new messages only. That means you couldn't see the old data in messages which were on the PostgreSQL side. Only new insert/update/delete operations (op: c, op:u and op:d) migrated to the Kafka Topic side.


 
6 - Connect to python container and run the following command to start chistada connector

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
python3 chistadata-connector.py
</code></pre>

According to operation names (op: c, op: u and op: d), python side will apply the changes to ClickHouse side. When we check the ClickHouse side, data should be see:


7- Now you can connect to clickhouse and check the data
<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
clickhouse-client

use default

select * from chista;
</code></pre






