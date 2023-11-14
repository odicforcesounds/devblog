# Format your hard drive

1. dd if=/dev/urandom of=/dev/sda status=progress bs=2M
2. dd if=/dev/random of=/dev/sda status=progress bs=2M
3. dd if=/dev/zero of=/dev/sda status=progress bs=2M

## Use LUKS 
cryptsetup -v -y -c aes-xts-plain64 -s 512 -h sha512 -i 5000 --use-random luksFormat /dev/sda3

# Gentookit 
emerge -av gentoolkit 

- Sugest: eclean-kernel, diffmask, flaggie, portpeek, smart-live-rebuild 


