#!/usr/bin/env bash
result=$(whiptail --menu "Welcome to ViBot Management System:" 15 50 3 1 Start 2 Stop 3 Check 4 Compare 3>&1 1>&2 2>&3 )

clear

if [ $result == 1 ]
then
	echo 'Starting Data Collections Agents'
	./src/threader.rb 1>/dev/null 2>/dev/null & disown
	ps aux | grep threader.rb
fi



if [ $result == 2 ]
then
	ps aux | grep threader.rb | tr -s ' '|cut -f'2' -d' ' | xargs kill
fi

if [ $result ==  3 ]
then
        ps aux | grep threader.rb
fi


if [ $result == 4 ]
then
	./src/compare.rb
fi
