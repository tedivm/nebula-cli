# nebula-cli

This project is used with the [Nebula Server](https://github.com/tedivm/nebula) to grant shell script and CLI access to the [Provisioning API](https://github.com/tedivm/nebula/wiki/Provisioning-API).

On newly launched Nebula user instances this program can be in conjection with the system's provisioning system to-

* Notify Nebula when provisioning has completed,
* Change the Name of the instance without granting permission for the machine to edit other AWS Tags,
* Restrict access to the machine to a specific user.


## Configuration

The configuration file will be looked for in these places and in this order, using the first readable file that is found.

* ./.nebulacli (current working directory)
* ~/.nebulacli
* /etc/nebulacli

The format of the file is simple-

```
token_id = d9e5d9ba0735
token = 6566b5d5-90cb-4529-81c5-565a4b10a5cd
url = https://nebula.example
```


## Install

This project can be installed using pip on a python3 system.

For Ubuntu16 that means settings up python3 and pip, as the python2 variants will not work-

```
apt-get install python3-pip
```

Now you can run the install-

```
pip3 install nebulacli
```

Now the program should be available as `nebulacli` to the system.


## Examples

To tell the Nebula that provisioning is finished and the system is ready for use:

```
nebulacli set_status Live
```

To tell Nebula the prefered hostname for the system (allowing Nebula to set the `Name` tag in AWS):

```
nebulacli set_name $(cat /etc/hostname)
```


## Help

This project is build using the [click]() library, and if you run it with no options an up to date help menu will appear. From there you can get help on specific commands by using the `--help` flag when calling any of them.
