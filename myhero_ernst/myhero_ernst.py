#! /usr/bin/python
'''
    Vote Processing Service for Simple Superhero Voting Application

    This is the Vote Processing Service for a basic microservice demo application.
    This service subscribes to a MQTT Queue where votes are submitted by the API
    service.  Votes are then processed into the data service.

    The application was designed to provide a simple demo for Cisco Mantl
'''

__author__ = 'hapresto'

import paho.mqtt.client as mqtt
import sys, os, socket, dns.resolver
import requests

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("MyHero-Votes")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # print(msg.topic+" "+str(msg.payload))
    topic = msg.topic
    payload = msg.payload
    sys.stdout.write("Placing Vote for " + payload + " - ")
    result = record_vote(payload)
    if result == "1" : sys.stdout.write("Vote Successful\n")
    else: sys.stdout.write("Vote UnSuccessful\n")

# Post Vote to Data API
def record_vote(hero):
    u = data_server + "/vote/" + hero
    data_requests_headers = {"key": data_key}
    page = requests.post(u, headers = data_requests_headers)
    result = page.json()["result"]
    return result


# Get SRV Lookup Details for Queueing Server
# The MQTT Server details are expected to be found by processing an SRV Lookup
# The target will be consul for deploments utilizing Mantl.io
# The underlying host running the service must have DNS servers configured to
# Resolve the lookup
def srv_lookup(name):
    resolver = dns.resolver.Resolver()
    results = []
    try:
        for rdata in resolver.query(name, 'SRV'):
            results.append((str(rdata.target), rdata.port))
        # print ("Resolved Service Location as {}".format(results))
    except:
        raise ValueError("Can't find SRV Record")
    return results

# Get IP for Host
def ip_lookup(name):
    resolver = dns.resolver.Resolver()
    results = ""
    try:
        for rdata in resolver.query(name, 'A'):
            results = str(rdata)
        # print ("Resolved Service Location as {}".format(results))
    except:
        raise ValueError("Can't find A Record")
    return results


if __name__=='__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser("MyHero Application Service")
    parser.add_argument(
        "-d", "--dataserver", help="Address of data server", required=False
    )
    parser.add_argument(
        "-k", "--datakey", help="Data Server Authentication Key Used in API Calls", required=False
    )
    parser.add_argument(
        "-q", "--mqttserver", help="MQTT Server FQDN for SRV Lookup", required=False
    )
    parser.add_argument(
        "-i", "--mqtthost", help="MQTT Server Host IP Address", required=False
    )
    parser.add_argument(
        "-p", "--mqttport", help="MQTT Server Port", required=False
    )


    args = parser.parse_args()

    data_server = args.dataserver
    # print "Arg Data: " + str(data_server)
    if (data_server == None):
        data_server = os.getenv("myhero_data_server")
        # print "Env Data: " + str(data_server)
        if (data_server == None):
            get_data_server = raw_input("What is the data server address? ")
            # print "Input Data: " + str(get_data_server)
            data_server = get_data_server
    # print "Data Server: " + data_server
    sys.stderr.write("Data Server: " + data_server + "\n")

    data_key = args.datakey
    # print "Arg Data Key: " + str(data_key)
    if (data_key == None):
        data_key = os.getenv("myhero_data_key")
        # print "Env Data Key: " + str(data_key)
        if (data_key == None):
            get_data_key = raw_input("What is the data server authentication key? ")
            # print "Input Data Key: " + str(get_data_key)
            data_key = get_data_key
    # print "Data Server Key: " + data_key
    sys.stderr.write("Data Server Key: " + data_key + "\n")


    # To find the MQTT Server, two options are possible
    # In order of priority
    # 1.  Explicitly Set mqtthost and mqttport details from Arguments or Environment Variables
    # 2.  Leveraging DNS to lookup an SRV Record to get HOST IP and PORT information
    # Try #1 Option for Explicitly Set Options
    mqtt_host = args.mqtthost
    mqtt_port = args.mqttport
    if (mqtt_host == None and mqtt_port == None):
        mqtt_host = os.getenv("myhero_mqtt_host")
        mqtt_port = os.getenv("myhero_mqtt_port")
        if (mqtt_host == None and mqtt_port == None):
            # Move onto #2 and Try DNS Lookup
            mqtt_server = args.mqttserver
            if (mqtt_server == None):
                mqtt_server = os.getenv("myhero_mqtt_server")
                if (mqtt_server == None):
                    mqtt_server = raw_input("What is the MQTT Server FQDN for an SRV Lookup? ")
            sys.stderr.write("MQTT Server: " + mqtt_server + "\n")
            # Lookup and resolve the IP and Port for the MQTT Server
            try:
                records = srv_lookup(mqtt_server)
                if len(records) != 1: raise Exception("More than 1 SRV Record Returned")
                # To find the HOST IP address need to take the returned hostname from the
                # SRV check and do an IP lookup on it
                mqtt_host = str(ip_lookup(records[0][0]))
                mqtt_port = records[0][1]
            except ValueError:
                raise ValueError("Message Queue Not Found")
    sys.stderr.write("MQTT Host: %s \nMQTT Port: %s\n" % (mqtt_host, mqtt_port))

    # Configure the MQTT Client and register processing functions
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    # Connect to the MQTT Server and Subscribe to the Topic for Votes
    client.connect(mqtt_host, mqtt_port, 60)
    client.loop_forever()
