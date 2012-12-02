useful views we should have:

- month summary: all users who visited, their total hours, whether they've gone over

- month full: all users, all visits: sorted by user should be ok
	- /beelogger/csvmonthdump/
		- doesn't yet support choosing month

- user summary: all visits in a month, doesn't make sense to have more 
	- /beelogger/csvuserdump/?pin=2
		- doesn't yet support choosing month

- day summary: everyone who's checked in/out today, and their status

- people exceeding their limits in a month


other existing dumps:

http://localhost:8080/beelogger/csvdump/
	- all time, grouped by user

http://localhost:8080/beelogger/csvuserdump/?pin=2
	- specified user's check-ins, all time

http://localhost:8080/beelogger/currentusers/
	- simple count of users currently checked in
