# Group 07 - Movie Recommendation System - Requirements

## 1. Product vision
SmartCine is an intelligent movie recommendation platform for film enthusiasts who struggle to decide what to watch next. Instead of making users browse through large catalogs themselves, SmartCine learns from their viewing history and ratings to provide personalized recommendations that increasingly match their tastes.

## 2. Personas

### 2.1. Persona 1

**Ngọc Duyên** - 19 - second-year student at Hanoi University of Science and Technology, living in a rented room.

**Description:** Duyen usually takes advantage of mealtimes or her free time to watch movies alone. Since she does not want to pay for movies, she mainly searches for movies on free movie-streaming websites and also frequently refers to online movie-review groups to discover new movies. She particularly enjoys movies that combine romance and thriller elements, especially those with complex plots and many unexpected “twists.” However, when there are too many choices and she does not know what to watch, Duyen often goes back to watching old movies that she has enjoyed before. She is also quite likely to stop watching a movie if its pace is slow and not engaging enough. Since she often watches movies during short periods of time, such as mealtimes, Duyen wants the system to provide suitable recommendations from the beginning, for example, by asking who she is watching the movie with.

**Desired recommendation feature:** Asking “Who are you watching this movie with?”

**Goal:** Make use of her mealtimes to watch movies and relax after a day of studying.

**Blocked by:** Too many choices and difficulty determining which movies are worth watching.

**In her words:** “There are so many movies to watch, but finding one I actually want to watch is the problem.”

**Technical skill:** Comfortable using smartphones, movie-streaming websites, social media, and online review groups. She primarily uses her phone when searching for and choosing movies.

### 2.2. Persona 2

**Thuy Trang** - 20 - third-year student at Hanoi University of Civil Engineering, living in a rented room.

**Description:** Trang usually takes advantage of mealtimes to watch movies alone, mainly searching for movies on free movie-streaming websites. She particularly enjoys horror or thriller movies with a sad and emotional tone. However, choosing a movie is not always that simple. When she cannot find a suitable movie, Trang often returns to movies she has watched before, sometimes turning to recommendations on TikTok. For Trang, the actors' appearance is a key factor in determining whether she continues watching a movie. She would like the system to ask about the topic or content she wants to watch beforehand to narrow down the choices. Normally, she takes only about two minutes to choose a movie, but when watching with her boyfriend or friends, the process can take considerably longer because she needs to consider the preferences of multiple people.

**Goal:** Quickly find a movie that matches her preferences and the preferences of the people she is watching with.

**Blocked by:** Difficulty choosing a movie when watching with her boyfriend or friends because their preferences may differ; she also needs to search through multiple sources before finding a suitable movie.

**In her words:** “Normally, I choose a movie very quickly, but when watching with others, I can never seem to decide what to watch.”

**Technical skill:** Familiar with smartphones and social media, especially TikTok. The interface should be visually clear, simple, and easy to use, particularly for first-time users.
## 3. Scenarios

## 4. User stories

## 5. Business rules
### BR1 - Watched Movies
The system must not recommend movies thet the user has already watched. 

***Worked example:**
If a user has watched **25 movies**, those 25 move is must be excluded from the recommendation list.

### BR2 - Age Rating Limit
The system must not recommend movies above the user's allowed age rating.

*** Worked example:**
If a user's age is **15**, movies rated **18** must not appear in their recommendations.

### BR3 - Maximum Recommendations
Each recommendation engine finds **18 suitable movies**, SmartCine must display only the top **10** recommendations.

**Worked example:**
If a user has rated only **3 movies**, SmartCine must not generate a fully personalized recommendation list and should use the cold-start recommendation rules instead.
### BR4 - Minimum Movie Rating 
A movie must have a rating of **6.0/10** to be included in personalized recommendations.

**Worked example:**
If a movie has a rating of **5.8/10**, it must be excluded. A movie rated **7.2/10** can be recommended.

### BR5 Minimum Preference Data
A returning user's personalized recommendations must use at least **5 rated or watched movies** as preference data.

**Worked example:**  
If a user has rated only **3 movies**, SmartCine must not generate a fully personalized recommendation list and should use the cold-start recommendation rules instead.

### BR6 — Cold-Start Recommendations
New users with fewer than **5 ratings** must receive recommendations based on trending or critically acclaimed movies rather than personalized preference data.

**Worked example:**  
If a new user has rated **2 movies**, SmartCine must use trending or critically acclaimed movies instead of personalized collaborative filtering.

### BR7 — Unique Recommendations
A movie must not appear more than **once** in the same recommendation result.

**Worked example:**  
If the system generates **10 recommendations**, all **10 movie IDs must be unique**. The same movie cannot appear at positions **3 and 8**.

### BR8 — Minimum Rating Count
A movie must have at least **100 ratings** to qualify for the critically acclaimed recommendation pool.

**Worked example:**  
If Movie A has **85 ratings** with an average score of **8.9/10**, it must be excluded. Movie B with **500 ratings** and an average score of **8.4/10** qualifies.
## 6. Screens and flow