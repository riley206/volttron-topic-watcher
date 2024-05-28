import gevent
import json
import os
import pytest
import sqlite3
from pathlib import Path
from volttron.client.known_identities import CONFIGURATION_STORE, PLATFORM_TOPIC_WATCHER
from volttron.utils import jsonapi
from volttrontesting.platformwrapper import PlatformWrapper

alert_messages = {}
db_connection = None
db_path = None
alert_uuid = None


@pytest.fixture(scope="module")
def agent(request, volttron_instance: PlatformWrapper):
    global db_connection, db_path, alert_uuid
    agent_path = Path(__file__).parents[1]

    alert_uuid = volttron_instance.install_agent(agent_dir=agent_path, vip_identity=PLATFORM_TOPIC_WATCHER, start=True)
    gevent.sleep(2)

    db_path = os.path.join(
        volttron_instance.volttron_home,
        "agents",
        "platform.topic_watcher",
        "data",
        "alert_log.sqlite",
    )

    print(f"DB PATH: {db_path}")
    db_connection = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

    agent = volttron_instance.build_agent()
    gevent.sleep(1)

    capabilities = {"edit_config_store": {"identity": PLATFORM_TOPIC_WATCHER}}
    volttron_instance.add_capabilities(agent.core.publickey, capabilities)

    def onmessage(peer, sender, bus, topic, headers, message):
        global alert_messages
        alert = jsonapi.loads(message)["context"]
        try:
            alert_messages[alert] += 1
        except KeyError:
            alert_messages[alert] = 1
        print("In on message: {}".format(alert_messages))

    agent.vip.pubsub.subscribe(peer="pubsub", prefix="alerts", callback=onmessage)

    def stop():
        volttron_instance.stop_agent(alert_uuid)
        agent.core.stop()
        db_connection.close()

    request.addfinalizer(stop)
    return agent


@pytest.fixture(scope="function")
def cleanup_db():
    global db_connection
    c = db_connection.cursor()
    c.execute("DELETE FROM topic_log")
    c.execute("DELETE FROM agent_log")
    db_connection.commit()


@pytest.mark.alert
def test_config_store(volttron_instance, agent, cleanup_db):
    """
    Test installing the agent with no configuration and applying
    one using the config store. We check if the topics are not
    seen, indicating the config has been stored and used.
    :param agent: fake agent used to make rpc calls to alert agent
    """
    global alert_messages
    gevent.sleep(1)

    capabilities = {"edit_config_store": {"identity": PLATFORM_TOPIC_WATCHER}}
    volttron_instance.add_capabilities(agent.core.publickey, capabilities)
    gevent.sleep(1)

    with open(Path(__file__).parent.resolve() / 'test_config.json') as f:
        agent_config = json.load(f)

    try:
        agent.vip.rpc.call(CONFIGURATION_STORE, "manage_store", PLATFORM_TOPIC_WATCHER, "config",
                           agent_config).get(timeout=10)
        print("Completed manage_store call")
    except Exception as e:
        print(f"Error during manage_store call: {e}")
        raise

    gevent.sleep(10)
    assert volttron_instance.is_agent_running(alert_uuid)

    alert_messages.clear()
    gevent.sleep(5)

    expected_message = "Topic(s) not published within time limit: ['fakedevice', 'fakedevice2/all', ('fakedevice2/all', 'point')]"
    assert expected_message in alert_messages.keys(), f"Expected message not found in alert messages: {alert_messages}"
