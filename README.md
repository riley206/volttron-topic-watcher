# volttron-topic-watcher

The Topic Watcher Agent listens to a set of configured topics and publishes an alert if they are not published within
some time limit.  In addition to for individual messages or data points, the Topic Watcher Agent supports inspecting
device "all" topics.  This can be useful when a device contains volatile points that may not be published.

## Requires

* python >= 3.10
* volttron >= 10.0

## Installation

Before installing, VOLTTRON should be installed and running.  Its virtual environment should be active.
Information on how to install of the VOLTTRON platform can be found
[here](https://github.com/eclipse-volttron/volttron-core).

Create a directory called `config` and use the change directory command to enter it.

```shell
mkdir config
cd config
```

After entering the config directory, create a file called `topic_watcher.json`. Use the instructions below to populate that file with the correct JSON.

Topics are organized by groups in a JSON structure with the group's identifier as the key. Any alerts raised will
summarize all missing topics in the group.

There are two configuration options for watching topics.  For single message topics (such as a single
device point), configuration consists of a key value pair of the topic to its time limit.

```json
{
    "groupname: {
        "devices/campus/building/point": 10
    }
}
```

For points published in an "all" style publish, configuration consts of a key mapping to an object as follows:
A `seconds` key for the time limit in seconds, and a `points` key consisting of a list of individual points in the
`all` publish.

The following is an example "all" publish configuration which configures the Topic Watcher to check for the `temperature`
and `PowerState` points which are expected to be inside the "all" publishes.

```json
{
    "groupname": {
            "devices/fakedriver1/all": {
            "seconds": 10,
            "points": ["temperature", "PowerState"]
        }
    }
}
```

It is possible to configure the Topic Watcher to handle both "all" topics and single point topics for the same group:

```json
{
    "groupname": {
        "devices/fakedriver0/all": 10,
        "devices/fakedriver1/all": {
            "seconds": 10,
            "points": ["temperature", "PowerState"]
        }
    }
}
```

After populating your configuration file, install and start topic watcher in VOLTTRON.

```shell
vctl install volttron-topic-watcher --agent-config topic_watcher.json --vip-identity platform.topic_watcher --start
```

View the status of the installed agent

```shell
vctl status
```

## Development

Please see the following for contributing guidelines [contributing](https://github.com/eclipse-volttron/volttron-core/blob/develop/CONTRIBUTING.md).

Please see the following helpful guide about [developing modular VOLTTRON agents](https://github.com/eclipse-volttron/volttron-core/blob/develop/DEVELOPING_ON_MODULAR.md)

## Disclaimer Notice

This material was prepared as an account of work sponsored by an agency of the
United States Government.  Neither the United States Government nor the United
States Department of Energy, nor Battelle, nor any of their employees, nor any
jurisdiction or organization that has cooperated in the development of these
materials, makes any warranty, express or implied, or assumes any legal
liability or responsibility for the accuracy, completeness, or usefulness or any
information, apparatus, product, software, or process disclosed, or represents
that its use would not infringe privately owned rights.

Reference herein to any specific commercial product, process, or service by
trade name, trademark, manufacturer, or otherwise does not necessarily
constitute or imply its endorsement, recommendation, or favoring by the United
States Government or any agency thereof, or Battelle Memorial Institute. The
views and opinions of authors expressed herein do not necessarily state or
reflect those of the United States Government or any agency thereof.
