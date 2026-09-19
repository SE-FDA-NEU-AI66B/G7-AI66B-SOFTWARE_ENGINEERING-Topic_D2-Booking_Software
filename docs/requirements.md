# Group 07 - Movie Recommendation System - Requirements

## 1. Product vision
SmartCine is an intelligent movie recommendation platform for film enthusiasts who struggle to decide what to watch next. Instead of making users browse through large catalogs themselves, SmartCine learns from their viewing history and ratings to provide personalized recommendations that increasingly match their tastes.

## 2. Personas

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