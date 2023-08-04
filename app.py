# WEB APP DEPLOYMENT FILE

#loading dependencies
import pandas as pd
import numpy as np
import difflib
import re
import streamlit as st
from PIL import Image
import requests
import pickle



#Load all data needed for recommendation
df_cb= pd.read_csv("cleaned_data/df_cb.csv")
popular_df= pd.read_csv("cleaned_data/popular_df.csv")
df_similarity=pd.read_csv("cleaned_data/df_similarity.csv")
df_title=pd.read_csv("cleaned_data/df_title.csv")
similar= pickle.load(open('cleaned_data/similar.pkl','rb'))
#similar_df=pd.read_csv("cleaned_data/similar_df.csv", index_col=False)


#movie poster
def get_poster(movie_id):
    url="https://api.themoviedb.org/3/movie/{}?api_key=800429a0eb302618f7e519cdce6026f7&language=en-US".format(movie_id)

    response = requests.get(url)
    response = response.json()
    path= response["poster_path"]
    poster = "http://image.tmdb.org/t/p/w500/" + path
    return poster
    

#clean movie title
def regex_clean(title):
    clean = re.sub('[^a-z0-9A-Z ]','' ,title)
    clean= clean.lower() #set all alphabets to lower case
    return clean


# CONTENT-BASED FILTERING ALGORITHM
title_list= df_cb['clean_title'].tolist()
movies= df_cb['title'].values
#similar=similar_df.drop('Unnamed: 0', axis=1)

def norm_title_cb(title:str):
    title = regex_clean(title)
    close_match = difflib.get_close_matches(title ,title_list, n = 1)[0]
    return close_match

#Recommender system for content based Algorithm
def recommender_cb(title:str):
    title = regex_clean(title)
    close_match = difflib.get_close_matches(title ,title_list, n = 1)[0]
    idx= df_cb[df_cb['clean_title']== close_match].index
    lst=similar[idx]
    df_scores= pd.DataFrame({'score':lst[0], 'title': title_list})
    df_scores= df_scores.sort_values(by= 'score', ascending=False).reset_index(drop=True).drop(index=0)
    recommended =df_scores.head(9)
    recommend_movies= recommended['title']#.tolist()
    recommended_movies=df_cb[df_cb['clean_title'].isin(recommend_movies)]['title'].tolist()
    recommend_homepage=df_cb[df_cb['clean_title'].isin(recommend_movies)]['homepage'].tolist()
    recommended_id=df_cb[df_cb['clean_title'].isin(recommend_movies)]['id'].tolist()
    recommendation=pd.DataFrame({'movies':recommended_movies, 'homepage': recommend_homepage, 'id': recommended_id})
        
    return recommendation


#COLLABORATIVE FILTERING ALGORITHM
def norm_title_cf(title:str):
    title = regex_clean(title)
    title = difflib.get_close_matches(title ,df_title['clean_title'], cutoff= 0.3, n = 1)[0]
    return title

#Recommender system for collaborative filtering Algorithm
df_similarity=df_similarity.set_index(['title'])
def recommender_cf(title:str):
    title = regex_clean(title)
    title = difflib.get_close_matches(title ,df_title['clean_title'], cutoff= 0.3, n = 1)[0]
    recommended_movies=df_similarity[title].sort_values(ascending=False).iloc[1:11]
    recommended=recommended_movies.index.tolist()
    recommended_movie=df_title[df_title['clean_title'].isin(recommended)]['title'].tolist()
    recommended_homepage=df_title[df_title['title'].isin(recommended_movie)]['homepage'].tolist()
    recommended_id=df_title[df_title['title'].isin(recommended_movie)]['id'].tolist()
    recommendation=pd.DataFrame({'movies':recommended_movie, 'homepage': recommended_homepage, 'id': recommended_id})
    
    return recommendation

#POPULARITY BASED ALGORITHM
def popular_recommender(popular_df):
    recommend_movies=popular_df.head(10)['title'].tolist()
    recommend_homepage=popular_df.head(10)['homepage'].tolist()
    recommend_id=popular_df.head(10)['id'].tolist()
    recommendation=pd.DataFrame({'movies':recommend_movies, 'homepage': recommend_homepage, 'id': recommend_id})

    return recommendation


def main():
    st.title('Movie Recommender App')

    menu=["Home", "Recommend", "About"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Home")
        st.text("Popular movies right now...")
        popular=popular_recommender(popular_df)
        col1, col2, col3, col4, col5= st.columns(5)
        col_list= [col1, col2, col3, col4, col5]
        
        j=0
        for row in popular.iterrows():
            name=row[1][0]
            homepage=row[1][1]
            id=row[1][2]
            with col_list[j]:
                st.image(get_poster(id))
                st.write(name)
                st.write('web page: ', homepage)
            j=j+1
            if j==5:
                j=0
                continue

    elif choice== "Recommend":
        st.subheader("Get Recommendations for Similar movies")
        search_title=st.selectbox('Type Movie name', movies)
        if st.button("Recommend"):
            if search_title is not None:
                st.text("Movie recommendations for: '{}'".format(norm_title_cb(search_title)))
                try:
                    result_cb=recommender_cb(search_title)
                    
                except:
                    st.text("Not found")
                
                col1, col2, col3, col4, col5= st.columns(5)
                col_list= [col1, col2, col3, col4, col5]
                j=0
                for row in result_cb.iterrows():
                    name=row[1][0]
                    homepage=row[1][1]
                    id=row[1][2]
                    with col_list[j]:
                        st.image(get_poster(id))
                        st.write(name)
                        st.write('web page: ', homepage)
                    j=j+1
                    if j==5:
                        j=0
                        continue
                
                st.subheader("People that watched '{}' also watched:".format(norm_title_cf(search_title)))
                result_cf=recommender_cf(search_title)
                col1, col2, col3, col4, col5= st.columns(5)
                col_list= [col1, col2, col3, col4, col5]
                j=0
                for row in result_cf.iterrows():
                    name=row[1][0]
                    homepage=row[1][1]
                    id=row[1][2]
                    with col_list[j]:
                        st.image(get_poster(id))
                        st.write(name)
                        st.write('web page: ', homepage)
                    j=j+1
                    if j==5:
                        j=0
                        continue
                        
    else:
        st.subheader("About")
        st.text("Movie recommendation System, built with streamlit and python")
        st.text("Aided by other python libraries such as; pandas sklearn, difflib and more")
        st.text("See popular recommendations in homepage")
        st.text("Get content based recommedations under similar movies in 'Recommend' page")
        st.text("Get collaborative filtering recommedations under similar users in 'Recommend' page")

if __name__=='__main__':
    main()
