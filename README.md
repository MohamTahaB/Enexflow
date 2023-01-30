# Exercice for Software engineering interns (optimization)
This small web server exposes a simple API where, given a JSON structure
as described in the class ```DailyData``` and ```DailyDecision```, return the optimal consumption
of raw materials (in our case, water and electricity), such that the revenue from selling hydrogen
production, as well as raw material leftover is maximal. For this problem, we assume that the company
does not get its required water and electricity from the grid (in other terms, we do not consider the 
case where the company purchases its raw materials, but rather gets them for free).

