
# openstack conf tool

create list of options of OpenStack from source code

    [DEFAULT]
    
    (snip...)
    
    compute_driver = None
    # class:      <class 'oslo_config.cfg.StrOpt'>
    # deprecated: False
    # multi:      False
    # required:   False
    # help:
    # Defines which driver to use for controlling virtualization.
    #
    # Possible values:
    #
    # * ``libvirt.LibvirtDriver``
    # * ``xenapi.XenAPIDriver``
    # * ``fake.FakeDriver``
    # * ``ironic.IronicDriver``
    # * ``vmwareapi.VMwareVCDriver``
    # * ``hyperv.HyperVDriver``
    
    (snip...)

## requirement

python 3.4-

python 2.7 may work but not tested

## usage

*use virtualenv*

    # git clone
    # cd path/to/oscfg-tool/
    # virtualenv .
    # bin/activate
    # python scripts/setup_env.py
    # ls tmp/json-*.sh | xargs -n 1 bash -x
    # ls tmp/text-*.sh | xargs -n 1 bash -x

## sample output

[list of nova options](output-sample-pre-ocata/text/nova.txt)

## how it works

1. load openstack source(e.g. [nova/conf/api.py](https://github.com/openstack/nova/blob/master/nova/conf/api.py))
1. call register_opts() or list_opts(), or read global variable cfg.CONF or *_OPTS
1. dump them all

So list may not be perfect.

## author

[wataken44](https://github.com/wataken44) [twitter](https://twitter.com/wataken44)

