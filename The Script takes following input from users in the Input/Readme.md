The Script takes following input from users in the Input/Output Console: 1). User Name 2). Email address 3). Favourite Shows Name

This is followed by storing these data into MySQL Database.

Now, the long string of TV_Series_input is split into Individual Series.

Now, web scraping for each individual series begins. :) First, the series name having spaces, is replaced by '+' and search on IMDb occurs for the series name. Now, we select the first search result and read from that page.

The current page is reading the series base page. We will now read data from the latest season page of the series.

Now, using the BeautifulSoup4 library, we will gather the episode dates from class: "airdate".

Three cases of Series are:

Exact date is mentioned for next episode.
Only year is mentioned for next season.
All the seasons are finished and no further details are available.
For case 3, I am looking at the title of the series, for Example: Friends series title will show: Friends (1994–2004) If show endDate exists, it falls under case 3.

For case 2, we look at the first episode date of the latest season. If the date format is 'YYYY', then it falls under case 2. Example: Game of Thrones, next season begins at 2019.

For case 1, we iterate over all the episode dates from class: "airdate" and go to the date which is larger than today's date. Example: The Big Bang Theory

Status: (for use case 1) Next episode airs on <yyyy - mm - dd>.

(for use case 2) The next season begins in < yyyy >.

(for use case 3) The show has finished streaming all its episodes.

These dates are stored in an array and sent to the user Email Address by my script
