SWAP UUID = cc6e0d5a-81b9-4e68-8133-a8791ea591ae

----

Pré-install

1. emerge -av cpuid2cpuflags 

```
# cpuid2cpuflags >> /etc/portage/make.conf 
```

2. Editar /etc/portage/make.conf 

DONOTUSE="-bindist -ipv6"
DOUSE=""
USE="${CPU_FLAGS_X86} ${DONOTUSE} ${DOUSE}"




