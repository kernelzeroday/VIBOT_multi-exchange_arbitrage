#!/bin/bash

# ViBot Installation Wizard Version 1.1
# Originally forked from VPSDeploy Version 3.0
# github.com/darkerego
##################################################
# Custom Ubuntu 16.04 Install Script for Vibot
##################################################
echo
echo "  ... welcome to the                                       ";
echo "...........................................................";
echo " _    ___ __          __     ____             __           ";
echo "| |  / (_) /_  ____  / /_   / __ \___  ____  / /___  __  __";
echo "| | / / / __ \/ __ \/ __/  / / / / _ \/ __ \/ / __ \/ / / /";
echo "| |/ / / /_/ / /_/ / /_   / /_/ /  __/ /_/ / / /_/ / /_/ / ";
echo "|___/_/_.___/\____/\__/  /_____/\___/ .___/_/\____/\__, /  ";
echo "                                   /_/            /____/   ";
echo "...........................................................";
echo "        ...wizard. Powered by #!/bin/bash                  ";
echo "        $ respect the power of the shell                   ";
echo "        DarkerEgo, 2018 ~ github.com/darkerego             ";
echo

# your ssh key. script will use this if you dont specify another one
# you still watching? 
# ok, so right here you would paste your default ssh key, or the script will prompt you for one.
default_ssh_key='ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC4BFXaH5qb55o/zBIbtZXngrwoG8/vTn07n162gD9u5FDIRGJMhQsvZ6qyYL+eUvMASKDWRn4pRVMe7Xv64HtHV3CCTtqwVTasomZ0CbzDbU+xmyGd8dSL/rP+N1Ur3fAaAguuXMUwev8Q40Myz9ql8C3VEjUx5fs6cyMGO2c06pgODKJO8IaZBSqfwz6Kpgk1sy7D8dNoDO8fx5aEyezu2w4fcH29jdlotIMjaY4mDK/fvHw275e1CaOaYZ3SN7B40ilvxvdxSGy/kYspKjBuQkjzqcsf1NmtP1McNVpQP5M5UmwaIItFMw+HcZ2iGvIkJICiMAgSsUNEaBWOmG9X'

# programs to install # added ruby to list of programs to intall	
GET_LIST='irssi secure-delete openvpn tor tor-arm git ufw htop whois mosquitto mosquitto-clients python-pip python3-pip ruby'


axxHostConf(){
# source hostnames
. hosts.sh
# allow mqtt from only these servers!
sudo ufw allow in on eth0 to any port 1883 from $vi1
sudo ufw allow in on eth0 to any port 1883 from $vi2
sudo ufw allow in on eth0 to any port 1883 from $vi3
sudo ufw allow in on eth0 to any port 1883 from $vi4
# somewhat redundant
sudo ufw allow in on eth0 to any port 22 from $vi1
sudo ufw allow in on eth0 to any port 22 from $vi2
sudo ufw allow in on eth0 to any port 22 from  $vi3
sudo ufw allow in on eth0 to any port 22 from $vi4
}


install_stuff(){
if [[ ! -f "~/.done" ]] ; then 
sudo apt -y update ;\
sudo apt -y upgrade;\
sudo apt -y install $GET_LIST
if [[ ! -d /var/lib/dnscrypt ]] ; then
  sleep 1;\
  read -p "Would you to install dnscrypt-proxy (optional) ? (yes/no) : " dnscYN
  if [[ "$dnscYN" == 'yes' ]] ; then 
    # this is optional, probably  dojnt need it, its from my custom install script config
    echo 'I will now install dnscrypt-proxy. Please follow the prompts.';\
    sleep 1;\
    cd /usr/local/src;\
    sudo git clone https://github.com/simonclausen/dnscrypt-autoinstall &&\
    cd dnscrypt-autoinstall &&\
    sudo ./dnscrypt-autoinstall || echo 'Error installing dnscrypt!'
  else
    echo 'Skipping dnscrypt intstallion...'
    return 0
  fi
else
  echo 'Already got dnscrypt...'
fi
# this sets up a tor gateway, ok hold oj
sudo cp /etc/tor/torrc /etc/tor/torrc.orig
sudo cp /etc/tor/torrc /tmp/torrc && \
sudo bash -c " echo 'HiddenServiceDir /var/lib/tor/ssh_service' >>/tmp/torrc" &&\
sudo bash -c " echo 'HiddenServicePort 22 127.0.0.1:22' >>/tmp/torrc " &&\
sudo bash -c "cp /tmp/torrc /etc/tor/torrc" || exit 1

(sudo service tor restart >/dev/null 2>&1 || sudo service tor start) || (echo "Failed to start tor! Wtf?";exit 1) &&\
echo 'Your SSH .onion url:'
sleep 1;echo '..';sleep 1;echo '...';sleep 1
sudo cat '/var/lib/tor/ssh_service/hostname' 2>/dev/null >$HOME/onion;cat $HOME/onion;echo
echo '1' >"~/.done"
sleep 1;echo '..';sleep 1;echo '...';sleep 1
fi
}

harden_ssh(){

echo "Hardening moduli..."
awk '$5 > 2000' /etc/ssh/moduli > "${HOME}/moduli"
if [[ $(wc -l "${HOME}/moduli") != "0" ]] ; then
  sudo mv "${HOME}/moduli" /etc/ssh/moduli
else
  echo "Creating moduli..."
  sudo ssh-keygen -G /etc/ssh/moduli.all -b 4096
  sudo ssh-keygen -T /etc/ssh/moduli.safe -f /etc/ssh/moduli.all
  sudo mv /etc/ssh/moduli.safe /etc/ssh/moduli
  sudo rm /etc/ssh/moduli.all
fi


echo "Creating host keys..."
cd /etc/ssh
sudo rm ssh_host_*key*
sudo ssh-keygen -t ed25519 -f ssh_host_ed25519_key -N "" < /dev/null
sudo ssh-keygen -t rsa -b 4096 -f ssh_host_rsa_key -N "" < /dev/null

echo "Creating hardened config file"

echo "\
# Package generated configuration file
# See the sshd_config(5) manpage for details

# What ports, IPs and protocols we listen for
Port 22
# Use these options to restrict which interfaces/protocols sshd will bind to
#ListenAddress ::
ListenAddress 0.0.0.0:22
Protocol 2
# HostKeys for protocol version 2
HostKey /etc/ssh/ssh_host_rsa_key
HostKey /etc/ssh/ssh_host_ed25519_key
#Privilege Separation is turned on for security
UsePrivilegeSeparation yes

# Lifetime and size of ephemeral version 1 server key
KeyRegenerationInterval 3600
ServerKeyBits 4096
AllowGroups ssh-users
# Logging
SyslogFacility AUTH
LogLevel INFO

# Authentication:
LoginGraceTime 120
PermitRootLogin no
StrictModes yes

RSAAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile	%h/.ssh/authorized_keys

# harden crypto
KexAlgorithms curve25519-sha256@libssh.org,diffie-hellman-group-exchange-sha256
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-ripemd160-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-512,hmac-sha2-256,hmac-ripemd160,umac-128@openssh.com

# Don't read the user's ~/.rhosts and ~/.shosts files
IgnoreRhosts yes
# For this to work you will also need host keys in /etc/ssh_known_hosts
RhostsRSAAuthentication no
# similar for protocol version 2
HostbasedAuthentication no
# Uncomment if you don't trust ~/.ssh/known_hosts for RhostsRSAAuthentication
#IgnoreUserKnownHosts yes

# To enable empty passwords, change to yes (NOT RECOMMENDED)
PermitEmptyPasswords no

# Change to yes to enable challenge-response passwords (beware issues with
# some PAM modules and threads)
ChallengeResponseAuthentication no

# Change to no to disable tunnelled clear text passwords
PasswordAuthentication no

# Kerberos options
#KerberosAuthentication no
#KerberosGetAFSToken no
#KerberosOrLocalPasswd yes
#KerberosTicketCleanup yes

# GSSAPI options
#GSSAPIAuthentication no
#GSSAPICleanupCredentials yes

X11Forwarding no
X11DisplayOffset 10
PrintMotd no
PrintLastLog yes
TCPKeepAlive yes
#UseLogin no

#MaxStartups 10:30:60
#Banner /etc/issue.net

# Allow client to pass locale environment variables
AcceptEnv LANG LC_*

Subsystem sftp /usr/lib/openssh/sftp-server -f auth -l info

# Set this to 'yes' to enable PAM authentication, account processing,
# and session processing. If this is enabled, PAM authentication will
# be allowed through the ChallengeResponseAuthentication and
# PasswordAuthentication.  Depending on your PAM configuration,
# PAM authentication via ChallengeResponseAuthentication may bypass
# the setting of 'PermitRootLogin without-password'.
# If you just want the PAM account and session checks to run without
# PAM authentication, then enable this but set PasswordAuthentication
# and ChallengeResponseAuthentication to 'no'.
UsePAM yes" >/tmp/sshd_config

if [[ -f /tmp/sshd_config ]] ; then
  sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.orig
  sudo mv /tmp/sshd_config /etc/ssh/sshd_config
  if [[ "$?" -eq "0" ]] ; then
    echo "Success!" ; return 0
  else 
   echo "Fail!" ; return 1 
  fi
fi
}


add_users(){

sudo groupadd ssh-users
unset users
unset added_one
echo "I need to know which users should be allowed to ssh in to this server."
while [[ -z "$users" ]] ; do
  echo "Please enter each user followed by a space in this format: 'user user2 user3'"
  read -p "Enter users : " users
done
for i in $(echo "$users") ; do
  if grep "^$i.*sh$" /etc/passwd >/dev/null 2>&1 ; then
    echo "Adding user $i to group ssh-users..."
    sudo usermod -a -G ssh-users $i && export added_one=true
  else
    echo "Error: $i is not a valid user account on this system!"
    read -p "Try again or add user to system? (y/n/add)  :" tryagain
    if [[ "$tryagain" == 'y' ]]; then
      read -p "Please enter a valid user account: " user_
      if [[ -n "$user_" ]] ; then 
        if grep "^$user_.*sh$" /etc/passwd >/dev/null 2>&1; then
          echo "User $user_ is valid!"
          sudo usermod -a -G ssh-users $i && export added_one=true
        fi
      fi
    
    elif [[ "$tryagain" == 'add' ]]; then
      if grep "^$i.*sh$" /etc/passwd >/dev/null 2>&1 ; then
        echo 'This account already exists!'
        sudo usermod -a -G ssh-users $i  &&  export added_one=true && echo " Successfully addeded $i"
      else
        #read -rsp "Enter password for user account $i : " thispw
        #echo 'Encrypting passsword...'
        #mkpasswd -V >/dev/null 2>&1 || sudo apt update && sudo apt -y -qq install whois
        #thispwd="$(mkpasswd -m sha-512 \"$thispw\")"
        #unset thispw
        #useradd -p "$thispwd" -s /bin/bash -G ssh-users $i
        adduser $i
        sudo usermod -a -G ssh-users $i
        if [[ $? -eq "0" ]] ; then
          echo "Success..."
        else
          echo 'Failed...'
        fi
      fi
    else
      echo 'Ok then'
   fi
fi
done
if $added_one ; then return 0 ; else return 1 ; fi
}

firewall_up(){
echo 'Hardening ssh...'
harden_ssh
for x in $(seq 1 5) ; do 
echo "Attempt $x/5 ..."
add_users && break ||\
 echo 'We need a valid user account. Try again!'
done
if $added_one ; then

  sudo ufw allow ssh
  sudo ufw enable
  echo 'SSH host keys have changed. You can safely ignore that warning.'
  read -p "Have you confirmed that you can log in with your public key? (yes/no)" I_am_not_an_idiot
  if ([[ $I_am_not_an_idiot == "yes" ]]||[[ $I_am_not_an_idiot == "y" ]]||[[ $I_am_not_an_idiot == "Y" ]]) ; then
    sudo service ssh restart
  else
    echo 'Remember to restart ssh after you have confirmed you can log in with your key!'
  fi
fi
}

conf_ssh(){
echo 'Configuring ssh'
mkdir ~/.ssh
chmod 700 ~/.ssh
read -p "Please paste your ssh key or press enter to use default" ssh_key
if [[ -n "$ssh_key" ]] ; then
  echo "$ssh_key" >~/.ssh/authorized_keys
else
  echo "$default_ssh_key" >~/.ssh/authorized_keys
fi

read -p 'Would you like to add this key to another user accounts (yes/no) : ' addToAcct

if [[ "$addToAcct" == 'yes' ]] ; then
    read -p "Please enter the user account" authUser

    if [[ -n "$authUser" ]] ; then 
        echo "$ssh_key" >> "/home/${authUser}/.ssh/authorized_keys"
        usermod -a -G "$authuser" ssh-users
        if [[ "$?" -eq "0" ]] ; then  echo 'Success.'   ;else echo 'Failed to add key to user account' ; fi
    fi
fi

echo 'Contents of authorized_keys:'
cat ~/.ssh/authorized_keys
cat "/home/${authUser}/.ssh/authorized_keys" 2>/dev/null

chmod 600 ~/.ssh/authorized_keys
chmod 600 "/home/${authUser}/.ssh/authorized_keys" 2>/dev/null

ip=$(wget -qO-  ipecho.net/plain) >/dev/null &&\
echo "Success. You can now test logging in with ssh:" &&\
echo "       $ ssh -i ~/.ssh/<key file> -v $USER@$ip"|| echo 'Temporary error. Try logging in with ssh key'

}


viBotDeps(){

echo
sleep 1
echo
sleep 1
echo

read -p 'Server configuration is complete, would you like to install vibot dependencies? (yes/no) : ' viDeps
if [[ "$viDeps" -eq "yes" ]] ; then
#  . install-deps.sh
  vibot_deps
else
  echo 'Quitting!'
fi


}

vibot_deps(){
# add python3.6 repos & install
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get -y install python3.6

# add golang repos & install
# if you have trouble, first remove old versions maybe
#sudo apt -y -qq remove golang
sudo add-apt-repository ppa:gophers/archive
sudo apt-get update
sudo apt-get -y install golang-1.10-go
# symlink
sudo ln -s /usr/lib/go-1.10/bin/go /usr/local/bin/go


# configure mosquitto

sudo bash -c 'printf "password_file /etc/mosquitto/passwd\nallow_anonymous false\n" >>/etc/mosquitto.conf'
cd /etc/mosquitto
read -p 'Enter the broker password (found in one of the many config files). press enter to continue...'
sudo mosquitto_passwd -c passwd vibot

sudo ufw allow 1883/tcp

# set the go path

echo 'export GOPATH=$HOME/go' >>~/.bashrc
sudo python3.6 -m pip install paho-mqtt cexio
mkdir ~/src 2>/dev/null;cd ~/src
git clone https://github.com/s4w3d0ff/python-poloniex.git && cd python-poloniex
sudo python3.6 setup.py build
sudo python3.6 setup.py install
mkdir ~/lib;cd ~/lib;wget https://raw.githubusercontent.com/darkerego/bittrex-python3/master/bittrex.py
}




selectViServer(){ 
read -p 'Which ViBoT server am I configuring? (vi1/vi2/vi3/vi4) : ' viSrv

echo "Configuring this server as $viSrv"
read -p 'Please ensure you are running as the correct user... Press any key to continue...' whatEver
if [[ "$(id -u)" -eq '0' ]]; then
  echo 'Not installing vibot as root! Bailing!'
  exit 1
fi

case $viSrv in

vi1)
read -p 'Configuring server as Vi1. Procceed ? (yes/no) : ' proceedYN

if [[ "$proceedYN" == 'yes' ]]; then
  echo 'Quitting at user request.'
fi


sudo ufw allow in on eth0 to any port 6697
cd ~
git clone https://bit6io@bitbucket.org/bit6io/vi1.git &&\
echo "$viSrv has been successfully configured!" ||\
{ echo 'Error cloning from repo! Check your network!' ; exit 1 ; }


;;

vi2)
read -p 'Configuring server as Vi2. Procceed ? (yes/no) : ' proceedYN

if [[ "$proceedYN" == 'yes' ]]; then
  echo 'Quitting at user request.'
fi



cd ~
git clone https://bit6io@bitbucket.org/bit6io/vi2.git &&\
echo "$viSrv has been successfully configured!" ||\
{ echo 'Error cloning from repo! Check your network!' ; exit 1 ; }
;;


vi3)
read -p 'Configuring server as Vi3. Procceed ? (yes/no) : ' proceedYN

if [[ "$proceedYN" == 'yes' ]]; then
  echo 'Quitting at user request.'
fi


cd ~
git clone https://bit6io@bitbucket.org/bit6io/vi3.git &&\
echo "$viSrv has been successfully configured!" ||\
{ echo 'Error cloning from repo! Check your network!' ; exit 1 ; }
;;


vi4)
read -p 'Configuring server as Vi4. Procceed ? (yes/no) : ' proceedYN

if [[ "$proceedYN" == 'yes' ]]; then
  echo 'Quitting at user request.'
fi



cd ~
git clone https://bit6io@bitbucket.org/bit6io/vi4.git &&\
echo "$viSrv has been successfully configured!" ||\
{ echo 'Error cloning from repo! Check your network!' ; exit 1 ; }
;;

esac

cd $viSrv
mv * .. >/dev/null 2>&1
mv .* .. >/dev/null 2>&1
cd ~
rm -rf $viSrv
echo 'Vibot has been installed on this server. Note that the ssh host keys have changed. Try logging in and out if you have problems.'
}

sudoUp(){
if [[ ! -f ~/.ssh/authorized_keys ]]  ; then
conf_ssh
fi

echo 'Done, updating system and installing software'

which sudo >/dev/null 2>&1 &&\
if groups $USER|grep sudo >/dev/null 2>&1 ; then gotSudo='True' ;fi


if [[ "$gotSudo" != "True" ]]; then
  (export user=$USER
  su -c "apt -y update ;apt -y install sudo;usermod -a -G sudo $user"
  echo 'Please log out of ssh and in again, and rerun this script to finish.')
fi
}

# ok now it will run all the  way through without error


case "$@" in
'--install'|'-a')

install_stuff
firewall_up
sudoUp
viBotDeps
selectViServer
axxHostConf

;;
'--deploy-only'|'-D')
install_stuff
firewall_up
sudoUp

;;

'--vibot'|'-vb')

selectViServer
axxHostConf

;;
--help|-h)
echo 'Usage: '
echo "     $0 --install / -a : Install Everything"
echo "     $0 --deploy-only/-D : Just Configure the Server Normally, Do not install vibot"
echo "     $0 --vibot/-vb : Just install vibot, don't configure server"
echo "     $0 --help / -h : Show usage "
;;

*)
read -p 'No option selected  (run deploy.sh --help), proceed with full installation? (yes/no) :' prcdYn
if [[ "$prcdYn" == 'yes' ]] ; then

install_stuff
firewall_up
sudoUp
viBotDeps
selectViServer
axxHostConf

else
echo 'Run --help'
exit
fi

;;

esac


exit
