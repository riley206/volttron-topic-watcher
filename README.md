# volttron-topic-watcher

The Topic Watcher Agent listens to a set of configured topics and publishes an alert if they are not published within
some time limit.  In addition to for individual messages or data points, the Topic Watcher Agent supports inspecting
device "all" topics.  This can be useful when a device contains volatile points that may not be published.

## Prerequisites

* Python 3.10

## Python

<details>
<summary>To install Python 3.10, we recommend using <a href="https://github.com/pyenv/pyenv"><code>pyenv</code></a>.</summary>

```bash
# install pyenv
git clone https://github.com/pyenv/pyenv ~/.pyenv

# setup pyenv (you should also put these three lines in .bashrc or similar)
export PATH="${HOME}/.pyenv/bin:${PATH}"
export PYENV_ROOT="${HOME}/.pyenv"
eval "$(pyenv init -)"

# install Python 3.10
pyenv install 3.10

# make it available globally
pyenv global system 3.10
```

</details>

## Installation

1. Create and activate a virtual environment.

```shell
python -m venv env
source env/bin/activate
```

2. Install volttron and start the platform.

```shell
pip install volttron

# Start platform with output going to volttron.log
volttron -vv -l volttron.log &
```

3. Create a config directory and navigate to it:

```shell
mkdir config
cd config
```

Navigate to the config directory and create a file called `topic_watcher.config`. Use the instructions below to populate that file with the correct JSON.

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

4. Intsall and start topic watcher in VOLTTRON.

```shell
vctl install volttron-topic-watcher --agent-config topic_watcher.config --vip-identity platform.topic_watcher --start --force
```

### Example Publish

The following is an example publish from the Topic Watcher Agent using the above configuration.

```log
Peer: pubsub
Sender: platform.topic_watcher
Bus:
Topic: alerts/AlertAgent/james_platform_topic_watcher
Headers: {'alert_key': 'AlertAgent Timeout for group group1', 'min_compatible_version': '3.0', 'max_compatible_version': ''}
Message: ('{"status": "BAD", "context": "Topic(s) not published within time limit: '
           '[\'devices/fakedriver0/all\']", "last_updated": '
           '"2021-01-25T23:10:07.905633+00:00"}')
```

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
