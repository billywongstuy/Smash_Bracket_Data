main:
	python get_player_data.py
	python pd_to_csv.py
	python ranking.py
	rm *.pyc

refresh:
	rm Data/parsed_tournaments.json
	rm Data/players_info.json
	python get_player_data.py
	python pd_to_csv.py
	python ranking.py
	rm *.pyc

clean:
	rm *~ *.pyc
