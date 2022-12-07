# Data-Archival-Project
The repository contains all the details and codes  about the Data archival projects

POSTGRESQL TO CLICKHOUSE 

Requirements
The wal_level setting must have a logical value and max_replication_slots parameter must have a value at least 2 in the PostgreSQL config file. 

Each replicated table must have one of the following replica identity:
primary key (by default)
index

So we decided to use Debezium PostgreSQL image for these requirements on the docker-compose. These settings are configured by default on this version.

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
clone git repo
</code></pre>


2) Choose PostgreSQL

So we should have these components

Docker-compose.yml - Docker components configuration. 
Chistadata-connector.py - Connecter built using python
Dockerfile - Has the code to build the docker container for Chistadata-connector
Requirements.txt - Has the modules to be installed while building the docker image

3) Run the “docker-compose.yml”

To use the yaml file properly, need to changes some hard coded stuff:
Before applying docker-compose, we need to write our local IP which specifies the “YOUR_LOCAL_IP” and inside the chistadata-connector.py sections. Also need to edit YOUR_COMPUTER_NAME on the kafka section on docker-compose.yaml For example my local IP was 192.168.1.64 and I’ll implement it into chistadata-connector.py. Also wrote my computer name to the folder side on the yaml file.

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 

 kafka:
    image: 'bitnami/kafka:latest'
    user: root
    environment:
      - KAFKA_BROKER_ID=1
      - KAFKA_CFG_ZOOKEEPER_CONNECT=zookeeper:2181
      - ALLOW_PLAINTEXT_LISTENER=yes
      - KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CLIENT:PLAINTEXT,EXTERNAL:PLAINTEXT
      - KAFKA_CFG_LISTENERS=CLIENT://:9092,EXTERNAL://:9093
      - KAFKA_CFG_ADVERTISED_LISTENERS=CLIENT://kafka:9092,EXTERNAL://192.168.1.64:9093
      - KAFKA_CFG_INTER_BROKER_LISTENER_NAME=CLIENT
    ports:
      - "9092:9092"
      - "29092:29092"
      - "9093:9093"
    depends_on:
      - zookeeper
    volumes:
      - /Users/ilkaycetindag/Desktop/PostgreSQL/chistadata-connector.py:/docker-entrypoint-initdb.d/chistadata-connector.py
      </code></pre>
      
  After apply these steps, we can start our docker-compose file with “docker-compose up -d”    

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 

 PostgreSQL docker-compose up -d                  
[+] Running 6/6
 ⠿ Network postgresql_default         Created                                                                                                                                                   0.0s
 ⠿ Container postgresql-postgres-1    Started                                                                                                                                                   0.7s
 ⠿ Container postgresql-zookeeper-1   Started                                                                                                                                                   0.7s
 ⠿ Container postgresql-kafka-1       Started                                                                                                                                                   0.9s
 ⠿ Container postgresql-debezium-1    Started                                                                                                                                                   1.6s
 ⠿ Container postgresql-clickhouse-1  Started   
   </code></pre>
   
   This commands should give us a five running container like
   
   <pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 

 PostgreSQL docker-compose up -d                  
➜  PostgreSQL docker ps
debezium/connect
bitnami/kafka:latest
debezium/postgres:13
confluentinc/cp-zookeeper:5.5.3
clickhouse/clickhouse-server 
   </code></pre>
   
   4) Create a table and insert some data to the PostgreSQL

After all of the components are created, we need to connect PostgreSQL side and create the table which name is shipments and insert some data: 

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
root@874d7d8b47fc:/# su - postgres
postgres@874d7d8b47fc:~$ psql -U postgresuser -d shipment_db
</code></pre>

Then;

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
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

5) Configure the Debezium side

Then, we could connect the Debezium Connector first and need to create a Debezium configuration file to connect to the PostgreSQL side. This script also creates a Kafka Topic which we specified.

Commands need to be done on the Debezium container for this PostgreSQL table. So, we just specified one table here. If necessary, we can use the “*” option to migrate all tables instead of one table name.

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
echo '{
  "name": "shipments-connector",  
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector", 
    "plugin.name": "pgoutput",
    "database.hostname": "postgres", 
    "database.port": "5432", 
    "database.user": "postgresuser", 
    "database.password": "postgrespw", 
    "database.dbname" : "shipment_db", 
    "database.server.name": "postgres", 
    "table.include.list": "public.shipments",
    "topic.prefix": "shipment",
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable": "false",
    "value.converter.schemas.enable": "false",
    "snapshot.mode": "always"
  }
}' > debezium.json
</code></pre>

To create Kafka Topic, apply this one on Debezium side this debezium.json

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 

curl -H 'Content-Type: application/json' debezium:8083/connectors --data "@debezium.json"
</code></pre>


6) Checking the Kafka Topic to have messages

So we can connect the Kafka container now:

With this command, we created the kafka topic which name is “shipments.public.shipment”
To check and validate this, need to connect kafka container and list the all topics:


<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 

/opt/bitnami/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9093  --list

</code></pre>

To see the messages on Kafka Topic, we need to read the messages. So when we manipulate the source db, it should be shown on the Kafka Topic as messages after the installed configuration.
Messages can read with:


<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 

/opt/bitnami/kafka/bin/kafka-console-consumer.sh  --bootstrap-server localhost:9093  --topic shipment.public.shipments --from-beginning
</code></pre>

For example I’ll insert some data on the PostgreSQL side and should see these new messages on the Kafka Topic side. After the Topic is created, we can see the new messages only. That means you couldn't see the old data in messages which were on the PostgreSQL side. Only new insert/update/delete operations (op: c, op:u and op:d) migrated to the Kafka Topic side.

On PostgreSQL container we inserted a row:

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
INSERT INTO shipments values (99999,10500,'2021-01-21','COMPLETED');
</code></pre>


Table is created on the ClickHouse side manually.So we should see new messages like “op: c” on the Kafka Topic side after this operation.

Now we clearly migrate the data PostgreSQL to Kafka until now. And now we need to create ClickHouse table to migrate:


7) Creating the table on ClickHouse side

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
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


Then, we need to migrate all the data that we have on the Kafka Topic side. To do this, we need to edit the python script first according to our environment. So we need to connect the Kafka container again (because python script runs on this container).

In the /docker-entrypoint-initdb.d folder, we need to edit chistadata-connector.py file like:
“consumer” side belongs to the Kafka Topic information and the “client” side represents the ClickHouse side.

8) Entering the correct informations to python side

These tools will be necessary for these steps on Kafka container

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
apt-get update
apt-get install vim -y


</code></pre>

Then,


<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
consumer = KafkaConsumer('shipment.public.shipments',
                         bootstrap_servers=['192.168.1.64:9093'],
                         auto_offset_reset='earliest',
                         group_id='my-group',
                         enable_auto_commit=False)
client = Client(host='192.168.1.64', port=8002)
</code></pre>


And needs to implement ClickHouse table information there. If we want to insert some data based on a where filter, then we can just write “insert into ... (select * from where …)” command.

<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
 if dat['op'] == 'c' or dat['op'] == 'u':

            client.execute('INSERT INTO default.kafka_table (shipment_id, order_id, date_created, status) VALUES',
                           data)       
            print(data)
        elif dat['op'] == 'd':

            client.execute(f"alter table default.kafka_table delete where shipment_id = {data[0]['shipment_id']}")
            print(data)

</code></pre>

After editing these configurations, we can exit all the containers and when we are in the PostgreSQL folder, we can build our dockerfile.


<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
docker build -t dockerfile:latest .
</code></pre>

And after then we can run the python script in the background:


<pre id="example"><code class="language-lang"  style="color: #333; background: #f8f8f8;"> 
docker run dockerfile:latest
</code></pre>

When this command hangs, it means the python script is running. So, we can see the new rows in the ClickHouse side which are op: c, op: u and op: d only.


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
