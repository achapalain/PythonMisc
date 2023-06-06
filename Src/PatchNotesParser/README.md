This is a simple chagnge log timeline analyzer.
It help visualizing the timeframe of updates for games and allow some highlights. Ex: frequency of new levels updates, new characters, bugfixes, etc.
Red dots are used for versions without dates, so the release date is a simple interpolation between the nearest patches.

* How to use?
- Find some changelog on the internet.
- Copy&Paste it in a text file, this will be used for the analyzer
- Currently only iOS AppStore changelog text format is supported, but other format parsing could easily be added
- Run patchNotesParser.py
- Click File>Load... and open your file

* How to add highlight tracks?
You can add highlight grammar at the beginning of file, using the following format (see pre-existing files samples for reference):

Highlight track name 1
	Searched pattern 1.1
	Searched pattern 1.2
Highlight track name 2
	Searched pattern 2.1
	...
