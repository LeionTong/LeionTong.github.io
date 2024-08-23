---
title: SSH-Key-authentication-fails
date: 2021-08-13T16:00:00.000Z
tags: null
---

# 记一次root用户进行秘钥登录验证失败问题
 ## 现象描述：
在一次常规给 root 用户配置秘钥登录过程中，通过命令  `ssh-copy-id` 正常导入秘钥到服务器端，在服务器上的 authorized_keys 文件里也能查到客户端的公钥信息，但使用秘钥登录时候仍然提示输入密码。


## 问题分析：
普通用户SSH秘钥登录没问题：
```
 ssh -vvv leion@lfs9.0 
OpenSSH_8.6p1, OpenSSL 1.1.1k  25 Mar 2021
debug1: Reading configuration data /home/leion/.ssh/config
debug1: /home/leion/.ssh/config line 1: Applying options for *
debug1: Reading configuration data /etc/ssh/ssh_config
<!-- more -->
debug3: expanded UserKnownHostsFile '~/.ssh/known_hosts' -> '/home/leion/.ssh/known_hosts'
debug3: expanded UserKnownHostsFile '~/.ssh/known_hosts2' -> '/home/leion/.ssh/known_hosts2'
debug2: resolving "lfs9.0" port 22
debug3: ssh_connect_direct: entering
debug1: Connecting to lfs9.0 [172.18.253.20] port 22.
debug3: set_sock_tos: set socket 3 IP_TOS 0x48
debug1: Connection established.
debug1: identity file /home/leion/.ssh/id_rsa type 0
debug1: identity file /home/leion/.ssh/id_rsa-cert type -1
debug1: identity file /home/leion/.ssh/id_dsa type -1
debug1: identity file /home/leion/.ssh/id_dsa-cert type -1
debug1: identity file /home/leion/.ssh/id_ecdsa type -1
debug1: identity file /home/leion/.ssh/id_ecdsa-cert type -1
debug1: identity file /home/leion/.ssh/id_ecdsa_sk type -1
debug1: identity file /home/leion/.ssh/id_ecdsa_sk-cert type -1
debug1: identity file /home/leion/.ssh/id_ed25519 type -1
debug1: identity file /home/leion/.ssh/id_ed25519-cert type -1
debug1: identity file /home/leion/.ssh/id_ed25519_sk type -1
debug1: identity file /home/leion/.ssh/id_ed25519_sk-cert type -1
debug1: identity file /home/leion/.ssh/id_xmss type -1
debug1: identity file /home/leion/.ssh/id_xmss-cert type -1
debug1: Local version string SSH-2.0-OpenSSH_8.6
debug1: Remote protocol version 2.0, remote software version OpenSSH_8.0
debug1: compat_banner: match: OpenSSH_8.0 pat OpenSSH* compat 0x04000000
debug2: fd 3 setting O_NONBLOCK
debug1: Authenticating to lfs9.0:22 as 'leion'
debug3: record_hostkey: found key type ED25519 in file /home/leion/.ssh/known_hosts:16
debug3: record_hostkey: found key type RSA in file /home/leion/.ssh/known_hosts:17
debug3: record_hostkey: found key type ECDSA in file /home/leion/.ssh/known_hosts:18
debug3: load_hostkeys_file: loaded 3 keys from lfs9.0
debug1: load_hostkeys: fopen /home/leion/.ssh/known_hosts2: No such file or directory
debug1: load_hostkeys: fopen /etc/ssh/ssh_known_hosts: No such file or directory
debug1: load_hostkeys: fopen /etc/ssh/ssh_known_hosts2: No such file or directory
debug3: order_hostkeyalgs: have matching best-preference key type ssh-ed25519-cert-v01@openssh.com, using HostkeyAlgorithms verbatim
debug3: send packet: type 20
debug1: SSH2_MSG_KEXINIT sent
debug3: receive packet: type 20
debug1: SSH2_MSG_KEXINIT received
debug2: local client KEXINIT proposal
debug2: KEX algorithms: curve25519-sha256,curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group-exchange-sha256,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,diffie-hellman-group14-sha256,ext-info-c
debug2: host key algorithms: ssh-ed25519-cert-v01@openssh.com,ecdsa-sha2-nistp256-cert-v01@openssh.com,ecdsa-sha2-nistp384-cert-v01@openssh.com,ecdsa-sha2-nistp521-cert-v01@openssh.com,sk-ssh-ed25519-cert-v01@openssh.com,sk-ecdsa-sha2-nistp256-cert-v01@openssh.com,rsa-sha2-512-cert-v01@openssh.com,rsa-sha2-256-cert-v01@openssh.com,ssh-rsa-cert-v01@openssh.com,ssh-ed25519,ecdsa-sha2-nistp256,ecdsa-sha2-nistp384,ecdsa-sha2-nistp521,sk-ssh-ed25519@openssh.com,sk-ecdsa-sha2-nistp256@openssh.com,rsa-sha2-512,rsa-sha2-256,ssh-rsa
debug2: ciphers ctos: chacha20-poly1305@openssh.com,aes128-ctr,aes192-ctr,aes256-ctr,aes128-gcm@openssh.com,aes256-gcm@openssh.com
debug2: ciphers stoc: chacha20-poly1305@openssh.com,aes128-ctr,aes192-ctr,aes256-ctr,aes128-gcm@openssh.com,aes256-gcm@openssh.com
debug2: MACs ctos: umac-64-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha1-etm@openssh.com,umac-64@openssh.com,umac-128@openssh.com,hmac-sha2-256,hmac-sha2-512,hmac-sha1
debug2: MACs stoc: umac-64-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha1-etm@openssh.com,umac-64@openssh.com,umac-128@openssh.com,hmac-sha2-256,hmac-sha2-512,hmac-sha1
debug2: compression ctos: none,zlib@openssh.com,zlib
debug2: compression stoc: none,zlib@openssh.com,zlib
debug2: languages ctos: 
debug2: languages stoc: 
debug2: first_kex_follows 0 
debug2: reserved 0 
debug2: peer server KEXINIT proposal
debug2: KEX algorithms: curve25519-sha256,curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group-exchange-sha256,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,diffie-hellman-group14-sha256,diffie-hellman-group14-sha1
debug2: host key algorithms: rsa-sha2-512,rsa-sha2-256,ssh-rsa,ecdsa-sha2-nistp256,ssh-ed25519
debug2: ciphers ctos: chacha20-poly1305@openssh.com,aes128-ctr,aes192-ctr,aes256-ctr,aes128-gcm@openssh.com,aes256-gcm@openssh.com
debug2: ciphers stoc: chacha20-poly1305@openssh.com,aes128-ctr,aes192-ctr,aes256-ctr,aes128-gcm@openssh.com,aes256-gcm@openssh.com
debug2: MACs ctos: umac-64-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha1-etm@openssh.com,umac-64@openssh.com,umac-128@openssh.com,hmac-sha2-256,hmac-sha2-512,hmac-sha1
debug2: MACs stoc: umac-64-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha1-etm@openssh.com,umac-64@openssh.com,umac-128@openssh.com,hmac-sha2-256,hmac-sha2-512,hmac-sha1
debug2: compression ctos: none,zlib@openssh.com
debug2: compression stoc: none,zlib@openssh.com
debug2: languages ctos: 
debug2: languages stoc: 
debug2: first_kex_follows 0 
debug2: reserved 0 
debug1: kex: algorithm: curve25519-sha256
debug1: kex: host key algorithm: ssh-ed25519
debug1: kex: server->client cipher: chacha20-poly1305@openssh.com MAC: <implicit> compression: none
debug1: kex: client->server cipher: chacha20-poly1305@openssh.com MAC: <implicit> compression: none
debug3: send packet: type 30
debug1: expecting SSH2_MSG_KEX_ECDH_REPLY
debug3: receive packet: type 31
debug1: SSH2_MSG_KEX_ECDH_REPLY received
debug1: Server host key: ssh-ed25519 SHA256:5qgDoZ2wLmGrg8sg76UjOpuT8r7ZPU86K27MzyjdoU0
debug3: record_hostkey: found key type ED25519 in file /home/leion/.ssh/known_hosts:16
debug3: record_hostkey: found key type RSA in file /home/leion/.ssh/known_hosts:17
debug3: record_hostkey: found key type ECDSA in file /home/leion/.ssh/known_hosts:18
debug3: load_hostkeys_file: loaded 3 keys from lfs9.0
debug1: load_hostkeys: fopen /home/leion/.ssh/known_hosts2: No such file or directory
debug1: load_hostkeys: fopen /etc/ssh/ssh_known_hosts: No such file or directory
debug1: load_hostkeys: fopen /etc/ssh/ssh_known_hosts2: No such file or directory
debug1: Host 'lfs9.0' is known and matches the ED25519 host key.
debug1: Found key in /home/leion/.ssh/known_hosts:16
debug3: send packet: type 21
debug2: set_newkeys: mode 1
debug1: rekey out after 134217728 blocks
debug1: SSH2_MSG_NEWKEYS sent
debug1: expecting SSH2_MSG_NEWKEYS
debug3: receive packet: type 21
debug1: SSH2_MSG_NEWKEYS received
debug2: set_newkeys: mode 0
debug1: rekey in after 134217728 blocks
debug1: Will attempt key: /home/leion/.ssh/id_rsa RSA SHA256:UXDMPHJtm3qgRkqPhOLEoGtkmpe1YeGshOPnfmLdIZU
debug1: Will attempt key: /home/leion/.ssh/id_dsa 
debug1: Will attempt key: /home/leion/.ssh/id_ecdsa 
debug1: Will attempt key: /home/leion/.ssh/id_ecdsa_sk 
debug1: Will attempt key: /home/leion/.ssh/id_ed25519 
debug1: Will attempt key: /home/leion/.ssh/id_ed25519_sk 
debug1: Will attempt key: /home/leion/.ssh/id_xmss 
debug2: pubkey_prepare: done
debug3: send packet: type 5
debug3: receive packet: type 7
debug1: SSH2_MSG_EXT_INFO received
debug1: kex_input_ext_info: server-sig-algs=<ssh-ed25519,ssh-rsa,rsa-sha2-256,rsa-sha2-512,ssh-dss,ecdsa-sha2-nistp256,ecdsa-sha2-nistp384,ecdsa-sha2-nistp521>
debug3: receive packet: type 6
debug2: service_accept: ssh-userauth
debug1: SSH2_MSG_SERVICE_ACCEPT received
debug3: send packet: type 50
debug3: receive packet: type 51
debug1: Authentications that can continue: publickey,password,keyboard-interactive
debug3: start over, passed a different list publickey,password,keyboard-interactive
debug3: preferred publickey,keyboard-interactive,password
debug3: authmethod_lookup publickey
debug3: remaining preferred: keyboard-interactive,password
debug3: authmethod_is_enabled publickey
debug1: Next authentication method: publickey
debug1: Offering public key: /home/leion/.ssh/id_rsa RSA SHA256:UXDMPHJtm3qgRkqPhOLEoGtkmpe1YeGshOPnfmLdIZU
debug3: send packet: type 50
debug2: we sent a publickey packet, wait for reply
debug3: receive packet: type 60
debug1: Server accepts key: /home/leion/.ssh/id_rsa RSA SHA256:UXDMPHJtm3qgRkqPhOLEoGtkmpe1YeGshOPnfmLdIZU
debug3: sign_and_send_pubkey: RSA SHA256:UXDMPHJtm3qgRkqPhOLEoGtkmpe1YeGshOPnfmLdIZU
debug3: sign_and_send_pubkey: signing using rsa-sha2-512 SHA256:UXDMPHJtm3qgRkqPhOLEoGtkmpe1YeGshOPnfmLdIZU
debug3: send packet: type 50
debug3: receive packet: type 52
debug1: Authentication succeeded (publickey).
Authenticated to lfs9.0 ([172.18.253.20]:22).
debug1: channel 0: new [client-session]
debug3: ssh_session2_open: channel_new: 0
debug2: channel 0: send open
debug3: send packet: type 90
debug1: Requesting no-more-sessions@openssh.com
debug3: send packet: type 80
debug1: Entering interactive session.
debug1: pledge: filesystem full
debug3: receive packet: type 80
debug1: client_input_global_request: rtype hostkeys-00@openssh.com want_reply 0
debug3: client_input_hostkeys: received RSA key SHA256:y7j2+X0eDHrJjPT3yvtphPJn96f5zdWhJHd1NCR5KgE
debug3: client_input_hostkeys: received ECDSA key SHA256:94uXUkX1Dtv7EfbjJ5AtoJchht5DqI+6qv+K7Zo2WX0
debug3: client_input_hostkeys: received ED25519 key SHA256:5qgDoZ2wLmGrg8sg76UjOpuT8r7ZPU86K27MzyjdoU0
debug1: client_input_hostkeys: searching /home/leion/.ssh/known_hosts for lfs9.0 / (none)
debug3: hostkeys_foreach: reading file "/home/leion/.ssh/known_hosts"
debug3: hostkeys_find: found ssh-ed25519 key at /home/leion/.ssh/known_hosts:16
debug3: hostkeys_find: found ssh-rsa key at /home/leion/.ssh/known_hosts:17
debug3: hostkeys_find: found ecdsa-sha2-nistp256 key at /home/leion/.ssh/known_hosts:18
debug1: client_input_hostkeys: searching /home/leion/.ssh/known_hosts2 for lfs9.0 / (none)
debug1: client_input_hostkeys: hostkeys file /home/leion/.ssh/known_hosts2 does not exist
debug3: client_input_hostkeys: 3 server keys: 0 new, 3 retained, 0 incomplete match. 0 to remove
debug1: client_input_hostkeys: no new or deprecated keys from server
debug3: receive packet: type 4
debug1: Remote: /home/leion/.ssh/authorized_keys:1: key options: agent-forwarding port-forwarding pty user-rc x11-forwarding
debug3: receive packet: type 4
debug1: Remote: /home/leion/.ssh/authorized_keys:1: key options: agent-forwarding port-forwarding pty user-rc x11-forwarding
debug3: receive packet: type 91
debug2: channel_input_open_confirmation: channel 0: callback start
debug2: fd 3 setting TCP_NODELAY
debug3: set_sock_tos: set socket 3 IP_TOS 0x48
debug2: client_session2_setup: id 0
debug2: channel 0: request pty-req confirm 1
debug3: send packet: type 98
debug2: channel 0: request shell confirm 1
debug3: send packet: type 98
debug2: channel_input_open_confirmation: channel 0: callback done
debug2: channel 0: open confirm rwindow 0 rmax 32768
debug3: receive packet: type 99
debug2: channel_input_status_confirm: type 99 id 0
debug2: PTY allocation request accepted on channel 0
debug2: channel 0: rcvd adjust 2097152
debug3: receive packet: type 99
debug2: channel_input_status_confirm: type 99 id 0
debug2: shell request accepted on channel 0
Last login: Fri Aug 13 03:25:05 2021 from 192.168.1.216
-bash-5.0$ 
-bash-5.0$ 
-bash-5.0$ 
-bash-5.0$ sudo reboot^C
-bash-5.0$ debug3: receive packet: type 98
debug1: client_input_channel_req: channel 0 rtype exit-status reply 0
debug3: receive packet: type 98
debug1: client_input_channel_req: channel 0 rtype eow@openssh.com reply 0
debug2: channel 0: rcvd eow
debug2: chan_shutdown_read: channel 0: (i0 o0 sock -1 wfd 4 efd 6 [write])
debug2: channel 0: input open -> closed
logout
debug3: receive packet: type 96
debug2: channel 0: rcvd eof
debug2: channel 0: output open -> drain
debug2: channel 0: obuf empty
debug2: chan_shutdown_write: channel 0: (i3 o1 sock -1 wfd 5 efd 6 [write])
debug2: channel 0: output drain -> closed
debug3: receive packet: type 97
debug2: channel 0: rcvd close
debug3: channel 0: will not send data after close
debug2: channel 0: almost dead
debug2: channel 0: gc: notify user
debug2: channel 0: gc: user detached
debug2: channel 0: send close
debug3: send packet: type 97
debug2: channel 0: is dead
debug2: channel 0: garbage collecting
debug1: channel 0: free: client-session, nchannels 1
debug3: channel 0: status: The following connections are open:
  #0 client-session (t4 r0 i3/0 o3/0 e[write]/0 fd -1/-1/6 sock -1 cc -1)

debug3: send packet: type 1
debug3: fd 1 is not O_NONBLOCK
Connection to lfs9.0 closed.
Transferred: sent 3300, received 3324 bytes, in 15.3 seconds
Bytes per second: sent 215.3, received 216.8
debug1: Exit status 130 
```

root用户SSH秘钥登录：
```
ssh -vvv root@lfs9.0 
OpenSSH_8.6p1, OpenSSL 1.1.1k  25 Mar 2021
debug1: Reading configuration data /home/leion/.ssh/config
debug1: /home/leion/.ssh/config line 1: Applying options for *
debug1: Reading configuration data /etc/ssh/ssh_config
debug3: expanded UserKnownHostsFile '~/.ssh/known_hosts' -> '/home/leion/.ssh/known_hosts'
debug3: expanded UserKnownHostsFile '~/.ssh/known_hosts2' -> '/home/leion/.ssh/known_hosts2'
debug2: resolving "lfs9.0" port 22
debug3: ssh_connect_direct: entering
debug1: Connecting to lfs9.0 [172.18.253.20] port 22.
debug3: set_sock_tos: set socket 3 IP_TOS 0x48
debug1: Connection established.
debug1: identity file /home/leion/.ssh/id_rsa type 0
debug1: identity file /home/leion/.ssh/id_rsa-cert type -1
debug1: identity file /home/leion/.ssh/id_dsa type -1
debug1: identity file /home/leion/.ssh/id_dsa-cert type -1
debug1: identity file /home/leion/.ssh/id_ecdsa type -1
debug1: identity file /home/leion/.ssh/id_ecdsa-cert type -1
debug1: identity file /home/leion/.ssh/id_ecdsa_sk type -1
debug1: identity file /home/leion/.ssh/id_ecdsa_sk-cert type -1
debug1: identity file /home/leion/.ssh/id_ed25519 type -1
debug1: identity file /home/leion/.ssh/id_ed25519-cert type -1
debug1: identity file /home/leion/.ssh/id_ed25519_sk type -1
debug1: identity file /home/leion/.ssh/id_ed25519_sk-cert type -1
debug1: identity file /home/leion/.ssh/id_xmss type -1
debug1: identity file /home/leion/.ssh/id_xmss-cert type -1
debug1: Local version string SSH-2.0-OpenSSH_8.6
debug1: Remote protocol version 2.0, remote software version OpenSSH_8.0
debug1: compat_banner: match: OpenSSH_8.0 pat OpenSSH* compat 0x04000000
debug2: fd 3 setting O_NONBLOCK
debug1: Authenticating to lfs9.0:22 as 'root'
debug3: record_hostkey: found key type ED25519 in file /home/leion/.ssh/known_hosts:16
debug3: record_hostkey: found key type RSA in file /home/leion/.ssh/known_hosts:17
debug3: record_hostkey: found key type ECDSA in file /home/leion/.ssh/known_hosts:18
debug3: load_hostkeys_file: loaded 3 keys from lfs9.0
debug1: load_hostkeys: fopen /home/leion/.ssh/known_hosts2: No such file or directory
debug1: load_hostkeys: fopen /etc/ssh/ssh_known_hosts: No such file or directory
debug1: load_hostkeys: fopen /etc/ssh/ssh_known_hosts2: No such file or directory
debug3: order_hostkeyalgs: have matching best-preference key type ssh-ed25519-cert-v01@openssh.com, using HostkeyAlgorithms verbatim
debug3: send packet: type 20
debug1: SSH2_MSG_KEXINIT sent
debug3: receive packet: type 20
debug1: SSH2_MSG_KEXINIT received
debug2: local client KEXINIT proposal
debug2: KEX algorithms: curve25519-sha256,curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group-exchange-sha256,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,diffie-hellman-group14-sha256,ext-info-c
debug2: host key algorithms: ssh-ed25519-cert-v01@openssh.com,ecdsa-sha2-nistp256-cert-v01@openssh.com,ecdsa-sha2-nistp384-cert-v01@openssh.com,ecdsa-sha2-nistp521-cert-v01@openssh.com,sk-ssh-ed25519-cert-v01@openssh.com,sk-ecdsa-sha2-nistp256-cert-v01@openssh.com,rsa-sha2-512-cert-v01@openssh.com,rsa-sha2-256-cert-v01@openssh.com,ssh-rsa-cert-v01@openssh.com,ssh-ed25519,ecdsa-sha2-nistp256,ecdsa-sha2-nistp384,ecdsa-sha2-nistp521,sk-ssh-ed25519@openssh.com,sk-ecdsa-sha2-nistp256@openssh.com,rsa-sha2-512,rsa-sha2-256,ssh-rsa
debug2: ciphers ctos: chacha20-poly1305@openssh.com,aes128-ctr,aes192-ctr,aes256-ctr,aes128-gcm@openssh.com,aes256-gcm@openssh.com
debug2: ciphers stoc: chacha20-poly1305@openssh.com,aes128-ctr,aes192-ctr,aes256-ctr,aes128-gcm@openssh.com,aes256-gcm@openssh.com
debug2: MACs ctos: umac-64-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha1-etm@openssh.com,umac-64@openssh.com,umac-128@openssh.com,hmac-sha2-256,hmac-sha2-512,hmac-sha1
debug2: MACs stoc: umac-64-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha1-etm@openssh.com,umac-64@openssh.com,umac-128@openssh.com,hmac-sha2-256,hmac-sha2-512,hmac-sha1
debug2: compression ctos: none,zlib@openssh.com,zlib
debug2: compression stoc: none,zlib@openssh.com,zlib
debug2: languages ctos: 
debug2: languages stoc: 
debug2: first_kex_follows 0 
debug2: reserved 0 
debug2: peer server KEXINIT proposal
debug2: KEX algorithms: curve25519-sha256,curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group-exchange-sha256,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,diffie-hellman-group14-sha256,diffie-hellman-group14-sha1
debug2: host key algorithms: rsa-sha2-512,rsa-sha2-256,ssh-rsa,ecdsa-sha2-nistp256,ssh-ed25519
debug2: ciphers ctos: chacha20-poly1305@openssh.com,aes128-ctr,aes192-ctr,aes256-ctr,aes128-gcm@openssh.com,aes256-gcm@openssh.com
debug2: ciphers stoc: chacha20-poly1305@openssh.com,aes128-ctr,aes192-ctr,aes256-ctr,aes128-gcm@openssh.com,aes256-gcm@openssh.com
debug2: MACs ctos: umac-64-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha1-etm@openssh.com,umac-64@openssh.com,umac-128@openssh.com,hmac-sha2-256,hmac-sha2-512,hmac-sha1
debug2: MACs stoc: umac-64-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha1-etm@openssh.com,umac-64@openssh.com,umac-128@openssh.com,hmac-sha2-256,hmac-sha2-512,hmac-sha1
debug2: compression ctos: none,zlib@openssh.com
debug2: compression stoc: none,zlib@openssh.com
debug2: languages ctos: 
debug2: languages stoc: 
debug2: first_kex_follows 0 
debug2: reserved 0 
debug1: kex: algorithm: curve25519-sha256
debug1: kex: host key algorithm: ssh-ed25519
debug1: kex: server->client cipher: chacha20-poly1305@openssh.com MAC: <implicit> compression: none
debug1: kex: client->server cipher: chacha20-poly1305@openssh.com MAC: <implicit> compression: none
debug3: send packet: type 30
debug1: expecting SSH2_MSG_KEX_ECDH_REPLY
debug3: receive packet: type 31
debug1: SSH2_MSG_KEX_ECDH_REPLY received
debug1: Server host key: ssh-ed25519 SHA256:5qgDoZ2wLmGrg8sg76UjOpuT8r7ZPU86K27MzyjdoU0
debug3: record_hostkey: found key type ED25519 in file /home/leion/.ssh/known_hosts:16
debug3: record_hostkey: found key type RSA in file /home/leion/.ssh/known_hosts:17
debug3: record_hostkey: found key type ECDSA in file /home/leion/.ssh/known_hosts:18
debug3: load_hostkeys_file: loaded 3 keys from lfs9.0
debug1: load_hostkeys: fopen /home/leion/.ssh/known_hosts2: No such file or directory
debug1: load_hostkeys: fopen /etc/ssh/ssh_known_hosts: No such file or directory
debug1: load_hostkeys: fopen /etc/ssh/ssh_known_hosts2: No such file or directory
debug1: Host 'lfs9.0' is known and matches the ED25519 host key.
debug1: Found key in /home/leion/.ssh/known_hosts:16
debug3: send packet: type 21
debug2: set_newkeys: mode 1
debug1: rekey out after 134217728 blocks
debug1: SSH2_MSG_NEWKEYS sent
debug1: expecting SSH2_MSG_NEWKEYS
debug3: receive packet: type 21
debug1: SSH2_MSG_NEWKEYS received
debug2: set_newkeys: mode 0
debug1: rekey in after 134217728 blocks
debug1: Will attempt key: /home/leion/.ssh/id_rsa RSA SHA256:UXDMPHJtm3qgRkqPhOLEoGtkmpe1YeGshOPnfmLdIZU
debug1: Will attempt key: /home/leion/.ssh/id_dsa 
debug1: Will attempt key: /home/leion/.ssh/id_ecdsa 
debug1: Will attempt key: /home/leion/.ssh/id_ecdsa_sk 
debug1: Will attempt key: /home/leion/.ssh/id_ed25519 
debug1: Will attempt key: /home/leion/.ssh/id_ed25519_sk 
debug1: Will attempt key: /home/leion/.ssh/id_xmss 
debug2: pubkey_prepare: done
debug3: send packet: type 5
debug3: receive packet: type 7
debug1: SSH2_MSG_EXT_INFO received
debug1: kex_input_ext_info: server-sig-algs=<ssh-ed25519,ssh-rsa,rsa-sha2-256,rsa-sha2-512,ssh-dss,ecdsa-sha2-nistp256,ecdsa-sha2-nistp384,ecdsa-sha2-nistp521>
debug3: receive packet: type 6
debug2: service_accept: ssh-userauth
debug1: SSH2_MSG_SERVICE_ACCEPT received
debug3: send packet: type 50
debug3: receive packet: type 51
debug1: Authentications that can continue: publickey,password,keyboard-interactive
debug3: start over, passed a different list publickey,password,keyboard-interactive
debug3: preferred publickey,keyboard-interactive,password
debug3: authmethod_lookup publickey
debug3: remaining preferred: keyboard-interactive,password
debug3: authmethod_is_enabled publickey
debug1: Next authentication method: publickey
debug1: Offering public key: /home/leion/.ssh/id_rsa RSA SHA256:UXDMPHJtm3qgRkqPhOLEoGtkmpe1YeGshOPnfmLdIZU
debug3: send packet: type 50
debug2: we sent a publickey packet, wait for reply
debug3: receive packet: type 51
debug1: Authentications that can continue: publickey,password,keyboard-interactive
debug1: Trying private key: /home/leion/.ssh/id_dsa
debug3: no such identity: /home/leion/.ssh/id_dsa: No such file or directory
debug1: Trying private key: /home/leion/.ssh/id_ecdsa
debug3: no such identity: /home/leion/.ssh/id_ecdsa: No such file or directory
debug1: Trying private key: /home/leion/.ssh/id_ecdsa_sk
debug3: no such identity: /home/leion/.ssh/id_ecdsa_sk: No such file or directory
debug1: Trying private key: /home/leion/.ssh/id_ed25519
debug3: no such identity: /home/leion/.ssh/id_ed25519: No such file or directory
debug1: Trying private key: /home/leion/.ssh/id_ed25519_sk
debug3: no such identity: /home/leion/.ssh/id_ed25519_sk: No such file or directory
debug1: Trying private key: /home/leion/.ssh/id_xmss
debug3: no such identity: /home/leion/.ssh/id_xmss: No such file or directory
debug2: we did not send a packet, disable method
debug3: authmethod_lookup keyboard-interactive
debug3: remaining preferred: password
debug3: authmethod_is_enabled keyboard-interactive
debug1: Next authentication method: keyboard-interactive
debug2: userauth_kbdint
debug3: send packet: type 50
debug2: we sent a keyboard-interactive packet, wait for reply
debug3: receive packet: type 51
debug1: Authentications that can continue: publickey,password,keyboard-interactive
debug3: userauth_kbdint: disable: no info_req_seen
debug2: we did not send a packet, disable method
debug3: authmethod_lookup password
debug3: remaining preferred: 
debug3: authmethod_is_enabled password
debug1: Next authentication method: password
root@lfs9.0's password: 

```

`diff` 对比两者输出注意到在使用秘钥协商的时候root用户登录过程相比普通用户登录过程的不同之处的关键点在于：
```
...
debug3: send packet: type 50
debug3: receive packet: type 51
...
```

## 原因：
使用命令 `ls -alh -d /root` 发现 /root 目录的属主是 nobody。
```
ls -alh -d /root  
drwxr-x--- 8 nobody root 4.0K  8月 12 15:18 /root
```

## 解决方法：
修正权限问题：

```
chown -R root.root /root
chmod 0550 /root
chmod 0700 /root/.ssh
chmod 0600 /root/.ssh/authorized_keys
```

## 总结：
重新梳理错误原因：客户端在用秘钥协商认证方式后，服务端由于对 root 的家目录（/root）不正确的权限问题影响无法读取 /root/.ssh/authorized_keys 文件因此无法验证公钥信息，也就是说服务器端已经接受导入了客户端的公钥，但登录认证时无法使用该公钥加密ssh通讯信道，从而无法认证客户端的登录操作。

 ## 参考：
 [sshd - SSH-Key authentication fails - Super User](https://superuser.com/questions/1137438/ssh-key-authentication-fails)
 [centos7 - Unable to ssh with authorized keys, password always prompted - Server Fault](https://serverfault.com/questions/1041098/unable-to-ssh-with-authorized-keys-password-always-prompted)
[Linux配置使用SSH Key登录并禁用root密码登录 - alterem - 博客园](https://www.cnblogs.com/alterem/p/11477843.html)
